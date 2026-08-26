from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db
from games.mafia import MafiaGame
from games.space import SpaceGame
from games.zombies import ZombieGame
from games.pirates import PirateGame
from games.mutation import MutationGame
from games.haunted import HauntedGame
from games.mind_wars import MindWarsGame
from games.city import CityGame
from games.spy import SpyGame
from games.dragons import DragonGame
from games.cards import CardGame
from games.detective import DetectiveGame
from games.racing import RacingGame
from keyboards.menus import get_main_menu, get_game_keyboard
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class GamesHandler:
    def __init__(self):
        self.mafia_game = MafiaGame()
        self.space_game = SpaceGame()
        self.zombie_game = ZombieGame()
        self.pirate_game = PirateGame()
        self.mutation_game = MutationGame()
        self.haunted_game = HauntedGame()
        self.mind_wars_game = MindWarsGame()
        self.city_game = CityGame()
        self.spy_game = SpyGame()
        self.dragon_game = DragonGame()
        self.card_game = CardGame()
        self.detective_game = DetectiveGame()
        self.racing_game = RacingGame()
    
    @staticmethod
    async def mafia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mafia command"""
        user = update.effective_user
        
        # Get or create mafia player data
        mafia_data = await db.find_one('mafia_players', {'user_id': user.id})
        if not mafia_data:
            mafia_data = {
                'user_id': user.id,
                'level': 1,
                'xp': 0,
                'hp': 100,
                'max_hp': 100,
                'energy': 50,
                'max_energy': 100,
                'attack': 10,
                'defense': 5,
                'luck': 5,
                'cash': 100,
                'bank': 0,
                'respect': 0,
                'wanted_level': 0,
                'gang': None,
                'weapon': None,
                'armor': None,
                'inventory': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            await db.insert_one('mafia_players', mafia_data)
        
        mafia_text = f"""
⚔️ **MAFIA RPG**
━━━━━━━━━━━━━━━━━━━━━

**Level:** {mafia_data.get('level', 1)}
**XP:** {mafia_data.get('xp', 0)} / {mafia_data.get('level', 1) * 100}
**HP:** {mafia_data.get('hp', 0)}/{mafia_data.get('max_hp', 100)}
**Energy:** {mafia_data.get('energy', 0)}/{mafia_data.get('max_energy', 100)}

**Stats:**
⚔️ Attack: {mafia_data.get('attack', 10)}
🛡️ Defense: {mafia_data.get('defense', 5)}
🍀 Luck: {mafia_data.get('luck', 5)}

**💰 Finances:**
Cash: {mafia_data.get('cash', 0)}
Bank: {mafia_data.get('bank', 0)}
Respect: {mafia_data.get('respect', 0)}
Wanted: {'⭐' * mafia_data.get('wanted_level', 0)}

**Weapon:** {mafia_data.get('weapon', 'None')}
**Armor:** {mafia_data.get('armor', 'None')}
**Gang:** {mafia_data.get('gang', 'None')}
        """
        
        await update.message.reply_text(
            mafia_text,
            parse_mode='Markdown',
            reply_markup=await get_game_keyboard('mafia', user.id)
        )
    
    @staticmethod
    async def space_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /space command"""
        user = update.effective_user
        
        space_text = """
🌌 **SPACE EMPIRE**
━━━━━━━━━━━━━━━━━━━━━

**Level:** 1
**XP:** 0/100
**Fleet Power:** 100
**Planets:** 1

**Resources:**
🪨 Ore: 100
💎 Crystals: 10
⚡ Energy: 50

**Commands:**
/explore - Explore the galaxy
/mine - Mine resources
/fleet - Manage your fleet
/planet - View your planets
        """
        
        keyboard = await get_game_keyboard('space', user.id)
        await update.message.reply_text(space_text, reply_markup=keyboard)
    
    @staticmethod
    async def zombies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /zombies command"""
        user = update.effective_user
        
        zombies_text = """
🧟 **ZOMBIE APOCALYPSE**
━━━━━━━━━━━━━━━━━━━━━

**Health:** 100/100
**Food:** 50
**Water:** 50
**Weapon:** None
**Shelter:** None

**Location:** Safe Zone
**Zombies Killed:** 0
**Survivors:** 1

