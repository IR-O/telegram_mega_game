from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db
from datetime import datetime, timedelta
import random

class ProfileHandler:
    @staticmethod
    async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        user = update.effective_user
        
        user_data = await db.find_one('users', {'telegram_id': user.id})
        if not user_data:
            if update.message:
                await update.message.reply_text("❌ Please start the bot with /start first")
            return
        
        economy = await db.find_one('economy', {'user_id': user.id})
        achievements = await db.find('achievements', {'user_id': user.id})
        
        profile_text = f"""
👤 **Profile**
━━━━━━━━━━━━━━━━━━━━━

**Name:** {user_data.get('first_name', 'Player')}
**Username:** @{user_data.get('username', 'N/A')}
**Level:** {user_data.get('level', 1)}
**XP:** {user_data.get('xp', 0)} / {user_data.get('level', 1) * 100}
**Respect:** {user_data.get('respect', 0)}

**💰 Economy**
━━━━━━━━━━━━━━━━━━━━━
**Coins:** {economy.get('coins', 0) if economy else 0}
**Gems:** {economy.get('gems', 0) if economy else 0}
**Bank:** {economy.get('bank', 0) if economy else 0}

**📊 Statistics**
━━━━━━━━━━━━━━━━━━━━━
**Wins:** {user_data.get('total_wins', 0)}
**Losses:** {user_data.get('total_losses', 0)}
**Games Played:** {user_data.get('games_played', 0)}
**Daily Streak:** {economy.get('daily_streak', 0) if economy else 0}

**🏆 Achievements:** {len(achievements)}
**Titles:** {', '.join(user_data.get('titles', ['None']))}

**📅 Member Since:** {user_data.get('created_at', datetime.utcnow()).strftime('%Y-%m-%d')}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Full Stats", callback_data="profile_full"),
                InlineKeyboardButton("🎯 Achievements", callback_data="profile_achievements")
            ],
            [
                InlineKeyboardButton("📜 Titles", callback_data="profile_titles"),
                InlineKeyboardButton("💰 Economy", callback_data="profile_economy")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(
                    profile_text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                await update.callback_query.message.reply_text(
                    profile_text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        elif update.message:
            await update.message.reply_text(
                profile_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle profile callbacks"""
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
        
        if data == "profile_full":
            user_data = await db.find_one('users', {'telegram_id': user.id})
            economy = await db.find_one('economy', {'user_id': user.id})
            
            stats_text = f"""
📊 **Full Statistics for {user_data.get('first_name', 'Player')}**
━━━━━━━━━━━━━━━━━━━━━

**🎮 Game Stats:**
━━━━━━━━━━━━━━━━━━━━━
**Mafia RPG:** Level {user_data.get('stats', {}).get('mafia', {}).get('level', 1)}
**Space Empire:** Level {user_data.get('stats', {}).get('space', {}).get('level', 1)}
**Zombies:** Level {user_data.get('stats', {}).get('zombies', {}).get('level', 1)}
**Pirates:** Level {user_data.get('stats', {}).get('pirates', {}).get('level', 1)}
**Cards:** Level {user_data.get('stats', {}).get('cards', {}).get('level', 1)}

**💎 Economy:**
━━━━━━━━━━━━━━━━━━━━━
**Total Earned:** {economy.get('total_earned', 0) if economy else 0}
**Total Spent:** {economy.get('total_spent', 0) if economy else 0}
**Gems Earned:** {economy.get('total_gems_earned', 0) if economy else 0}
            """
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Profile", callback_data="profile")]])
            try:
                await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.message.reply_text(stats_text, parse_mode='Markdown', reply_markup=keyboard)
        
        elif data == "profile_achievements":
            achievements = await db.find('achievements', {'user_id': user.id})
            
            if not achievements:
                text = "🎯 No achievements yet. Keep playing to earn them!"
            else:
                text = "🎯 **Your Achievements**\n\n"
                for i, achievement in enumerate(achievements[:10], 1):
                    text += f"{i}. {achievement.get('name', 'Unknown')} - {achievement.get('description', '')}\n"
                if len(achievements) > 10:
                    text += f"\n... and {len(achievements) - 10} more"
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Profile", callback_data="profile")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)
        
        elif data == "profile_titles":
            user_data = await db.find_one('users', {'telegram_id': user.id})
            titles = user_data.get('titles', [])
            
            text = "📜 **Your Titles**\n\n" + "\n".join([f"• {title}" for title in titles]) if titles else "📜 No titles yet. Earn titles through gameplay!"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Profile", callback_data="profile")]])
            
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)
        
        elif data == "profile_economy":
            economy = await db.find_one('economy', {'user_id': user.id})
            
            if not economy:
                text = "💰 No economy data found."
            else:
                text = f"""
💰 **Economy Details**
━━━━━━━━━━━━━━━━━━━━━

**Coins:** {economy.get('coins', 0)}
**Gems:** {economy.get('gems', 0)}
**Bank Balance:** {economy.get('bank', 0)}
**Total Earned:** {economy.get('total_earned', 0)}
**Total Spent:** {economy.get('total_spent', 0)}
**Gems Earned:** {economy.get('total_gems_earned', 0)}
**Daily Streak:** {economy.get('daily_streak', 0)}
**Properties:** {len(economy.get('properties', []))}
**Businesses:** {len(economy.get('businesses', []))}
                """
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Profile", callback_data="profile")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)
        
        elif data == "profile":
            await ProfileHandler.profile_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            try:
                await query.edit_message_text("🎮 Select a game to play:", reply_markup=await get_main_menu(user.id))
            except Exception:
                await query.message.reply_text("🎮 Select a game to play:", reply_markup=await get_main_menu(user.id))

profile_handler = ProfileHandler()
