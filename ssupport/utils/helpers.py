import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Union
import discord
from discord.ext import commands
from utils.config import Config

def log_command(ctx_or_interaction: Union[commands.Context, discord.Interaction], command_name: str, 
                success: bool = True, error_msg: str = None):
    """Log command usage"""
    user = ctx_or_interaction.user if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = f"{user.name}#{user.discriminator} (ID: {user.id})"
    
    if hasattr(ctx_or_interaction, 'guild') and ctx_or_interaction.guild:
        server = f"{ctx_or_interaction.guild.name} (ID: {ctx_or_interaction.guild.id})"
    else:
        server = "DM"
    
    status = "SUCCESS" if success else f"FAILED: {error_msg}"
    log_msg = f"[{timestamp}] [COMMAND] {command_name.upper()} - User: {user_info} - Server: {server} - Status: {status}"
    print(log_msg)
    
    os.makedirs("logs", exist_ok=True)
    with open("logs/bot_commands.log", "a", encoding='utf-8') as f:
        f.write(log_msg + "\n")

async def has_permission(ctx_or_interaction: Union[commands.Context, discord.Interaction]) -> bool:
    """Check if user has permission to use admin commands"""
    user = ctx_or_interaction.user if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author
    
    if user.id in Config.BLACKLISTED_USER_IDS:
        return False
    
    if not hasattr(ctx_or_interaction, 'guild') or not ctx_or_interaction.guild:
        return user.id == Config.YOUR_USER_ID or user.id in Config.WHITELISTED_USER_IDS
    
    return (user.id == Config.YOUR_USER_ID or
            user.id in Config.WHITELISTED_USER_IDS or
            user.guild_permissions.administrator or
            user == ctx_or_interaction.guild.owner)

# Spam detection
user_message_counts = defaultdict(list)

async def check_and_handle_spam(message: discord.Message):
    """Check for spam and handle it"""
    if message.author.bot:
        return

    now = datetime.now()
    user_id = message.author.id
    user_message_counts[user_id].append(now)

    # Remove old timestamps
    user_message_counts[user_id] = [
        ts for ts in user_message_counts[user_id]
        if now - ts < timedelta(seconds=Config.SPAM_TIME_WINDOW)
    ]

    if len(user_message_counts[user_id]) > Config.SPAM_THRESHOLD:
        print(f"Detected spam from {message.author.name}#{message.author.discriminator} (ID: {user_id})")
        messages_to_delete = []
        
        for msg_time in user_message_counts[user_id]:
            async for past_msg in message.channel.history(limit=None, after=msg_time - timedelta(seconds=1), before=msg_time + timedelta(seconds=1)):
                if past_msg.author.id == user_id:
                    messages_to_delete.append(past_msg)

        if messages_to_delete:
            deleted_count = len(set(messages_to_delete))
            for msg in set(messages_to_delete):
                try:
                    await msg.delete()
                except discord.NotFound:
                    pass
                except discord.Forbidden:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SPAM] Could not delete message from {message.author.id} due to permissions.")
                    break

            if deleted_count > 0:
                try:
                    await message.channel.send(f"⚠️ {message.author.mention}, please avoid spamming. {deleted_count} of your recent messages have been deleted.")
                except discord.Forbidden:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SPAM] Could not send spam warning in {message.channel.id} due to permissions.")

        user_message_counts[user_id].clear()
