from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db

class LeaderboardHandler:
    @staticmethod
    async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /top command"""
        keyboard = [
            [
                InlineKeyboardButton("💰 Richest", callback_data="top_richest"),
                InlineKeyboardButton("📈 Highest Level", callback_data="top_level")
            ],
            [
                InlineKeyboardButton("⭐ Most Respect", callback_data="top_respect"),
                InlineKeyboardButton("⚔️ Strongest", callback_data="top_strength")
            ],
            [
                InlineKeyboardButton("🏆 Most Wins", callback_data="top_wins"),
                InlineKeyboardButton("🏅 Best Gang", callback_data="top_gang")
            ],
            [
                InlineKeyboardButton("🐉 Best Dragon Trainer", callback_data="top_dragon"),
                InlineKeyboardButton("🏴‍☠️ Best Pirate", callback_data="top_pirate")
            ],
            [
                InlineKeyboardButton("🏎️ Best Racer", callback_data="top_racer"),
                InlineKeyboardButton("🌌 Galaxy Leader", callback_data="top_galaxy")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            "🏆 **Leaderboards**\n\nSelect a category:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle leaderboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "top_richest":
            # Get richest users
            users = await db.find(
                'users',
                {},
                limit=10,
                sort=[('coins', -1)]
            )
            
            text = "💰 **Richest Players**\n\n"
            for i, user in enumerate(users, 1):
                name = user.get('first_name', 'Unknown')
                coins = user.get('coins', 0)
                text += f"{i}. {name} - {coins:,} coins\n"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Top", callback_data="top")]
                ])
            )
        
        elif data == "top_level":
            users = await db.find(
                'users',
                {},
                limit=10,
                sort=[('level', -1)]
            )
            
            text = "📈 **Highest Level Players**\n\n"
            for i, user in enumerate(users, 1):
                name = user.get('first_name', 'Unknown')
                level = user.get('level', 1)
                xp = user.get('xp', 0)
                text += f"{i}. {name} - Level {level} (XP: {xp})\n"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Top", callback_data="top")]
                ])
            )
        
        elif data == "top_respect":
            users = await db.find(
                'users',
                {},
                limit=10,
                sort=[('respect', -1)]
            )
            
            text = "⭐ **Most Respectable Players**\n\n"
            for i, user in enumerate(users, 1):
                name = user.get('first_name', 'Unknown')
                respect = user.get('respect', 0)
                text += f"{i}. {name} - {respect} respect\n"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Top", callback_data="top")]
                ])
            )
        
        elif data == "top":
            await LeaderboardHandler.top_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            await query.edit_message_text(
                "🎮 Select a game to play:",
                reply_markup=await get_main_menu(update.effective_user.id)
            )
        
        else:
            await query.edit_message_text(
                "🏆 **Leaderboard**\n\n"
                "Category coming soon!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Top", callback_data="top")]
                ])
            )

leaderboard_handler = LeaderboardHandler()
