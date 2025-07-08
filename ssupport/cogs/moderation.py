import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import log_command, has_permission
from utils.config import Config

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.check(has_permission)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"✅ Banned {member.mention} for: {reason or 'No reason provided'}")
            log_command(ctx, "ban", success=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban members.")
            log_command(ctx, "ban", success=False, error_msg="Missing permissions")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            log_command(ctx, "ban", success=False, error_msg=str(e))

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="The member to ban", reason="Reason for the ban")
    async def slash_ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if not await has_permission(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"✅ Banned {member.mention} for: {reason or 'No reason provided'}")
            log_command(interaction, "ban", success=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to ban members.", ephemeral=True)
            log_command(interaction, "ban", success=False, error_msg="Missing permissions")
        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
            log_command(interaction, "ban", success=False, error_msg=str(e))

    @bot.command()
@commands.check(has_permission)
@commands.guild_only()
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ Kicked {member.mention} for: {reason or 'No reason provided'}")
        log_command(ctx, "kick", success=True)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to kick members.")
        log_command(ctx, "kick", success=False, error_msg="Missing permissions")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "kick", success=False, error_msg=str(e))

@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="The member to kick", reason="Reason for the kick")
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not await has_permission(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ Kicked {member.mention} for: {reason or 'No reason provided'}")
        log_command(interaction, "kick", success=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to kick members.", ephemeral=True)
        log_command(interaction, "kick", success=False, error_msg="Missing permissions")
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
        log_command(interaction, "kick", success=False, error_msg=str(e))

@bot.command()
@commands.check(has_permission)
@commands.guild_only()
async def timeout(ctx, member: discord.Member, duration: str, *, reason=None):
    try:
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unit = duration[-1].lower()
        if unit not in time_units:
            raise ValueError("Invalid time unit")
        amount = int(duration[:-1])
        seconds = amount * time_units[unit]

        until = discord.utils.utcnow() + timedelta(seconds=seconds)
        await member.timeout(until, reason=reason)
        await ctx.send(f"✅ Timed out {member.mention} for {duration} for: {reason or 'No reason provided'}")
        log_command(ctx, "timeout", success=True)
    except ValueError:
        await ctx.send("❌ Invalid duration format. Example: 1h, 30m, 1d")
        log_command(ctx, "timeout", success=False, error_msg="Invalid duration")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to timeout members.")
        log_command(ctx, "timeout", success=False, error_msg="Missing permissions")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "timeout", success=False, error_msg=str(e))

@bot.tree.command(name="timeout", description="Timeout a member")
@app_commands.describe(
    member="The member to timeout",
    duration="Duration (e.g., 1h, 30m, 1d)",
    reason="Reason for the timeout"
)
async def slash_timeout(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = None):
    if not await has_permission(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    try:
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unit = duration[-1].lower()
        if unit not in time_units:
            raise ValueError("Invalid time unit")
        amount = int(duration[:-1])
        seconds = amount * time_units[unit]

        until = discord.utils.utcnow() + timedelta(seconds=seconds)
        await member.timeout(until, reason=reason)
        await interaction.response.send_message(
            f"✅ Timed out {member.mention} for {duration} for: {reason or 'No reason provided'}"
        )
        log_command(interaction, "timeout", success=True)
    except ValueError:
        await interaction.response.send_message(
            "❌ Invalid duration format. Example: 1h, 30m, 1d",
            ephemeral=True
        )
        log_command(interaction, "timeout", success=False, error_msg="Invalid duration")
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I don't have permission to timeout members.",
            ephemeral=True
        )
        log_command(interaction, "timeout", success=False, error_msg="Missing permissions")
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}",
            ephemeral=True
        )
        log_command(interaction, "timeout", success=False, error_msg=str(e))

@bot.command()
@commands.check(has_permission)
@commands.guild_only()
async def roles(ctx, member: discord.Member, action: str, *, role: discord.Role):
    """Manage user roles (prefix version)"""
    try:
        action = action.lower()
        if action == "add":
            await member.add_roles(role)
            await ctx.send(f"✅ Added {role.name} to {member.mention}")
            log_command(ctx, "roles_add", success=True)
        elif action == "remove":
            await member.remove_roles(role)
            await ctx.send(f"✅ Removed {role.name} from {member.mention}")
            log_command(ctx, "roles_remove", success=True)
        else:
            await ctx.send("❌ Invalid action. Use 'add' or 'remove'")
            log_command(ctx, "roles", success=False, error_msg="Invalid action")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to manage roles.")
        log_command(ctx, "roles", success=False, error_msg="Missing permissions")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "roles", success=False, error_msg=str(e))

