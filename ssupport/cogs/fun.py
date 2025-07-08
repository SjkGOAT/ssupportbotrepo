import random
import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import log_command
from utils.config import Config

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Sports commands
    @commands.command(name="penalty", aliases=["soccer", "football"])
    async def penalty(self, ctx):
        """Attempt to score a penalty kick (60% success rate)"""
        outcomes = [
            ("⚽ GOAL! Perfect placement in the top corner!", 0.60),
            ("🧤 Saved by the keeper! Good attempt.", 0.25),
            ("🚫 Oh no! You blasted it over the crossbar!", 0.10),
            ("⛔ The post denies you! So close!", 0.05)
        ]
        result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]
        
        embed = discord.Embed(
            title="🏟️ Penalty Kick Attempt",
            description=f"{ctx.author.mention} steps up to take the penalty...\n\n**{result}**",
            color=discord.Color.green() if "GOAL" in result else discord.Color.red()
        )
        await ctx.send(embed=embed)
        log_command(ctx, "penalty", success=True)

    @app_commands.command(name="penalty", description="Attempt a soccer penalty kick (60% success)")
    async def slash_penalty(self, interaction: discord.Interaction):
        outcomes = [
            ("⚽ GOAL! Perfect placement in the top corner!", 0.60),
            ("🧤 Saved by the keeper! Good attempt.", 0.25),
            ("🚫 Oh no! You blasted it over the crossbar!", 0.10),
            ("⛔ The post denies you! So close!", 0.05)
        ]
        result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]
        
        embed = discord.Embed(
            title="🏟️ Penalty Kick Attempt",
            description=f"{interaction.user.mention} steps up to take the penalty...\n\n**{result}**",
            color=discord.Color.green() if "GOAL" in result else discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        log_command(interaction, "penalty", success=True)

    # Basketball Free Throw
@bot.command(name="freethrow", aliases=["basketball"])
async def freethrow(ctx):
    """Shoot a basketball free throw (75% success rate)"""
    outcomes = [
        ("🏀 SWISH! Nothing but net!", 0.75),
        ("🔨 Clank! Hit the rim and bounced out.", 0.15),
        ("✋ Blocked by an imaginary defender!", 0.05),
        ("💨 Airball... Embarrassing.", 0.05)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]
    
    embed = discord.Embed(
        title="🏀 Free Throw Attempt",
        description=f"{ctx.author.mention} shoots from the line...\n\n**{result}**",
        color=discord.Color.orange() if "SWISH" in result else discord.Color.red()
    )
    embed.set_thumbnail(url="https://i.imgur.com/nNtVbQq.png")
    await ctx.send(embed=embed)

@bot.tree.command(name="freethrow", description="Shoot a basketball free throw (75% success)")
async def slash_freethrow(interaction: discord.Interaction):
    outcomes = [
        ("🏀 SWISH! Nothing but net!", 0.75),
        ("🔨 Clank! Hit the rim and bounced out.", 0.15),
        ("✋ Blocked by an imaginary defender!", 0.05),
        ("💨 Airball... Embarrassing.", 0.05)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]
    
    embed = discord.Embed(
        title="🏀 Free Throw Attempt",
        description=f"{interaction.user.mention} shoots from the line...\n\n**{result}**",
        color=discord.Color.orange() if "SWISH" in result else discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

# Baseball Pitch
@bot.command(name="pitch", aliases=["baseball"])
async def pitch(ctx):
    """Throw a baseball pitch with random outcomes"""
    pitches = ["Fastball", "Curveball", "Slider", "Changeup", "Knuckleball"]
    pitch_type = random.choice(pitches)
    
    outcomes = [
        (f"🎯 STRIKE! Perfect {pitch_type} fools the batter!", 0.50),
        (f"💥 CRACK! {pitch_type} gets hit for a home run!", 0.15),
        (f"🏃‍♂️ Base hit! {pitch_type} was too hittable.", 0.25),
        (f"🦵 Oof! Wild {pitch_type} hits the batter.", 0.10)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]
    
    embed = discord.Embed(
        title="⚾ Pitch Outcome",
        description=f"{ctx.author.mention} throws a {pitch_type}...\n\n**{result}**",
        color=discord.Color.dark_gold()
    )
    embed.set_thumbnail(url="https://i.imgur.com/7QZ4Q9x.png")
    await ctx.send(embed=embed)

@bot.tree.command(name="pitch", description="Throw a baseball pitch with random outcomes")
async def slash_pitch(interaction: discord.Interaction):
    pitches = ["Fastball", "Curveball", "Slider", "Changeup", "Knuckleball"]
    pitch_type = random.choice(pitches)
    outcomes = [
        (f"🎯 STRIKE! Perfect {pitch_type} fools the batter!", 0.50),
        (f"💥 CRACK! {pitch_type} gets hit for a home run!", 0.15),
        (f"🏃‍♂️ Base hit! {pitch_type} was too hittable.", 0.25),
        (f"🦵 Oof! Wild {pitch_type} hits the batter.", 0.10)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]

    embed = discord.Embed(
        title="⚾ Pitch Outcome",
        description=f"{interaction.user.mention} throws a {pitch_type}...\n\n**{result}**",
        color=discord.Color.dark_gold()
    )
    embed.set_thumbnail(url="https://i.imgur.com/7QZ4Q9x.png")
    await interaction.response.send_message(embed=embed)

# Golf Swing
@bot.command(name="golfswing", aliases=["golf"])
async def golfswing(ctx):
    """Take a golf swing with random results"""
    clubs = ["Driver", "Iron", "Putter", "Wedge"]
    club = random.choice(clubs)
    
    outcomes = [
        (f"⛳ Perfect {club} shot! Lands 1ft from the hole!", 0.20),
        (f"🏌️‍♂️ Nice {club}! On the fairway/green.", 0.50),
        (f"🌳 Uh oh! {club} shot goes into the woods.", 0.20),
        (f"💦 Splash! {club} shot lands in the water.", 0.10)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]
    
    embed = discord.Embed(
        title="🏌️‍♂️ Golf Swing",
        description=f"{ctx.author.mention} swings the {club}...\n\n**{result}**",
        color=discord.Color.dark_green()
    )
    await ctx.send(embed=embed)

# Tennis Serve
@bot.command(name="tennisserve", aliases=["tennis"])
async def tennisserve(ctx):
    """Attempt a tennis serve"""
    serve_types = ["Flat", "Slice", "Kick"]
    serve = random.choice(serve_types)
    
    outcomes = [
        (f"🎾 ACE! Unreturnable {serve} serve!", 0.30),
        (f"🏸 Good {serve} serve! Rally begins.", 0.50),
        (f"🚫 Fault! {serve} serve misses.", 0.15),
        (f"😱 Double fault! Oh no!", 0.05)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]
    
    embed = discord.Embed(
        title="🎾 Tennis Serve",
        description=f"{ctx.author.mention} attempts a {serve} serve...\n\n**{result}**",
        color=discord.Color.teal()
    )
    await ctx.send(embed=embed)

@bot.tree.command(name="tennisserve", description="Attempt a tennis serve")
async def slash_tennisserve(interaction: discord.Interaction):
    serve_types = ["Flat", "Slice", "Kick"]
    serve = random.choice(serve_types)
    outcomes = [
        (f"🎾 ACE! Unreturnable {serve} serve!", 0.30),
        (f"🏸 Good {serve} serve! Rally begins.", 0.50),
        (f"🚫 Fault! {serve} serve misses.", 0.15),
        (f"😱 Double fault! Oh no!", 0.05)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]

    embed = discord.Embed(
        title="🎾 Tennis Serve",
        description=f"{interaction.user.mention} attempts a {serve} serve...\n\n**{result}**",
        color=discord.Color.teal()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="golfswing", description="Take a golf swing with random results")
async def slash_golfswing(interaction: discord.Interaction):
    clubs = ["Driver", "Iron", "Putter", "Wedge"]
    club = random.choice(clubs)
    outcomes = [
        (f"⛳ Perfect {club} shot! Lands 1ft from the hole!", 0.20),
        (f"🏌️‍♂️ Nice {club}! On the fairway/green.", 0.50),
        (f"🌳 Uh oh! {club} shot goes into the woods.", 0.20),
        (f"💦 Splash! {club} shot lands in the water.", 0.10)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]

    embed = discord.Embed(
        title="🏌️‍♂️ Golf Swing",
        description=f"{interaction.user.mention} swings the {club}...\n\n**{result}**",
        color=discord.Color.dark_green()
    )
    await interaction.response.send_message(embed=embed)

@bot.command(name="volleyball", aliases=["spike"])
async def volleyball(ctx):
    outcomes = [
        ("🔥 Monster spike! Point!", 0.40),
        ("🏐 Good serve, rally continues", 0.45),
        ("🚫 Serve into the net...", 0.10),
        ("😨 Completely whiffed the ball!", 0.05)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]
    await ctx.send(f"{ctx.author.mention} attempts a volleyball play...\n\n**{result}**")

@bot.tree.command(name="volleyball", description="Try to spike or serve in volleyball")
async def slash_volleyball(interaction: discord.Interaction):
    outcomes = [
        ("🔥 Monster spike! Point!", 0.40),
        ("🏐 Good serve, rally continues", 0.45),
        ("🚫 Serve into the net...", 0.10),
        ("😨 Completely whiffed the ball!", 0.05)
    ]
    result = random.choices([o[0] for o in outcomes], weights=[o[1] for o in outcomes])[0]
    await interaction.response.send_message(f"{interaction.user.mention} attempts a volleyball play...\n\n**{result}**")

@bot.command(name="flip", aliases=["coinflip", "heads-or-tails"])
async def flip(ctx):
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f"🎲 {ctx.author.mention} flipped a coin and got **{result}**!")
    log_command(ctx, "flip", success=True)

@bot.tree.command(name="flip", description="Flip a coin (heads or tails)")
async def slash_flip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🎲 {interaction.user.mention} flipped a coin and got **{result}**!")
    log_command(interaction, "flip", success=True)

@bot.command(name="roll", aliases=["dice"])
async def roll(ctx, sides: int = 6):
    if sides < 2:
        await ctx.send("❌ Dice must have at least 2 sides!")
        return
    result = random.randint(1, sides)
    await ctx.send(f"🎲 {ctx.author.mention} rolled a {sides}-sided die and got **{result}**!")
    log_command(ctx, "roll", success=True)

@bot.tree.command(name="roll", description="Roll a dice")
@app_commands.describe(sides="Number of sides on the dice (default: 6)")
async def slash_roll(interaction: discord.Interaction, sides: int = 6):
    if sides < 2:
        await interaction.response.send_message("❌ Dice must have at least 2 sides!", ephemeral=True)
        return
    result = random.randint(1, sides)
    await interaction.response.send_message(f"🎲 {interaction.user.mention} rolled a {sides}-sided die and got **{result}**!")
    log_command(interaction, "roll", success=True)

@bot.command(name="choose", aliases=["pick"])
async def choose(ctx, *options: str):
    """Let the bot choose between multiple options (prefix version)"""
    if len(options) < 2:
        await ctx.send("❌ Please provide at least 2 options to choose from!")
        return
    
    # Remove empty options if any
    options = [opt for opt in options if opt.strip()]
    
    if len(options) < 2:
        await ctx.send("❌ Please provide at least 2 valid options to choose from!")
        return
    
    choice = random.choice(options)
    await ctx.send(f"🤔 I choose **{choice}** from: {', '.join(f'`{o}`' for o in options)}")
    log_command(ctx, "choose", success=True)

@bot.tree.command(name="choose", description="Make the bot choose between options")
@app_commands.describe(options="Options separated by commas (e.g. pizza, burger, sushi)")
async def slash_choose(interaction: discord.Interaction, options: str):
    """Let the bot choose between multiple options (slash version)"""
    # Split by comma and clean up whitespace
    options_list = [opt.strip() for opt in options.split(",") if opt.strip()]
    
    if len(options_list) < 2:
        await interaction.response.send_message(
            "❌ Please provide at least 2 valid options separated by commas! (e.g. pizza, burger, sushi)",
            ephemeral=True
        )
        return
    
    choice = random.choice(options_list)
    await interaction.response.send_message(
        f"🤔 I choose **{choice}** from: {', '.join(f'`{o}`' for o in options_list)}"
    )
    log_command(interaction, "choose", success=True)

@bot.command(name="8ball", aliases=["ask"])
async def eight_ball(ctx, *, question: str):
    """Ask the magic 8-ball a question (prefix version)"""
    if not question.endswith('?'):
        await ctx.send("❌ That doesn't look like a question! Try ending with a '?'")
        return
    
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
        "My reply is no.", "My sources say no.", "Outlook not so good.",
        "Very doubtful."
    ]
    answer = random.choice(responses)
    await ctx.send(f"🎱 **Question:** {question}\n**Answer:** {answer}")
    log_command(ctx, "8ball", success=True)

