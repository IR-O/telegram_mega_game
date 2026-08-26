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
from handlers.inventory import inventory_handler
from handlers.trading import trading_handler
from handlers.missions import missions_handler
from services.events import EventService
from services.achievements import AchievementService
from services.notifications import NotificationService
import datetime
import random
import signal
import sys
import os

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
        self.notification_service = NotificationService()
        self.background_tasks = []
        self.is_running = False
        self.shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """Initialize bot components"""
        try:
            # Connect to MongoDB
            await db.connect()
            logger.info("MongoDB connected")
            
            # Create application with simpler approach
            self.application = Application.builder().token(Config.BOT_TOKEN).build()
            
            # Register handlers
            self.register_handlers()
            
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            self.is_running = True
            logger.info("Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.is_running = False
        self.shutdown_event.set()
    
    def register_handlers(self):
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
        app.add_handler(CommandHandler("inventory", inventory_handler.inventory_command))
        app.add_handler(CommandHandler("trade", trading_handler.trade_command))
        app.add_handler(CommandHandler("missions", missions_handler.missions_command))
        
        # Game command handlers
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
        
        # Callback query handlers - use pattern matching for specific callbacks
        app.add_handler(CallbackQueryHandler(games_handler.handle_callback, pattern="^(game_|main_menu|mafia_|space_|zombies_|pirates_|mutation_|haunted_|mind_|city_|spy_|dragons_|cards_|detective_|racing_)"))
        app.add_handler(CallbackQueryHandler(profile_handler.handle_callback, pattern="^profile"))
        app.add_handler(CallbackQueryHandler(economy_handler.handle_callback, pattern="^(bank|balance|transactions|bank_deposit|bank_withdraw|bank_stats|bank_interest)"))
        app.add_handler(CallbackQueryHandler(settings_handler.handle_callback, pattern="^settings|^lang_"))
        app.add_handler(CallbackQueryHandler(admin_handler.handle_callback, pattern="^admin"))
        app.add_handler(CallbackQueryHandler(leaderboard_handler.handle_callback, pattern="^top"))
        app.add_handler(CallbackQueryHandler(inventory_handler.handle_callback, pattern="^inventory"))
        app.add_handler(CallbackQueryHandler(trading_handler.handle_callback, pattern="^trade"))
        app.add_handler(CallbackQueryHandler(missions_handler.handle_callback, pattern="^missions"))
        
        # Fallback callback handler for any unhandled callbacks
        app.add_handler(CallbackQueryHandler(self.fallback_callback_handler))
        
        # Message handlers (for group chats)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_group_message))
        
        # Error handler
        app.add_error_handler(self.error_handler)
    
    async def fallback_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any unhandled callbacks"""
        query = update.callback_query
        if query:
            try:
                await query.answer("⚠️ This feature is not available yet.")
            except Exception as e:
                logger.error(f"Error in fallback callback: {e}")
    
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
            
            # Random reward for activity (1% chance)
            if random.random() < 0.01:
                from services.economy import EconomyService
                await EconomyService.add_coins(
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
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
    async def run_background_tasks(self):
        """Run background tasks"""
        while self.is_running and not self.shutdown_event.is_set():
            try:
                # Check and spawn events
                await self.event_service.check_and_spawn_events()
                
                # Check achievements for all users (run less frequently)
                if random.random() < 0.1:  # 10% chance each minute
                    await self.achievement_service.check_achievements()
                
                # Clean expired cooldowns
                await db.delete_many(
                    'cooldowns',
                    {'expires_at': {'$lt': datetime.datetime.utcnow()}}
                )
                
                # Process notifications
                await self.notification_service.process_notifications()
                
                # Update group worlds
                await self.update_group_worlds()
                
                # Wait with check for shutdown
                for _ in range(60):
                    if self.shutdown_event.is_set():
                        break
                    await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                logger.info("Background task cancelled")
                break
            except Exception as e:
                logger.error(f"Background task error: {e}")
                await asyncio.sleep(60)
    
    async def update_group_worlds(self):
        """Update group world statistics"""
        try:
            groups = await db.find('group_worlds', {})
            for group in groups:
                try:
                    last_active = group.get('last_active')
                    if not last_active:
                        await db.update_one(
                            'group_worlds',
                            {'group_id': group.get('group_id')},
                            {'$set': {'last_active': datetime.datetime.utcnow()}}
                        )
                        continue
                    
                    hours_since = (datetime.datetime.utcnow() - last_active).total_seconds() / 3600
                    if hours_since > 24:
                        threat_increase = min(10, hours_since / 24)
                        current_threat = group.get('threat_level', 0)
                        if isinstance(current_threat, dict):
                            current_threat = 0
                        await db.update_one(
                            'group_worlds',
                            {'group_id': group.get('group_id')},
                            {
                                '$set': {
                                    'threat_level': current_threat + threat_increase,
                                    'updated_at': datetime.datetime.utcnow()
                                }
                            }
                        )
                except Exception as e:
                    logger.error(f"Error updating group {group.get('group_id', 'unknown')}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error updating group worlds: {e}")
    
    async def run(self):
        """Start the bot"""
        try:
            await self.initialize()
            
            # Start background tasks
            task = asyncio.create_task(self.run_background_tasks())
            self.background_tasks.append(task)
            
            # Start bot with polling
            logger.info("Starting bot polling...")
            
            # Initialize and start the application
            await self.application.initialize()
            await self.application.start()
            
            # Use the correct polling method
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
            # Keep the bot running until shutdown signal
            while self.is_running and not self.shutdown_event.is_set():
                await asyncio.sleep(1)
                
            logger.info("Bot is shutting down...")
                
        except asyncio.CancelledError:
            logger.info("Bot task cancelled")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the bot gracefully"""
        logger.info("Starting graceful shutdown...")
        
        self.is_running = False
        self.shutdown_event.set()
        
        if self.background_tasks:
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=5.0)
                    except asyncio.TimeoutError:
                        logger.warning("Background task timeout during shutdown")
                    except asyncio.CancelledError:
                        pass
        
        if self.application:
            try:
                if hasattr(self.application, 'updater') and self.application.updater:
                    await asyncio.wait_for(self.application.updater.stop(), timeout=5.0)
                await asyncio.wait_for(self.application.stop(), timeout=5.0)
                await asyncio.wait_for(self.application.shutdown(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Application shutdown timeout")
            except Exception as e:
                logger.error(f"Error during application shutdown: {e}")
        
        try:
            await asyncio.wait_for(db.close(), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Database shutdown timeout")
        except Exception as e:
            logger.error(f"Error during database shutdown: {e}")
        
        logger.info("Bot shutdown complete")

async def main():
    """Main entry point"""
    bot = MegaGameBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        await bot.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await bot.shutdown()
        raise
    finally:
        logger.info("Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
