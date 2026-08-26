from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.economy import EconomyService
from database.mongodb import db
import random
import logging

logger = logging.getLogger(__name__)

class EconomyHandler:
    @staticmethod
    async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        user = update.effective_user
        
        balance = await EconomyService.get_balance(user.id)
        
        balance_text = f"""
💰 **Your Balance**
━━━━━━━━━━━━━━━━━━━━━

**Coins:** {balance['coins']}
**Gems:** {balance['gems']}
**Bank:** {balance['bank']}

Total Worth: {balance['coins'] + balance['bank']} coins
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
        
        await update.message.reply_text(
            balance_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /daily command"""
        user = update.effective_user
        
        result = await EconomyService.claim_daily(user.id)
        
        if result['claimed']:
            message = f"""
🎁 **Daily Reward Claimed!**
━━━━━━━━━━━━━━━━━━━━━

**Coins:** +{result['coins']}
**Gems:** +{result['gems']}
**Streak:** {result['streak']} days

{result['message']}
            """
        else:
            message = f"❌ {result['message']}\n\nCome back tomorrow for your daily reward!"
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def work_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /work command"""
        user = update.effective_user
        
        # Check cooldown
        cooldown = await db.find_one('cooldowns', {
            'user_id': user.id,
            'type': 'work'
        })
        
        from datetime import datetime, timedelta
        if cooldown and cooldown.get('expires_at', datetime.utcnow()) > datetime.utcnow():
            remaining = (cooldown['expires_at'] - datetime.utcnow()).seconds
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"⏰ Please wait {minutes}m {seconds}s before working again."
            )
            return
        
        # Work jobs
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
        
        # Add coins
        success = await EconomyService.add_coins(
            user.id,
            earned,
            f'Worked as {job["name"]}'
        )
        
        if success:
            # Set cooldown (5 minutes)
            await db.update_one(
                'cooldowns',
                {'user_id': user.id, 'type': 'work'},
                {
                    '$set': {
                        'expires_at': datetime.utcnow() + timedelta(minutes=5)
                    }
                },
                upsert=True
            )
            
            # Random event chance
            event_chance = random.random()
            event_message = ""
            
            if event_chance < 0.1:  # 10% chance for bonus
                bonus = random.randint(10, 50)
                await EconomyService.add_coins(user.id, bonus, 'Work bonus event')
                event_message = f"\n🎉 Bonus event! +{bonus} extra coins!"
            elif event_chance < 0.05:  # 5% chance for negative event
                penalty = random.randint(10, 30)
                await EconomyService.remove_coins(user.id, penalty, 'Work penalty event')
                event_message = f"\n⚠️ Bad luck! -{penalty} coins stolen!"
            
            await update.message.reply_text(
                f"💼 You worked as a **{job['name']}**\n"
                f"Earned: +{earned} coins{event_message}\n"
                f"⏰ Next work available in 5 minutes"
            )
        else:
            await update.message.reply_text("❌ Failed to process work reward.")
    
    @staticmethod
    async def bank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /bank command"""
        economy = await db.find_one('economy', {'user_id': update.effective_user.id})
        
        if not economy:
            await update.message.reply_text("❌ Please start with /start first")
            return
        
        bank_text = f"""
🏦 **Bank of Mega Game**
━━━━━━━━━━━━━━━━━━━━━

**Current Balance:** {economy.get('bank', 0)} coins
**Interest Rate:** 2% daily
**Protection:** Active

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
        
        await update.message.reply_text(
            bank_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle economy callbacks"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        if query.data == "bank_deposit":
            # Deposit logic would go here
            await query.edit_message_text(
                "💰 **Deposit**\n\n"
                "Send the amount you want to deposit.\n"
                "Example: `/deposit 1000`\n\n"
                "Your current balance: [check with /balance]",
                parse_mode='Markdown'
            )
        
        elif query.data == "bank_withdraw":
            await query.edit_message_text(
                "💳 **Withdraw**\n\n"
                "Send the amount you want to withdraw.\n"
                "Example: `/withdraw 500`\n\n"
                "Your current bank balance: [check with /balance]",
                parse_mode='Markdown'
            )
        
        elif query.data == "bank_stats":
            economy = await db.find_one('economy', {'user_id': user.id})
            stats_text = f"""
📊 **Bank Statistics**
━━━━━━━━━━━━━━━━━━━━━

**Current Balance:** {economy.get('bank', 0)}
**Total Deposited:** {economy.get('total_deposited', 0)}
**Total Withdrawn:** {economy.get('total_withdrawn', 0)}
**Interest Earned:** {economy.get('interest_earned', 0)}
            """
            await query.edit_message_text(
                stats_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Bank", callback_data="bank")]
                ])
            )
        
        elif query.data == "bank":
            await EconomyHandler.bank_command(update, context)
        
        elif query.data == "transactions":
            # Show transaction history
            transactions = await db.find(
                'transactions',
                {'user_id': user.id},
                limit=10,
                sort=[('timestamp', -1)]
            )
            
            if not transactions:
                await query.edit_message_text(
                    "📊 No transactions found.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back", callback_data="balance")]
                    ])
                )
                return
            
            text = "📊 **Recent Transactions**\n\n"
            for tx in transactions:
                sign = "+" if tx.get('amount', 0) > 0 else ""
                text += f"• {tx.get('type', 'Unknown')}: {sign}{tx.get('amount', 0)} coins\n"
                text += f"  {tx.get('description', '')}\n"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="balance")]
                ])
            )

economy_handler = EconomyHandler()
