import discord
import requests
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.presences = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Variable to store the API key and simulate refresh
api_key = '7c429ccc-8863-4366-9456-6b8fcfc76475'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    track_price.start()
    activity = discord.Activity(type=discord.ActivityType.watching, name="Solana Price ")
    await bot.change_presence(activity=activity)


@tasks.loop(minutes=10)  # Set the interval for checking the price
async def track_price():
    sol_price = get_sol_price()
    if sol_price is not None:
        new_bot_name = f'SOL-${sol_price:.2f}'
        await bot.user.edit(username=new_bot_name)
        print(f"name changed to :{new_bot_name}")

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
            headers['X-CMC_PRO_API_KEY'] = api_key  # Update the header with the new token
        else:
            print(f'HTTP error: {e}')
        return None
    except Exception as e:
        print(f'Error fetching SOL price: {e}')
        return None


if __name__ == "__main__":
    bot.run('MTE1NTk1Mzg1ODEwMzc0NjYzMg.GU-2L5.qi77ivcxMSeTNJZjMLR43tW_wr7YCZ6k3iys_Q')  
