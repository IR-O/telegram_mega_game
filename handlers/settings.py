from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db
from locales.translations import get_translation, SUPPORTED_LANGUAGES

class SettingsHandler:
    @staticmethod
    async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command"""
        user = update.effective_user
        
        # Get current language
        user_data = await db.find_one('users', {'telegram_id': user.id})
        current_lang = user_data.get('language', 'en') if user_data else 'en'
        
        # Create language keyboard
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
        
        await update.message.reply_text(
            f"🌐 **Select Language**\n\nCurrent: {SUPPORTED_LANGUAGES.get(current_lang, 'English')}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user = update.effective_user
        user_data = await db.find_one('users', {'telegram_id': user.id})
        settings = user_data.get('settings', {}) if user_data else {}
        
        notifications = "✅" if settings.get('notifications', True) else "❌"
        
        settings_text = f"""
⚙️ **Settings**
━━━━━━━━━━━━━━━━━━━━━

**Notifications:** {notifications}
**Language:** {SUPPORTED_LANGUAGES.get(settings.get('language', 'en'), 'English')}
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
        
        await update.message.reply_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings callbacks"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        data = query.data
        
        if data.startswith("lang_"):
            lang_code = data.replace("lang_", "")
            
            # Update user language
            await db.update_one(
                'users',
                {'telegram_id': user.id},
                {
                    '$set': {
                        'language': lang_code,
                        'settings.language': lang_code
                    }
                }
            )
            
            await query.edit_message_text(
                f"✅ Language changed to {SUPPORTED_LANGUAGES.get(lang_code, 'English')}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
                ])
            )
        
        elif data == "settings_language":
            await SettingsHandler.language_command(update, context)
        
        elif data == "settings_notifications":
            # Toggle notifications
            user_data = await db.find_one('users', {'telegram_id': user.id})
            current = user_data.get('settings', {}).get('notifications', True)
            
            await db.update_one(
                'users',
                {'telegram_id': user.id},
                {'$set': {'settings.notifications': not current}}
            )
            
            await query.edit_message_text(
                f"🔔 Notifications {'enabled' if not current else 'disabled'}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]
                ])
            )
        
        elif data == "settings":
            await SettingsHandler.settings_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            await query.edit_message_text(
                "🎮 Select a game to play:",
                reply_markup=await get_main_menu(user.id)
            )

settings_handler = SettingsHandler()
