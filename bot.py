import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import Config
from database.mongodb import db
from handlers.start import start_handler
from handlers.profile import profile_handler
from handlers.economy import economy_handler
from handlers.games import games_handler
from handlers.leaderboard import leaderboard_handler
from handlers.settings import settings_handler
from handlers.admin import admin_handler
from services.events import EventService
from services.achievements import AchievementService
import datetime

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MegaGameBot:
    def __init__(self):
        self.application = None
        self.event_service = EventService()
        self.achievement_service = AchievementService()
    
    async def initialize(self):
        """Initialize bot components"""
        # Connect to MongoDB
        await db.connect()
        logger.info("MongoDB connected")
        
        # Create application
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Register handlers
        await self.register_handlers()
        
        logger.info("Bot initialized successfully")
    
    async def register_handlers(self):
        """Register all command and callback handlers"""
        app = self.application
        
        # Command handlers
        app.add_handler(CommandHandler("start", start_handler.start_command))
        app.add_handler(CommandHandler("games", start_handler.games_command))
        app.add_handler(CommandHandler("help", start_handler.help_command))
        app.add_handler(CommandHandler("profile", profile_handler.profile_command))
        app.add_handler(CommandHandler("balance", economy_handler.balance_command))
        app.add_handler(CommandHandler("daily", economy_handler.daily_command))
        app.add_handler(CommandHandler("work", economy_handler.work_command))
        app.add_handler(CommandHandler("bank", economy_handler.bank_command))
        app.add_handler(CommandHandler("top", leaderboard_handler.top_command))
        app.add_handler(CommandHandler("language", settings_handler.language_command))
        app.add_handler(CommandHandler("settings", settings_handler.settings_command))
        app.add_handler(CommandHandler("admin", admin_handler.admin_command))
        app.add_handler(CommandHandler("mafia", games_handler.mafia_command))
        app.add_handler(CommandHandler("space", games_handler.space_command))
        app.add_handler(CommandHandler("zombies", games_handler.zombies_command))
        app.add_handler(CommandHandler("pirates", games_handler.pirates_command))
        app.add_handler(CommandHandler("mutation", games_handler.mutation_command))
        app.add_handler(CommandHandler("haunted", games_handler.haunted_command))
        app.add_handler(CommandHandler("mindwars", games_handler.mind_wars_command))
        app.add_handler(CommandHandler("city", games_handler.city_command))
        app.add_handler(CommandHandler("spy", games_handler.spy_command))
        app.add_handler(CommandHandler("dragons", games_handler.dragons_command))
        app.add_handler(CommandHandler("cards", games_handler.cards_command))
        app.add_handler(CommandHandler("detective", games_handler.detective_command))
        app.add_handler(CommandHandler("racing", games_handler.racing_command))
        
        # Callback query handlers
        app.add_handler(CallbackQueryHandler(games_handler.handle_callback))
        app.add_handler(CallbackQueryHandler(profile_handler.handle_callback))
        app.add_handler(CallbackQueryHandler(economy_handler.handle_callback))
        app.add_handler(CallbackQueryHandler(settings_handler.handle_callback))
        app.add_handler(CallbackQueryHandler(admin_handler.handle_callback))
        
        # Message handlers (for group chats)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_group_message))
        
        # Error handler
        app.add_error_handler(self.error_handler)
    
    async def handle_group_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle group messages for activity rewards"""
        if update.effective_chat and update.effective_chat.type in ['group', 'supergroup']:
            user = update.effective_user
            if not user:
                return
            
            # Update last activity
            await db.update_one(
                'users',
                {'telegram_id': user.id},
                {'$set': {'last_active': datetime.datetime.utcnow()}}
            )
            
            # Check for message streak (random reward chance)
            if random.random() < 0.01:  # 1% chance
                await economy_handler.add_coins(
                    user.id,
                    random.randint(1, 5),
                    'Message bonus'
                )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors gracefully"""
        logger.error(f"Update {update} caused error {context.error}")
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ An error occurred. Please try again later."
                )
        except:
            pass
    
    async def run_background_tasks(self):
        """Run background tasks"""
        while True:
            try:
                # Check events
                await self.event_service.check_and_spawn_events()
                
                # Check achievements
                await self.achievement_service.check_achievements()
                
                # Clean expired cooldowns
                await db.delete_many(
                    'cooldowns',
                    {'expires_at': {'$lt': datetime.datetime.utcnow()}}
                )
                
                # Update group worlds
                await self.update_group_worlds()
                
                await asyncio.sleep(60)  # Run every minute
            except Exception as e:
                logger.error(f"Background task error: {e}")
                await asyncio.sleep(60)
    
    async def update_group_worlds(self):
        """Update group world statistics"""
        # Update group worlds periodically
        pass
    
    async def run(self):
        """Start the bot"""
        await self.initialize()
        
        # Start background tasks
        asyncio.create_task(self.run_background_tasks())
        
        # Start bot
        logger.info("Starting bot...")
        await self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    
    async def shutdown(self):
        """Shutdown the bot"""
        if self.application:
            await self.application.shutdown()
        await db.close()
        logger.info("Bot shutdown complete")

async def main():
    """Main entry point"""
    bot = MegaGameBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        await bot.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await bot.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
