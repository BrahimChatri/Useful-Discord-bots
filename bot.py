"""
make sure to install libraries first by running :
pip install libraries discord
"""

import discord
from discord.ext import commands
from discord import Status 
import random
import asyncio
import re

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

TOKEN = 'Your_bot_token' # Remplace it with ur bot token 
VERIFIED_ROLE_NAME = 'Wolf'  # VERIFIED_ROLE_NAME to trak and give Wolf suppoeter role 
ADDITIONAL_ROLE_NAME = '🐺Wolf Supporter'
BOT_LOGS_CHANNEL_ID = 123456789000000000 # channel ID To send logs 

  

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync() # Sync commands 
        print(f"synced {len(synced)} commands")
        activity = discord.Activity(type=discord.ActivityType.watching, name="Messages and Command's")
        await bot.change_presence(activity=activity)

    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Define a regular expression for detecting links
    link_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    # Check if the message contains a link
    if link_pattern.search(message.content):
        moderator_role = discord.utils.get(message.guild.roles, name='Moderator')
        founder_role = discord.utils.get(message.guild.roles, name='Founder')

        # Check if the user has either the "Moderator" or "Founder" role
        if founder_role not in message.author.roles and moderator_role not in message.author.roles:
            await message.delete()
            await message.channel.send(f'{message.author.mention}, links are not allowed here! Please follow the rules. https://discord.com/channels/1190688700988936192/1190689150849011762')

    await bot.process_commands(message)


@bot.event
async def on_member_update(before, after):
    verified_role = discord.utils.get(after.roles, name=VERIFIED_ROLE_NAME)

    # Check if the "Verified Wolf" role was added during the update
    if verified_role is not None and verified_role not in before.roles and verified_role in after.roles:
        # Calculate online, offline, and non-offline member counts
        #online_members = sum(1 for m in after.guild.members if m.status == Status.online)
        offline_members = sum(1 for m in after.guild.members if m.status == Status.offline)
        non_offline_members = len(after.guild.members) - offline_members

        # Send a message to the bot logs channel
        bot_logs_channel = after.guild.get_channel(BOT_LOGS_CHANNEL_ID)
        if bot_logs_channel is not None:
            await bot_logs_channel.send(f'{after.mention} Has joined the server and verified!!. \n **Offline Members:** __{offline_members}__,\n **Online Members:** __{non_offline_members}__,\n **Total members:** __{len(after.guild.members)}__')

@bot.tree.command(name="help", description="Get some help!")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message("Try using `/guess` To play the guessing game or `/hangman` To play Hangman!, `/cardgame` To play Card Guessing Game, `/fact`To see cool fact, `/joke` To see a cool joke")

"Some cool games you can play with slash commands"

@bot.tree.command(name="guess", description="Play the Number Guessing Game")
async def play_guess(interaction: discord.Interaction):
    await interaction.response.send_message(f"Welcome to the Number Guessing Game, {interaction.user.mention}! Guess a number between 0 and 50.")

    secret_number = random.randint(0, 50)
    attempts = 0

    while attempts < 5:
        try:
            user_guess_payload = await bot.wait_for("message", check=lambda m: m.author == interaction.user, timeout=30.0)
            user_guess = int(user_guess_payload.content)

            attempts += 1

            if user_guess == secret_number:
                await interaction.followup.send(f"{interaction.user.mention} Congratulations! You guessed the correct number {secret_number} in {attempts} attempts.")
                return
            elif user_guess < secret_number:
                await interaction.followup.send("Too low! Try again.")
            else:
                await interaction.followup.send("Too high! Try again.")

        except ValueError:
            await interaction.followup.send("Invalid input. Please enter a valid number.")

    await interaction.followup.send(f"You reached the maximum number of attempts! The correct number was {secret_number}.")

