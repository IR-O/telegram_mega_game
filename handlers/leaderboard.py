from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db

class LeaderboardHandler:
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape special characters for Markdown"""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

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
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        text = "🏆 **Leaderboards**\n\nSelect a category:"
        
        if update.message:
            try:
                await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception:
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        elif update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception:
                await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle leaderboard callbacks"""
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
        
        if data == "top_richest":
            users = await db.find('users', {}, limit=10, sort=[('coins', -1)])
            text = "💰 **Richest Players**\n\n"
            for i, u in enumerate(users, 1):
                name = LeaderboardHandler.escape_markdown(u.get('first_name', 'Unknown'))
                coins = u.get('coins', 0)
                text += f"{i}. {name} - {coins:,} coins\n"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Top", callback_data="top")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "top_level":
            users = await db.find('users', {}, limit=10, sort=[('level', -1)])
            text = "📈 **Highest Level Players**\n\n"
            for i, u in enumerate(users, 1):
                name = LeaderboardHandler.escape_markdown(u.get('first_name', 'Unknown'))
                level = u.get('level', 1)
                text += f"{i}. {name} - Level {level}\n"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Top", callback_data="top")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "top_respect":
            users = await db.find('users', {}, limit=10, sort=[('respect', -1)])
            text = "⭐ **Most Respectable Players**\n\n"
            for i, u in enumerate(users, 1):
                name = LeaderboardHandler.escape_markdown(u.get('first_name', 'Unknown'))
                respect = u.get('respect', 0)
                text += f"{i}. {name} - {respect} respect\n"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Top", callback_data="top")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "top_strength":
            users = await db.find('users', {}, limit=10, sort=[('total_wins', -1)])
            text = "⚔️ **Strongest Players**\n\n"
            for i, u in enumerate(users, 1):
                name = LeaderboardHandler.escape_markdown(u.get('first_name', 'Unknown'))
                wins = u.get('total_wins', 0)
                text += f"{i}. {name} - {wins} wins\n"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Top", callback_data="top")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "top_wins":
            users = await db.find('users', {}, limit=10, sort=[('total_wins', -1)])
            text = "🏆 **Most Wins**\n\n"
            for i, u in enumerate(users, 1):
                name = LeaderboardHandler.escape_markdown(u.get('first_name', 'Unknown'))
                wins = u.get('total_wins', 0)
                text += f"{i}. {name} - {wins} wins\n"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Top", callback_data="top")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "top_gang":
            gangs = await db.find('gangs', {}, limit=10, sort=[('power', -1)])
            text = "🏅 **Best Gangs**\n\n"
            for i, g in enumerate(gangs, 1):
                name = LeaderboardHandler.escape_markdown(g.get('name', 'Unknown'))
                power = g.get('power', 0)
                members = g.get('members', 0)
                text += f"{i}. {name} - Power: {power}, Members: {members}\n"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Top", callback_data="top")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "top":
            await LeaderboardHandler.top_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            try:
                await query.edit_message_text("🎮 Select a game to play:", reply_markup=await get_main_menu(user.id))
            except Exception:
                await query.message.reply_text("🎮 Select a game to play:", reply_markup=await get_main_menu(user.id))

leaderboard_handler = LeaderboardHandler()
