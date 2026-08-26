from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
from database.mongodb import db
from services.economy import EconomyService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AdminHandler:
    @staticmethod
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user = update.effective_user
        
        # Check if user is admin
        if user.id not in Config.ADMIN_IDS:
            await update.message.reply_text("❌ Unauthorized access.")
            return
        
        admin_text = """
🔐 **Admin Panel**
━━━━━━━━━━━━━━━━━━━━━

**Commands:**
🔍 /search [username] - Search user
💰 /givecoins [id] [amount] - Give coins
💎 /givegems [id] [amount] - Give gems
📊 /stats - View statistics
📢 /broadcast [message] - Broadcast message
🎮 /adminevent - Manage events
🏢 /admingang - Manage gangs
🌍 /adminworld - Manage worlds

**System:**
Database: MongoDB
Users: Loading...
Status: Online
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("💰 Economy", callback_data="admin_economy"),
                InlineKeyboardButton("🎮 Events", callback_data="admin_events")
            ],
            [
                InlineKeyboardButton("🏢 Gangs", callback_data="admin_gangs"),
                InlineKeyboardButton("🌍 Worlds", callback_data="admin_worlds")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton("📅 Seasons", callback_data="admin_seasons")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            admin_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin callbacks"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        # Check if user is admin
        if user.id not in Config.ADMIN_IDS:
            await query.edit_message_text("❌ Unauthorized access.")
            return
        
        data = query.data
        
        if data == "admin_stats":
            # Get statistics
            total_users = await db.db.users.count_documents({})
            total_transactions = await db.db.transactions.count_documents({})
            total_battles = await db.db.battles.count_documents({})
            total_gangs = await db.db.gangs.count_documents({})
            
            stats_text = f"""
📊 **System Statistics**
━━━━━━━━━━━━━━━━━━━━━

**Users:** {total_users}
**Transactions:** {total_transactions}
**Battles:** {total_battles}
**Gangs:** {total_gangs}
**Active Groups:** [checking]
**Database Status:** Online

**Economy Stats:**
[Calculating...]
            """
            
            await query.edit_message_text(
                stats_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin")]
                ])
            )
        
        elif data == "admin_economy":
            # Get economy stats
            pipeline = [
                {'$group': {
                    '_id': None,
                    'total_coins': {'$sum': '$coins'},
                    'total_gems': {'$sum': '$gems'},
                    'avg_coins': {'$avg': '$coins'},
                    'total_bank': {'$sum': '$bank'}
                }}
            ]
            
            result = await db.aggregate('economy', pipeline)
            
            if result:
                stats = result[0]
                eco_text = f"""
💰 **Economy Statistics**
━━━━━━━━━━━━━━━━━━━━━

**Total Coins in Circulation:** {stats.get('total_coins', 0):,}
**Total Gems:** {stats.get('total_gems', 0):,}
**Average Coins per User:** {int(stats.get('avg_coins', 0)):,}
**Total Bank Deposits:** {stats.get('total_bank', 0):,}

**Daily Activity:**
[Calculating...]
                """
            else:
                eco_text = "💰 No economy data found."
            
            await query.edit_message_text(
                eco_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin")]
                ])
            )
        
        elif data == "admin_events":
            # Manage events
            events_text = """
🎮 **Event Management**
━━━━━━━━━━━━━━━━━━━━━

**Active Events:**
1. None

**Create New Event:**
Use /adminevent create [type] [duration]

**Event Types:**
- zombie_outbreak
- alien_invasion
- pirate_raid
- paranormal_night
- dragon_attack
- mafia_war
- galaxy_war
            """
            
            await query.edit_message_text(
                events_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("📋 List Events", callback_data="admin_events_list"),
                        InlineKeyboardButton("➕ Create Event", callback_data="admin_events_create")
                    ],
                    [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin")]
                ])
            )
        
        elif data == "admin":
            await AdminHandler.admin_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            await query.edit_message_text(
                "🎮 Select a game to play:",
                reply_markup=await get_main_menu(user.id)
            )
        
        else:
            await query.edit_message_text(
                "🛠️ Admin feature coming soon.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin")]
                ])
            )

admin_handler = AdminHandler()