@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question")
@app_commands.describe(question="Your question for the magic 8-ball")
async def slash_eight_ball(interaction: discord.Interaction, question: str):
    """Ask the magic 8-ball a question (slash version)"""
    if not question.endswith('?'):
        await interaction.response.send_message(
            "❌ That doesn't look like a question! Try ending with a '?'",
            ephemeral=True
        )
        return
    
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
        "My reply is no.", "My sources say no.", "Outlook not so good.",
        "Very doubtful."
    ]
    answer = random.choice(responses)
    await interaction.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {answer}")
    log_command(interaction, "8ball", success=True)

@bot.command(name="ship", aliases=["match", "love"])
async def ship(ctx, *, inputs: str):
    """Calculate love compatibility between two users or text (prefix version)"""
    # Split the input into two parts
    parts = inputs.split()
    
    if len(parts) < 2:
        await ctx.send("❌ Please provide two names or mention two users!")
        return
    
    # Try to extract mentioned users
    mentioned_users = ctx.message.mentions
    
    if len(mentioned_users) >= 2:
        # Use mentioned users
        user1, user2 = mentioned_users[0], mentioned_users[1]
        name1 = user1.display_name
        name2 = user2.display_name
    elif len(mentioned_users) == 1:
        # One mention + one text
        user1 = mentioned_users[0]
        name1 = user1.display_name
        name2 = ' '.join(parts[1:])  # Use the rest as second name
    else:
        # Pure text inputs
        half = len(parts) // 2
        name1 = ' '.join(parts[:half])
        name2 = ' '.join(parts[half:])
    
    # Don't allow shipping identical inputs
    if name1.lower() == name2.lower():
        await ctx.send("❌ You can't ship something with itself! That's just sad...")
        return
    
    # Create ship name (first 3 letters of each)
    ship_name = (name1[:3].lower() + name2[:3].lower()).capitalize()
    
    # Calculate compatibility (consistent for same inputs)
    random.seed(f"{name1}{name2}".lower())
    compatibility = random.randint(0, 100)
    
    # Generate message based on percentage
    if compatibility < 20:
        message = "💔 Not a good match... At all."
    elif compatibility < 40:
        message = "❤️‍🩹 There might be some potential... Maybe?"
    elif compatibility < 60:
        message = "💖 A decent match! Could work out!"
    elif compatibility < 80:
        message = "💘 Great chemistry! Go for it!"
    else:
        message = "💞 SOULMATES! Perfect match!!!"
    
    # Create embed
    embed = discord.Embed(
        title=f"💖 {name1} + {name2} = {ship_name}",
        description=f"**Compatibility:** {compatibility}%\n{message}",
        color=discord.Color.pink()
    )
    embed.set_thumbnail(url="https://i.imgur.com/rVaN5PZ.png")
    
    await ctx.send(embed=embed)
    log_command(ctx, "ship", success=True)

