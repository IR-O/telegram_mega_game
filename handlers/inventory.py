from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongodb import db
from datetime import datetime

class InventoryHandler:
    @staticmethod
    async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /inventory command"""
        user = update.effective_user
        
        # Get user's inventory from various collections
        mafia_player = await db.find_one('mafia_players', {'user_id': user.id})
        space_player = await db.find_one('space_players', {'user_id': user.id})
        zombie_player = await db.find_one('zombie_players', {'user_id': user.id})
        pirate_player = await db.find_one('pirates', {'user_id': user.id})
        mutation_player = await db.find_one('mutations', {'user_id': user.id})
        card_player = await db.find_one('cards', {'user_id': user.id})
        dragon_player = await db.find_one('dragons', {'user_id': user.id})
        
        # Build inventory display
        inventory_text = "📦 **INVENTORY**\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Weapons
        weapons = []
        if mafia_player and mafia_player.get('weapon'):
            weapons.append(mafia_player['weapon'])
        
        # Armor
        armor = []
        if mafia_player and mafia_player.get('armor'):
            armor.append(mafia_player['armor'])
        
        # Cards
        cards = []
        if card_player:
            cards = card_player.get('cards', [])
        
        # Dragons
        dragons = []
        if dragon_player:
            dragons = dragon_player.get('dragons', [])
        
        # Creatures
        creatures = []
        if mutation_player:
            creatures = mutation_player.get('creatures', [])
        
        inventory_text += f"⚔️ **Weapons:** {len(weapons)}\n"
        inventory_text += f"🛡️ **Armor:** {len(armor)}\n"
        inventory_text += f"🎴 **Cards:** {len(cards)}\n"
        inventory_text += f"🐉 **Dragons:** {len(dragons)}\n"
        inventory_text += f"🧬 **Creatures:** {len(creatures)}\n\n"
        
        # Show items
        if weapons:
            inventory_text += "**⚔️ Weapons:**\n"
            for weapon in weapons[:5]:
                inventory_text += f"• {weapon}\n"
            if len(weapons) > 5:
                inventory_text += f"... and {len(weapons) - 5} more\n"
            inventory_text += "\n"
        
        if cards:
            inventory_text += "**🎴 Top Cards:**\n"
            for card in cards[:5]:
                inventory_text += f"• {card.get('name', 'Unknown')} ({card.get('rarity', 'Common')})\n"
            if len(cards) > 5:
                inventory_text += f"... and {len(cards) - 5} more\n"
            inventory_text += "\n"
        
        if dragons:
            inventory_text += "**🐉 Dragons:**\n"
            for dragon in dragons[:5]:
                inventory_text += f"• {dragon.get('name', 'Unknown')} (Level {dragon.get('level', 1)})\n"
            if len(dragons) > 5:
                inventory_text += f"... and {len(dragons) - 5} more\n"
        
        keyboard = [
            [
                InlineKeyboardButton("⚔️ Weapons", callback_data="inventory_weapons"),
                InlineKeyboardButton("🛡️ Armor", callback_data="inventory_armor")
            ],
            [
                InlineKeyboardButton("🎴 Cards", callback_data="inventory_cards"),
                InlineKeyboardButton("🐉 Dragons", callback_data="inventory_dragons")
            ],
            [
                InlineKeyboardButton("🧬 Creatures", callback_data="inventory_creatures"),
                InlineKeyboardButton("📊 Full Inventory", callback_data="inventory_full")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            inventory_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inventory callbacks"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        data = query.data
        
        if data == "inventory_weapons":
            # Show weapons
            mafia_player = await db.find_one('mafia_players', {'user_id': user.id})
            weapons = []
            if mafia_player and mafia_player.get('weapon'):
                weapons.append(mafia_player['weapon'])
            
            if not weapons:
                await query.edit_message_text(
                    "⚔️ No weapons found.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Inventory", callback_data="inventory")]
                    ])
                )
                return
            
            text = "⚔️ **Your Weapons**\n\n"
            for weapon in weapons:
                text += f"• {weapon}\n"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Inventory", callback_data="inventory")]
                ])
            )
        
        elif data == "inventory_cards":
            # Show cards
            card_player = await db.find_one('cards', {'user_id': user.id})
            cards = card_player.get('cards', []) if card_player else []
            
            if not cards:
                await query.edit_message_text(
                    "🎴 No cards found.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Inventory", callback_data="inventory")]
                    ])
                )
                return
            
            text = "🎴 **Your Cards**\n\n"
            for i, card in enumerate(cards[:10], 1):
                text += f"{i}. {card.get('name', 'Unknown')} - {card.get('rarity', 'Common')}\n"
            
            if len(cards) > 10:
                text += f"\n... and {len(cards) - 10} more"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Inventory", callback_data="inventory")]
                ])
            )
        
        elif data == "inventory_dragons":
            # Show dragons
            dragon_player = await db.find_one('dragons', {'user_id': user.id})
            dragons = dragon_player.get('dragons', []) if dragon_player else []
            
            if not dragons:
                await query.edit_message_text(
                    "🐉 No dragons found.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Inventory", callback_data="inventory")]
                    ])
                )
                return
            
            text = "🐉 **Your Dragons**\n\n"
            for i, dragon in enumerate(dragons[:10], 1):
                text += f"{i}. {dragon.get('name', 'Unknown')} (Level {dragon.get('level', 1)}) - {dragon.get('rarity', 'Common')}\n"
            
            if len(dragons) > 10:
                text += f"\n... and {len(dragons) - 10} more"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Inventory", callback_data="inventory")]
                ])
            )
        
        elif data == "inventory":
            await InventoryHandler.inventory_command(update, context)
        
        elif data == "main_menu":
            from keyboards.menus import get_main_menu
            await query.edit_message_text(
                "🎮 Select a game to play:",
                reply_markup=await get_main_menu(user.id)
            )

inventory_handler = InventoryHandler()
