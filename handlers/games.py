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
    async def mutation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mutation command"""
        user = update.effective_user
        if not user:
            return
        
        mutation_data = await db.find_one('mutations', {'user_id': user.id})
        if not mutation_data:
            mutation_data = {
                'user_id': user.id,
                'level': 1,
                'xp': 0,
                'eggs': 3,
                'dna': 10,
                'creatures': [],
                'mutations': 0,
                'evolutions': 0,
                'battles_won': 0,
                'battles_lost': 0,
                'experiments': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            await db.insert_one('mutations', mutation_data)
        
        text = f"""
🧪 **MUTATION LAB**
━━━━━━━━━━━━━━━━━━━━━

**Eggs:** {mutation_data.get('eggs', 0)}
**DNA:** {mutation_data.get('dna', 0)}
**Creatures:** {len(mutation_data.get('creatures', []))}
**Mutations:** {mutation_data.get('mutations', 0)}
**Evolutions:** {mutation_data.get('evolutions', 0)}
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
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def dragons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /dragons command"""
        user = update.effective_user
        if not user:
            return
        
        dragon_data = await db.find_one('dragons', {'user_id': user.id})
        if not dragon_data:
            dragon_data = {
                'user_id': user.id,
                'level': 1,
                'xp': 0,
                'kingdom_level': 1,
                'dragons': [],
                'eggs': 1,
                'resources': 100,
                'elements': {
                    'fire': 0, 'ice': 0, 'lightning': 0,
                    'water': 0, 'nature': 0, 'dark': 0, 'light': 0
                },
                'battles_won': 0,
                'battles_lost': 0,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            await db.insert_one('dragons', dragon_data)
        
        elements = dragon_data.get('elements', {})
        
        text = f"""
🐉 **DRAGON KINGDOM**
━━━━━━━━━━━━━━━━━━━━━

**Kingdom Level:** {dragon_data.get('kingdom_level', 1)}
**Dragons:** {len(dragon_data.get('dragons', []))}
**Eggs:** {dragon_data.get('eggs', 0)}
**Resources:** {dragon_data.get('resources', 100)}