**Commands:**
/fight - Fight zombies
/explore - Explore area
/shelter - Manage shelter
/craft - Craft items
        """
        
        keyboard = await get_game_keyboard('zombies', user.id)
        await update.message.reply_text(zombies_text, reply_markup=keyboard)
    
    @staticmethod
    async def pirates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pirates command"""
        user = update.effective_user
        
        pirates_text = """
🏴‍☠️ **PIRATE EMPIRE**
━━━━━━━━━━━━━━━━━━━━━

**Ship:** Sloop
**Crew:** 5
**Level:** 1
**XP:** 0/100

**Resources:**
💰 Gold: 100
⚓ Cannons: 2
🏝️ Islands: 0

**Commands:**
/sail - Set sail
/raid - Raid ships
/islands - Manage islands
/ship - Upgrade ship
        """
        
        keyboard = await get_game_keyboard('pirates', user.id)
        await update.message.reply_text(pirates_text, reply_markup=keyboard)
    
    @staticmethod
    async def mutation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mutation command"""
        mutation_text = """
🧪 **MUTATION LAB**
━━━━━━━━━━━━━━━━━━━━━

**Eggs:** 0
**DNA:** 0
**Creatures:** 0
**Mutations:** 0

**Available Experiment:**
Common Mutation: 1 DNA
Rare Mutation: 3 DNA
Epic Mutation: 5 DNA

**Commands:**
/collect - Collect resources
/breed - Breed creatures
/evolve - Evolve creatures
/battle - Battle creatures
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🧪 Collect", callback_data="mutation_collect"),
                InlineKeyboardButton("🧬 Breed", callback_data="mutation_breed")
            ],
            [
                InlineKeyboardButton("⬆ Evolve", callback_data="mutation_evolve"),
                InlineKeyboardButton("⚔️ Battle", callback_data="mutation_battle")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(mutation_text, reply_markup=keyboard)
    
    @staticmethod
    async def haunted_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /haunted command"""
        haunted_text = """
👻 **HAUNTED TELEGRAM**
━━━━━━━━━━━━━━━━━━━━━

**Location:** Abandoned House
**Ghosts Found:** 0
**Evidence:** 0
**Equipment:** Flashlight

**Areas:**
🏚️ Haunted House
🏥 Hospital
🌲 Dark Forest
⚰️ Cemetery

**Commands:**
/investigate - Investigate area
/equipment - Manage equipment
/evidence - Collect evidence
/ghosts - View ghost collection
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔍 Investigate", callback_data="haunted_investigate"),
                InlineKeyboardButton("📦 Equipment", callback_data="haunted_equipment")
            ],
            [
                InlineKeyboardButton("📊 Evidence", callback_data="haunted_evidence"),
                InlineKeyboardButton("👻 Ghosts", callback_data="haunted_ghosts")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(haunted_text, reply_markup=keyboard)
    
    @staticmethod
    async def mind_wars_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mindwars command"""
        mindwars_text = """
🧠 **MIND WARS**
━━━━━━━━━━━━━━━━━━━━━

**Games:**
1. 🧩 Memory
2. ➗ Mathematics
3. 📝 Word Puzzles
4. 🔍 Pattern Recognition
5. ⏱️ Reaction Tests
6. ❓ Trivia
7. 🧠 Logic Puzzles

**Stats:**
Wins: 0
Losses: 0
Rating: 1000

**Commands:**
/challenge @username - Challenge someone
/rankings - View rankings
/daily - Daily challenge
/tournament - Group tournament
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🧩 Memory", callback_data="mind_memory"),
                InlineKeyboardButton("➗ Math", callback_data="mind_math")
            ],
            [
                InlineKeyboardButton("📝 Word", callback_data="mind_word"),
                InlineKeyboardButton("🔍 Pattern", callback_data="mind_pattern")
            ],
            [
                InlineKeyboardButton("⏱️ Reaction", callback_data="mind_reaction"),
                InlineKeyboardButton("❓ Trivia", callback_data="mind_trivia")
            ],
            [
                InlineKeyboardButton("🧠 Logic", callback_data="mind_logic"),
                InlineKeyboardButton("🏆 Rankings", callback_data="mind_rankings")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(mindwars_text, reply_markup=keyboard)
    
    @staticmethod
    async def city_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /city command"""
        city_text = """
🏙️ **BUILD YOUR CITY**
━━━━━━━━━━━━━━━━━━━━━

**City Name:** None
**Level:** 1
**Population:** 100
**Happiness:** 50%
**Economy:** 100
**Security:** 50%
**Income:** 10/hour

**Buildings:**
🏠 Houses: 0
🏢 Offices: 0
🏭 Factories: 0
🏪 Shops: 0
🏥 Hospitals: 0

**Commands:**
/build - Build new building
/upgrade - Upgrade building
/stats - View city stats
/visit @username - Visit another city
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🏗️ Build", callback_data="city_build"),
                InlineKeyboardButton("⬆ Upgrade", callback_data="city_upgrade")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="city_stats"),
                InlineKeyboardButton("👤 Visit", callback_data="city_visit")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(city_text, reply_markup=keyboard)
    
    @staticmethod
    async def spy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /spy command"""
        spy_text = """
