import json
import os
from typing import Optional

class Config:
    # Bot configuration
    BOT_TOKEN = 'bot_token'
    YOUR_USER_ID = 1247167546441072706
    WHITELISTED_USER_IDS = [869941430225862706]
    BLACKLISTED_USER_IDS = []
    DEFAULT_PREFIX = 'ss!'
    
    # File paths
    TICKET_DB = "data/tickets.json"
    JOIN_ROLES_FILE = "data/join_roles.json"
    ECONOMY_FILE = "data/economy.json"
    BLACKLIST_FILE = "data/blacklist.json"
    
    # Economy settings
    DAILY_AMOUNT = 100
    WORK_MIN = 50
    WORK_MAX = 150
    BEG_MIN = 1
    BEG_MAX = 50
    BEG_SUCCESS_RATE = 0.7
    GAMBLE_WIN_RATE = 0.4
    GAMBLE_MULTIPLIER = 2
    ROB_SUCCESS_RATE = 0.3
    ROB_PENALTY_RATE = 0.5
    FISHING_MIN = 20
    FISHING_MAX = 150
    MINING_MIN = 30
    MINING_MAX = 200
    HEALTH_MAX = 100
    ATTACK_MAX = 100
    DEFENSE_MAX = 100
    MAX_SPAM_LIMIT = 3000
    
    # Spam detection
    SPAM_THRESHOLD = 5
    SPAM_TIME_WINDOW = 10
    
    # Shop items
    SHOP_ITEMS = {
    # Food
    "apple": {"price": 50, "description": "🍎 A delicious apple (+10 health)", "type": "food"},
    "pizza": {"price": 200, "description": "🍕 Slice of pizza (+30 health)", "type": "food"},
    "ramen": {"price": 150, "description": "🍜 Hot ramen (+25 health)", "type": "food"},
    "burger": {"price": 120, "description": "🍔 Juicy burger (+20 health)", "type": "food"},
    
    # Weapons
    "sword": {"price": 300, "description": "⚔️ Sharp sword (+25 attack)", "type": "weapon"},
    "dagger": {"price": 150, "description": "🗡️ Small dagger (+15 attack)", "type": "weapon"},
    "bow": {"price": 400, "description": "🏹 Bow and arrows (+30 attack)", "type": "weapon"},
    "gun": {"price": 1000, "description": "🔫 Powerful gun (+50 attack)", "type": "weapon"},
    
    # Armor
    "shield": {"price": 250, "description": "🛡️ Sturdy shield (+20 defense)", "type": "armor"},
    "helmet": {"price": 200, "description": "⛑️ Protective helmet (+15 defense)", "type": "armor"},
    "armor": {"price": 500, "description": "🥋 Full armor (+40 defense)", "type": "armor"},
    
    # Tools
    "laptop": {"price": 1000, "description": "💻 Programming laptop (+50% work income)", "type": "tool"},
    "pickaxe": {"price": 600, "description": "⛏️ Mining pickaxe (better mining rewards)", "type": "tool"},
    "fishingrod": {"price": 450, "description": "🎣 Fishing rod (better fishing rewards)", "type": "tool"},
    
    # Luxury
    "diamond": {"price": 5000, "description": "💎 Rare diamond (status symbol)", "type": "luxury"},
    "goldbar": {"price": 3000, "description": "🪙 Solid gold bar (investment)", "type": "luxury"},
    "watch": {"price": 2500, "description": "⌚ Luxury watch (flex item)", "type": "luxury"},
    
    # Special
    "lifepotion": {"price": 1500, "description": "🧪 Life potion (revive after death)", "type": "special"},
    "multiplier": {"price": 2000, "description": "✨ 2x Multiplier (1 hour)", "type": "special"},
    "lootbox": {"price": 800, "description": "🎁 Lootbox (random item)", "type": "special"}
}
    
    # Custom prefixes storage
    custom_prefixes = {}
    
    @classmethod
    def get_prefix(cls, bot, message):
        if not message.guild:
            return cls.DEFAULT_PREFIX
        return commands.when_mentioned_or(cls.custom_prefixes.get(message.guild.id, cls.DEFAULT_PREFIX))(bot, message)
    
    @classmethod
    def load_join_roles(cls):
        if os.path.exists(cls.JOIN_ROLES_FILE):
            with open(cls.JOIN_ROLES_FILE, "r") as f:
                return json.load(f)
        return {}
    
    @classmethod
    def save_join_roles(cls, data):
        os.makedirs(os.path.dirname(cls.JOIN_ROLES_FILE), exist_ok=True)
        with open(cls.JOIN_ROLES_FILE, "w") as f:
            json.dump(data, f, indent=4)
    
    @classmethod
    def load_blacklist(cls):
        if os.path.exists(cls.BLACKLIST_FILE):
            with open(cls.BLACKLIST_FILE, "r") as f:
                return json.load(f)
        return {}
    
    @classmethod
    def save_blacklist(cls, data):
        os.makedirs(os.path.dirname(cls.BLACKLIST_FILE), exist_ok=True)
        with open(cls.BLACKLIST_FILE, "w") as f:
            json.dump(data, f, indent=4)
