import asyncio
import datetime
import logging
import random
from contextlib import suppress

from telegram import Update
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
        self.application = None

        self.event_service = EventService()
        self.achievement_service = AchievementService()
        self.notification_service = NotificationService()

        self.background_task = None
        self.shutdown_event = asyncio.Event()

        self.is_running = False

    # ========================================================
    # INITIALIZATION
    # ========================================================

    async def initialize(self):
        """Initialize MongoDB, Telegram application and handlers."""

        logger.info("Initializing MegaGameBot...")

        # ----------------------------------------------------
        # MongoDB
        # ----------------------------------------------------

        await db.connect()
        logger.info("MongoDB connected")

        # ----------------------------------------------------
        # Telegram Application
        # ----------------------------------------------------

        self.application = (
            Application.builder()
            .token(Config.BOT_TOKEN)
            .build()
        )

        await self.register_handlers()

        logger.info("Bot initialized successfully")

    # ========================================================
    # HANDLERS
    # ========================================================

    async def register_handlers(self):
        """Register Telegram handlers."""

        app = self.application

        # ----------------------------------------------------
        # Basic commands
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Profile
        # ----------------------------------------------------

        app.add_handler(
            CommandHandler(
                "profile",
                profile_handler.profile_command
            )
        )

        # ----------------------------------------------------
        # Economy
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Leaderboard
        # ----------------------------------------------------

        app.add_handler(
            CommandHandler(
                "top",
                leaderboard_handler.top_command
            )
        )

        # ----------------------------------------------------
        # Settings
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Admin
        # ----------------------------------------------------

        app.add_handler(
            CommandHandler(
                "admin",
                admin_handler.admin_command
            )
        )

        # ----------------------------------------------------
        # Inventory
        # ----------------------------------------------------

        app.add_handler(
            CommandHandler(
                "inventory",
                inventory_handler.inventory_command
            )
        )

        # ----------------------------------------------------
        # Trading
        # ----------------------------------------------------

        app.add_handler(
            CommandHandler(
                "trade",
                trading_handler.trade_command
            )
        )

        # ----------------------------------------------------
        # Missions
        # ----------------------------------------------------

        app.add_handler(
            CommandHandler(
                "missions",
                missions_handler.missions_command
            )
        )

        # ====================================================
        # GAME COMMANDS
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
        # GAME CALLBACKS
        # ====================================================

        game_callback_patterns = [
            r"^game_",
            r"^mafia_",
            r"^space_",
            r"^zombies_",
            r"^pirates_",
            r"^mutation_",
            r"^haunted_",
            r"^mind_",
            r"^city_",
            r"^spy_",
            r"^dragons_",
            r"^cards_",
            r"^detective_",
            r"^racing_",
            r"^main_menu",
        ]

        for pattern in game_callback_patterns:
            app.add_handler(
                CallbackQueryHandler(
                    games_handler.handle_callback,
                    pattern=pattern,
                )
            )

        # ====================================================
        # GENERAL CALLBACKS
        # ====================================================

        app.add_handler(
            CallbackQueryHandler(
                profile_handler.handle_callback,
                pattern=r"^profile",
            )
        )

        app.add_handler(
            CallbackQueryHandler(
                economy_handler.handle_callback,
                pattern=r"^(bank|balance|transactions)",
            )
        )

        app.add_handler(
            CallbackQueryHandler(
                settings_handler.handle_callback,
                pattern=r"^settings",
            )
        )

        app.add_handler(
            CallbackQueryHandler(
                admin_handler.handle_callback,
                pattern=r"^admin",
            )
        )

        app.add_handler(
            CallbackQueryHandler(
                leaderboard_handler.handle_callback,
                pattern=r"^top",
            )
        )

        app.add_handler(
            CallbackQueryHandler(
                inventory_handler.handle_callback,
                pattern=r"^inventory",
            )
        )

        app.add_handler(
            CallbackQueryHandler(
                trading_handler.handle_callback,
                pattern=r"^trade",
            )
        )

        app.add_handler(
            CallbackQueryHandler(
                missions_handler.handle_callback,
                pattern=r"^missions",
            )
        )

        # ====================================================
        # GROUP ACTIVITY
        # ====================================================

        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_group_message,
            )
        )

        # ====================================================
        # ERROR HANDLER
        # ====================================================

        app.add_error_handler(self.error_handler)

        logger.info("All Telegram handlers registered")

    # ========================================================
    # GROUP MESSAGE
    # ========================================================

    async def handle_group_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        """Handle normal group messages."""

        if not update.effective_chat:
            return

        if update.effective_chat.type not in (
            "group",
            "supergroup",
        ):
            return

        user = update.effective_user

        if not user:
            return

        try:
            # Update last activity
            await db.update_one(
                "users",
                {"telegram_id": user.id},
                {
                    "$set": {
                        "last_active": datetime.datetime.utcnow()
                    }
                },
            )

            # 1% activity reward
            if random.random() < 0.01:

                from services.economy import EconomyService

                await EconomyService.add_coins(
                    user.id,
                    random.randint(1, 5),
                    "Message bonus",
                )

        except Exception:
            logger.exception(
                "Error processing group message from user %s",
                user.id,
            )

    # ========================================================
    # ERROR HANDLER
    # ========================================================

    async def error_handler(
        self,
        update: object,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        """Global Telegram error handler."""

        error = context.error

        logger.error(
            "Telegram update error: %s",
            error,
            exc_info=error,
        )

        # Do not try to reply to every Telegram error.
        # Some errors happen when a message is already deleted,
        # callback expired, user blocked the bot, etc.

    # ========================================================
    # BACKGROUND TASK
    # ========================================================

    async def run_background_tasks(self):
        """Run periodic game maintenance."""

        logger.info("Background task started")

        while self.is_running:

            try:
                # ------------------------------------------------
                # Events
                # ------------------------------------------------

                await self.event_service.check_and_spawn_events()

                # ------------------------------------------------
                # Achievements
                # ------------------------------------------------

                await self.achievement_service.check_achievements()

                # ------------------------------------------------
                # Expired cooldowns
                # ------------------------------------------------

                await db.delete_many(
                    "cooldowns",
                    {
                        "expires_at": {
                            "$lt": datetime.datetime.utcnow()
                        }
                    },
                )

                # ------------------------------------------------
                # Notifications
                # ------------------------------------------------

                await self.notification_service.process_notifications()

                # ------------------------------------------------
                # Group worlds
                # ------------------------------------------------

                await self.update_group_worlds()

            except asyncio.CancelledError:
                logger.info("Background task cancelled")
                raise

            except Exception:
                logger.exception(
                    "Background task error"
                )

            # ----------------------------------------------------
            # Sleep
            # ----------------------------------------------------

            try:
                await asyncio.wait_for(
                    self.shutdown_event.wait(),
                    timeout=60,
                )

                # shutdown_event was triggered
                break

            except asyncio.TimeoutError:
                # Normal 60 second interval
                pass

        logger.info("Background task stopped")

    # ========================================================
    # GROUP WORLD UPDATE
    # ========================================================

    async def update_group_worlds(self):
        """Update group world statistics."""

        try:
            groups = await db.find(
                "group_worlds",
                {},
            )

            now = datetime.datetime.utcnow()

            for group in groups:

                last_active = group.get(
                    "last_active",
                    now,
                )

                hours_since = (
                    now - last_active
                ).total_seconds() / 3600

                if hours_since > 24:

                    threat_increase = min(
                        10,
                        hours_since / 24,
                    )

                    await db.update_one(
                        "group_worlds",
                        {
                            "group_id": group["group_id"]
                        },
                        {
                            "$inc": {
                                "threat_level": threat_increase
                            }
                        },
                    )

        except Exception:
            logger.exception(
                "Error updating group worlds"
            )

    # ========================================================
    # START
    # ========================================================

    async def start(self):
        """Start Telegram bot and background services."""

        await self.initialize()

        self.is_running = True

        # ----------------------------------------------------
        # Initialize Telegram application
        # ----------------------------------------------------

        await self.application.initialize()

        # ----------------------------------------------------
        # Start Telegram application
        # ----------------------------------------------------

        await self.application.start()

        # ----------------------------------------------------
        # Start polling
        # ----------------------------------------------------

        await self.application.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )

        logger.info("Starting bot polling...")

        # ----------------------------------------------------
        # Background task
        # ----------------------------------------------------

        self.background_task = asyncio.create_task(
            self.run_background_tasks(),
            name="mega_game_background_task",
        )

        logger.info("Bot is now running")

        # ----------------------------------------------------
        # Keep process alive
        # ----------------------------------------------------

        try:
            await self.shutdown_event.wait()

        finally:
            await self.stop()

    # ========================================================
    # STOP
    # ========================================================

    async def stop(self):
        """Gracefully stop the bot."""

        if not self.is_running:
            return

        logger.info("Shutting down bot...")

        self.is_running = False

        # Wake up background task immediately
        self.shutdown_event.set()

        # ----------------------------------------------------
        # Stop background task
        # ----------------------------------------------------

        if self.background_task:

            if not self.background_task.done():

                self.background_task.cancel()

                with suppress(
                    asyncio.CancelledError
                ):
                    await self.background_task

            self.background_task = None

        # ----------------------------------------------------
        # Stop Telegram updater
        # ----------------------------------------------------

        if self.application:

            try:

                if (
                    self.application.updater
                    and self.application.updater.running
                ):
                    await self.application.updater.stop()

            except Exception:
                logger.exception(
                    "Error stopping Telegram updater"
                )

            # ------------------------------------------------
            # Stop application
            # ------------------------------------------------

            try:
                if self.application.running:
                    await self.application.stop()

            except Exception:
                logger.exception(
                    "Error stopping Telegram application"
                )

            # ------------------------------------------------
            # Shutdown application
            # ------------------------------------------------

            try:
                await self.application.shutdown()

            except Exception:
                logger.exception(
                    "Error shutting down Telegram application"
                )

        # ----------------------------------------------------
        # Close MongoDB
        # ----------------------------------------------------

        try:
            await db.close()

        except Exception:
            logger.exception(
                "Error closing MongoDB"
            )

        logger.info("Bot shutdown complete")


# ============================================================
# MAIN
# ============================================================

async def main():

    bot = MegaGameBot()

    try:

        await bot.start()

    except asyncio.CancelledError:

        logger.info(
            "Main task cancelled"
        )

    except KeyboardInterrupt:

        logger.info(
            "Keyboard interrupt received"
        )

    except Exception:

        logger.exception(
            "Fatal bot error"
        )

        raise

    finally:

        # Safety cleanup
        if bot.is_running:
            await bot.stop()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        pass