@bot.tree.command(name="roles", description="Manage user roles")
@app_commands.describe(
    member="The member to modify",
    action="add or remove",
    role="The role to add/remove"
)
async def slash_roles(interaction: discord.Interaction, member: discord.Member, action: str, role: discord.Role):
    """Manage user roles (slash version)"""
    if not await has_permission(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    try:
        action = action.lower()
        if action == "add":
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Added {role.name} to {member.mention}")
            log_command(interaction, "roles_add", success=True)
        elif action == "remove":
            await member.remove_roles(role)
            await interaction.response.send_message(f"✅ Removed {role.name} from {member.mention}")
            log_command(interaction, "roles_remove", success=True)
        else:
            await interaction.response.send_message("❌ Invalid action. Use 'add' or 'remove'", ephemeral=True)
            log_command(interaction, "roles", success=False, error_msg="Invalid action")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to manage roles.", ephemeral=True)
        log_command(interaction, "roles", success=False, error_msg="Missing permissions")
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
        log_command(interaction, "roles", success=False, error_msg=str(e))

@bot.command()
@commands.check(has_permission)
@commands.guild_only()
async def deletechannel(ctx, channel: discord.TextChannel):
    """Delete a channel (prefix version)"""
    try:
        channel_name = channel.name
        await channel.delete()
        await ctx.send(f"✅ Deleted channel #{channel_name}")
        log_command(ctx, "deletechannel", success=True)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to delete channels.")
        log_command(ctx, "deletechannel", success=False, error_msg="Missing permissions")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "deletechannel", success=False, error_msg=str(e))

