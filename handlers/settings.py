from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db
from locales.translations import SUPPORTED_LANGUAGES

class SettingsHandler:
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape special characters for Markdown"""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    @staticmethod
    async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command"""
        user = update.effective_user
        
        user_data = await db.find_one('users', {'telegram_id': user.id})
        current_lang = user_data.get('language', 'en') if user_data else 'en'
        
        keyboard = []
        row = []
        for code, name in SUPPORTED_LANGUAGES.items():
            flag = {
                'en': '🇬🇧', 'hi': '🇮🇳', 'bn': '🇮🇳', 'ta': '🇮🇳',
                'te': '🇮🇳', 'mr': '🇮🇳', 'gu': '🇮🇳', 'pa': '🇮🇳',
                'kn': '🇮🇳', 'ml': '🇮🇳', 'ur': '🇵🇰', 'ne': '🇳🇵',
                'id': '🇮🇩', 'es': '🇪🇸', 'fr': '🇫🇷', 'de': '🇩🇪',
                'ru': '🇷🇺', 'tr': '🇹🇷', 'pt': '🇧🇷', 'ar': '🇸🇦',
                'ja': '🇯🇵', 'ko': '🇰🇷', 'zh': '🇨🇳'
            }.get(code, '🌐')
            
            button_text = f"{flag} {name}"
            if code == current_lang:
                button_text += " ✅"
            
            row.append(InlineKeyboardButton(button_text, callback_data=f"lang_{code}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
        
        text = f"🌐 **Select Language**\n\nCurrent: {SUPPORTED_LANGUAGES.get(current_lang, 'English')}"
        
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
    async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user = update.effective_user
        user_data = await db.find_one('users', {'telegram_id': user.id})
        settings = user_data.get('settings', {}) if user_data else {}
        
        notifications = "✅" if settings.get('notifications', True) else "❌"
        lang_name = SUPPORTED_LANGUAGES.get(settings.get('language', 'en'), 'English')
        
        settings_text = f"""
⚙️ **Settings**
━━━━━━━━━━━━━━━━━━━━━

**Notifications:** {notifications}
**Language:** {lang_name}
**Privacy:** Public
**Game Mode:** Normal

**Commands:**
/language - Change language
/notifications - Toggle notifications
/privacy - Privacy settings
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
                InlineKeyboardButton("🌐 Language", callback_data="settings_language")
            ],
            [
                InlineKeyboardButton("🔒 Privacy", callback_data="settings_privacy"),
                InlineKeyboardButton("🎮 Game Mode", callback_data="settings_gamemode")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        if update.message:
            try:
                await update.message.reply_text(settings_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception:
                await update.message.reply_text(settings_text, reply_markup=InlineKeyboardMarkup(keyboard))
        elif update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(settings_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception:
                await update.callback_query.edit_message_text(settings_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings callbacks"""
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
        
        if data.startswith("lang_"):
            lang_code = data.replace("lang_", "")
            
            await db.update_one(
                'users',
                {'telegram_id': user.id},
                {'$set': {'language': lang_code, 'settings.language': lang_code}}
            )
            
            text = f"✅ Language changed to {SUPPORTED_LANGUAGES.get(lang_code, 'English')}"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]])
            
            try:
                await query.edit_message_text(text, reply_markup=keyboard)
            except Exception:
                await query.message.reply_text(text, reply_markup=keyboard)
        
        elif data == "settings_language":
            await SettingsHandler.language_command(update, context)
        
        elif data == "settings_notifications":
            user_data = await db.find_one('users', {'telegram_id': user.id})
            current = user_data.get('settings', {}).get('notifications', True)
            
            await db.update_one(
                'users',
                {'telegram_id': user.id},
                {'$set': {'settings.notifications': not current}}
            )
            
            text = f"🔔 Notifications {'enabled' if not current else 'disabled'}"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
            
            try:
                await query.edit_message_text(text, reply_markup=keyboard)
            except Exception:
                await query.message.reply_text(text, reply_markup=keyboard)
        
        elif data == "settings_privacy":
            text = """
🔒 **Privacy Settings**
━━━━━━━━━━━━━━━━━━━━━

**Profile Visibility:** Public
**Show Online Status:** Yes
**Show Game Stats:** Yes
**Show Achievements:** Yes

To change privacy settings, contact an admin.
            """
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "settings_gamemode":
            text = """
🎮 **Game Mode Settings**
━━━━━━━━━━━━━━━━━━━━━

**Current Mode:** Normal

**Available Modes:**
• Normal - Standard gameplay
• Hardcore - Increased difficulty, better rewards
• Casual - Relaxed gameplay, lower rewards

To change game mode, contact an admin.
            """
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "settings":
            await SettingsHandler.settings_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            try:
                await query.edit_message_text("🎮 Select a game to play:", reply_markup=await get_main_menu(user.id))
            except Exception:
                await query.message.reply_text("🎮 Select a game to play:", reply_markup=await get_main_menu(user.id))

settings_handler = SettingsHandler()
