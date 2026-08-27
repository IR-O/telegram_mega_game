from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database.mongodb import db
from locales.translations import get_translation
from config import Config

async def get_main_menu(user_id: int) -> InlineKeyboardMarkup:
    """Get main game menu with translations"""
    # Get user's language
    user_data = await db.find_one('users', {'telegram_id': user_id})
    lang = user_data.get('language', 'en') if user_data else 'en'
    
    keyboard = [
        [
            InlineKeyboardButton("⚔️ Mafia", callback_data="game_mafia"),
            InlineKeyboardButton("🌌 Space", callback_data="game_space")
        ],
        [
            InlineKeyboardButton("🧟 Zombies", callback_data="game_zombies"),
            InlineKeyboardButton("🏴‍☠️ Pirates", callback_data="game_pirates")
        ],
        [
            InlineKeyboardButton("🧪 Mutation", callback_data="game_mutation"),
            InlineKeyboardButton("👻 Haunted", callback_data="game_haunted")
        ],
        [
            InlineKeyboardButton("🧠 Mind Wars", callback_data="game_mindwars"),
            InlineKeyboardButton("🏙️ City", callback_data="game_city")
        ],
        [
            InlineKeyboardButton("🕵️ Spy", callback_data="game_spy"),
            InlineKeyboardButton("🐉 Dragons", callback_data="game_dragons")
        ],
        [
            InlineKeyboardButton("🎴 Cards", callback_data="game_cards"),
            InlineKeyboardButton("🔎 Detective", callback_data="game_detective")
        ],
        [
            InlineKeyboardButton("🏎️ Racing", callback_data="game_racing")
        ],
        [
            InlineKeyboardButton("👤 Profile", callback_data="profile"),
            InlineKeyboardButton("💰 Balance", callback_data="balance")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="top"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Get profile keyboard with translations"""
    user_data = await db.find_one('users', {'telegram_id': user_id})
    lang = user_data.get('language', 'en') if user_data else 'en'
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Stats", callback_data="profile_stats"),
            InlineKeyboardButton("🎯 Achievements", callback_data="profile_achievements")
        ],
        [
            InlineKeyboardButton("📜 Titles", callback_data="profile_titles"),
            InlineKeyboardButton("💰 Economy", callback_data="profile_economy")
        ],
        [
            InlineKeyboardButton("📈 Full Stats", callback_data="profile_full"),
            InlineKeyboardButton("📋 Games Stats", callback_data="profile_games")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_game_keyboard(game_name: str, user_id: int) -> InlineKeyboardMarkup:
    """Get game-specific keyboard with translations"""
    user_data = await db.find_one('users', {'telegram_id': user_id})
    lang = user_data.get('language', 'en') if user_data else 'en'
    
    keyboards = {
        'mafia': [
            [
                InlineKeyboardButton("⚔️ Fight", callback_data="mafia_fight"),
                InlineKeyboardButton("💰 Rob", callback_data="mafia_rob")
            ],
            [
                InlineKeyboardButton("💼 Work", callback_data="mafia_work"),
                InlineKeyboardButton("📋 Missions", callback_data="mafia_missions")
            ],
            [
                InlineKeyboardButton("🛒 Shop", callback_data="mafia_shop"),
                InlineKeyboardButton("🏢 Gang", callback_data="mafia_gang")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ],
        'space': [
            [
                InlineKeyboardButton("🚀 Explore", callback_data="space_explore"),
                InlineKeyboardButton("⛏️ Mine", callback_data="space_mine")
            ],
            [
                InlineKeyboardButton("🚀 Fleet", callback_data="space_fleet"),
                InlineKeyboardButton("🌍 Planets", callback_data="space_planets")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ],
        'zombies': [
            [
                InlineKeyboardButton("🧟 Fight", callback_data="zombies_fight"),
                InlineKeyboardButton("🔍 Explore", callback_data="zombies_explore")
            ],
            [
                InlineKeyboardButton("🏠 Shelter", callback_data="zombies_shelter"),
                InlineKeyboardButton("📦 Craft", callback_data="zombies_craft")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ],
        'pirates': [
            [
                InlineKeyboardButton("⛵ Sail", callback_data="pirates_sail"),
                InlineKeyboardButton("💀 Raid", callback_data="pirates_raid")
            ],
            [
                InlineKeyboardButton("🏝️ Islands", callback_data="pirates_islands"),
                InlineKeyboardButton("🛥️ Ship", callback_data="pirates_ship")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
    }
    return InlineKeyboardMarkup(keyboards.get(game_name, [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ]))