@bot.tree.command(name="deletechannel", description="Delete a text channel")
@app_commands.describe(channel="The channel to delete")
async def slash_deletechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Delete a channel (slash version)"""
    if not await has_permission(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    try:
        channel_name = channel.name
        await channel.delete()
        await interaction.response.send_message(f"✅ Deleted channel #{channel_name}")
        log_command(interaction, "deletechannel", success=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to delete channels.", ephemeral=True)
        log_command(interaction, "deletechannel", success=False, error_msg="Missing permissions")
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
        log_command(interaction, "deletechannel", success=False, error_msg=str(e))

@bot.command()
@commands.check(has_permission)
@commands.guild_only()
async def renamechannel(ctx, channel: discord.TextChannel, *, new_name: str):
    """Rename a channel (prefix version)"""
    try:
        old_name = channel.name
        await channel.edit(name=new_name)
        await ctx.send(f"✅ Renamed channel from #{old_name} to #{new_name}")
        log_command(ctx, "renamechannel", success=True)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to rename channels.")
        log_command(ctx, "renamechannel", success=False, error_msg="Missing permissions")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "renamechannel", success=False, error_msg=str(e))

@bot.tree.command(name="renamechannel", description="Rename a text channel")
@app_commands.describe(
    channel="The channel to rename",
    new_name="The new channel name"
)
async def slash_renamechannel(interaction: discord.Interaction, channel: discord.TextChannel, new_name: str):
    """Rename a channel (slash version)"""
    if not await has_permission(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    try:
        old_name = channel.name
        await channel.edit(name=new_name)
        await interaction.response.send_message(f"✅ Renamed channel from #{old_name} to #{new_name}")
        log_command(interaction, "renamechannel", success=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to rename channels.", ephemeral=True)
        log_command(interaction, "renamechannel", success=False, error_msg="Missing permissions")
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
        log_command(interaction, "renamechannel", success=False, error_msg=str(e))

@bot.command()
@commands.check(has_permission)
@commands.guild_only()
async def purge(ctx, amount: int):
    """Delete multiple messages (prefix version)"""
    try:
        if amount < 1 or amount > 100:
            await ctx.send("❌ Please provide a number between 1 and 100")
            return
            
        await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
        msg = await ctx.send(f"✅ Deleted {amount} messages")
        await asyncio.sleep(3)
        await msg.delete()
        log_command(ctx, "purge", success=True)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to delete messages.")
        log_command(ctx, "purge", success=False, error_msg="Missing permissions")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "purge", success=False, error_msg=str(e))

@bot.tree.command(name="purge", description="Delete multiple messages")
@app_commands.describe(amount="Number of messages to delete (1-100)")
async def slash_purge(interaction: discord.Interaction, amount: int):
    """Delete multiple messages (slash version)"""
    if not await has_permission(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    try:
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Please provide a number between 1 and 100", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.purge(limit=amount + 1)
        await interaction.followup.send(f"✅ Deleted {amount} messages", ephemeral=True)
        log_command(interaction, "purge", success=True)
    except discord.Forbidden:
        await interaction.followup.send("❌ I don't have permission to delete messages.", ephemeral=True)
        log_command(interaction, "purge", success=False, error_msg="Missing permissions")
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
        log_command(interaction, "purge", success=False, error_msg=str(e))

@bot.command()
@commands.check(has_permission)
@commands.guild_only()
async def banall(ctx):
    """Mass ban all non-admin members (prefix version)"""
    if ctx.author.id not in [YOUR_USER_ID] + WHITELISTED_USER_IDS:
        await ctx.send("❌ This command is restricted to bot owner and whitelisted users only.")
        return
    
    try:
        count = 0
        failed = 0
        async for member in ctx.guild.fetch_members():
            if not member.guild_permissions.administrator and member != ctx.guild.owner:
                try:
                    await member.ban(reason="Mass ban")
                    count += 1
                    await asyncio.sleep(1)  # Rate limit protection
                except:
                    failed += 1
                    continue
        
        await ctx.send(f"✅ Banned {count} members. Failed to ban {failed} members.")
        log_command(ctx, "banall", success=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "banall", success=False, error_msg=str(e))

@bot.tree.command(name="banall", description="Mass ban all non-admin members (Owner/Whitelist only)")
async def slash_banall(interaction: discord.Interaction):
    """Mass ban all non-admin members (slash version)"""
    if interaction.user.id not in [YOUR_USER_ID] + WHITELISTED_USER_IDS:
        await interaction.response.send_message("❌ This command is restricted to bot owner and whitelisted users only.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer()
        count = 0
        failed = 0
        async for member in interaction.guild.fetch_members():
            if not member.guild_permissions.administrator and member != interaction.guild.owner:
                try:
                    await member.ban(reason="Mass ban")
                    count += 1
                    await asyncio.sleep(1)  # Rate limit protection
                except:
                    failed += 1
                    continue
        
        await interaction.followup.send(f"✅ Banned {count} members. Failed to ban {failed} members.")
        log_command(interaction, "banall", success=True)
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {str(e)}")
        log_command(interaction, "banall", success=False, error_msg=str(e))

@bot.command()
@commands.check(has_permission)
@commands.guild_only()
async def unbanall(ctx):
    """Mass unban all members (prefix version)"""
    if ctx.author.id not in [YOUR_USER_ID] + WHITELISTED_USER_IDS:
        await ctx.send("❌ This command is restricted to bot owner and whitelisted users only.")
        return
    
    try:
        count = 0
        failed = 0
        bans = [ban_entry async for ban_entry in ctx.guild.bans()]
        for ban_entry in bans:
            try:
                await ctx.guild.unban(ban_entry.user)
                count += 1
                await asyncio.sleep(1)  # Rate limit protection
            except:
                failed += 1
                continue
        
        await ctx.send(f"✅ Unbanned {count} members. Failed to unban {failed} members.")
        log_command(ctx, "unbanall", success=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "unbanall", success=False, error_msg=str(e))

@bot.tree.command(name="unbanall", description="Mass unban all members (Owner/Whitelist only)")
async def slash_unbanall(interaction: discord.Interaction):
    """Mass unban all members (slash version)"""
    if interaction.user.id not in [YOUR_USER_ID] + WHITELISTED_USER_IDS:
        await interaction.response.send_message("❌ This command is restricted to bot owner and whitelisted users only.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer()
        count = 0
        failed = 0
        bans = [ban_entry async for ban_entry in interaction.guild.bans()]
        for ban_entry in bans:
            try:
                await interaction.guild.unban(ban_entry.user)
                count += 1
                await asyncio.sleep(1)  # Rate limit protection
            except:
                failed += 1
                continue
        
        await interaction.followup.send(f"✅ Unbanned {count} members. Failed to unban {failed} members.")
        log_command(interaction, "unbanall", success=True)
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {str(e)}")
        log_command(interaction, "unbanall", success=False, error_msg=str(e))

@bot.command()
@commands.check(has_permission)
@commands.guild_only()
async def spam(ctx, amount: int, *, message: str):
    """Spam messages (prefix version)"""
    if amount > MAX_SPAM_LIMIT:
        await ctx.send(f"❌ Maximum spam limit is {MAX_SPAM_LIMIT} messages")
        return
    if amount < 1:
        await ctx.send("❌ Please provide a positive number")
        return
    
    try:
        for _ in range(amount):
            await ctx.send(message)
            await asyncio.sleep(0.5)  # Prevent rate limiting
        log_command(ctx, "spam", success=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "spam", success=False, error_msg=str(e))

@bot.tree.command(name="spam", description="Spam messages")
@app_commands.describe(
    amount="Number of messages to send",
    message="The message to spam"
)
async def slash_spam(interaction: discord.Interaction, amount: int, message: str):
    """Spam messages (slash version)"""
    if not await has_permission(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    if amount > MAX_SPAM_LIMIT:
        await interaction.response.send_message(f"❌ Maximum spam limit is {MAX_SPAM_LIMIT} messages", ephemeral=True)
        return
    if amount < 1:
        await interaction.response.send_message("❌ Please provide a positive number", ephemeral=True)
        return
    
    try:
        await interaction.response.defer()
        for _ in range(amount):
            await interaction.channel.send(message)
            await asyncio.sleep(0.5)
        await interaction.followup.send(f"✅ Sent {amount} messages", ephemeral=True)
        log_command(interaction, "spam", success=True)
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
        log_command(interaction, "spam", success=False, error_msg=str(e))

@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock_channel(ctx, channel: discord.TextChannel = None):
    """Lock a channel (prefix version)"""
    channel = channel or ctx.channel
    
    try:
        # Set permissions for @everyone to not send messages
        await channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False,
            reason=f"Channel locked by {ctx.author}"
        )
        
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"{channel.mention} has been locked by {ctx.author.mention}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        log_command(ctx, "lock", success=True)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to lock this channel!")
        log_command(ctx, "lock", success=False, error_msg="Missing permissions")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "lock", success=False, error_msg=str(e))

@bot.tree.command(name="lock", description="Lock a text channel")
@app_commands.describe(channel="The channel to lock (defaults to current)")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_lock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """Lock a channel (slash version)"""
    channel = channel or interaction.channel
    
    try:
        await channel.set_permissions(
            interaction.guild.default_role,
            send_messages=False,
            reason=f"Channel locked by {interaction.user}"
        )
        
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"{channel.mention} has been locked by {interaction.user.mention}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        log_command(interaction, "lock", success=True)
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I don't have permission to lock this channel!",
            ephemeral=True
        )
        log_command(interaction, "lock", success=False, error_msg="Missing permissions")
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}",
            ephemeral=True
        )
        log_command(interaction, "lock", success=False, error_msg=str(e))

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx, channel: discord.TextChannel = None):
    """Unlock a channel (prefix version)"""
    channel = channel or ctx.channel
    
    try:
        # Reset permissions for @everyone to default
        await channel.set_permissions(
            ctx.guild.default_role,
            send_messages=None,
            reason=f"Channel unlocked by {ctx.author}"
        )
        
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"{channel.mention} has been unlocked by {ctx.author.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        log_command(ctx, "unlock", success=True)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unlock this channel!")
        log_command(ctx, "unlock", success=False, error_msg="Missing permissions")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        log_command(ctx, "unlock", success=False, error_msg=str(e))

@bot.tree.command(name="unlock", description="Unlock a text channel")
@app_commands.describe(channel="The channel to unlock (defaults to current)")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_unlock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """Unlock a channel (slash version)"""
    channel = channel or interaction.channel
    
    try:
        await channel.set_permissions(
            interaction.guild.default_role,
            send_messages=None,
            reason=f"Channel unlocked by {interaction.user}"
        )
        
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"{channel.mention} has been unlocked by {interaction.user.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        log_command(interaction, "unlock", success=True)
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I don't have permission to unlock this channel!",
            ephemeral=True
        )
        log_command(interaction, "unlock", success=False, error_msg="Missing permissions")
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}",
            ephemeral=True
        )
        log_command(interaction, "unlock", success=False, error_msg=str(e))
@bot.command(name="setjoinrole")
@commands.has_permissions(manage_roles=True)
async def set_join_role_cmd(ctx, role: discord.Role):
    """Set the role to assign when a member joins (prefix version)"""
    join_roles[str(ctx.guild.id)] = role.id
    save_join_roles(join_roles)
    await ctx.send(f"✅ New members will now receive the {role.mention} role when they join.")

@bot.command(name="removejoinrole")
@commands.has_permissions(manage_roles=True)
async def remove_join_role_cmd(ctx):
    """Remove the auto-assign join role (prefix version)"""
    if str(ctx.guild.id) in join_roles:
        del join_roles[str(ctx.guild.id)]
        save_join_roles(join_roles)
        await ctx.send("✅ Removed the auto-assign join role.")
    else:
        await ctx.send("❌ No join role was set for this server.")

@bot.tree.command(name="joinrole", description="Set the role to assign when a member joins")
@app_commands.describe(role="The role to assign to new members")
@app_commands.checks.has_permissions(manage_roles=True)
async def set_join_role(interaction: discord.Interaction, role: discord.Role):
    """Set the join role (slash version)"""
    join_roles[str(interaction.guild_id)] = role.id
    save_join_roles(join_roles)
    await interaction.response.send_message(
        f"✅ New members will now receive the {role.mention} role when they join.",
        ephemeral=True
    )

@bot.tree.command(name="removejoinrole", description="Remove the auto-assign join role")
@app_commands.checks.has_permissions(manage_roles=True)
async def remove_join_role(interaction: discord.Interaction):
    """Remove the join role (slash version)"""
    if str(interaction.guild_id) in join_roles:
        del join_roles[str(interaction.guild_id)]
        save_join_roles(join_roles)
        await interaction.response.send_message(
            "✅ Removed the auto-assign join role.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ No join role was set for this server.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Moderation(bot))