🕵️ **SPY NETWORK**
━━━━━━━━━━━━━━━━━━━━━

**Agent Level:** 1
**Reputation:** 0
**Intelligence:** 0
**Equipment:** None

**Missions:**
📋 Available: 3
✅ Completed: 0
❌ Failed: 0

**Commands:**
/missions - View missions
/equipment - Manage equipment
/intelligence - Intelligence reports
/spy @username - Spy on someone
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📋 Missions", callback_data="spy_missions"),
                InlineKeyboardButton("📦 Equipment", callback_data="spy_equipment")
            ],
            [
                InlineKeyboardButton("📊 Reports", callback_data="spy_reports"),
                InlineKeyboardButton("🕵️ Spy", callback_data="spy_action")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(spy_text, reply_markup=keyboard)
    
    @staticmethod
    async def dragons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /dragons command"""
        dragons_text = """
🐉 **DRAGON KINGDOM**
━━━━━━━━━━━━━━━━━━━━━

**Kingdom Level:** 1
**Dragons:** 0
**Eggs:** 0
**Resources:** 100

**Elements:**
🔥 Fire: 0
❄️ Ice: 0
⚡ Lightning: 0
💧 Water: 0
🌿 Nature: 0
🌑 Dark: 0
✨ Light: 0

**Commands:**
/hatch - Hatch dragon
/train - Train dragon
/breed - Breed dragons
/battle - Dragon battle
/kingdom - Manage kingdom
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🥚 Hatch", callback_data="dragons_hatch"),
                InlineKeyboardButton("⚔️ Train", callback_data="dragons_train")
            ],
            [
                InlineKeyboardButton("🧬 Breed", callback_data="dragons_breed"),
                InlineKeyboardButton("⚔️ Battle", callback_data="dragons_battle")
            ],
            [
                InlineKeyboardButton("🏰 Kingdom", callback_data="dragons_kingdom"),
                InlineKeyboardButton("📊 Stats", callback_data="dragons_stats")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(dragons_text, reply_markup=keyboard)
    
    @staticmethod
    async def cards_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cards command"""
        cards_text = """
🎴 **COLLECTIBLE CARD BATTLE**
━━━━━━━━━━━━━━━━━━━━━

**Cards:** 0
**Deck Size:** 0
**Rating:** 1000
**Wins:** 0
**Losses:** 0

**Card Types:**
⚔️ Warriors: 0
🧙 Mages: 0
🐉 Dragons: 0
😈 Demons: 0
🧝 Elves: 0
🤖 Robots: 0
🦸 Heroes: 0

**Commands:**
/collection - View collection
/deck - Manage deck
/battle @username - Card battle
/pack - Open card pack
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📚 Collection", callback_data="cards_collection"),
                InlineKeyboardButton("🃏 Deck", callback_data="cards_deck")
            ],
            [
                InlineKeyboardButton("⚔️ Battle", callback_data="cards_battle"),
                InlineKeyboardButton("📦 Pack", callback_data="cards_pack")
            ],
            [
                InlineKeyboardButton("🏆 Rankings", callback_data="cards_rankings"),
                InlineKeyboardButton("📊 Stats", callback_data="cards_stats")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(cards_text, reply_markup=keyboard)
    
    @staticmethod
    async def detective_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /detective command"""
        detective_text = """
🔎 **CRIME DETECTIVE**
━━━━━━━━━━━━━━━━━━━━━

**Case:** None
**Suspects:** 0
**Clues:** 0
**Cases Solved:** 0
**Rating:** 1000

**Commands:**
/newcase - Start new case
/investigate - Investigate
/clues - View clues
/suspects - View suspects
/vote - Vote for suspect
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📋 New Case", callback_data="detective_newcase"),
                InlineKeyboardButton("🔍 Investigate", callback_data="detective_investigate")
            ],
            [
                InlineKeyboardButton("📊 Clues", callback_data="detective_clues"),
                InlineKeyboardButton("👤 Suspects", callback_data="detective_suspects")
            ],
            [
                InlineKeyboardButton("🗳️ Vote", callback_data="detective_vote"),
                InlineKeyboardButton("🏆 Rankings", callback_data="detective_rankings")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(detective_text, reply_markup=keyboard)
    
    @staticmethod
    async def racing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /racing command"""
        racing_text = """
🏎️ **STREET RACING EMPIRE**
━━━━━━━━━━━━━━━━━━━━━

**Car:** None
**Level:** 1
**Wins:** 0
**Losses:** 0
**Rating:** 1000

**Car Stats:**
Speed: 0
Acceleration: 0
Handling: 0
Nitro: 0
Durability: 0

**Commands:**
/garage - View garage
/race @username - Race someone
/upgrade - Upgrade car
/leaderboard - Racing rankings
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🏎️ Garage", callback_data="racing_garage"),
                InlineKeyboardButton("🏁 Race", callback_data="racing_race")
            ],
            [
                InlineKeyboardButton("⬆ Upgrade", callback_data="racing_upgrade"),
                InlineKeyboardButton("🏆 Rankings", callback_data="racing_rankings")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="racing_stats"),
                InlineKeyboardButton("👥 Crew", callback_data="racing_crew")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(racing_text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle game callbacks with proper error handling"""
        query = update.callback_query
        
        if not query:
            logger.warning("Callback query is None")
            return
        
        try:
            await query.answer()
        except Exception as e:
            logger.error(f"Error answering callback: {e}")
            return
        
        user = update.effective_user
        if not user:
            logger.warning("User is None in callback")
            return
        
        data = query.data
        if not data:
            logger.warning("Callback data is None")
            return
        
        # Check if message exists
        if not query.message:
            logger.warning("Message is None in callback")
            try:
                await query.edit_message_text("❌ This message is no longer available. Please use /start to continue.")
            except Exception:
                pass
            return
        
        if data == "main_menu":
            try:
                await query.edit_message_text(
                    "🎮 Select a game to play:",
                    reply_markup=await get_main_menu(user.id)
                )
            except Exception as e:
                logger.error(f"Error showing main menu: {e}")
        
        elif data.startswith("game_"):
            game_name = data.replace("game_", "")
            
            # Map game names to handlers
            game_handlers = {
                "mafia": GamesHandler.mafia_command,
                "space": GamesHandler.space_command,
                "zombies": GamesHandler.zombies_command,
                "pirates": GamesHandler.pirates_command,
                "mutation": GamesHandler.mutation_command,
                "haunted": GamesHandler.haunted_command,
                "mindwars": GamesHandler.mind_wars_command,
                "city": GamesHandler.city_command,
                "spy": GamesHandler.spy_command,
                "dragons": GamesHandler.dragons_command,
                "cards": GamesHandler.cards_command,
                "detective": GamesHandler.detective_command,
                "racing": GamesHandler.racing_command
            }
            
            if game_name in game_handlers:
                try:
                    # Create a new message for the game
                    await query.edit_message_text(
                        f"🎮 Loading {game_name.title()}...",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("⏳ Loading...", callback_data="dummy")]
                        ])
                    )
                    # Send the game content as a new message
                    await game_handlers[game_name](update, context)
                except Exception as e:
                    logger.error(f"Error loading game {game_name}: {e}")
                    try:
                        await query.edit_message_text(
                            f"❌ Error loading {game_name}. Please try again.",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
                            ])
                        )
                    except Exception:
                        pass
            else:
                try:
                    await query.edit_message_text(
                        f"🎮 {game_name.title()} game coming soon!",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
                        ])
                    )
                except Exception as e:
                    logger.error(f"Error showing game coming soon: {e}")

games_handler = GamesHandler()