@bot.tree.command(name="ship", description="Calculate love compatibility between two users or text")
@app_commands.describe(
    input1="First name or @user",
    input2="Second name or @user"
)
async def slash_ship(interaction: discord.Interaction, input1: str, input2: str):
    """Calculate love compatibility (slash version)"""
    # Check if inputs are user mentions
    try:
        user1 = await commands.MemberConverter().convert(interaction, input1)
        name1 = user1.display_name
    except:
        name1 = input1
    
    try:
        user2 = await commands.MemberConverter().convert(interaction, input2)
        name2 = user2.display_name
    except:
        name2 = input2
    
    # Don't allow shipping identical inputs
    if name1.lower() == name2.lower():
        await interaction.response.send_message(
            "❌ You can't ship something with itself! That's just sad...",
            ephemeral=True
        )
        return
    
    # Create ship name
    ship_name = (name1[:3].lower() + name2[:3].lower()).capitalize()
    
    # Calculate compatibility
    random.seed(f"{name1}{name2}".lower())
    compatibility = random.randint(0, 100)
    
    # Generate message
    if compatibility < 20:
        message = "💔 Not a good match... At all."
    elif compatibility < 40:
        message = "❤️‍🩹 There might be some potential... Maybe?"
    elif compatibility < 60:
        message = "💖 A decent match! Could work out!"
    elif compatibility < 80:
        message = "💘 Great chemistry! Go for it!"
    else:
        message = "💞 SOULMATES! Perfect match!!!"
    
    # Create embed
    embed = discord.Embed(
        title=f"💖 {name1} + {name2} = {ship_name}",
        description=f"**Compatibility:** {compatibility}%\n{message}",
        color=discord.Color.pink()
    )
    embed.set_thumbnail(url="https://i.imgur.com/rVaN5PZ.png")
    
    await interaction.response.send_message(embed=embed)
    log_command(interaction, "ship", success=True)

@bot.command(name="say")
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message: str):
    try:
        await ctx.message.delete()
        await ctx.send(message)
        log_command(ctx, "say", success=True)
    except discord.Forbidden:
        await ctx.send("❌ I need permissions to delete messages!", delete_after=5)
        log_command(ctx, "say", success=False, error_msg="Missing delete permissions")

@bot.tree.command(name="say", description="Make the bot say something")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(message="The message to send")
async def slash_say(interaction: discord.Interaction, message: str):
    try:
        await interaction.response.send_message(message)
        try:
            await interaction.delete_original_response()
        except discord.Forbidden:
            pass
        log_command(interaction, "say", success=True)
    except Exception as e:
        log_command(interaction, "say", success=False, error_msg=str(e))
        await interaction.response.send_message("❌ Failed to send message!", ephemeral=True)


    # Add all other fun commands here following the same pattern...
    # (flip, roll, choose, 8ball, ship, freethrow, pitch, golfswing, tennisserve, volleyball)

async def setup(bot):
    await bot.add_cog(Fun(bot))
