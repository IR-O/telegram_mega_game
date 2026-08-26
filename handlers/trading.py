from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TradingHandler:
    @staticmethod
    async def trade_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trade command"""
        user = update.effective_user
        
        trade_text = """
💱 **TRADING SYSTEM**
━━━━━━━━━━━━━━━━━━━━━

**Available Trades:** None

**Trading Rules:**
• Both parties must confirm the trade
• Only eligible items can be traded
• No real-money trading allowed
• Trades are final once confirmed

**How to Trade:**
1. /tradeoffer @username [item] - Send trade offer
2. /tradeaccept [offer_id] - Accept trade offer
3. /tradedecline [offer_id] - Decline trade offer

**Eligible Items:**
• Cards
• Creatures
• Cars
• Resources
• Items
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📤 Make Offer", callback_data="trade_offer"),
                InlineKeyboardButton("📥 View Offers", callback_data="trade_offers")
            ],
            [
                InlineKeyboardButton("📊 Trade History", callback_data="trade_history"),
                InlineKeyboardButton("📋 Rules", callback_data="trade_rules")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            trade_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle trading callbacks"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        data = query.data
        
        if data == "trade_offer":
            await query.edit_message_text(
                "📤 **Make a Trade Offer**\n\n"
                "To make a trade offer, use:\n"
                "`/tradeoffer @username item_name`\n\n"
                "Example: `/tradeoffer @john Dragon_Card`\n\n"
                "The other player will receive your offer and can accept or decline.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Trading", callback_data="trade")]
                ])
            )
        
        elif data == "trade_offers":
            # Check for pending offers
            offers = await db.find('trades', {
                'recipient_id': user.id,
                'status': 'pending'
            })
            
            if not offers:
                await query.edit_message_text(
                    "📥 No pending trade offers.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Trading", callback_data="trade")]
                    ])
                )
                return
            
            text = "📥 **Pending Trade Offers**\n\n"
            for offer in offers[:10]:
                text += f"🔹 From: {offer.get('sender_name', 'Unknown')}\n"
                text += f"📦 Item: {offer.get('item', 'Unknown')}\n"
                text += f"⏰ Expires: {offer.get('expires_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')}\n\n"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Trading", callback_data="trade")]
                ])
            )
        
        elif data == "trade_history":
            # Show trade history
            trades = await db.find('trades', {
                '$or': [
                    {'sender_id': user.id},
                    {'recipient_id': user.id}
                ],
                'status': {'$in': ['completed', 'declined']}
            }, limit=10, sort=[('timestamp', -1)])
            
            if not trades:
                await query.edit_message_text(
                    "📊 No trade history.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Trading", callback_data="trade")]
                    ])
                )
                return
            
            text = "📊 **Trade History**\n\n"
            for trade in trades:
                status = "✅ Completed" if trade.get('status') == 'completed' else "❌ Declined"
                text += f"• {trade.get('item', 'Unknown')} - {status}\n"
                text += f"  {trade.get('timestamp', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')}\n"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Trading", callback_data="trade")]
                ])
            )
        
        elif data == "trade_rules":
            rules_text = """
📋 **Trading Rules**
━━━━━━━━━━━━━━━━━━━━━

1. **Eligible Items:** Only virtual items can be traded
2. **No Real Money:** Real-money trading is strictly prohibited
3. **Two-Step Confirmation:** Both parties must confirm
4. **No Duplication:** Items are transferred, not duplicated
5. **Atomic Operations:** Trades are processed securely
6. **Fair Trading:** Both parties must agree on terms
7. **Time Limit:** Offers expire after 24 hours
8. **Final:** Trades are final once confirmed

**Penalties for Violations:**
• First violation: Warning
• Second violation: 24-hour trade ban
• Third violation: Permanent trade ban
            """
            
            await query.edit_message_text(
                rules_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Trading", callback_data="trade")]
                ])
            )
        
        elif data == "trade":
            await TradingHandler.trade_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            await query.edit_message_text(
                "🎮 Select a game to play:",
                reply_markup=await get_main_menu(user.id)
            )

trading_handler = TradingHandler()
