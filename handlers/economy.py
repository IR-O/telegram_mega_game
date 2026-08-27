from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.economy import EconomyService
from database.mongodb import db
from locales.translations import get_translation
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EconomyHandler:
    @staticmethod
    async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        user = update.effective_user
        
        # Get user's language
        user_data = await db.find_one('users', {'telegram_id': user.id})
        lang = user_data.get('language', 'en') if user_data else 'en'
        
        balance = await EconomyService.get_balance(user.id)
        
        balance_text = f"""
💰 **{get_translation('balance', lang)}**
━━━━━━━━━━━━━━━━━━━━━

**{get_translation('balance_coins', lang)}:** {balance['coins']}
**{get_translation('balance_gems', lang)}:** {balance['gems']}
**{get_translation('balance_bank', lang)}:** {balance['bank']}

**{get_translation('balance_total_worth', lang)}:** {balance['coins'] + balance['bank']} coins
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💰 Deposit", callback_data="bank_deposit"),
                InlineKeyboardButton("💳 Withdraw", callback_data="bank_withdraw")
            ],
            [
                InlineKeyboardButton("🏦 Bank Info", callback_data="bank_info"),
                InlineKeyboardButton("📊 Transaction History", callback_data="transactions")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(
                    balance_text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                await update.callback_query.edit_message_text(
                    balance_text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        elif update.message:
            try:
                await update.message.reply_text(
                    balance_text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                await update.message.reply_text(
                    balance_text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
    
    @staticmethod
    async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /daily command"""
        user = update.effective_user
        
        user_data = await db.find_one('users', {'telegram_id': user.id})
        lang = user_data.get('language', 'en') if user_data else 'en'
        
        result = await EconomyService.claim_daily(user.id)
        
        if result['claimed']:
            message = f"""
🎁 **{get_translation('daily_reward', lang)}**
━━━━━━━━━━━━━━━━━━━━━

**{get_translation('balance_coins', lang)}:** +{result['coins']}
**{get_translation('balance_gems', lang)}:** +{result['gems']}
**{get_translation('daily_streak', lang, streak=result['streak'])}**

{result['message']}
            """
        else:
            message = f"❌ {result['message']}\n\nCome back tomorrow for your daily reward!"
        
        if update.message:
            try:
                await update.message.reply_text(message, parse_mode='Markdown')
            except Exception:
                await update.message.reply_text(message)
        elif update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(message, parse_mode='Markdown')
            except Exception:
                await update.callback_query.edit_message_text(message)
    
    @staticmethod
    async def work_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /work command"""
        user = update.effective_user
        
        user_data = await db.find_one('users', {'telegram_id': user.id})
        lang = user_data.get('language', 'en') if user_data else 'en'
        
        cooldown = await db.find_one('cooldowns', {'user_id': user.id, 'type': 'work'})
        
        if cooldown and cooldown.get('expires_at', datetime.utcnow()) > datetime.utcnow():
            remaining = (cooldown['expires_at'] - datetime.utcnow()).seconds
            minutes = remaining // 60
            seconds = remaining % 60
            msg = get_translation('work_cooldown', lang, minutes=minutes, seconds=seconds)
            if update.message:
                await update.message.reply_text(msg)
            return
        
        jobs = [
            {'name': 'Street Racer', 'min': 50, 'max': 150},
            {'name': 'Hacker', 'min': 100, 'max': 300},
            {'name': 'Driver', 'min': 80, 'max': 200},
            {'name': 'Dealer', 'min': 150, 'max': 400},
            {'name': 'Bodyguard', 'min': 120, 'max': 250},
            {'name': 'Mercenary', 'min': 200, 'max': 500},
            {'name': 'Businessman', 'min': 300, 'max': 800}
        ]
        
        job = random.choice(jobs)
        earned = random.randint(job['min'], job['max'])
        
        success = await EconomyService.add_coins(user.id, earned, f'Worked as {job["name"]}')
        
        if success:
            await db.update_one(
                'cooldowns',
                {'user_id': user.id, 'type': 'work'},
                {'$set': {'expires_at': datetime.utcnow() + timedelta(minutes=5)}},
                upsert=True
            )
            
            event_message = ""
            if random.random() < 0.1:
                bonus = random.randint(10, 50)
                await EconomyService.add_coins(user.id, bonus, 'Work bonus event')
                event_message = get_translation('work_event_bonus', lang, bonus=bonus)
            elif random.random() < 0.05:
                penalty = random.randint(10, 30)
                await EconomyService.remove_coins(user.id, penalty, 'Work penalty event')
                event_message = get_translation('work_event_penalty', lang, penalty=penalty)
            
            msg = f"💼 {get_translation('work_job', lang, job=job['name'])}\n"
            msg += f"{get_translation('work_earned', lang, earned=earned)}{event_message}\n"
            msg += f"⏰ {get_translation('work_next', lang, time='5 minutes')}"
            
            if update.message:
                try:
                    await update.message.reply_text(msg, parse_mode='Markdown')
                except Exception:
                    await update.message.reply_text(msg)
        else:
            if update.message:
                await update.message.reply_text("❌ Failed to process work reward.")
    
    @staticmethod
    async def bank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /bank command"""
        user = update.effective_user
        
        user_data = await db.find_one('users', {'telegram_id': user.id})
        lang = user_data.get('language', 'en') if user_data else 'en'
        
        economy = await db.find_one('economy', {'user_id': user.id})
        
        if not economy:
            if update.message:
                await update.message.reply_text("❌ Please start with /start first")
            return
        
        bank_text = f"""
🏦 **{get_translation('bank', lang)}**
━━━━━━━━━━━━━━━━━━━━━

**{get_translation('bank_balance', lang)}:** {economy.get('bank', 0)} coins
**{get_translation('bank_interest', lang)}**
**{get_translation('bank_protection', lang)}**

**Features:**
• 2% daily interest on savings
• Protection against robbery (50% of bank is protected)
• No withdrawal fees
• Secure transactions

**Commands:**
/deposit [amount] - Deposit coins
/withdraw [amount] - Withdraw coins
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💰 Deposit", callback_data="bank_deposit"),
                InlineKeyboardButton("💳 Withdraw", callback_data="bank_withdraw")
            ],
            [
                InlineKeyboardButton("📊 Bank Stats", callback_data="bank_stats"),
                InlineKeyboardButton("📈 Interest History", callback_data="bank_interest")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        if update.message:
            try:
                await update.message.reply_text(bank_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception:
                await update.message.reply_text(bank_text, reply_markup=InlineKeyboardMarkup(keyboard))
        elif update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(bank_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception:
                await update.callback_query.edit_message_text(bank_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle economy callbacks"""
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
        
        # Get user's language
        user_data = await db.find_one('users', {'telegram_id': user.id})
        lang = user_data.get('language', 'en') if user_data else 'en'
        
        data = query.data
        
        if data == "bank_deposit":
            text = f"💰 **{get_translation('bank_deposit', lang)}**\n\nSend the amount you want to deposit.\nExample: `/deposit 1000`"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Bank", callback_data="bank")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "bank_withdraw":
            text = f"💳 **{get_translation('bank_withdraw', lang)}**\n\nSend the amount you want to withdraw.\nExample: `/withdraw 500`"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Bank", callback_data="bank")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "bank_stats":
            economy = await db.find_one('economy', {'user_id': user.id})
            text = f"""
📊 **{get_translation('bank_stats', lang)}**
━━━━━━━━━━━━━━━━━━━━━

**{get_translation('bank_balance', lang)}:** {economy.get('bank', 0)}
**{get_translation('bank_total_deposited', lang)}:** {economy.get('total_deposited', 0)}
**{get_translation('bank_total_withdrawn', lang)}:** {economy.get('total_withdrawn', 0)}
**{get_translation('bank_interest_earned', lang)}:** {economy.get('interest_earned', 0)}
            """
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Bank", callback_data="bank")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "bank_interest":
            text = f"""
📈 **Interest History**
━━━━━━━━━━━━━━━━━━━━━

Daily interest is calculated at 2% of your bank balance.
Interest is added automatically every 24 hours.

**Current Balance:** Check with /balance
**Next Interest:** In 24 hours
            """
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Bank", callback_data="bank")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "bank_info":
            text = f"""
🏦 **{get_translation('bank_info', lang)}**
━━━━━━━━━━━━━━━━━━━━━

**{get_translation('bank_interest', lang)}:** 2% daily
**Protection:** 50% of bank is protected from robbery
**Withdrawal Fee:** None
**Deposit Fee:** None
**{get_translation('bank_min_deposit', lang)}**
**{get_translation('bank_min_withdraw', lang)}**

**Benefits:**
• Safe storage for your coins
• Daily interest earnings
• Protection from robbery
• No fees
            """
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Bank", callback_data="bank")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "bank":
            await EconomyHandler.bank_command(update, context)
        
        elif data == "transactions":
            transactions = await db.find('transactions', {'user_id': user.id}, limit=10, sort=[('timestamp', -1)])
            
            if not transactions:
                text = "📊 No transactions found."
            else:
                text = "📊 **Recent Transactions**\n\n"
                for tx in transactions:
                    sign = "+" if tx.get('amount', 0) > 0 else ""
                    text += f"• {tx.get('type', 'Unknown')}: {sign}{tx.get('amount', 0)} coins\n  {tx.get('description', '')}\n"
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="balance")]])
            try:
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except Exception:
                await query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "balance":
            await EconomyHandler.balance_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            try:
                await query.edit_message_text("🎮 Select a game to play:", reply_markup=await get_main_menu(user.id))
            except Exception:
                await query.message.reply_text("🎮 Select a game to play:", reply_markup=await get_main_menu(user.id))

economy_handler = EconomyHandler()
