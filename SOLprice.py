import discord
import requests
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.presences = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
api_key = 'API Key ' # Remplace this with ur coinmarketcap api key 
TOKEN = "Your bot token here"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    track_price.start()

@tasks.loop(minutes=10)  # Set the interval for checking the price
async def track_price():
    sol_price = get_sol_price()
    if sol_price is not None:
        new_bot_name = f'SOL-${sol_price:.2f}'
        await bot.user.edit(username=new_bot_name)

def get_sol_price():
    global api_key
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {
        'symbol': 'SOL',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        sol_price = data['data']['SOL']['quote']['USD']['price']
        return sol_price
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:  # Unauthorized, possibly due to an expired token
            print("Token expired. Refreshing token...")
            api_key = simulate_refresh(api_key)  # Simulate token refresh
            headers['X-CMC_PRO_API_KEY'] = api_key  # Update the header with the new token
        else:
            print(f'HTTP error: {e}')
        return None
    except Exception as e:
        print(f'Error fetching SOL price: {e}')
        return None

def simulate_refresh(current_token):
    print("Simulating token refresh...")
    new_token = 'your_new_token_here'
    return new_token

if __name__ == "__main__":
    bot.run(TOKEN)  
