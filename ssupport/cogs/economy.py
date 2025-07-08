import random
import json
import os
from datetime import datetime, timedelta
import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import log_command
from utils.config import Config

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def load_economy(self):
        if not os.path.exists(Config.ECONOMY_FILE):
            return {}
        try:
            with open(Config.ECONOMY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_economy(self, data):
        with open(Config.ECONOMY_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get_user_data(self, guild_id, user_id):
        economy = self.load_economy()
        
        if str(guild_id) not in economy:
            economy[str(guild_id)] = {}
        
        if str(user_id) not in economy[str(guild_id)]:
            economy[str(guild_id)][str(user_id)] = {
                "balance": 100,
                "last_daily": 0,
                "last_work": 0,
                "last_beg": 0,
                "last_fish": 0,
                "last_mine": 0,
                "health": Config.HEALTH_MAX,
                "attack": 0,
                "defense": 0,
                "inventory": {},
                "stats": {
                    "daily_claimed": 0,
                    "work_count": 0,
                    "beg_success": 0,
                    "gambles_won": 0,
                    "gambles_lost": 0,
                    "robs_success": 0,
                    "robs_failed": 0,
                    "fish_caught": 0,
                    "mined": 0,
                    "total_earned": 100
                }
            }
            self.save_economy(economy)
        
        return economy[str(guild_id)][str(user_id)]

    def update_user_data(self, guild_id, user_id, data):
        economy = self.load_economy()
        economy[str(guild_id)][str(user_id)] = data
        self.save_economy(economy)

    @commands.command(name="balance", aliases=["bal", "wallet"])
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_data = self.get_user_data(ctx.guild.id, member.id)
        
        embed = discord.Embed(
            title=f"💰 {member.display_name}'s Balance",
            description=f"**Wallet:** {user_data['balance']} <:coin:1378233650583306262>",
            color=discord.Color.gold()
        )
        
        inventory = user_data.get("inventory", {})
        if inventory:
            items = "\n".join([f"{item} x{count}" for item, count in inventory.items()][:3])
            embed.add_field(name="Inventory Preview", value=items, inline=False)
        
        embed.set_footer(text=f"Use {ctx.prefix}shop to see items you can buy")
        await ctx.send(embed=embed)
        log_command(ctx, "balance", success=True)

    @bot.tree.command(name="balance", description="Check your coin balance")
@app_commands.describe(member="The member to check (optional)")
async def slash_balance(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    user_data = get_user_data(interaction.guild_id, member.id)
    
    embed = discord.Embed(
        title=f"💰 {member.display_name}'s Balance",
        description=f"**Wallet:** {user_data['balance']}<:coin:1378233650583306262>coins",
        color=discord.Color.gold()
    )
    
    inventory = user_data.get("inventory", {})
    if inventory:
        items = "\n".join([f"{item} x{count}" for item, count in inventory.items()][:3])
        embed.add_field(name="Inventory Preview", value=items, inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.command(name="daily")
async def daily(ctx):
    """Claim your daily coins"""
    user_data = get_user_data(ctx.guild.id, ctx.author.id)
    now = datetime.now().timestamp()
    
    # Check if daily was already claimed
    if now - user_data["last_daily"] < 86400:  # 24 hours
        next_claim = datetime.fromtimestamp(user_data["last_daily"] + 86400)
        time_left = next_claim - datetime.now()
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        await ctx.send(f"⏳ You've already claimed your daily today! Come back in {hours}h {minutes}m")
        return
    
    # Give daily reward
    bonus = 0
    # Check for laptop item bonus
    if "laptop" in user_data.get("inventory", {}):
        bonus = 50
    
    amount = DAILY_AMOUNT + bonus
    user_data["balance"] += amount
    user_data["last_daily"] = now
    user_data["stats"]["daily_claimed"] += 1
    update_user_data(ctx.guild.id, ctx.author.id, user_data)
    
    embed = discord.Embed(
        title="💰 Daily Reward Claimed!",
        description=f"{ctx.author.mention} received **{amount} coins**!",
        color=discord.Color.green()
    )
    if bonus:
        embed.add_field(name="Laptop Bonus", value=f"+{bonus} coins for owning a laptop!", inline=False)
    embed.set_footer(text="Come back tomorrow for more!")
    await ctx.send(embed=embed)

@bot.tree.command(name="daily", description="Claim your daily coins")
async def slash_daily(interaction: discord.Interaction):
    user_data = get_user_data(interaction.guild_id, interaction.user.id)
    now = datetime.now().timestamp()
    
    if now - user_data["last_daily"] < 86400:
        next_claim = datetime.fromtimestamp(user_data["last_daily"] + 86400)
        time_left = next_claim - datetime.now()
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        await interaction.response.send_message(
            f"⏳ You've already claimed your daily today! Come back in {hours}h {minutes}m",
            ephemeral=True
        )
        return
    
    bonus = 0
    if "laptop" in user_data.get("inventory", {}):
        bonus = 50
    
    amount = DAILY_AMOUNT + bonus
    user_data["balance"] += amount
    user_data["last_daily"] = now
    user_data["stats"]["daily_claimed"] += 1
    update_user_data(interaction.guild_id, interaction.user.id, user_data)
    
    embed = discord.Embed(
        title="💰 Daily Reward Claimed!",
        description=f"{interaction.user.mention} received **{amount} <:coin:1378233650583306262>**!",
        color=discord.Color.green()
    )
    if bonus:
        embed.add_field(name="Laptop Bonus", value=f"+{bonus} <:coin:1378233650583306262> for owning a laptop!", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.command(name="work")
async def work(ctx):
    """Work to earn coins (1 hour cooldown)"""
    user_data = get_user_data(ctx.guild.id, ctx.author.id)
    now = datetime.now().timestamp()
    
    # Check cooldown
    if now - user_data["last_work"] < 3600:  # 1 hour
        next_work = datetime.fromtimestamp(user_data["last_work"] + 3600)
        time_left = next_work - datetime.now()
        minutes = time_left.seconds // 60
        await ctx.send(f"⏳ You're too tired to work! Come back in {minutes} minutes")
        return
    
    # Calculate earnings
    amount = random.randint(WORK_MIN, WORK_MAX)
    user_data["balance"] += amount
    user_data["last_work"] = now
    user_data["stats"]["work_count"] += 1
    update_user_data(ctx.guild.id, ctx.author.id, user_data)
    
    jobs = [
        "flipped burgers at Krusty Krab",
        "programmed a Discord bot",
        "mowed lawns in the neighborhood",
        "streamed on Twitch",
        "delivered packages for Amazon",
        "designed a website for a client",
        "sold vintage items on eBay"
    ]
    
    embed = discord.Embed(
        title="💼 Work Completed!",
        description=f"{ctx.author.mention} {random.choice(jobs)} and earned **{amount} <:coin:1378233650583306262>**!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.tree.command(name="work", description="Work to earn coins (1 hour cooldown)")
async def slash_work(interaction: discord.Interaction):
    user_data = get_user_data(interaction.guild_id, interaction.user.id)
    now = datetime.now().timestamp()
    
    if now - user_data["last_work"] < 3600:
        next_work = datetime.fromtimestamp(user_data["last_work"] + 3600)
        time_left = next_work - datetime.now()
        minutes = time_left.seconds // 60
        await interaction.response.send_message(
            f"⏳ You're too tired to work! Come back in {minutes} minutes",
            ephemeral=True
        )
        return
    
    amount = random.randint(WORK_MIN, WORK_MAX)
    user_data["balance"] += amount
    user_data["last_work"] = now
    user_data["stats"]["work_count"] += 1
    update_user_data(interaction.guild_id, interaction.user.id, user_data)
    
    jobs = [
        "flipped burgers at Krusty Krab",
        "programmed a Discord bot",
        "mowed lawns in the neighborhood",
        "streamed on Twitch",
        "delivered packages for Amazon",
        "designed a website for a client",
        "sold vintage items on eBay"
    ]
    
    embed = discord.Embed(
        title="💼 Work Completed!",
        description=f"{interaction.user.mention} {random.choice(jobs)} and earned **{amount} coins**!",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@bot.command(name="beg")
async def beg(ctx):
    """Beg for coins (30 second cooldown)"""
    user_data = get_user_data(ctx.guild.id, ctx.author.id)
    now = datetime.now().timestamp()
    
    # Check cooldown
    if now - user_data["last_beg"] < 30:
        next_beg = datetime.fromtimestamp(user_data["last_beg"] + 30)
        time_left = next_beg - datetime.now()
        seconds = time_left.seconds
        await ctx.send(f"⏳ No one wants to give you money right now. Try again in {seconds} seconds")
        return
    
    # Calculate success
    success = random.random() < BEG_SUCCESS_RATE
    user_data["last_beg"] = now
    
    if success:
        amount = random.randint(BEG_MIN, BEG_MAX)
        user_data["balance"] += amount
        user_data["stats"]["beg_success"] += 1
        responses = [
            f"💵 A kind stranger gave you **{amount} coins**!",
            f"🧓 An old lady took pity and gave you **{amount} coins**!",
            f"👑 The king felt generous and gave you **{amount} coins**!",
            f"🏦 The bank made an error in your favor! You got **{amount} coins**!"
        ]
        await ctx.send(random.choice(responses))
    else:
        responses = [
            "😢 No one gave you any money...",
            "🚶‍♂️ People ignored you and walked by...",
            "👮 A police officer told you to move along...",
            "🐕 A dog barked at you and scared away potential donors..."
        ]
        await ctx.send(random.choice(responses))
    
    update_user_data(ctx.guild.id, ctx.author.id, user_data)

@bot.tree.command(name="beg", description="Beg for coins (30 second cooldown)")
async def slash_beg(interaction: discord.Interaction):
    user_data = get_user_data(interaction.guild_id, interaction.user.id)
    now = datetime.now().timestamp()
    
    if now - user_data["last_beg"] < 30:
        next_beg = datetime.fromtimestamp(user_data["last_beg"] + 30)
        time_left = next_beg - datetime.now()
        seconds = time_left.seconds
        await interaction.response.send_message(
            f"⏳ No one wants to give you money right now. Try again in {seconds} seconds",
            ephemeral=True
        )
        return
    
    success = random.random() < BEG_SUCCESS_RATE
    user_data["last_beg"] = now
    
    if success:
        amount = random.randint(BEG_MIN, BEG_MAX)
        user_data["balance"] += amount
        user_data["stats"]["beg_success"] += 1
        responses = [
            f"💵 A kind stranger gave you **{amount} coins**!",
            f"🧓 An old lady took pity and gave you **{amount} coins**!",
            f"👑 The king felt generous and gave you **{amount} coins**!",
            f"🏦 The bank made an error in your favor! You got **{amount} coins**!"
        ]
        await interaction.response.send_message(random.choice(responses))
    else:
        responses = [
            "😢 No one gave you any money...",
            "🚶‍♂️ People ignored you and walked by...",
            "👮 A police officer told you to move along...",
            "🐕 A dog barked at you and scared away potential donors..."
        ]
        await interaction.response.send_message(random.choice(responses))
    
    update_user_data(interaction.guild_id, interaction.user.id, user_data)

@bot.command(name="gamble")
async def gamble(ctx, amount: int):
    """Gamble your coins (50/50 chance to double or lose)"""
    if amount <= 0:
        await ctx.send("❌ Please enter a positive amount to gamble!")
        return
    
    user_data = get_user_data(ctx.guild.id, ctx.author.id)
    
    if user_data["balance"] < amount:
        await ctx.send("❌ You don't have enough coins to gamble that amount!")
        return
    
    # Calculate win/loss
    win = random.random() < GAMBLE_WIN_RATE
    if win:
        winnings = amount * GAMBLE_MULTIPLIER
        user_data["balance"] += winnings
        user_data["stats"]["gambles_won"] += 1
        await ctx.send(f"🎰 **JACKPOT!** You won **{winnings} <:coin:1378233650583306262>**! Your balance is now **{user_data['balance']} coins**")
    else:
        user_data["balance"] -= amount
        user_data["stats"]["gambles_lost"] += 1
        await ctx.send(f"💸 **BAD LUCK!** You lost **{amount} <:coin:1378233650583306262>**! Your balance is now **{user_data['balance']} coins**")
    
    update_user_data(ctx.guild.id, ctx.author.id, user_data)

@bot.tree.command(name="gamble", description="Gamble your coins (50/50 chance to double or lose)")
@app_commands.describe(amount="Amount of coins to gamble")
async def slash_gamble(interaction: discord.Interaction, amount: int):
    if amount <= 0:
        await interaction.response.send_message("❌ Please enter a positive amount to gamble!", ephemeral=True)
        return
    
    user_data = get_user_data(interaction.guild_id, interaction.user.id)
    
    if user_data["balance"] < amount:
        await interaction.response.send_message("❌ You don't have enough coins to gamble that amount!", ephemeral=True)
        return
    
    win = random.random() < GAMBLE_WIN_RATE
    if win:
        winnings = amount * GAMBLE_MULTIPLIER
        user_data["balance"] += winnings
        user_data["stats"]["gambles_won"] += 1
        message = f"🎰 **JACKPOT!** You won **{winnings} <:coin:1378233650583306262>**! Your balance is now **{user_data['balance']} <:coin:1378233650583306262>**"
    else:
        user_data["balance"] -= amount
        user_data["stats"]["gambles_lost"] += 1
        message = f"💸 **BAD LUCK!** You lost **{amount} <:coin:1378233650583306262>**! Your balance is now **{user_data['balance']} <:coin:1378233650583306262>**"
    
    update_user_data(interaction.guild_id, interaction.user.id, user_data)
    await interaction.response.send_message(message)

@bot.command(name="rob")
async def rob(ctx, member: discord.Member):
    """Attempt to rob another user (30% success rate)"""
    if member.bot:
        await ctx.send("❌ You can't rob bots!")
        return
    
    if member.id == ctx.author.id:
        await ctx.send("❌ You can't rob yourself!")
        return
    
    robber_data = get_user_data(ctx.guild.id, ctx.author.id)
    victim_data = get_user_data(ctx.guild.id, member.id)
    
    if victim_data["balance"] < 10:
        await ctx.send(f"❌ {member.display_name} is too poor to rob!")
        return
    
    # Calculate success
    success = random.random() < ROB_SUCCESS_RATE
    amount = random.randint(10, min(500, victim_data["balance"]))
    
    if success:
        # Successful robbery
        robber_data["balance"] += amount
        victim_data["balance"] -= amount
        robber_data["stats"]["robs_success"] += 1
        
        responses = [
            f"🔫 You successfully robbed **{amount} <:coin:1378233650583306262>** from {member.display_name}!",
            f"🏃‍♂️ You snatched **{amount} <:coin:1378233650583306262>** from {member.display_name} and escaped!",
            f"🦹 You pulled off a heist and stole **{amount} <:coin:1378233650583306262>** from {member.display_name}!"
        ]
        await ctx.send(random.choice(responses))
    else:
        # Failed robbery - pay penalty
        penalty = int(amount * ROB_PENALTY_RATE)
        robber_data["balance"] -= penalty
        robber_data["balance"] = max(0, robber_data["balance"])  # Prevent negative balance
        robber_data["stats"]["robs_failed"] += 1
        
        responses = [
            f"🚨 You got caught trying to rob {member.display_name} and paid a **{penalty} <:coin:1378233650583306262>** fine!",
            f"👮 The police arrested you during your robbery attempt! You paid **{penalty} <:coin:1378233650583306262>** in bail!",
            f"🥊 {member.display_name} fought back and took **{penalty} <:coin:1378233650583306262>** from you instead!"
        ]
        await ctx.send(random.choice(responses))
    
    update_user_data(ctx.guild.id, ctx.author.id, robber_data)
    update_user_data(ctx.guild.id, member.id, victim_data)

@bot.tree.command(name="rob", description="Attempt to rob another user (30% success rate)")
@app_commands.describe(member="The member to rob")
async def slash_rob(interaction: discord.Interaction, member: discord.Member):
    if member.bot:
        await interaction.response.send_message("❌ You can't rob bots!", ephemeral=True)
        return
    
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't rob yourself!", ephemeral=True)
        return
    
    robber_data = get_user_data(interaction.guild_id, interaction.user.id)
    victim_data = get_user_data(interaction.guild_id, member.id)
    
    if victim_data["balance"] < 10:
        await interaction.response.send_message(f"❌ {member.display_name} is too poor to rob!", ephemeral=True)
        return
    
    success = random.random() < ROB_SUCCESS_RATE
    amount = random.randint(10, min(500, victim_data["balance"]))
    
    if success:
        robber_data["balance"] += amount
        victim_data["balance"] -= amount
        robber_data["stats"]["robs_success"] += 1
        responses = [
            f"🔫 You successfully robbed **{amount} <:coin:1378233650583306262>** from {member.display_name}!",
            f"🏃‍♂️ You snatched **{amount} <:coin:1378233650583306262>** from {member.display_name} and escaped!",
            f"🦹 You pulled off a heist and stole **{amount} <:coin:1378233650583306262>** from {member.display_name}!"
        ]
        message = random.choice(responses)
    else:
        penalty = int(amount * ROB_PENALTY_RATE)
        robber_data["balance"] -= penalty
        robber_data["balance"] = max(0, robber_data["balance"])
        robber_data["stats"]["robs_failed"] += 1
        responses = [
            f"🚨 You got caught trying to rob {member.display_name} and paid a **{penalty} <:coin:1378233650583306262>** fine!",
            f"👮 The police arrested you during your robbery attempt! You paid **{penalty} <:coin:1378233650583306262>** in bail!",
            f"🥊 {member.display_name} fought back and took **{penalty} <:coin:1378233650583306262>** from you instead!"
        ]
        message = random.choice(responses)
    
    update_user_data(interaction.guild_id, interaction.user.id, robber_data)
    update_user_data(interaction.guild_id, member.id, victim_data)
    await interaction.response.send_message(message)

@bot.command(name="shop")
async def shop(ctx):
    """View items available in the shop"""
    embed = discord.Embed(
        title="🛒 Item Shop",
        description="Buy items with your coins!",
        color=discord.Color.blue()
    )
    
    for item, details in SHOP_ITEMS.items():
        embed.add_field(
            name=f"{item.capitalize()} - {details['price']} coins",
            value=details["description"],
            inline=False
        )
    
    embed.set_footer(text=f"Use {ctx.prefix}buy [item] to purchase an item")
    await ctx.send(embed=embed)

@bot.tree.command(name="shop", description="View items available in the shop")
async def slash_shop(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛒 Item Shop",
        description="Buy items with your coins!",
        color=discord.Color.blue()
    )
    
    for item, details in SHOP_ITEMS.items():
        embed.add_field(
            name=f"{item.capitalize()} - {details['price']} <:coin:1378233650583306262>",
            value=details["description"],
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.command(name="buy")
async def buy(ctx, item: str):
    """Purchase an item from the shop"""
    item = item.lower()
    if item not in SHOP_ITEMS:
        await ctx.send(f"❌ That item doesn't exist! Use `{ctx.prefix}shop` to see available items.")
        return
    
    price = SHOP_ITEMS[item]["price"]
    user_data = get_user_data(ctx.guild.id, ctx.author.id)
    
    if user_data["balance"] < price:
        await ctx.send(f"❌ You need {price}<:coin:1378233650583306262> to buy a {item}! You only have {user_data['balance']} coins.")
        return
    
    # Process purchase
    user_data["balance"] -= price
    inventory = user_data.get("inventory", {})
    inventory[item] = inventory.get(item, 0) + 1
    user_data["inventory"] = inventory
    
    update_user_data(ctx.guild.id, ctx.author.id, user_data)
    
    embed = discord.Embed(
        title="🛍️ Purchase Complete!",
        description=f"You bought a **{item}** for **{price} <:coin:1378233650583306262>**!",
        color=discord.Color.green()
    )
    embed.add_field(name="Description", value=SHOP_ITEMS[item]["description"])
    embed.set_footer(text=f"Your new balance: {user_data['balance']} <:coin:1378233650583306262>")
    await ctx.send(embed=embed)

@bot.tree.command(name="buy", description="Purchase an item from the shop")
@app_commands.describe(item="The item you want to buy")
async def slash_buy(interaction: discord.Interaction, item: str):
    item = item.lower()
    if item not in SHOP_ITEMS:
        await interaction.response.send_message(
            f"❌ That item doesn't exist! Use `/shop` to see available items.",
            ephemeral=True
        )
        return
    
    price = SHOP_ITEMS[item]["price"]
    user_data = get_user_data(interaction.guild_id, interaction.user.id)
    
    if user_data["balance"] < price:
        await interaction.response.send_message(
            f"❌ You need {price} <:coin:1378233650583306262> to buy a {item}! You only have {user_data['balance']} <:coin:1378233650583306262>.",
            ephemeral=True
        )
        return
    
    user_data["balance"] -= price
    inventory = user_data.get("inventory", {})
    inventory[item] = inventory.get(item, 0) + 1
    user_data["inventory"] = inventory
    
    update_user_data(interaction.guild_id, interaction.user.id, user_data)
    
    embed = discord.Embed(
        title="🛍️ Purchase Complete!",
        description=f"You bought a **{item}** for **{price} <:coin:1378233650583306262>**!",
        color=discord.Color.green()
    )
    embed.add_field(name="Description", value=SHOP_ITEMS[item]["description"])
    await interaction.response.send_message(embed=embed)

@bot.command(name="inventory", aliases=["inv"])
async def inventory(ctx, member: discord.Member = None):
    """View your inventory"""
    member = member or ctx.author
    user_data = get_user_data(ctx.guild.id, member.id)
    inventory = user_data.get("inventory", {})
    
    if not inventory:
        await ctx.send(f"{member.display_name}'s inventory is empty!")
        return
    
    embed = discord.Embed(
        title=f"🎒 {member.display_name}'s Inventory",
        color=discord.Color.dark_gold()
    )
    
    for item, count in inventory.items():
        item_info = SHOP_ITEMS.get(item, {"description": "Unknown item"})
        embed.add_field(
            name=f"{item.capitalize()} x{count}",
            value=item_info["description"],
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.tree.command(name="inventory", description="View your inventory")
@app_commands.describe(member="The member to view (optional)")
async def slash_inventory(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    user_data = get_user_data(interaction.guild_id, member.id)
    inventory = user_data.get("inventory", {})
    
    if not inventory:
        await interaction.response.send_message(f"{member.display_name}'s inventory is empty!")
        return
    
    embed = discord.Embed(
        title=f"🎒 {member.display_name}'s Inventory",
        color=discord.Color.dark_gold()
    )
    
    for item, count in inventory.items():
        item_info = SHOP_ITEMS.get(item, {"description": "Unknown item"})
        embed.add_field(
            name=f"{item.capitalize()} x{count}",
            value=item_info["description"],
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.command(name="pay")
async def pay(ctx, member: discord.Member, amount: int):
    """Pay coins to another user"""
    if amount <= 0:
        await ctx.send("❌ Please enter a positive amount to pay!")
        return
    
    if member.bot:
        await ctx.send("❌ You can't pay bots!")
        return
    
    if member.id == ctx.author.id:
        await ctx.send("❌ You can't pay yourself!")
        return
    
    sender_data = get_user_data(ctx.guild.id, ctx.author.id)
    receiver_data = get_user_data(ctx.guild.id, member.id)
    
    if sender_data["balance"] < amount:
        await ctx.send(f"❌ You only have {sender_data['balance']} <:coin:1378233650583306262>! You can't pay {amount} <:coin:1378233650583306262>.")
        return
    
    # Process payment
    sender_data["balance"] -= amount
    receiver_data["balance"] += amount
    
    update_user_data(ctx.guild.id, ctx.author.id, sender_data)
    update_user_data(ctx.guild.id, member.id, receiver_data)
    
    embed = discord.Embed(
        title="💸 Payment Sent!",
        description=f"{ctx.author.mention} paid **{amount} <:coin:1378233650583306262>** to {member.mention}!",
        color=discord.Color.green()
    )
    embed.add_field(name="Your New Balance", value=f"{sender_data['balance']} <:coin:1378233650583306262>")
    await ctx.send(embed=embed)

@bot.tree.command(name="pay", description="Pay coins to another user")
@app_commands.describe(
    member="The member to pay",
    amount="Amount of coins to send"
)
async def slash_pay(interaction: discord.Interaction, member: discord.Member, amount: int):
    if amount <= 0:
        await interaction.response.send_message("❌ Please enter a positive amount to pay!", ephemeral=True)
        return
    
    if member.bot:
        await interaction.response.send_message("❌ You can't pay bots!", ephemeral=True)
        return
    
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't pay yourself!", ephemeral=True)
        return
    
    sender_data = get_user_data(interaction.guild_id, interaction.user.id)
    receiver_data = get_user_data(interaction.guild_id, member.id)
    
    if sender_data["balance"] < amount:
        await interaction.response.send_message(
            f"❌ You only have {sender_data['balance']} coins! You can't pay {amount} <:coin:1378233650583306262>.",
            ephemeral=True
        )
        return
    
    sender_data["balance"] -= amount
    receiver_data["balance"] += amount
    
    update_user_data(interaction.guild_id, interaction.user.id, sender_data)
    update_user_data(interaction.guild_id, member.id, receiver_data)
    
    embed = discord.Embed(
        title="💸 Payment Sent!",
        description=f"{interaction.user.mention} paid **{amount}<:coin:1378233650583306262>** to {member.mention}!",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.command(name="leaderboard", aliases=["lb"])
async def leaderboard(ctx):
    """Show the wealthiest members in this server"""
    economy = load_economy()
    guild_data = economy.get(str(ctx.guild.id), {})
    
    # Get top 10 users by balance
    top_users = []
    for user_id, data in guild_data.items():
        try:
            member = ctx.guild.get_member(int(user_id))
            if member:
                top_users.append((member.display_name, data["balance"]))
        except:
            continue
    
    # Sort by balance descending
    top_users.sort(key=lambda x: x[1], reverse=True)
    top_users = top_users[:10]  # Get top 10
    
    if not top_users:
        await ctx.send("No economy data available for this server!")
        return
    
    embed = discord.Embed(
        title="🏆 Server Leaderboard",
        description="Top 10 Richest Members",
        color=discord.Color.gold()
    )
    
    for i, (name, balance) in enumerate(top_users, 1):
        embed.add_field(
            name=f"{i}. {name}",
            value=f"{balance} <:coin:1378233650583306262>",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.tree.command(name="leaderboard", description="Show the wealthiest members in this server")
async def slash_leaderboard(interaction: discord.Interaction):
    economy = load_economy()
    guild_data = economy.get(str(interaction.guild_id), {})
    
    top_users = []
    for user_id, data in guild_data.items():
        try:
            member = interaction.guild.get_member(int(user_id))
            if member:
                top_users.append((member.display_name, data["balance"]))
        except:
            continue
    
    top_users.sort(key=lambda x: x[1], reverse=True)
    top_users = top_users[:10]
    
    if not top_users:
        await interaction.response.send_message("No economy data available for this server!")
        return
    
    embed = discord.Embed(
        title="🏆 Server Leaderboard",
        description="Top 10 Richest Members",
        color=discord.Color.gold()
    )
    
    for i, (name, balance) in enumerate(top_users, 1):
        embed.add_field(
            name=f"{i}. {name}",
            value=f"{balance} <:coin:1378233650583306262>",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

# FISHING COMMAND
@bot.command(name="fish")
async def fish(ctx):
    """Go fishing to earn coins (30 min cooldown)"""
    user_data = get_user_data(ctx.guild.id, ctx.author.id)
    now = datetime.now().timestamp()
    
    has_rod = "fishingrod" in user_data.get("inventory", {})
    
    if now - user_data.get("last_fish", 0) < 1800:  # 30 minutes
        next_fish = datetime.fromtimestamp(user_data["last_fish"] + 1800)
        time_left = next_fish - datetime.now()
        minutes = time_left.seconds // 60
        await ctx.send(f"⏳ You need to wait {minutes} minutes before fishing again!")
        return
    
    base_amount = random.randint(FISHING_MIN, FISHING_MAX)
    if has_rod:
        bonus = int(base_amount * 0.5)  # 50% bonus with fishing rod
        amount = base_amount + bonus
    else:
        amount = base_amount
    
    user_data["balance"] += amount
    user_data["last_fish"] = now
    user_data["stats"]["fish_caught"] = user_data.get("stats", {}).get("fish_caught", 0) + 1
    user_data["stats"]["total_earned"] = user_data["stats"].get("total_earned", 0) + amount
    update_user_data(ctx.guild.id, ctx.author.id, user_data)
    
    catches = [
        "caught a small fish",
        "reeled in a medium-sized fish",
        "found a rare fish species",
        "caught an old boot (but it had coins inside!)",
        "discovered a treasure chest while fishing"
    ]
    
    embed = discord.Embed(
        title="🎣 Fishing Trip",
        description=f"{ctx.author.mention} {random.choice(catches)} and earned **{amount} <:coin:1378233650583306262>**!" + 
                   ("\n\n🎣 **Fishing Rod Bonus**: +50% income!" if has_rod else ""),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.tree.command(name="fish", description="Go fishing to earn coins (30 min cooldown)")
async def slash_fish(interaction: discord.Interaction):
    user_data = get_user_data(interaction.guild_id, interaction.user.id)
    now = datetime.now().timestamp()
    
    has_rod = "fishingrod" in user_data.get("inventory", {})
    
    if now - user_data.get("last_fish", 0) < 1800:
        next_fish = datetime.fromtimestamp(user_data["last_fish"] + 1800)
        time_left = next_fish - datetime.now()
        minutes = time_left.seconds // 60
        await interaction.response.send_message(
            f"⏳ You need to wait {minutes} minutes before fishing again!",
            ephemeral=True
        )
        return
    
    base_amount = random.randint(FISHING_MIN, FISHING_MAX)
    if has_rod:
        bonus = int(base_amount * 0.5)
        amount = base_amount + bonus
    else:
        amount = base_amount
    
    user_data["balance"] += amount
    user_data["last_fish"] = now
    user_data["stats"]["fish_caught"] = user_data.get("stats", {}).get("fish_caught", 0) + 1
    user_data["stats"]["total_earned"] = user_data["stats"].get("total_earned", 0) + amount
    update_user_data(interaction.guild_id, interaction.user.id, user_data)
    
    catches = [
        "caught a small fish",
        "reeled in a medium-sized fish",
        "found a rare fish species",
        "caught an old boot (but it had coins inside!)",
        "discovered a treasure chest while fishing"
    ]
    
    embed = discord.Embed(
        title="🎣 Fishing Trip",
        description=f"{interaction.user.mention} {random.choice(catches)} and earned **{amount} <:coin:1378233650583306262>**!" + 
                   ("\n\n🎣 **Fishing Rod Bonus**: +50% income!" if has_rod else ""),
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

# MINING COMMAND
@bot.command(name="mine")
async def mine(ctx):
    """Go mining to earn coins (45 min cooldown)"""
    user_data = get_user_data(ctx.guild.id, ctx.author.id)
    now = datetime.now().timestamp()
    
    has_pickaxe = "pickaxe" in user_data.get("inventory", {})
    
    if now - user_data.get("last_mine", 0) < 2700:  # 45 minutes
        next_mine = datetime.fromtimestamp(user_data["last_mine"] + 2700)
        time_left = next_mine - datetime.now()
        minutes = time_left.seconds // 60
        await ctx.send(f"⏳ You're too tired to mine! Try again in {minutes} minutes")
        return
    
    base_amount = random.randint(MINING_MIN, MINING_MAX)
    if has_pickaxe:
        bonus = int(base_amount * 0.6)  # 60% bonus with pickaxe
        amount = base_amount + bonus
    else:
        amount = base_amount
    
    user_data["balance"] += amount
    user_data["last_mine"] = now
    user_data["stats"]["mined"] = user_data.get("stats", {}).get("mined", 0) + 1
    user_data["stats"]["total_earned"] = user_data["stats"].get("total_earned", 0) + amount
    update_user_data(ctx.guild.id, ctx.author.id, user_data)
    
    finds = [
        "mined some coal",
        "found copper ore",
        "discovered iron deposits",
        "struck silver",
        "unearthed gold nuggets"
    ]
    
    embed = discord.Embed(
        title="⛏️ Mining Expedition",
        description=f"{ctx.author.mention} {random.choice(finds)} and earned **{amount} <:coin:1378233650583306262>**!" + 
                   ("\n\n⛏️ **Pickaxe Bonus**: +60% income!" if has_pickaxe else ""),
        color=discord.Color.dark_grey()
    )
    await ctx.send(embed=embed)

# USE ITEM COMMAND
@bot.command(name="use")
async def use(ctx, item: str):
    """Use an item from your inventory"""
    item = item.lower()
    user_data = get_user_data(ctx.guild.id, ctx.author.id)
    inventory = user_data.get("inventory", {})
    
    if item not in inventory or inventory[item] < 1:
        await ctx.send(f"❌ You don't have any {item} in your inventory!")
        return
    
    item_info = SHOP_ITEMS.get(item, {})
    
    if item_info.get("type") == "food":
        health_gain = int(item_info["description"].split("+")[1].split(")")[0])
        user_data["health"] = min(HEALTH_MAX, user_data.get("health", HEALTH_MAX) + health_gain)
        message = f"🍽️ You ate the {item} and gained +{health_gain} health!"
    
    elif item == "lootbox":
        possible_items = [i for i in SHOP_ITEMS.keys() if i != "lootbox"]
        reward = random.choice(possible_items)
        user_data["inventory"][reward] = user_data["inventory"].get(reward, 0) + 1
        message = f"🎁 You opened a lootbox and found a **{reward}**!"
    
    elif item == "multiplier":
        user_data["multiplier"] = {
            "active": True,
            "expires": now + 3600,
            "type": "earnings"
        }
        message = "✨ You activated a 2x earnings multiplier for 1 hour!"
    
    else:
        await ctx.send(f"❌ You can't use this item directly!")
        return
    
    user_data["inventory"][item] -= 1
    if user_data["inventory"][item] <= 0:
        del user_data["inventory"][item]
    
    update_user_data(ctx.guild.id, ctx.author.id, user_data)
    await ctx.send(message)

# STATS COMMAND
@bot.command(name="stats")
async def stats(ctx, member: discord.Member = None):
    """View your or another member's stats"""
    member = member or ctx.author
    user_data = get_user_data(ctx.guild.id, member.id)
    stats = user_data.get("stats", {})
    
    embed = discord.Embed(
        title=f"📊 {member.display_name}'s Stats",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="💰 Economy",
        value=f"Balance: {user_data['balance']} <:coin:1378233650583306262>\n" +
              f"Daily Streak: {stats.get('daily_streak', 0)} days\n" +
              f"Total Earned: {stats.get('total_earned', 0)} <:coin:1378233650583306262>",
        inline=False
    )
    
    embed.add_field(
        name="🏆 Activities",
        value=f"Worked: {stats.get('work_count', 0)} times\n" +
              f"Fish Caught: {stats.get('fish_caught', 0)}\n" +
              f"Ores Mined: {stats.get('mined', 0)}",
        inline=False
    )
    
    embed.add_field(
        name="⚔️ Combat",
        value=f"Robberies: {stats.get('robs_success', 0)}/{stats.get('robs_failed', 0)}\n" +
              f"Gambles: {stats.get('gambles_won', 0)}/{stats.get('gambles_lost', 0)}",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ADMIN ECONOMY COMMANDS
@bot.command(name="addmoney")
@commands.has_permissions(administrator=True)
async def add_money(ctx, member: discord.Member, amount: int):
    """Add money to a user's balance (Admin only)"""
    if amount <= 0:
        await ctx.send("❌ Please enter a positive amount!")
        return
    
    user_data = get_user_data(ctx.guild.id, member.id)
    user_data["balance"] += amount
    
    stats = user_data.get("stats", {})
    stats["total_earned"] = stats.get("total_earned", 0) + amount
    user_data["stats"] = stats
    
    update_user_data(ctx.guild.id, member.id, user_data)
    
    embed = discord.Embed(
        title="💰 Admin Action",
        description=f"Added **{amount} <:coin:1378233650583306262>** to {member.mention}'s balance",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="removemoney")
@commands.has_permissions(administrator=True)
async def remove_money(ctx, member: discord.Member, amount: int):
    """Remove money from a user's balance (Admin only)"""
    if amount <= 0:
        await ctx.send("❌ Please enter a positive amount!")
        return
    
    user_data = get_user_data(ctx.guild.id, member.id)
    
    if user_data["balance"] < amount:
        await ctx.send(f"❌ {member.display_name} only has {user_data['balance']} <:coin:1378233650583306262>!")
        return
    
    user_data["balance"] -= amount
    update_user_data(ctx.guild.id, member.id, user_data)
    
    embed = discord.Embed(
        title="💰 Admin Action",
        description=f"Removed **{amount} <:coin:1378233650583306262>** from {member.mention}'s balance",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command(name="resetcooldowns")
async def reset_cooldowns(ctx, member: discord.Member = None):
    """Reset your or another member's cooldowns (Admin only)"""
    member = member or ctx.author
    is_admin = ctx.author.guild_permissions.administrator
    
    if member != ctx.author and not is_admin:
        await ctx.send("❌ You can only reset your own cooldowns!")
        return
    
    user_data = get_user_data(ctx.guild.id, member.id)
    
    user_data["last_daily"] = 0
    user_data["last_work"] = 0
    user_data["last_beg"] = 0
    user_data["last_fish"] = 0
    user_data["last_mine"] = 0
    
    update_user_data(ctx.guild.id, member.id, user_data)
    
    embed = discord.Embed(
        title="⏱️ Cooldowns Reset",
        description=f"{member.mention}'s cooldowns have been reset!" + 
                   ("\n\n*Reset by admin*" if is_admin and member != ctx.author else ""),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ADMIN SLASH COMMANDS
@bot.tree.command(name="addmoney", description="Add money to a user's balance (Admin only)")
@app_commands.describe(
    member="The member to add money to",
    amount="Amount of coins to add"
)
@app_commands.checks.has_permissions(administrator=True)
async def slash_add_money(interaction: discord.Interaction, member: discord.Member, amount: int):
    if amount <= 0:
        await interaction.response.send_message(
            "❌ Please enter a positive amount!",
            ephemeral=True
        )
        return
    
    user_data = get_user_data(interaction.guild_id, member.id)
    user_data["balance"] += amount
    
    stats = user_data.get("stats", {})
    stats["total_earned"] = stats.get("total_earned", 0) + amount
    user_data["stats"] = stats
    
    update_user_data(interaction.guild_id, member.id, user_data)
    
    embed = discord.Embed(
        title="💰 Admin Action",
        description=f"Added **{amount} <:coin:1378233650583306262>** to {member.mention}'s balance",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removemoney", description="Remove money from a user's balance (Admin only)")
@app_commands.describe(
    member="The member to remove money from",
    amount="Amount of coins to remove"
)
@app_commands.checks.has_permissions(administrator=True)
async def slash_remove_money(interaction: discord.Interaction, member: discord.Member, amount: int):
    if amount <= 0:
        await interaction.response.send_message(
            "❌ Please enter a positive amount!",
            ephemeral=True
        )
        return
    
    user_data = get_user_data(interaction.guild_id, member.id)
    
    if user_data["balance"] < amount:
        await interaction.response.send_message(
            f"❌ {member.display_name} only has {user_data['balance']} <:coin:1378233650583306262>!",
            ephemeral=True
        )
        return
    
    user_data["balance"] -= amount
    update_user_data(interaction.guild_id, member.id, user_data)
    
    embed = discord.Embed(
        title="💰 Admin Action",
        description=f"Removed **{amount} <:coin:1378233650583306262>** from {member.mention}'s balance",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="resetcooldowns", description="Reset your or another member's cooldowns (Admin only)")
@app_commands.describe(member="The member to reset cooldowns for (optional)")
async def slash_reset_cooldowns(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    is_admin = interaction.user.guild_permissions.administrator
    
    if member != interaction.user and not is_admin:
        await interaction.response.send_message(
            "❌ You can only reset your own cooldowns!",
            ephemeral=True
        )
        return
    
    user_data = get_user_data(interaction.guild_id, member.id)
    
    user_data["last_daily"] = 0
    user_data["last_work"] = 0
    user_data["last_beg"] = 0
    user_data["last_fish"] = 0
    user_data["last_mine"] = 0
    
    update_user_data(interaction.guild_id, member.id, user_data)
    
    embed = discord.Embed(
        title="⏱️ Cooldowns Reset",
        description=f"{member.mention}'s cooldowns have been reset!" + 
                   ("\n\n*Reset by admin*" if is_admin and member != interaction.user else ""),
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

# HEALTH AND COMBAT COMMANDS
@bot.command(name="heal")
async def heal(ctx):
    """Check your current health status"""
    user_data = get_user_data(ctx.guild.id, ctx.author.id)
    
    health = user_data.get("health", HEALTH_MAX)
    max_health = HEALTH_MAX
    
    health_bar = "❤️" * (health // 10) + "🖤" * ((max_health - health) // 10)
    
    embed = discord.Embed(
        title=f"❤️ {ctx.author.display_name}'s Health",
        description=f"{health_bar}\n{health}/{max_health} HP",
        color=discord.Color.red()
    )
    
    if "lifepotion" in user_data.get("inventory", {}):
        embed.add_field(
            name="Lifepotion Available",
            value="You have a lifepotion in your inventory! Use it with `ss!use lifepotion` if you need to revive.",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.tree.command(name="heal", description="Check your current health status")
async def slash_heal(interaction: discord.Interaction):
    user_data = get_user_data(interaction.guild_id, interaction.user.id)
    
    health = user_data.get("health", HEALTH_MAX)
    max_health = HEALTH_MAX
    
    health_bar = "❤️" * (health // 10) + "🖤" * ((max_health - health) // 10)
    
    embed = discord.Embed(
        title=f"❤️ {interaction.user.display_name}'s Health",
        description=f"{health_bar}\n{health}/{max_health} HP",
        color=discord.Color.red()
    )
    
    if "lifepotion" in user_data.get("inventory", {}):
        embed.add_field(
            name="Lifepotion Available",
            value="You have a lifepotion in your inventory! Use it with `/use lifepotion` if you need to revive.",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.command(name="attack")
async def attack(ctx, member: discord.Member):
    """Attack another user (combat system)"""
    if member.bot:
        await ctx.send("❌ You can't attack bots!")
        return
    
    if member.id == ctx.author.id:
        await ctx.send("❌ You can't attack yourself!")
        return
    
    attacker_data = get_user_data(ctx.guild.id, ctx.author.id)
    defender_data = get_user_data(ctx.guild.id, member.id)
    
    # Calculate attack and defense
    attacker_power = attacker_data.get("attack", 0)
    defender_power = defender_data.get("defense", 0)
    
    damage = max(1, attacker_power - defender_power)
    
    # Apply damage
    defender_data["health"] = defender_data.get("health", HEALTH_MAX) - damage
    
    # Check if defender was defeated
    if defender_data["health"] <= 0:
        defender_data["health"] = 0
        reward = random.randint(50, 200)
        attacker_data["balance"] += reward
        result = f"💀 **DEFEATED!** {member.display_name} was knocked out! You stole {reward} <:coin:1378233650583306262> from them!"
    else:
        result = f"⚔️ You attacked {member.display_name} for {damage} damage! They have {defender_data['health']} HP remaining."
    
    update_user_data(ctx.guild.id, ctx.author.id, attacker_data)
    update_user_data(ctx.guild.id, member.id, defender_data)
    
    embed = discord.Embed(
        title="⚔️ Combat Results",
        description=result,
        color=discord.Color.dark_red()
    )
    await ctx.send(embed=embed)

@bot.tree.command(name="attack", description="Attack another user (combat system)")
@app_commands.describe(member="The member to attack")
async def slash_attack(interaction: discord.Interaction, member: discord.Member):
    if member.bot:
        await interaction.response.send_message("❌ You can't attack bots!", ephemeral=True)
        return
    
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't attack yourself!", ephemeral=True)
        return
    
    attacker_data = get_user_data(interaction.guild_id, interaction.user.id)
    defender_data = get_user_data(interaction.guild_id, member.id)
    
    attacker_power = attacker_data.get("attack", 0)
    defender_power = defender_data.get("defense", 0)
    
    damage = max(1, attacker_power - defender_power)
    defender_data["health"] = defender_data.get("health", HEALTH_MAX) - damage
    
    if defender_data["health"] <= 0:
        defender_data["health"] = 0
        reward = random.randint(50, 200)
        attacker_data["balance"] += reward
        result = f"💀 **DEFEATED!** {member.display_name} was knocked out! You stole {reward} <:coin:1378233650583306262> from them!"
    else:
        result = f"⚔️ You attacked {member.display_name} for {damage} damage! They have {defender_data['health']} HP remaining."
    
    update_user_data(interaction.guild_id, interaction.user.id, attacker_data)
    update_user_data(interaction.guild_id, member.id, defender_data)
    
    embed = discord.Embed(
        title="⚔️ Combat Results",
        description=result,
        color=discord.Color.dark_red()
    )
    await interaction.response.send_message(embed=embed)

    

async def setup(bot):
    await bot.add_cog(Economy(bot))
