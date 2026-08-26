from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from database.mongodb import db
from services.economy import EconomyService
from keyboards.menus import get_main_menu
from locales.translations import get_translation
from datetime import datetime, timedelta
import logging
import random

logger = logging.getLogger(__name__)

class StartHandler:
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Get or create user
        user_data = await db.find_one('users', {'telegram_id': user.id})
        
        if not user_data:
            # Create new user with language from Telegram
            user_lang = user.language_code if user.language_code in ['en', 'hi', 'bn', 'ta', 'te', 'mr', 'gu', 'pa', 'kn', 'ml', 'ur', 'ne', 'id', 'es', 'fr', 'de', 'ru', 'tr', 'pt', 'ar', 'ja', 'ko', 'zh'] else 'en'
            
            user_data = {
                'telegram_id': user.id,
                'username': user.username or '',
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'language': user_lang,
                'level': 1,
                'xp': 0,
                'coins': 1000,
                'gems': 10,
                'respect': 0,
                'achievements': [],
                'titles': ['Newbie'],
                'daily_streak': 0,
                'last_daily': None,
                'total_wins': 0,
                'total_losses': 0,
                'games_played': 0,
                'created_at': datetime.utcnow(),
                'last_active': datetime.utcnow(),
                'settings': {
                    'notifications': True,
                    'language': user_lang
                },
                'stats': {
                    'mafia': {'level': 1, 'xp': 0, 'wins': 0, 'losses': 0},
                    'space': {'level': 1, 'xp': 0, 'wins': 0, 'losses': 0},
                    'zombies': {'level': 1, 'xp': 0, 'wins': 0, 'losses': 0},
                    'pirates': {'level': 1, 'xp': 0, 'wins': 0, 'losses': 0},
                    'cards': {'level': 1, 'xp': 0, 'wins': 0, 'losses': 0}
                }
            }
            await db.insert_one('users', user_data)
            
            # Initialize economy
            await EconomyService.initialize_user(user.id)
            
            # Send welcome message in user's language
            welcome_text = get_translation('welcome', user_lang, name=user.first_name) + "\n\n"
            welcome_text += "I am your ultimate gaming hub with 13 exciting games!\n"
            welcome_text += "Use /games to explore all available games.\n"
            welcome_text += "Use /profile to check your stats.\n"
            welcome_text += "Use /help for assistance."
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=await get_main_menu(user.id)
            )
        else:
            # Get user's language
            user_lang = user_data.get('language', 'en')
            
            # Update last active
            await db.update_one(
                'users',
                {'telegram_id': user.id},
                {'$set': {'last_active': datetime.utcnow()}}
            )
            
            # Send welcome back message
            welcome_text = get_translation('welcome_back', user_lang, name=user.first_name)
            await update.message.reply_text(
                welcome_text,
                reply_markup=await get_main_menu(user.id)
            )
    
    @staticmethod
    async def games_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /games command"""
        user = update.effective_user
        user_data = await db.find_one('users', {'telegram_id': user.id})
        lang = user_data.get('language', 'en') if user_data else 'en'
        
        text = get_translation('main_menu', lang)
        await update.message.reply_text(
            text,
            reply_markup=await get_main_menu(user.id)
        )
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user = update.effective_user
        user_data = await db.find_one('users', {'telegram_id': user.id})
        lang = user_data.get('language', 'en') if user_data else 'en'
        
        help_text = get_translation('help', lang) + """
━━━━━━━━━━━━━━━━━━━━━

**General Commands:**
/start - Start the bot
/games - Show game menu
/profile - View your profile
/balance - Check your balance
/daily - Claim daily reward
/help - Show this help

**Game Commands:**
/mafia - Play Mafia RPG
/space - Explore Space Empire
/zombies - Survive Zombie Apocalypse
/pirates - Become a Pirate
/mutation - Mutate creatures
/haunted - Hunt ghosts
/mindwars - Challenge your mind
/city - Build your city
/spy - Spy missions
/dragons - Train dragons
/cards - Card battles
/detective - Solve mysteries
/racing - Street racing

**Economy:**
/work - Work for coins
/bank - Banking services
/shop - Buy items
/inventory - View items

**Social:**
/gang - Gang management
/top - Leaderboards
/trade - Trade items

**Settings:**
/language - Change language
/settings - Game settings
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')

start_handler = StartHandler()