@bot.tree.command(name="hangman", description="Play Hangman")
async def play_hangman(interaction: discord.Interaction):
    words = ["chaotic", "wolves", "Alpha", "collection", "nfts", "wolf","hunter","art","solana","Blockchain","Token","Digital"]
    chosen_word = random.choice(words).lower()
    guessed_word = ["_"] * len(chosen_word)
    incorrect_guesses = 0
    max_attempts = 6
    guessed_letters = set()

    def display_word():
        return " ".join(guessed_word)

    await interaction.response.send_message(f"Welcome to Hangman, {interaction.user.mention}! Try to guess the word enter letter by letter !!: `{display_word()}`")

    while incorrect_guesses < max_attempts and "_" in guessed_word:
        try:
            user_guess_payload = await bot.wait_for(
                "message",
                check=lambda m: m.author == interaction.user and m.content.isalpha() and len(m.content) == 1 and m.content.lower() not in guessed_letters,
                timeout=30.0
            )
            user_guess = user_guess_payload.content.lower()
            guessed_letters.add(user_guess)

            if user_guess in chosen_word:
                for i, letter in enumerate(chosen_word):
                    if letter == user_guess:
                        guessed_word[i] = user_guess
                await interaction.followup.send(f"Good guess! `{display_word()}`")
            else:
                incorrect_guesses += 1
                await interaction.followup.send(f"Wrong guess! Attempts left: {max_attempts - incorrect_guesses}. `{display_word()}`")

        except asyncio.TimeoutError:
            await interaction.followup.send("Time's up! The game has ended.")
            return

    if "_" not in guessed_word:
        await interaction.followup.send(f"{interaction.user.mention}Congratulations! You guessed the word: `{chosen_word}`")
    else:
        await interaction.followup.send(f"Sorry, you ran out of attempts. The correct word was: `{chosen_word}`")

@bot.tree.command(name="cardgame", description="Play the Card Guessing Game")
async def play_card_game(interaction: discord.Interaction):
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

    chosen_suit = random.choice(suits)
    chosen_rank = random.choice(ranks)

    await interaction.response.send_message(f"Welcome to the Card Guessing Game, {interaction.user.mention}! Try to guess the suit and rank of the card.")

    attempts = 0

    while attempts < 3:
        try:
            user_suit_payload = await bot.wait_for("message", check=lambda m: m.author == interaction.user, timeout=30.0)
            user_suit = user_suit_payload.content.capitalize()

            user_rank_payload = await bot.wait_for("message", check=lambda m: m.author == interaction.user, timeout=30.0)
            user_rank = user_rank_payload.content.capitalize()

            attempts += 1

            if user_suit == chosen_suit and user_rank == chosen_rank:
                await interaction.followup.send(f"{interaction.user.mention} Congratulations! You guessed the correct card ({chosen_rank} of {chosen_suit}) in {attempts} attempts.")
                return
            else:
                await interaction.followup.send(f"Wrong guess! Attempts left: {3 - attempts}. Try again.")

        except asyncio.TimeoutError:
            await interaction.followup.send("Time's up! The game has ended.")
            return

    await interaction.followup.send(f"You reached the maximum number of attempts! The correct card was {chosen_rank} of {chosen_suit}.")

