import discord
from discord.ext import commands
from utils.config import Config

HELP_CATEGORIES = [
    {
        "name": "🛡️ Moderation",
        "commands": [
            "/ban @user [reason] - Ban a user",
            "/kick @user [reason] - Kick a user",
            "/timeout @user [duration] [reason] - Timeout user",
            "/roles @user [add/remove] [role] - Manage roles",
            "/deletechannel [channel] - Delete channel",
            "/renamechannel [channel] [new_name] - Rename channel",
            "/purge [amount] - Bulk delete messages"
        ]
    },
    {
        "name": "💰 Economy",
        "commands": [
            "/balance - Check balance",
            "/daily - Claim daily reward",
            "/work - Earn money hourly",
            "/gamble [amount] - Gamble money",
            "/rob @user - Attempt robbery",
            "/shop - View shop items",
            "/buy [item] - Purchase items",
            "/inventory - View inventory",
            "/pay @user - Send money",
            "/leaderboard - Richest players",
            "/beg - Beg for money",
            "/attack @user - Attack user"
        ]
    },
    {
        "name": "🎮 Fun Games",
        "commands": [
            "/flip - Flip a coin",
            "/roll [sides] - Roll dice",
            "/8ball [question] - Magic 8-ball",
            "/choose [options] - Choose between options",
            "/ship [user1] [user2] - Love compatibility",
            "/penalty - Soccer penalty kick",
            "/freethrow - Basketball shot",
            "/golfswing - Golf swing",
            "/tennisserve - Tennis serve",
            "/pitch - Baseball pitch",
            "/volleyball - Volleyball play"
        ]
    },
    {
        "name": "🔧 Utility",
        "commands": [
            "/help - Show this help",
            "/say [message] - Make bot say something",
            "/prefix [new_prefix] - Set new prefix",
            "/tickethelp - Ticket system commands",
            "/joinrole [role] - Set auto-role",
            "/removejoinrole - Remove auto-role",
            "/spam [amount] [message]"
        ]
    },
    {
        "name": "💬 Tickets",
        "commands": [
            "/createpanel - Create ticket panel in current channel.",
            "/close - Closes current ticket",
            "/add @user - Adds user to current ticket",
            "/remove @user - Removes user from current ticket"
        ]
    }
]

class HelpView(discord.ui.View):
    def __init__(self, prefix: str, is_slash: bool = False):
        super().__init__(timeout=60)
        self.prefix = prefix
        self.is_slash = is_slash
        self.add_item(HelpSelect(prefix, is_slash))

class HelpSelect(discord.ui.Select):
    def __init__(self, prefix: str, is_slash: bool):
        self.prefix = prefix
        self.is_slash = is_slash
        
        options = []
        for category in HELP_CATEGORIES:
            options.append(discord.SelectOption(
                label=category["name"][2:],
                value=category["name"],
                emoji=category["name"][0]
            ))
        
        super().__init__(
            placeholder="Select a category...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        category = next(c for c in HELP_CATEGORIES if c["name"] == selected)
        
        embed = discord.Embed(
            title=f"{category['name']} Commands",
            color=discord.Color.blue()
        )
        
        formatted_commands = []
        for cmd in category["commands"]:
            if self.is_slash:
                formatted_commands.append(f"`{cmd}`")
            else:
                prefix_cmd = cmd.replace("/", self.prefix)
                formatted_commands.append(f"`{prefix_cmd}`")
        
        embed.description = "\n".join(formatted_commands)
        
        await interaction.response.edit_message(embed=embed)
