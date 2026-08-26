from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProfileHandler:
    """Handle user profiles and profile-related callbacks."""

    @staticmethod
    def _get_name(user_data: dict, telegram_user=None) -> str:
        """Safely get a user's display name."""
        name = user_data.get("first_name")

        if not name and telegram_user:
            name = telegram_user.first_name

        return str(name or "Player")

    @staticmethod
    def _format_date(value) -> str:
        """Safely format a MongoDB datetime."""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return "Unknown"

    @staticmethod
    async def _get_user_data(user_id: int):
        """Load user and economy data."""
        user_data = await db.find_one(
            "users",
            {"telegram_id": user_id}
        )

        economy = await db.find_one(
            "economy",
            {"user_id": user_id}
        )

        return user_data, economy

    @staticmethod
    def _profile_keyboard():
        """Main profile keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📊 Full Stats",
                    callback_data="profile_full"
                ),
                InlineKeyboardButton(
                    "🎯 Achievements",
                    callback_data="profile_achievements"
                )
            ],
            [
                InlineKeyboardButton(
                    "📜 Titles",
                    callback_data="profile_titles"
                ),
                InlineKeyboardButton(
                    "💰 Economy",
                    callback_data="profile_economy"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Menu",
                    callback_data="main_menu"
                )
            ]
        ])

    @staticmethod
    def _back_keyboard():
        """Back to profile keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 Back to Profile",
                    callback_data="profile"
                )
            ]
        ])

    @staticmethod
    async def _safe_edit(
        query,
        text: str,
        reply_markup=None
    ):
        """
        Safely edit a Telegram message.

        No parse_mode is used intentionally.
        This prevents Markdown/HTML entity errors caused
        by usernames, titles and other dynamic data.
        """
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return True

        except Exception as edit_error:
            logger.warning(
                "Could not edit profile message: %s",
                edit_error
            )

            try:
                await query.message.reply_text(
                    text=text,
                    reply_markup=reply_markup
                )
                return True

            except Exception as reply_error:
                logger.error(
                    "Could not send profile message: %s",
                    reply_error
                )
                return False

    @staticmethod
    async def profile_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /profile command and profile callback."""

        user = update.effective_user

        if not user:
            return

        try:
            user_data, economy = await ProfileHandler._get_user_data(
                user.id
            )

            if not user_data:
                if update.message:
                    await update.message.reply_text(
                        "❌ Please start the bot with /start first."
                    )
                elif update.callback_query:
                    await update.callback_query.answer(
                        "❌ Please start the bot with /start first.",
                        show_alert=True
                    )
                return

            achievements = await db.find(
                "achievements",
                {"user_id": user.id}
            )

            name = ProfileHandler._get_name(
                user_data,
                user
            )

            username = user_data.get("username")

            if username:
                username_text = f"@{username}"
            else:
                username_text = "N/A"

            level = user_data.get("level", 1)
            xp = user_data.get("xp", 0)
            respect = user_data.get("respect", 0)

            coins = economy.get("coins", 0) if economy else 0
            gems = economy.get("gems", 0) if economy else 0
            bank = economy.get("bank", 0) if economy else 0

            wins = user_data.get("total_wins", 0)
            losses = user_data.get("total_losses", 0)
            games_played = user_data.get("games_played", 0)

            daily_streak = (
                economy.get("daily_streak", 0)
                if economy
                else 0
            )

            titles = user_data.get("titles", [])

            if not isinstance(titles, list):
                titles = []

            titles_text = ", ".join(
                str(title) for title in titles
            ) if titles else "None"

            created_at = user_data.get("created_at")

            member_since = ProfileHandler._format_date(
                created_at
            )

            profile_text = (
                "👤 Profile\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"

                f"Name: {name}\n"
                f"Username: {username_text}\n"
                f"Level: {level}\n"
                f"XP: {xp} / {level * 100}\n"
                f"Respect: {respect}\n\n"

                "💰 Economy\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"Coins: {coins}\n"
                f"Gems: {gems}\n"
                f"Bank: {bank}\n\n"

                "📊 Statistics\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"Wins: {wins}\n"
                f"Losses: {losses}\n"
                f"Games Played: {games_played}\n"
                f"Daily Streak: {daily_streak}\n\n"

                f"🏆 Achievements: {len(achievements)}\n"
                f"Titles: {titles_text}\n\n"

                f"📅 Member Since: {member_since}"
            )

            keyboard = ProfileHandler._profile_keyboard()

            # Callback request
            if update.callback_query:
                query = update.callback_query

                try:
                    await query.answer()
                except Exception:
                    pass

                await ProfileHandler._safe_edit(
                    query,
                    profile_text,
                    keyboard
                )
                return

            # /profile command
            if update.message:
                await update.message.reply_text(
                    profile_text,
                    reply_markup=keyboard
                )

        except Exception as error:
            logger.exception(
                "Error in profile_command: %s",
                error
            )

            try:
                if update.callback_query:
                    await update.callback_query.answer(
                        "❌ Could not load your profile.",
                        show_alert=True
                    )
                elif update.message:
                    await update.message.reply_text(
                        "❌ Could not load your profile. "
                        "Please try again later."
                    )
            except Exception:
                pass

    @staticmethod
    async def handle_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle profile callback buttons."""

        query = update.callback_query

        if not query:
            return

        try:
            await query.answer()
        except Exception:
            pass

        user = update.effective_user

        if not user or not query.message:
            return

        data = query.data

        try:

            # =========================================================
            # FULL STATISTICS
            # =========================================================

            if data == "profile_full":

                user_data, economy = (
                    await ProfileHandler._get_user_data(
                        user.id
                    )
                )

                if not user_data:
                    await query.answer(
                        "❌ Please start the bot first.",
                        show_alert=True
                    )
                    return

                name = ProfileHandler._get_name(
                    user_data,
                    user
                )

                stats = user_data.get("stats", {})

                if not isinstance(stats, dict):
                    stats = {}

                mafia = stats.get("mafia", {})
                space = stats.get("space", {})
                zombies = stats.get("zombies", {})
                pirates = stats.get("pirates", {})
                cards = stats.get("cards", {})

                stats_text = (
                    f"📊 Full Statistics for {name}\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n\n"

                    "🎮 Game Stats:\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Mafia RPG: Level "
                    f"{mafia.get('level', 1)}\n"
                    f"Space Empire: Level "
                    f"{space.get('level', 1)}\n"
                    f"Zombies: Level "
                    f"{zombies.get('level', 1)}\n"
                    f"Pirates: Level "
                    f"{pirates.get('level', 1)}\n"
                    f"Cards: Level "
                    f"{cards.get('level', 1)}\n\n"

                    "💎 Economy:\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Total Earned: "
                    f"{economy.get('total_earned', 0) if economy else 0}\n"
                    f"Total Spent: "
                    f"{economy.get('total_spent', 0) if economy else 0}\n"
                    f"Gems Earned: "
                    f"{economy.get('total_gems_earned', 0) if economy else 0}"
                )

                await ProfileHandler._safe_edit(
                    query,
                    stats_text,
                    ProfileHandler._back_keyboard()
                )

                return

            # =========================================================
            # ACHIEVEMENTS
            # =========================================================

            if data == "profile_achievements":

                achievements = await db.find(
                    "achievements",
                    {"user_id": user.id}
                )

                if not achievements:
                    text = (
                        "🎯 Achievements\n\n"
                        "No achievements yet.\n"
                        "Keep playing to earn them!"
                    )
                else:
                    lines = [
                        "🎯 Your Achievements",
                        "━━━━━━━━━━━━━━━━━━━━━",
                        ""
                    ]

                    for index, achievement in enumerate(
                        achievements[:10],
                        1
                    ):
                        ach_name = str(
                            achievement.get(
                                "name",
                                "Unknown"
                            )
                        )

                        description = str(
                            achievement.get(
                                "description",
                                ""
                            )
                        )

                        lines.append(
                            f"{index}. {ach_name}"
                        )

                        if description:
                            lines.append(
                                f"   {description}"
                            )

                        lines.append("")

                    if len(achievements) > 10:
                        lines.append(
                            f"... and "
                            f"{len(achievements) - 10} more"
                        )

                    text = "\n".join(lines)

                await ProfileHandler._safe_edit(
                    query,
                    text,
                    ProfileHandler._back_keyboard()
                )

                return

            # =========================================================
            # TITLES
            # =========================================================

            if data == "profile_titles":

                user_data = await db.find_one(
                    "users",
                    {"telegram_id": user.id}
                )

                if not user_data:
                    await query.answer(
                        "❌ User profile not found.",
                        show_alert=True
                    )
                    return

                titles = user_data.get(
                    "titles",
                    []
                )

                if not isinstance(titles, list):
                    titles = []

                if titles:
                    lines = [
                        "📜 Your Titles",
                        "━━━━━━━━━━━━━━━━━━━━━",
                        ""
                    ]

                    for title in titles:
                        lines.append(
                            f"• {str(title)}"
                        )

                    text = "\n".join(lines)

                else:
                    text = (
                        "📜 Titles\n\n"
                        "No titles yet.\n"
                        "Earn titles through gameplay!"
                    )

                await ProfileHandler._safe_edit(
                    query,
                    text,
                    ProfileHandler._back_keyboard()
                )

                return

            # =========================================================
            # ECONOMY
            # =========================================================

            if data == "profile_economy":

                economy = await db.find_one(
                    "economy",
                    {"user_id": user.id}
                )

                if not economy:
                    text = (
                        "💰 Economy Details\n\n"
                        "No economy data found."
                    )
                else:
                    text = (
                        "💰 Economy Details\n"
                        "━━━━━━━━━━━━━━━━━━━━━\n\n"

                        f"Coins: "
                        f"{economy.get('coins', 0)}\n"

                        f"Gems: "
                        f"{economy.get('gems', 0)}\n"

                        f"Bank Balance: "
                        f"{economy.get('bank', 0)}\n"

                        f"Total Earned: "
                        f"{economy.get('total_earned', 0)}\n"

                        f"Total Spent: "
                        f"{economy.get('total_spent', 0)}\n"

                        f"Gems Earned: "
                        f"{economy.get('total_gems_earned', 0)}\n"

                        f"Daily Streak: "
                        f"{economy.get('daily_streak', 0)}\n"

                        f"Properties: "
                        f"{len(economy.get('properties', []))}\n"

                        f"Businesses: "
                        f"{len(economy.get('businesses', []))}"
                    )

                await ProfileHandler._safe_edit(
                    query,
                    text,
                    ProfileHandler._back_keyboard()
                )

                return

            # =========================================================
            # BACK TO PROFILE
            # =========================================================

            if data == "profile":

                await ProfileHandler.profile_command(
                    update,
                    context
                )

                return

            # =========================================================
            # MAIN MENU
            # =========================================================

            if data == "main_menu":

                from keyboards.menus import get_main_menu

                keyboard = await get_main_menu(
                    user.id
                )

                await ProfileHandler._safe_edit(
                    query,
                    "🎮 Select a game to play:",
                    keyboard
                )

                return

        except Exception as error:
            logger.exception(
                "Error handling profile callback '%s': %s",
                data,
                error
            )

            try:
                await query.answer(
                    "❌ Something went wrong. Please try again.",
                    show_alert=True
                )
            except Exception:
                pass


profile_handler = ProfileHandler()