@bot.tree.command(name="joke", description="Get a good laugh with a random joke.")
async def get_joke(interaction: discord.Interaction):
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Parallel lines have so much in common. It's a shame they'll never meet.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "I told my wife she should embrace her mistakes. She gave me a hug.",
        "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them.",
        "Why did the coffee file a police report? It got mugged.",
        "I used to play piano by ear, but now I use my hands and fingers.",
        "What do you call fake spaghetti? An impasta.",
        "Why do chicken coops only have two doors? Because if they had four, they’d be a chicken sedan.",
        "I told my computer I needed a break, and now it won't stop sending me vacation ads.",
        "Why don't skeletons fight each other? They don't have the guts.",
        "What do you call a fish wearing a crown? A kingfish.",
        "Why did the bicycle fall over? It was two-tired.",
        "How does a penguin build its house? Igloos it together.",
        "Why don't oysters donate to charity? Because they are shellfish.",
        "What's a vampire's favorite fruit? A blood orange.",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why did the tomato turn red? Because it saw the salad dressing!",
        "How does a snowman get around? By riding an 'icicle.",
        "I asked the librarian if the library had books on paranoia. She whispered, 'They're right behind you.'",
        "Why couldn't the bicycle stand up by itself? It was two-tired.",
        "I'm reading a book on anti-gravity. It's impossible to put down!",
        "What do you call a snowman with a six-pack? An abdominal snowman.",
        "Why don't scientists trust atoms? Because they make up everything!",
        "Parallel lines have so much in common. It's a shame they'll never meet.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "I told my wife she should embrace her mistakes. She gave me a hug.",
        "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them.",
        "Why did the coffee file a police report? It got mugged.",
        "I used to play piano by ear, but now I use my hands and fingers.",
        "What do you call fake spaghetti? An impasta.",
        "Why do chicken coops only have two doors? Because if they had four, they’d be a chicken sedan.",
        "I told my computer I needed a break, and now it won't stop sending me vacation ads.",
        "Why don't skeletons fight each other? They don't have the guts.",
        "What do you call a fish wearing a crown? A kingfish.",
        "Why did the bicycle fall over? It was two-tired.",
        "How does a penguin build its house? Igloos it together.",
        "Why don't oysters donate to charity? Because they are shellfish.",
        "What's a vampire's favorite fruit? A blood orange.",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why did the tomato turn red? Because it saw the salad dressing!",
        "How does a snowman get around? By riding an 'icicle.",
        "I asked the librarian if the library had books on paranoia. She whispered, 'They're right behind you.'"
    ]

    random_joke = random.choice(jokes)

    embed = discord.Embed(
        title="🌟 Random Joke",
        description=f"**{random_joke}**",
        color=discord.Color.blurple()  # You can customize the color
    )

    # Send the embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="fact", description="get some cool facts")
async def get_random_fact(interaction: discord.Interaction):
    random_facts =[
        
        "The Eiffel Tower can be 15 cm taller during the summer due to thermal expansion.",
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
        "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
        "The average person will spend six months of their life waiting for red lights to turn green.",
        "Bananas are berries, but strawberries aren't.",
        "The longest word without a vowel is 'rhythms.'",
        "Cows have best friends and can become stressed when they are separated.",
        "Humans and giraffes have the same number of neck vertebrae (seven).",
        "The world's largest desert is Antarctica.",
        "The original name for Bank of America was 'Bank of Italy.'",
        "The inventor of the frisbee was turned into a frisbee. Walter Morrison's ashes were turned into a frisbee after he passed away.",
        "Octopuses have three hearts.",
        "A group of flamingos is called a 'flamboyance.'",
        "The Great Wall of China is not visible from the moon with the naked eye.",
        "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
        "A day on Venus (one full rotation) is longer than a year on Venus (one full orbit around the Sun).",
        "The word 'nerd' was first coined by Dr. Seuss in 'If I Ran the Zoo' in 1950.",
        "The world's oldest known recipe is for beer.",
        "The longest word in the English language without a vowel is 'rhythms.'",
        "The world's largest living structure is the Great Barrier Reef.",
        "The Mona Lisa has no eyebrows. It was fashionable in Renaissance Florence to shave them off.",
        "Coca-Cola was originally green.",
        "Honeybees can recognize human faces.",
        "A single cloud can weigh more than a million pounds.",
        "A 'jiffy' is an actual unit of time, equal to 1/100th of a second.",
        "Koalas have fingerprints that are indistinguishable from humans.",
        "A 'butterfly' used to be called a 'flutterby.'",
        "The first computer mouse was made of wood.",
        "Penguins can jump up to 6 feet in the air.",
        "A group of owls is called a 'parliament.'",
        "The dot over the letter 'i' is called a tittle.",
        "The world's largest pizza was 131 feet in diameter.",
        "The longest English word without a vowel is 'rhythms.'",
        "A day on Venus (one full rotation) is longer than a year on Venus (one full orbit around the Sun).",
        "Hippopotomonstrosesquippedaliophobia is the fear of long words.",
        "Banging your head against a wall burns 150 calories an hour.",
        "The oldest known animal on Earth is the sponge.",
    ]

    random_fact = random.choice(random_facts)

    embed = discord.Embed(
        title="🌟 Random Fact",
        description=f"**{random_fact}**",
        color=discord.Color.blurple()  # You can customize the color
    )

    
    await interaction.response.send_message(embed=embed)
    
bot.run(TOKEN)
