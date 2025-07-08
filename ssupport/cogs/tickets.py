import json
import os
import discord
from discord import ui
from discord.ext import commands
from utils.helpers import log_command
from utils.config import Config

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="Create Ticket", style=discord.ButtonStyle.green, custom_id="persistent_ticket:create")
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        try:
            tickets = self.load_tickets()
            ticket_num = len([k for k in tickets.keys() if str(interaction.guild.id) in k]) + 1
            ticket_name = f"ticket-{interaction.guild.id}-{ticket_num}"
            
            category = discord.utils.get(interaction.guild.categories, name="TICKETS")
            if not category:
                category = await interaction.guild.create_category("TICKETS")
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            
            channel = await category.create_text_channel(
                name=ticket_name,
                overwrites=overwrites
            )
            
            tickets[ticket_name] = {
                "user": interaction.user.id,
                "channel": channel.id,
                "open": True
            }
            self.save_tickets(tickets)
            
            embed = discord.Embed(
                title=f"Ticket #{ticket_num}",
                description=f"Hello {interaction.user.mention}! Support will be with you shortly.\n\nUse `/close` to close this ticket.",
                color=discord.Color.green()
            )
            await channel.send(embed=embed, view=CloseView())
            await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)
            log_command(interaction, "create_ticket", success=True)
        except Exception as e:
            print(f"Error creating ticket: {e}")
            await interaction.response.send_message("❌ Failed to create ticket. Please try again.", ephemeral=True)
            log_command(interaction, "create_ticket", success=False, error_msg=str(e))

class CloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="persistent_ticket:close")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        try:
            tickets = self.load_tickets()
            ticket_name = interaction.channel.name
            
            if ticket_name not in tickets:
                return await interaction.response.send_message("This is not a valid ticket channel.", ephemeral=True)
            
            if tickets[ticket_name]["user"] != interaction.user.id and not interaction.user.guild_permissions.administrator:
                return await interaction.response.send_message("You don't have permission to close this ticket.", ephemeral=True)
            
            await interaction.channel.edit(name=f"closed-{ticket_name}")
            
            tickets[ticket_name]["open"] = False
            self.save_tickets(tickets)
            
            embed = discord.Embed(
                title="Ticket Closed",
                description=f"This ticket has been closed by {interaction.user.mention}.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            await asyncio.sleep(10)
            await interaction.channel.delete()
            log_command(interaction, "close_ticket", success=True)
        except Exception as e:
            print(f"Error closing ticket: {e}")
            await interaction.response.send_message("❌ Failed to close ticket. Please try again.", ephemeral=True)
            log_command(interaction, "close_ticket", success=False, error_msg=str(e))

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def load_tickets(self):
        try:
            if os.path.exists(Config.TICKET_DB):
                with open(Config.TICKET_DB, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading tickets: {e}")
            return {}

    def save_tickets(self, data):
        try:
            os.makedirs(os.path.dirname(Config.TICKET_DB), exist_ok=True)
            with open(Config.TICKET_DB, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving tickets: {e}")

    @commands.command(name="createpanel")
    @commands.has_permissions(administrator=True)
    async def create_panel(self, ctx):
        embed = discord.Embed(
            title="Support Tickets",
            description="Click the button below to create a support ticket!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=TicketView())
        log_command(ctx, "createpanel", success=True)
    # Close Ticket Command
@bot.command(name="close")
async def close_ticket(ctx):
    try:
        tickets = load_tickets()
        ticket_name = ctx.channel.name
        
        if ticket_name not in tickets:
            return await ctx.send("This is not a valid ticket channel.")
        
        if tickets[ticket_name]["user"] != ctx.author.id and not ctx.author.guild_permissions.administrator:
            return await ctx.send("You don't have permission to close this ticket.")
        
        # Archive channel
        await ctx.channel.edit(name=f"closed-{ticket_name}")
        
        # Update DB
        tickets[ticket_name]["open"] = False
        save_tickets(tickets)
        
        # Send confirmation
        embed = discord.Embed(
            title="Ticket Closed",
            description=f"This ticket has been closed by {ctx.author.mention}.",
            color=discord.Color.red()
        )
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await ctx.channel.delete()
        log_command(ctx, "close", success=True)
    except Exception as e:
        print(f"Error closing ticket (prefix): {e}")
        await ctx.send("❌ Failed to close ticket. Please try again.")
        log_command(ctx, "close", success=False, error_msg=str(e))

# Add User to Ticket
@bot.command(name="add")
@commands.has_permissions(manage_channels=True)
async def add_user(ctx, member: discord.Member):
    tickets = load_tickets()
    ticket_name = ctx.channel.name
    
    if ticket_name not in tickets:
        return await ctx.send("This is not a valid ticket channel.")
    
    await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
    await ctx.send(f"{member.mention} has been added to the ticket!")
    log_command(ctx, "add", success=True)

# Remove User from Ticket
@bot.command(name="remove")
@commands.has_permissions(manage_channels=True)
async def remove_user(ctx, member: discord.Member):
    tickets = load_tickets()
    ticket_name = ctx.channel.name
    
    if ticket_name not in tickets:
        return await ctx.send("This is not a valid ticket channel.")
    
    await ctx.channel.set_permissions(member, read_messages=False, send_messages=False)
    await ctx.send(f"{member.mention} has been removed from the ticket!")
    log_command(ctx, "remove", success=True)

# TICKET COMMANDS (SLASH VERSION)

# Slash Command: Create Panel
@bot.tree.command(name="createpanel", description="Create a ticket creation panel (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def slash_create_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Support Tickets",
        description="Click the button below to create a support ticket!",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=TicketView())
    log_command(interaction, "createpanel", success=True)

# Slash Command: Close Ticket
@bot.tree.command(name="close", description="Close the current ticket")
async def slash_close_ticket(interaction: discord.Interaction):
    try:
        tickets = load_tickets()
        ticket_name = interaction.channel.name
        
        if ticket_name not in tickets:
            return await interaction.response.send_message("This is not a valid ticket channel.", ephemeral=True)
        
        if tickets[ticket_name]["user"] != interaction.user.id and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You don't have permission to close this ticket.", ephemeral=True)
        
        # Update DB first
        tickets[ticket_name]["open"] = False
        save_tickets(tickets)
        
        # Send confirmation
        embed = discord.Embed(
            title="Ticket Closed",
            description=f"This ticket has been closed by {interaction.user.mention}.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        
        # Archive and delete after delay
        await interaction.channel.edit(name=f"closed-{ticket_name}")
        await asyncio.sleep(10)
        await interaction.channel.delete()
    except Exception as e:
        print(f"Error closing ticket: {e}")
        await interaction.response.send_message("❌ Failed to close ticket. Please try again.", ephemeral=True)

# Slash Command: Add User
@bot.tree.command(name="add", description="Add a user to the ticket (Staff only)")
@app_commands.describe(user="The user to add to the ticket")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_add_user(interaction: discord.Interaction, user: discord.Member):
    tickets = load_tickets()
    ticket_name = interaction.channel.name
    
    if ticket_name not in tickets:
        return await interaction.response.send_message("This is not a valid ticket channel.", ephemeral=True)
    
    await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
    await interaction.response.send_message(f"{user.mention} has been added to the ticket!")
    log_command(interaction, "add", success=True)

# Slash Command: Remove User
@bot.tree.command(name="remove", description="Remove a user from the ticket (Staff only)")
@app_commands.describe(user="The user to remove from the ticket")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_remove_user(interaction: discord.Interaction, user: discord.Member):
    tickets = load_tickets()
    ticket_name = interaction.channel.name
    
    if ticket_name not in tickets:
        return await interaction.response.send_message("This is not a valid ticket channel.", ephemeral=True)
    
    await interaction.channel.set_permissions(user, read_messages=False, send_messages=False)
    await interaction.response.send_message(f"{user.mention} has been removed from the ticket!")
    log_command(interaction, "remove", success=True)

    

async def setup(bot):
    await bot.add_cog(Tickets(bot))
