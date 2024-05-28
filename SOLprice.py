import discord, aiohttp
import requests
from discord.ext import commands, tasks
from datetime import datetime, timezone
import asyncio, logging

intents = discord.Intents.all()
intents.presences = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN ="Bot_Token_here" # Your discord token here 
API_KEY = 'Coinmarketcap_api' # your coinmarketcap api key here  get one at its free : https://pro.coinmarketcap.com/

# Configure logging
logging.basicConfig(level=logging.INFO)


@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')
    activity = discord.Activity(type=discord.ActivityType.watching, name="Solana Price")
    await bot.change_presence(activity=activity)
    synced = await bot.tree.sync()
    logging.info(f"Synced {len(synced)} commands")
    change_bot_description.start()
    
@tasks.loop(minutes=10)
async def change_bot_description():
    try:
        sol_data = await get_sol_data()
        if sol_data is not None:
            sol_price = sol_data['price']
            new_nickname = f'SOL-${sol_price:.2f}'

            for guild in bot.guilds:
                member = guild.get_member(bot.user.id)
                if member:
                    await member.edit(nick=new_nickname)
            logging.info(f"Nickname changed to: {new_nickname}")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    await asyncio.sleep(600)

# Function to fetch data from api "you can edit this as you want it works also for other crypto coins"
async def get_sol_data():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {
        'symbol': 'SOL',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                sol_data = data['data']['SOL']['quote']['USD']

                return {
                    'price': sol_data.get('price', None),
                    'change_1h': sol_data.get('percent_change_1h', None),
                    'change_24h': sol_data.get('percent_change_24h', None),
                    'change_7d': sol_data.get('percent_change_7d', None),
                    'change_30d': sol_data.get('percent_change_30d', None),
                    'change_60d': sol_data.get('percent_change_60d', None),
                    'change_90d': sol_data.get('percent_change_90d', None),
                    'volume_24h': sol_data.get('volume_24h', None),
                    'market_cap': sol_data.get('market_cap', None),
                    'market_cap_dominance': sol_data.get('market_cap_dominance', None),
                    'fully_diluted_market_cap': sol_data.get('fully_diluted_market_cap', None),
                    'high_24h': sol_data.get('high_24h', None),
                    'low_24h': sol_data.get('low_24h', None),
                    'all_time_high': data['data']['SOL'].get('ath', None),
                    'all_time_high_date': data['data']['SOL'].get('ath_date', None)
                }
        except aiohttp.ClientResponseError as e:
            logging.error(f'HTTP error: {e}')
            return None
        except Exception as e:
            logging.error(f'Error fetching SOL data: {e}')
            return None

# Help command
@bot.tree.command(name="help", description="Get some help")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Help - Solana Bot",
        description="List of available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="`/solana`",
        value="Fetches and displays the current Solana market information.",
        inline=False
    )
    embed.add_field(
        name="`/help`",
        value="Displays this help message with a list of available commands.",
        inline=False
    )
    embed.set_footer(text="Use the commands '/' to interact with the bot.")

    await interaction.response.send_message(embed=embed)

# Command to send Solana info
@bot.tree.command(name="solana", description="Get Solana Market info")
async def set_embed_channel(interaction: discord.Interaction):
    sol_data = await get_sol_data()
    guild = interaction.guild
    guild_icon_url = guild.icon.url if guild.icon else None
    current_date_utc = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")

    if sol_data is None:
        await interaction.response.send_message("Failed to fetch SOL data.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"Solana (SOL) Price USD ${sol_data['price']:.2f}",
        description="Current Solana Price Information",
        color=discord.Color.dark_gold()
    )

    embed.add_field(name="Change 1h", value=f"{sol_data['change_1h']:+.2f}%" if sol_data['change_1h'] is not None else "N/A", inline=True)
    embed.add_field(name="Change 24h", value=f"{sol_data['change_24h']:+.2f}%" if sol_data['change_24h'] is not None else "N/A", inline=True)
    embed.add_field(name="Change 7d", value=f"{sol_data['change_7d']:+.2f}%" if sol_data['change_7d'] is not None else "N/A", inline=True)
    embed.add_field(name="Change 30d", value=f"{sol_data['change_30d']:+.2f}%" if sol_data['change_30d'] is not None else "N/A", inline=True)
    embed.add_field(name="24h High / Low", value=f"${sol_data['high_24h']:.2f} / ${sol_data['low_24h']:.2f}" if sol_data['high_24h'] is not None and sol_data['low_24h'] is not None else "N/A", inline=False)
    embed.add_field(name="Volume 24h", value=f"{sol_data['volume_24h']:,}" if sol_data['volume_24h'] is not None else "N/A", inline=True)
    embed.add_field(name="Market Cap", value=f"${sol_data['market_cap']:,}" if sol_data['market_cap'] is not None else "N/A", inline=True)
    embed.add_field(name="Market Cap Dominance", value=f"{sol_data['market_cap_dominance']:.2f}%" if sol_data['market_cap_dominance'] is not None else "N/A", inline=True)
    embed.add_field(name="Fully Diluted Market Cap", value=f"${sol_data['fully_diluted_market_cap']:,}" if sol_data['fully_diluted_market_cap'] is not None else "N/A", inline=True)
    embed.add_field(name="All Time High", value=f"${sol_data['all_time_high']:.2f}" if sol_data['all_time_high'] is not None else "N/A", inline=True)
    embed.set_footer(text=f"{current_date_utc} ", icon_url=guild_icon_url)

    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)