**Elements:**
🔥 Fire: {elements.get('fire', 0)}
❄️ Ice: {elements.get('ice', 0)}
⚡ Lightning: {elements.get('lightning', 0)}
💧 Water: {elements.get('water', 0)}
🌿 Nature: {elements.get('nature', 0)}
🌑 Dark: {elements.get('dark', 0)}
✨ Light: {elements.get('light', 0)}
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
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def mafia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mafia command"""
        user = update.effective_user
        if not user:
            return
        
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
        
        text = f"""
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
        
        keyboard = await get_game_keyboard('mafia', user.id)
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)
    
    @staticmethod
    async def space_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /space command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
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
        """
        
        keyboard = await get_game_keyboard('space', user.id)
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def zombies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /zombies command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
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
        """
        
        keyboard = await get_game_keyboard('zombies', user.id)
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def pirates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pirates command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
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
        """
        
        keyboard = await get_game_keyboard('pirates', user.id)
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def haunted_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /haunted command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
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
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def mind_wars_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mindwars command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
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
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def city_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /city command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
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
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def spy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /spy command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
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
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def cards_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cards command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
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
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def detective_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /detective command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
🔎 **CRIME DETECTIVE**
━━━━━━━━━━━━━━━━━━━━━

**Case:** None
**Suspects:** 0
**Clues:** 0
**Cases Solved:** 0
**Rating:** 1000
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
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def racing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /racing command"""
        user = update.effective_user
        if not user:
            return
        
        text = """
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
        
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                await update.callback_query.message.reply_text(text, reply_markup=keyboard)
        elif update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all game callbacks"""
        query = update.callback_query
        if not query:
            return
        
        try:
            await query.answer()
        except:
            pass
        
        user = update.effective_user
        if not user or not query.message:
            return
        
        data = query.data
        if not data:
            return
        
        # Mutation actions
        if data == "mutation_collect":
            from games.mutation import MutationGame
            result = await MutationGame.collect(user.id)
            if 'error' in result:
                await query.edit_message_text(f"❌ {result['error']}\n\nUse /mutation to continue.")
            else:
                await query.edit_message_text(f"{result['message']}\n\nUse /mutation to continue.")
            return
        
        elif data == "mutation_breed":
            from games.mutation import MutationGame
            result = await MutationGame.breed(user.id)
            if 'error' in result:
                await query.edit_message_text(f"❌ {result['error']}\n\nUse /mutation to continue.")
            else:
                await query.edit_message_text(f"{result['message']}\n\nUse /mutation to continue.")
            return
        
        elif data == "mutation_evolve":
            from games.mutation import MutationGame
            result = await MutationGame.evolve(user.id)
            if 'error' in result:
                await query.edit_message_text(f"❌ {result['error']}\n\nUse /mutation to continue.")
            else:
                await query.edit_message_text(f"{result['message']}\n\nUse /mutation to continue.")
            return
        
        elif data == "mutation_battle":
            await query.edit_message_text("⚔️ Battle feature coming soon!\n\nUse /mutation to continue.")
            return
        
        # Dragon actions
        elif data == "dragons_hatch":
            from games.dragons import DragonGame
            result = await DragonGame.hatch_egg(user.id)
            if 'error' in result:
                await query.edit_message_text(f"❌ {result['error']}\n\nUse /dragons to continue.")
            else:
                await query.edit_message_text(f"{result['message']}\n\nUse /dragons to continue.")
            return
        
        elif data == "dragons_train":
            from games.dragons import DragonGame
            result = await DragonGame.train_dragon(user.id)
            if 'error' in result:
                await query.edit_message_text(f"❌ {result['error']}\n\nUse /dragons to continue.")
            else:
                await query.edit_message_text(f"{result['message']}\n\nUse /dragons to continue.")
            return
        
        elif data == "dragons_breed":
            await query.edit_message_text("🧬 Breeding feature coming soon!\n\nUse /dragons to continue.")
            return
        
        elif data == "dragons_battle":
            await query.edit_message_text("⚔️ Dragon battle feature coming soon!\n\nUse /dragons to continue.")
            return
        
        elif data == "dragons_kingdom":
            await query.edit_message_text("🏰 Kingdom management coming soon!\n\nUse /dragons to continue.")
            return
        
        elif data == "dragons_stats":
            dragon_data = await db.find_one('dragons', {'user_id': user.id})
            if dragon_data:
                text = f"""
📊 **Dragon Stats**
━━━━━━━━━━━━━━━━━━━━━

**Kingdom Level:** {dragon_data.get('kingdom_level', 1)}
**Total Dragons:** {len(dragon_data.get('dragons', []))}
**Eggs:** {dragon_data.get('eggs', 0)}
**Resources:** {dragon_data.get('resources', 100)}
**Battles Won:** {dragon_data.get('battles_won', 0)}
**Battles Lost:** {dragon_data.get('battles_lost', 0)}
                """
                await query.edit_message_text(text)
            else:
                await query.edit_message_text("No dragon data found.")
            return
        
        # Mafia actions
        elif data == "mafia_fight":
            await query.edit_message_text("⚔️ Fight feature coming soon!\n\nUse /mafia to continue.")
            return
        
        elif data == "mafia_rob":
            await query.edit_message_text("💰 Rob feature coming soon!\n\nUse /mafia to continue.")
            return
        
        elif data == "mafia_work":
            await query.edit_message_text("💼 Work feature coming soon!\n\nUse /mafia to continue.")
            return
        
        elif data == "mafia_missions":
            await query.edit_message_text("📋 Missions feature coming soon!\n\nUse /mafia to continue.")
            return
        
        elif data == "mafia_shop":
            await query.edit_message_text("🛒 Shop feature coming soon!\n\nUse /mafia to continue.")
            return
        
        elif data == "mafia_gang":
            await query.edit_message_text("🏢 Gang feature coming soon!\n\nUse /mafia to continue.")
            return
        
        # Space actions
        elif data.startswith("space_"):
            await query.edit_message_text("🌌 Space features coming soon!\n\nUse /space to continue.")
            return
        
        # Zombies actions
        elif data.startswith("zombies_"):
            await query.edit_message_text("🧟 Zombies features coming soon!\n\nUse /zombies to continue.")
            return
        
        # Pirates actions
        elif data.startswith("pirates_"):
            await query.edit_message_text("🏴‍☠️ Pirates features coming soon!\n\nUse /pirates to continue.")
            return
        
        # Haunted actions
        elif data.startswith("haunted_"):
            await query.edit_message_text("👻 Haunted features coming soon!\n\nUse /haunted to continue.")
            return
        
        # Mind Wars actions
        elif data.startswith("mind_"):
            await query.edit_message_text("🧠 Mind Wars features coming soon!\n\nUse /mindwars to continue.")
            return
        
        # City actions
        elif data.startswith("city_"):
            await query.edit_message_text("🏙️ City features coming soon!\n\nUse /city to continue.")
            return
        
        # Spy actions
        elif data.startswith("spy_"):
            await query.edit_message_text("🕵️ Spy features coming soon!\n\nUse /spy to continue.")
            return
        
        # Cards actions
        elif data.startswith("cards_"):
            await query.edit_message_text("🎴 Cards features coming soon!\n\nUse /cards to continue.")
            return
        
        # Detective actions
        elif data.startswith("detective_"):
            await query.edit_message_text("🔎 Detective features coming soon!\n\nUse /detective to continue.")
            return
        
        # Racing actions
        elif data.startswith("racing_"):
            await query.edit_message_text("🏎️ Racing features coming soon!\n\nUse /racing to continue.")
            return
        
        # Main menu navigation
        elif data == "main_menu":
            try:
                await query.edit_message_text(
                    "🎮 Select a game to play:",
                    reply_markup=await get_main_menu(user.id)
                )
            except:
                pass
            return
        
        # Game navigation
        elif data.startswith("game_"):
            game_name = data.replace("game_", "")
            
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
                    await game_handlers[game_name](update, context)
                except Exception as e:
                    logger.error(f"Error loading game {game_name}: {e}")
                    await query.edit_message_text(
                        f"❌ Error loading {game_name}. Please try again.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
                        ])
                    )
            else:
                await query.edit_message_text(
                    f"🎮 {game_name.title()} game coming soon!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
                    ])
                )
            return
        
        # Default response
        else:
            await query.edit_message_text(
                "⚠️ This feature is not available yet.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
                ])
            )

games_handler = GamesHandler()
