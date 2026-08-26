from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class MissionsHandler:
    @staticmethod
    async def missions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /missions command"""
        user = update.effective_user
        
        # Get player's missions
        mafia_player = await db.find_one('mafia_players', {'user_id': user.id})
        
        missions_text = """
📋 **MISSIONS CENTER**
━━━━━━━━━━━━━━━━━━━━━

**Daily Missions:**
1. 🎯 Complete 3 fights - 0/3
2. 💰 Earn 500 coins - 0/500
3. ⚔️ Win 2 battles - 0/2

**Weekly Missions:**
1. 🏆 Win 10 fights - 0/10
2. 💎 Collect 50 gems - 0/50
3. 👑 Reach level 5 - 0/5

**Story Missions:**
1. 📖 The Beginning - 🟢 Available
2. 📖 Rise to Power - 🔒 Locked
3. 📖 The Boss - 🔒 Locked

**Gang Missions:**
1. 🏢 Recruit 3 members - 0/3
2. ⚔️ Win 5 gang wars - 0/5
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📅 Daily", callback_data="missions_daily"),
                InlineKeyboardButton("📆 Weekly", callback_data="missions_weekly")
            ],
            [
                InlineKeyboardButton("📖 Story", callback_data="missions_story"),
                InlineKeyboardButton("🏢 Gang", callback_data="missions_gang")
            ],
            [
                InlineKeyboardButton("🎯 Claim Rewards", callback_data="missions_claim"),
                InlineKeyboardButton("📊 Progress", callback_data="missions_progress")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            missions_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle missions callbacks"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        data = query.data
        
        if data == "missions_daily":
            # Show daily missions
            daily_text = """
📅 **Daily Missions**
━━━━━━━━━━━━━━━━━━━━━

🎯 **Combat Training:**
Fight 3 times today
Progress: 0/3
Reward: 100 coins, 50 XP

💰 **Coin Collector:**
Earn 500 coins today
Progress: 0/500
Reward: 200 coins, 100 XP

⚔️ **Victory Streak:**
Win 2 battles today
Progress: 0/2
Reward: 150 coins, 75 XP

**Bonus:** Complete all 3 for 50 gems!
            """
            
            await query.edit_message_text(
                daily_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Missions", callback_data="missions")]
                ])
            )
        
        elif data == "missions_weekly":
            weekly_text = """
📆 **Weekly Missions**
━━━━━━━━━━━━━━━━━━━━━

🏆 **Combat Master:**
Win 10 fights this week
Progress: 0/10
Reward: 500 coins, 200 XP

💎 **Gem Collector:**
Collect 50 gems this week
Progress: 0/50
Reward: 300 coins, 150 XP

👑 **Level Up:**
Reach level 5 this week
Progress: 0/5
Reward: 1000 coins, 500 XP

**Bonus:** Complete all 3 for 100 gems!
            """
            
            await query.edit_message_text(
                weekly_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Missions", callback_data="missions")]
                ])
            )
        
        elif data == "missions_story":
            story_text = """
📖 **Story Missions**
━━━━━━━━━━━━━━━━━━━━━

**Chapter 1: The Beginning** 🟢
Complete your first fight
Reward: 50 coins, 25 XP

**Chapter 2: Rise to Power** 🔒
Reach level 3
Reward: 100 coins, 50 XP

**Chapter 3: The Boss** 🔒
Defeat the Mafia Boss
Reward: 500 coins, 200 XP

**Chapter 4: Kingpin** 🔒
Reach level 10
Reward: 1000 coins, 500 XP
            """
            
            await query.edit_message_text(
                story_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Missions", callback_data="missions")]
                ])
            )
        
        elif data == "missions_gang":
            gang_text = """
🏢 **Gang Missions**
━━━━━━━━━━━━━━━━━━━━━

📊 **Recruitment Drive:**
Recruit 3 members to your gang
Progress: 0/3
Reward: 200 coins, 100 XP

⚔️ **Gang War Victory:**
Win 5 gang wars
Progress: 0/5
Reward: 500 coins, 200 XP

🏆 **Gang Dominance:**
Control 3 territories
Progress: 0/3
Reward: 1000 coins, 500 XP
            """
            
            await query.edit_message_text(
                gang_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Missions", callback_data="missions")]
                ])
            )
        
        elif data == "missions_claim":
            await query.edit_message_text(
                "🎯 **Claim Rewards**\n\n"
                "You have no pending rewards to claim.\n"
                "Complete missions to earn rewards!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Missions", callback_data="missions")]
                ])
            )
        
        elif data == "missions_progress":
            progress_text = """
📊 **Mission Progress**
━━━━━━━━━━━━━━━━━━━━━

**Daily:** 0% complete
**Weekly:** 0% complete
**Story:** 0% complete
**Gang:** 0% complete

**Total Missions Completed:** 0
**Total Rewards Earned:** 0 coins, 0 XP

Keep playing to complete more missions!
            """
            
            await query.edit_message_text(
                progress_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Missions", callback_data="missions")]
                ])
            )
        
        elif data == "missions":
            await MissionsHandler.missions_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            await query.edit_message_text(
                "🎮 Select a game to play:",
                reply_markup=await get_main_menu(user.id)
            )

missions_handler = MissionsHandler()
