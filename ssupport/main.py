import discord
from discord.ext import commands
import logging
import traceback
from utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=Config.get_prefix,
            intents=intents,
            help_command=None,
            activity=discord.Game(name=f"{Config.DEFAULT_PREFIX}help or /help")
        )
        
    async def setup_hook(self):
        """Initialize the bot and load extensions"""
        await self.load_extensions()
        await self.tree.sync()
        
    async def load_extensions(self):
        """Load all bot extensions"""
        initial_extensions = [
            'cogs.fun',
            'cogs.moderation',
            'cogs.economy',
            'cogs.tickets',
            'cogs.events'
        ]
        
        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
                logger.info(f'Successfully loaded extension: {extension}')
            except Exception as e:
                logger.error(f'Failed to load extension {extension}: {e}')
                traceback.print_exc()

bot = MyBot()

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} guilds')
    logger.info('------')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    else:
        logger.error(f'Error in command {ctx.command}: {error}')
        traceback.print_exc()

async def main():
    """Main entry point"""
    async with bot:
        try:
            await bot.start(Config.BOT_TOKEN)
        except KeyboardInterrupt:
            logger.info("Bot shutting down due to keyboard interrupt...")
        except Exception as e:
            logger.critical(f"Bot crashed: {e}")
            traceback.print_exc()
        finally:
            logger.info("Bot has shut down")

if __name__ == '__main__':
    asyncio.run(main())
