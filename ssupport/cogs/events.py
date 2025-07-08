import discord
from discord.ext import commands
from utils.helpers import check_and_handle_spam
from utils.config import Config

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        await self.bot.process_commands(message)
        await check_and_handle_spam(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        join_roles = Config.load_join_roles()
        role_id = join_roles.get(str(member.guild.id))
        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Auto-assigned join role")
                    print(f"Assigned join role {role.name} to {member.display_name}")
                except discord.Forbidden:
                    print(f"⚠️ Missing permissions to assign role {role.name} in {member.guild.name}.")
                except Exception as e:
                    print(f"Error assigning join role: {e}")

async def setup(bot):
    await bot.add_cog(Events(bot))
