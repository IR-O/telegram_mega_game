import asyncio
import datetime
import logging
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import Config
from database.mongodb import db

from handlers.start import start_handler
from handlers.profile import profile_handler
from handlers.economy import economy_handler
from handlers.games import games_handler
from handlers.leaderboard import leaderboard_handler
from handlers.settings import settings_handler
from handlers.admin import admin_handler
from handlers.inventory import inventory_handler
from handlers.trading import trading_handler
from handlers.missions import missions_handler

from services.events import EventService
from services.achievements import AchievementService
from services.notifications import NotificationService

from games.dragons import DragonGame


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# BOT
# ============================================================

class MegaGameBot:

    def __init__(self):
        self.event_service = EventService()
        self.achievement_service = AchievementService()
        self.notification_service = NotificationService()

        self.background_task = None
        self.background_stop = asyncio.Event()

    # ========================================================
    # POST INIT
    # ========================================================

    async def post_init(self, application: Application):
        """
        Runs automatically after Telegram application initialization.
        """

        logger.info("Initializing MegaGameBot...")

        try:
            # ------------------------------------------------
            # MongoDB
            # ------------------------------------------------

            await db.connect()
            logger.info("MongoDB connected")

            # ------------------------------------------------
            # Start background worker
            # ------------------------------------------------

            self.background_stop.clear()

            self.background_task = asyncio.create_task(
                self.run_background_tasks()
            )

            logger.info("Background task started")

            logger.info("Bot initialized successfully")

        except Exception:
            logger.exception("Failed during bot initialization")
            raise

    # ========================================================
    # POST SHUTDOWN
    # ========================================================

    async def post_shutdown(self, application: Application):
        """
        Clean shutdown.
        PTB handles SIGTERM/SIGINT through run_polling().
        """

        logger.info("Starting graceful shutdown...")

        # ----------------------------------------------------
        # Stop background worker
        # ----------------------------------------------------

        self.background_stop.set()

        if self.background_task and not self.background_task.done():

            self.background_task.cancel()

            try:
                await asyncio.wait_for(
                    self.background_task,
                    timeout=5
                )
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                logger.warning(
                    "Background task did not stop within timeout"
                )
            except Exception:
                logger.exception(
                    "Error stopping background task"
                )

        # ----------------------------------------------------
        # MongoDB
        # ----------------------------------------------------

        try:
            await asyncio.wait_for(
                db.close(),
                timeout=5
            )

            logger.info("MongoDB connection closed")

        except asyncio.TimeoutError:
            logger.warning(
                "MongoDB shutdown timeout"
            )

        except Exception:
            logger.exception(
                "Error closing MongoDB"
            )

        logger.info("Bot shutdown complete")

    # ========================================================
    # REGISTER HANDLERS
    # ========================================================

    def register_handlers(self, application: Application):

        app = application

        # ====================================================
        # BASIC COMMANDS
        # ====================================================

        app.add_handler(
            CommandHandler(
                "start",
                start_handler.start_command
            )
        )

        app.add_handler(
            CommandHandler(
                "games",
                start_handler.games_command
            )
        )

        app.add_handler(
            CommandHandler(
                "help",
                start_handler.help_command
            )
        )

        app.add_handler(
            CommandHandler(
                "profile",
                profile_handler.profile_command
            )
        )

        app.add_handler(
            CommandHandler(
                "balance",
                economy_handler.balance_command
            )
        )

        app.add_handler(
            CommandHandler(
                "daily",
                economy_handler.daily_command
            )
        )

        app.add_handler(
            CommandHandler(
                "work",
                economy_handler.work_command
            )
        )

        app.add_handler(
            CommandHandler(
                "bank",
                economy_handler.bank_command
            )
        )

        app.add_handler(
            CommandHandler(
                "top",
                leaderboard_handler.top_command
            )
        )

        app.add_handler(
            CommandHandler(
                "language",
                settings_handler.language_command
            )
        )

        app.add_handler(
            CommandHandler(
                "settings",
                settings_handler.settings_command
            )
        )

        app.add_handler(
            CommandHandler(
                "admin",
                admin_handler.admin_command
            )
        )

        app.add_handler(
            CommandHandler(
                "inventory",
                inventory_handler.inventory_command
            )
        )

        app.add_handler(
            CommandHandler(
                "trade",
                trading_handler.trade_command
            )
        )

        app.add_handler(
            CommandHandler(
                "missions",
                missions_handler.missions_command
            )
        )

        # ====================================================
        # MAIN GAMES
        # ====================================================

        app.add_handler(
            CommandHandler(
                "mafia",
                games_handler.mafia_command
            )
        )

        app.add_handler(
            CommandHandler(
                "space",
                games_handler.space_command
            )
        )

        app.add_handler(
            CommandHandler(
                "zombies",
                games_handler.zombies_command
            )
        )

        app.add_handler(
            CommandHandler(
                "pirates",
                games_handler.pirates_command
            )
        )

        app.add_handler(
            CommandHandler(
                "mutation",
                games_handler.mutation_command
            )
        )

        app.add_handler(
            CommandHandler(
                "haunted",
                games_handler.haunted_command
            )
        )

        app.add_handler(
            CommandHandler(
                "mindwars",
                games_handler.mind_wars_command
            )
        )

        app.add_handler(
            CommandHandler(
                "city",
                games_handler.city_command
            )
        )

        app.add_handler(
            CommandHandler(
                "spy",
                games_handler.spy_command
            )
        )

        app.add_handler(
            CommandHandler(
                "dragons",
                games_handler.dragons_command
            )
        )

        app.add_handler(
            CommandHandler(
                "cards",
                games_handler.cards_command
            )
        )

        app.add_handler(
            CommandHandler(
                "detective",
                games_handler.detective_command
            )
        )

        app.add_handler(
            CommandHandler(
                "racing",
                games_handler.racing_command
            )
        )

        # ====================================================
        # DRAGON DIRECT COMMANDS
        # ====================================================

        app.add_handler(
            CommandHandler(
                "hatch",
                self.dragon_hatch_command
            )
        )

        app.add_handler(
            CommandHandler(
                "train",
                self.dragon_train_command
            )
        )

        # ====================================================
        # GAME CALLBACKS
        #
        # Specific patterns first.
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                games_handler.handle_callback,
                pattern=r"^(game_|mafia_|space_|zombies_|pirates_|mutation_|haunted_|mind_|city_|spy_|dragons_|cards_|detective_|racing_|main_menu)"
            )
        )

        # ====================================================
        # PROFILE CALLBACKS
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                profile_handler.handle_callback,
                pattern=r"^profile"
            )
        )

        # ====================================================
        # ECONOMY CALLBACKS
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                economy_handler.handle_callback,
                pattern=r"^(bank|balance|transactions)"
            )
        )

        # ====================================================
        # SETTINGS
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                settings_handler.handle_callback,
                pattern=r"^settings"
            )
        )

        # ====================================================
        # ADMIN
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                admin_handler.handle_callback,
                pattern=r"^admin"
            )
        )

        # ====================================================
        # LEADERBOARD
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                leaderboard_handler.handle_callback,
                pattern=r"^top"
            )
        )

        # ====================================================
        # INVENTORY
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                inventory_handler.handle_callback,
                pattern=r"^inventory"
            )
        )

        # ====================================================
        # TRADING
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                trading_handler.handle_callback,
                pattern=r"^trade"
            )
        )

        # ====================================================
        # MISSIONS
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                missions_handler.handle_callback,
                pattern=r"^missions"
            )
        )

        # ====================================================
        # GROUP MESSAGE ACTIVITY
        # ====================================================

        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_group_message
            )
        )

        # ====================================================
        # ERROR HANDLER
        # ====================================================

        app.add_error_handler(
            self.error_handler
        )

        logger.info("All Telegram handlers registered")

    # ========================================================
    # DRAGON - HATCH
    # ========================================================

    async def dragon_hatch_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        if not update.effective_user or not update.effective_message:
            return

        user_id = update.effective_user.id

        try:

            result = await DragonGame.hatch_egg(user_id)

            if result.get("error"):

                await update.effective_message.reply_text(
                    f"❌ {result['error']}"
                )

                return

            stats = result.get("stats", {})

            text = (
                "🥚 DRAGON HATCHED!\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🐉 Dragon: {result.get('dragon', 'Unknown')}\n"
                f"✨ Rarity: {result.get('rarity', 'Unknown')}\n"
                f"🌟 Element: {str(result.get('element', 'Unknown')).title()}\n\n"
                "📊 STATS\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"❤️ HP: {stats.get('hp', 0)}\n"
                f"⚔️ Attack: {stats.get('attack', 0)}\n"
                f"🛡 Defense: {stats.get('defense', 0)}\n"
                f"💨 Speed: {stats.get('speed', 0)}"
            )

            await update.effective_message.reply_text(
                text
            )

        except Exception:
            logger.exception(
                "Dragon hatch command failed"
            )

            await update.effective_message.reply_text(
                "❌ Failed to hatch dragon. Please try again."
            )

    # ========================================================
    # DRAGON - TRAIN
    # ========================================================

    async def dragon_train_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        if not update.effective_user or not update.effective_message:
            return

        user_id = update.effective_user.id

        # /train dragon_id
        if not context.args:

            player = await DragonGame.get_player(user_id)

            dragons = player.get("dragons", [])

            if not dragons:

                await update.effective_message.reply_text(
                    "🐉 You don't have any dragons yet.\n\n"
                    "Use /hatch to hatch your first dragon."
                )

                return

            lines = [
                "🐉 YOUR DRAGONS",
                "━━━━━━━━━━━━━━━━━━━━",
                "",
                "Use:",
                "/train <dragon_id>",
                ""
            ]

            for dragon in dragons:
                lines.append(
                    f"🐲 {dragon.get('name', 'Dragon')}"
                )

                lines.append(
                    f"🆔 {dragon.get('id', 'unknown')}"
                )

                lines.append(
                    f"⭐ Level: {dragon.get('level', 1)}"
                )

                lines.append("")

            await update.effective_message.reply_text(
                "\n".join(lines)
            )

            return

        dragon_id = context.args[0]

        try:

            result = await DragonGame.train_dragon(
                user_id,
                dragon_id
            )

            if result.get("error"):

                await update.effective_message.reply_text(
                    f"❌ {result['error']}"
                )

                return

            text = (
                "⚔️ DRAGON TRAINED!\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🐉 {result.get('dragon', 'Dragon')}\n"
                f"⭐ New Level: {result.get('new_level', 1)}\n\n"
                "📈 GAINS\n"
                f"❤️ HP: +{result.get('hp_gain', 0)}\n"
                f"⚔️ Attack: +{result.get('attack_gain', 0)}\n"
                f"🛡 Defense: +{result.get('defense_gain', 0)}\n"
                f"💨 Speed: +{result.get('speed_gain', 0)}"
            )

            await update.effective_message.reply_text(
                text
            )

        except Exception:
            logger.exception(
                "Dragon train command failed"
            )

            await update.effective_message.reply_text(
                "❌ Failed to train dragon."
            )

    # ========================================================
    # GROUP MESSAGE
    # ========================================================

    async def handle_group_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        chat = update.effective_chat
        user = update.effective_user

        if not chat or not user:
            return

        if chat.type not in (
            "group",
            "supergroup"
        ):
            return

        try:

            now = datetime.datetime.utcnow()

            await db.update_one(
                "users",
                {
                    "telegram_id": user.id
                },
                {
                    "$set": {
                        "last_active": now
                    }
                }
            )

            # 1% activity reward
            if random.random() < 0.01:

                from services.economy import EconomyService

                coins = random.randint(1, 5)

                await EconomyService.add_coins(
                    user.id,
                    coins,
                    "Message bonus"
                )

        except Exception:
            logger.exception(
                "Group activity handler error"
            )

    # ========================================================
    # ERROR HANDLER
    # ========================================================

    async def error_handler(
        self,
        update: object,
        context: ContextTypes.DEFAULT_TYPE
    ):

        error = context.error

        logger.error(
            "Telegram update error: %s",
            error,
            exc_info=True
        )

        # Don't try to send another Markdown-formatted
        # message from the global error handler.
        try:

            if isinstance(update, Update):

                message = update.effective_message

                if message:

                    await message.reply_text(
                        "❌ Something went wrong. Please try again."
                    )

        except Exception:

            logger.exception(
                "Error while sending error message"
            )

    # ========================================================
    # BACKGROUND TASK
    # ========================================================

    async def run_background_tasks(self):

        logger.info(
            "Background worker is running"
        )

        achievement_counter = 0

        while not self.background_stop.is_set():

            try:

                # ------------------------------------------------
                # EVENTS
                # ------------------------------------------------

                try:

                    await self.event_service.check_and_spawn_events()

                except Exception:

                    logger.exception(
                        "Event background task failed"
                    )

                # ------------------------------------------------
                # ACHIEVEMENTS
                #
                # Don't run every minute.
                # Run every 10 minutes.
                # ------------------------------------------------

                achievement_counter += 1

                if achievement_counter >= 10:

                    achievement_counter = 0

                    try:

                        await self.achievement_service.check_achievements()

                    except Exception:

                        logger.exception(
                            "Achievement background task failed"
                        )

                # ------------------------------------------------
                # COOLDOWNS
                # ------------------------------------------------

                try:

                    await db.delete_many(
                        "cooldowns",
                        {
                            "expires_at": {
                                "$lt": datetime.datetime.utcnow()
                            }
                        }
                    )

                except Exception:

                    logger.exception(
                        "Cooldown cleanup failed"
                    )

                # ------------------------------------------------
                # NOTIFICATIONS
                # ------------------------------------------------

                try:

                    await self.notification_service.process_notifications()

                except Exception:

                    logger.exception(
                        "Notification processing failed"
                    )

                # ------------------------------------------------
                # GROUP WORLDS
                # ------------------------------------------------

                try:

                    await self.update_group_worlds()

                except Exception:

                    logger.exception(
                        "Group world update failed"
                    )

                # ------------------------------------------------
                # WAIT
                # ------------------------------------------------

                try:

                    await asyncio.wait_for(
                        self.background_stop.wait(),
                        timeout=60
                    )

                except asyncio.TimeoutError:

                    pass

            except asyncio.CancelledError:

                logger.info(
                    "Background worker cancelled"
                )

                break

            except Exception:

                logger.exception(
                    "Unexpected background worker error"
                )

                try:

                    await asyncio.wait_for(
                        self.background_stop.wait(),
                        timeout=60
                    )

                except asyncio.TimeoutError:

                    pass

        logger.info(
            "Background worker stopped"
        )

    # ========================================================
    # GROUP WORLDS
    # ========================================================

    async def update_group_worlds(self):

        groups = await db.find(
            "group_worlds",
            {}
        )

        if not groups:
            return

        now = datetime.datetime.utcnow()

        for group in groups:

            try:

                if not isinstance(group, dict):
                    continue

                group_id = group.get("group_id")

                if not group_id:
                    continue

                last_active = group.get(
                    "last_active"
                )

                if not isinstance(
                    last_active,
                    datetime.datetime
                ):

                    last_active = now

                hours_since = (
                    now - last_active
                ).total_seconds() / 3600

                if hours_since <= 24:
                    continue

                current_threat = group.get(
                    "threat_level",
                    0
                )

                if not isinstance(
                    current_threat,
                    (int, float)
                ):

                    current_threat = 0

                threat_increase = min(
                    10,
                    hours_since / 24
                )

                await db.update_one(
                    "group_worlds",
                    {
                        "group_id": group_id
                    },
                    {
                        "$set": {
                            "threat_level":
                                current_threat +
                                threat_increase,
                            "updated_at": now
                        }
                    }
                )

            except Exception:

                logger.exception(
                    "Failed updating group world"
                )

    # ========================================================
    # BUILD APPLICATION
    # ========================================================

    def build_application(self):

        application = (
            Application.builder()
            .token(Config.BOT_TOKEN)
            .post_init(self.post_init)
            .post_shutdown(self.post_shutdown)
            .build()
        )

        self.register_handlers(
            application
        )

        return application

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        logger.info(
            "Starting MegaGameBot..."
        )

        application = self.build_application()

        logger.info(
            "Starting bot polling..."
        )

        # IMPORTANT:
        # Let python-telegram-bot manage:
        # - event loop
        # - polling
        # - SIGTERM
        # - SIGINT
        # - graceful shutdown
        #
        # This is much safer on Heroku than manually
        # starting/stopping updater.

        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=True,
        )


# ============================================================
# MAIN
# ============================================================

def main():

    bot = MegaGameBot()

    try:

        bot.run()

    except KeyboardInterrupt:

        logger.info(
            "Keyboard interrupt received"
        )

    except Exception:

        logger.exception(
            "Fatal bot error"
        )

        raise


if __name__ == "__main__":
    main()
