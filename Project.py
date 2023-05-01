import os
import discord
from discord.ext import commands
import openai
from datetime import datetime, timedelta
import asyncio
import random
from googletrans import Translator
import aiohttp
import webbrowser
import re
from collections import defaultdict
import wikipediaapi
import aiosqlite
import asyncio
import sqlite3
from cachetools import TTLCache
from bs4 import BeautifulSoup
import requests
import json
from urllib.parse import quote
from dotenv import load_dotenv



# Leveling system
xp_per_message = 5
reward_levels = {10: "Bronze", 20: "Silver", 30: "Gold"}

# Spam check system
recent_messages = {}  # key: user_id, value: list of message timestamps


polls = defaultdict(dict)
load_dotenv()
    # Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Configure the OpenAI API client
openai.api_key = OPENAI_API_KEY
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
GIPHY_API_KEY = os.environ.get("GIPHY_API_KEY")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
GENIUS_API_KEY = os.environ.get("GENIUS_API_KEY")
OTD_API_KEY = os.environ.get("OTD_API_KEY")
NEWS_API_KEY = "your_news_api_key_here"

wiki_lang = "en"
wiki = wikipediaapi.Wikipedia(wiki_lang)
    # Set the command prefix for your bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

# Rate limiting and caching
cache = TTLCache(maxsize=100, ttl=3600)


bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")


async def fetch_random_exercise():
    url = "https://wger.de/api/v2/exercise/?format=json&language=2&limit=1&offset=" + str(random.randint(1, 300))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="workout")
async def workout(ctx):
    exercise_data = await fetch_random_exercise()
    exercise_name = exercise_data["results"][0]["name"]
    exercise_description = exercise_data["results"][0]["description"].replace("<p>", "").replace("</p>", "")
    await ctx.send(f"Exercise: {exercise_name}\nDescription: {exercise_description}")


async def fetch_prompt():
    url = "https://www.reddit.com/r/WritingPrompts/random.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def fetch_random_fact():
    url = "https://api.chucknorris.io/jokes/random"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="random_fact")
async def random_fact(ctx):
    fact_data = await fetch_random_fact()
    fact = fact_data["value"]
    await ctx.send(fact)

async def fetch_random_cat():
    url = "https://api.thecatapi.com/v1/images/search"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def fetch_random_dog():
    url = "https://dog.ceo/api/breeds/image/random"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="random_pet")
async def random_pet(ctx, pet: str = "cat"):
    if pet.lower() == "cat":
        pet_data = await fetch_random_cat()
        pet_image = pet_data[0]["url"]
    elif pet.lower() == "dog":
        pet_data = await fetch_random_dog()
        pet_image = pet_data["message"]
    else:
        await ctx.send("Invalid pet type. Available types are 'cat' and 'dog'.")
        return

    await ctx.send(pet_image)

async def fetch_random_quote():
    url = "https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
            
async def fetch_subreddit_posts(subreddit: str):
    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
            
async def fetch_random_poem():
    url = "https://www.poemist.com/api/v1/randompoems"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def fetch_random_cocktail():
    url = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def fetch_random_wine():
    url = "https://api.sampleapis.com/wines/reds"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def fetch_news(query: str):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="news")
async def news(ctx, *, query: str):
    news_data = await fetch_news(query)
    articles = news_data["articles"]
    for article in articles[:5]:
        title = article["title"]
        url = article["url"]
        await ctx.send(f"{title}\n{url}")


@bot.command(name="wine")
async def wine(ctx):
    wine_data = await fetch_random_wine()
    random_wine = random.choice(wine_data)
    wine_name = random_wine["name"]
    wine_origin = random_wine["origin"]
    await ctx.send(f"Wine recommendation: {wine_name}\nOrigin: {wine_origin}")
    
    


@bot.command(name="cocktail")
async def cocktail(ctx):
    cocktail_data = await fetch_random_cocktail()
    cocktail_name = cocktail_data["drinks"][0]["strDrink"]
    cocktail_instructions = cocktail_data["drinks"][0]["strInstructions"]
    await ctx.send(f"{cocktail_name}\nInstructions: {cocktail_instructions}")


@bot.command(name="poem")
async def poem(ctx):
    poem_data = await fetch_random_poem()
    poem_title = poem_data[0]["title"]
    poem_content = poem_data[0]["content"]
    poem_author = poem_data[0]["poet"]["name"]
    await ctx.send(f'"{poem_title}" by {poem_author}\n{poem_content}')


@bot.command(name="reddit")
async def reddit(ctx, subreddit: str):
    post_data = await fetch_subreddit_posts(subreddit)
    posts = post_data["data"]["children"]
    for post in posts[:5]:
        title = post["data"]["title"]
        url = post["data"]["url"]
        await ctx.send(f"{title}\n{url}")


@bot.command(name="rquote")
async def rquote(ctx):
    rquote_data = await fetch_random_quote()
    rquote_text = rquote_data["rquoteText"]
    rquote_author = rquote_data["rquoteAuthor"]
    await ctx.send(f'"{rquote_text}" - {rquote_author}')



@bot.command(name="prompt")
async def prompt(ctx):
    prompt_data = await fetch_prompt()
    prompt_title = prompt_data[0]["data"]["children"][0]["data"]["title"]
    await ctx.send(prompt_title)

wiki_lang = "en"
wiki = wikipediaapi.Wikipedia(wiki_lang)

@bot.command(name="wikipedia")
async def wikipedia(ctx, *, search: str):
    page = wiki.page(search)
    if page.exists():
        summary = page.summary[:1500] + ("..." if len(page.summary) > 1500 else "")
        await ctx.send(f"{page.title}\n{summary}\nLink: {page.fullurl}")
    else:
        await ctx.send("No Wikipedia page found for that search.")


async def fetch_trivia():
    url = f"https://opentdb.com/api.php?amount=1&apikey={OTD_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="trivia")
async def trivia(ctx):
    trivia_data = await fetch_trivia()
    question = trivia_data["results"][0]["question"]
    answer = trivia_data["results"][0]["correct_answer"]
    await ctx.send(f"Trivia question: {question}\nAnswer: {answer}")


def parse_duration(duration_str):
    units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    duration = int(duration_str[:-1]) * units[duration_str[-1]]
    return duration

    # Helper function
def find_member(ctx, member_str):
    return discord.utils.find(lambda m: m.name.lower() == member_str.lower(), ctx.guild.members)
    
@bot.command(name='freechamps')
async def freechamps_command(ctx):
    free_champion_rotation = get_free_champion_rotation()
    if free_champion_rotation:
        response_text = f"Current Free Champion Rotation:\n{free_champion_rotation}"
        await ctx.send(response_text)
    else:
        await ctx.send("Could not find the current free champion rotation")

def get_free_champion_rotation():
    region = "na1"  # Change this based on the desired region
    free_champ_url = f"https://{region}.api.riotgames.com/lol/platform/v3/champion-rotations?api_key={RIOT_API_KEY}"
    free_champ_response = requests.get(free_champ_url)

    if free_champ_response.status_code != 200:
        return None

    free_champ_data = free_champ_response.json()
    free_champion_ids = free_champ_data["freeChampionIds"]
    free_champion_names = [champion_id_to_name(champion_id) for champion_id in free_champion_ids]

    return ", ".join(free_champion_names)
	
@bot.command(name='matchhistory')
async def matchhistory_command(ctx, *, summoner_name: str):
    match_history = get_match_history(summoner_name)
    if match_history:
        response_text = f"Match History for {summoner_name}:\n{match_history}"
        await ctx.send(response_text)
    else:
        await ctx.send(f"Could not find match history for '{summoner_name}'")

def get_match_history(summoner_name: str):
    account_id = get_account_id(summoner_name)
    if not account_id:
        return None

    region = "na1"  # Change this based on the desired region
    match_history_url = f"https://{region}.api.riotgames.com/lol/match/v4/matchlists/by-account/{account_id}?api_key={RIOT_API_KEY}"
    match_history_response = requests.get(match_history_url)

    if match_history_response.status_code != 200:
        return None

    match_history_data = match_history_response.json()
    matches = match_history_data["matches"]

    formatted_matches = "\n".join(
        [
            f"{index+1}. Game Mode: {match['queue']} | Champion: {champion_id_to_name(match['champion'])} | Timestamp: {match['timestamp']}"
            for index, match in enumerate(matches[:10])  # Limit to the last 10 matches
        ]
    )

    return formatted_matches

def get_account_id(summoner_name: str):
    region = "na1"  # Change this based on the desired region
    summoner_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={RIOT_API_KEY}"
    summoner_response = requests.get(summoner_url)

    if summoner_response.status_code != 200:
        return None

    summoner_data = summoner_response.json()
    return summoner_data["accountId"]


@bot.command(name='tierlist')
async def tierlist_command(ctx):
    tier_list = get_tier_list()
    if tier_list:
        response_text = f"Current Tier List:\n{tier_list}"
        await ctx.send(response_text)
    else:
        await ctx.send("Could not fetch the tier list.")

def get_tier_list():
    url = "https://www.leagueofgraphs.com/champions/overview"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    tier_list_sections = soup.find_all("div", {"class": "medium-6"})

    if not tier_list_sections:
        return None

    formatted_tier_list = ""
    for section in tier_list_sections:
        role_title = section.find("h3")
        if not role_title:
            continue

        role = role_title.text.strip()
        champions = section.find_all("div", {"class": "championBox"})

        tier_champions = [
            f"{index + 1}. {champion.find('div', {'class': 'name'}).text.strip()} - Win Rate: {champion.find('div', {'class': 'winRate'}).text.strip()}"
            for index, champion in enumerate(champions)
        ]

        formatted_tier_list += f"{role}:\n" + "\n".join(tier_champions) + "\n\n"

    return formatted_tier_list.strip()



@bot.command(name='counters')
async def counters_command(ctx, *, champion_name: str):
    counters = get_champion_counters(champion_name.lower())
    if counters:
        response_text = f"Counters for {champion_name.capitalize()}:\n{counters}"
        await ctx.send(response_text)
    else:
        await ctx.send(f"Could not find counters for '{champion_name}'")

def get_champion_counters(champion_name: str):
    url = f"https://www.leagueofgraphs.com/en/champions/counters/{champion_name.lower()}/all"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    start_index = response.text.find("data: ") + 6
    end_index = response.text.find("\n", start_index) - 1
    json_data = response.text[start_index:end_index]
    counters_data = json.loads(json_data)

    formatted_counters = "\n".join(
        [
            f"{index + 1}. {counter['champion']} - Win Rate: {counter['winRate']}%, Matches: {counter['matchNumber']}"
            for index, counter in enumerate(counters_data)
        ]
    )

    return formatted_counters


@bot.command(name='esports')
async def esports_command(ctx):
    esports_matches = get_esports_matches()
    if esports_matches:
        response_text = f"Upcoming and Ongoing eSports Matches:\n{esports_matches}"
        await ctx.send(response_text)
    else:
        await ctx.send("No upcoming or ongoing eSports matches found")

def get_esports_matches():
    PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
    url = f"https://api.pandascore.co/lol/matches/upcoming_and_running?token={PANDASCORE_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    matches_data = response.json()
    formatted_matches = "\n".join(
        [
            f"{match['name']} - {match['league']['name']} ({match['scheduled_at']})"
            for match in matches_data
        ]
    )

    return formatted_matches

	
@bot.command(name='patchnotes')
async def patchnotes_command(ctx):
    latest_patch_notes_url = get_latest_patch_notes_url()
    if latest_patch_notes_url:
        response_text = f"Latest Patch Notes: {latest_patch_notes_url}"
        await ctx.send(response_text)
    else:
        await ctx.send("Could not find the latest patch notes")

def get_latest_patch_notes_url():
    base_url = "https://na.leagueoflegends.com"
    patch_notes_url = f"{base_url}/en-us/news/game-updates/"

    response = requests.get(patch_notes_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    patch_notes_links = soup.find_all("a", class_="style--preview-card")

    if not patch_notes_links:
        return None

    latest_patch_notes_url = base_url + patch_notes_links[0]["href"]
    return latest_patch_notes_url
	
@bot.command(name='champion')
async def champion_command(ctx, *, champion_name: str):
    champion_data = get_champion_data(champion_name.lower())
    if champion_data:
        response_text = format_champion_data(champion_data)
        await ctx.send(response_text)
    else:
        await ctx.send(f"Could not find champion '{champion_name}'")

def load_champion_data():
    with open("data/champion.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        return data["data"]
		
@bot.command(name='livegame')
async def livegame_command(ctx, *, summoner_name: str):
    live_game_data = get_live_game_data(summoner_name)
    if live_game_data:
        response_text = format_live_game_data(live_game_data)
        await ctx.send(response_text)
    else:
        await ctx.send(f"No live game found for summoner '{summoner_name}'")
		
def champion_id_to_name(champion_id: int):
    for champion_key, champion_info in champion_data_cache.items():
        if int(champion_info["key"]) == champion_id:
            return champion_info["name"]
    return "Unknown"


def get_live_game_data(summoner_name: str):
    summoner_data = get_summoner_data(summoner_name)
    if not summoner_data:
        return None

    region = "na1"  # Change this based on the desired region
    summoner_id = summoner_data["id"]
    live_game_url = f"https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}?api_key={RIOT_API_KEY}"
    live_game_response = requests.get(live_game_url)

    if live_game_response.status_code != 200:
        return None

    return live_game_response.json()

def format_live_game_data(live_game_data: dict):
    game_mode = live_game_data["gameMode"]
    game_length = live_game_data["gameLength"] // 60

    participants = live_game_data["participants"]
    formatted_participants = "\n".join(
        [f"{participant['summonerName']} ({champion_id_to_name(participant['championId'])})" for participant in participants]
    )

    response_text = f"Live Game - {game_mode}\nDuration: {game_length} minutes\n\nParticipants:\n{formatted_participants}"
    return response_text



champion_data_cache = load_champion_data()

def get_champion_data(champion_name: str):
    for champion_key, champion_info in champion_data_cache.items():
        if champion_info["name"].lower() == champion_name:
            return champion_info
    return None

def format_champion_data(champion_data: dict):
    title = champion_data["title"]
    name = champion_data["name"]
    passive = champion_data["passive"]
    abilities = champion_data["spells"]

    formatted_abilities = "\n\n".join(
        [f"{ability['name']} ({ability['key']}): {ability['description']}" for ability in abilities]
    )

    response_text = f"{name}, {title}\n\nPassive: {passive['name']} - {passive['description']}\n\nAbilities:\n\n{formatted_abilities}"
    return response_text
	
@bot.command(name='summoner')
async def summoner_command(ctx, *, summoner_name: str):
    summoner_data = get_summoner_data(summoner_name)
    if summoner_data:
        response_text = f"Summoner '{summoner_name}' has level {summoner_data['summonerLevel']} and is ranked {summoner_data['tier']} {summoner_data['rank']} with {summoner_data['leaguePoints']} LP in Solo/Duo."
        await ctx.send(response_text)
    else:
        await ctx.send(f"Could not find summoner '{summoner_name}'")

def get_summoner_data(summoner_name: str):
    region = "na1"  # Change this based on the desired region
    summoner_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={RIOT_API_KEY}"
    summoner_response = requests.get(summoner_url)

    if summoner_response.status_code != 200:
        return None

    summoner_data = summoner_response.json()
    summoner_id = summoner_data["id"]

    league_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={RIOT_API_KEY}"
    league_response = requests.get(league_url)

    if league_response.status_code != 200:
        return None

    league_data = league_response.json()
    solo_duo_data = None

    for entry in league_data:
        if entry["queueType"] == "RANKED_SOLO_5x5":
            solo_duo_data = entry
            break

    if solo_duo_data:
        summoner_data["tier"] = solo_duo_data["tier"]
        summoner_data["rank"] = solo_duo_data["rank"]
        summoner_data["leaguePoints"] = solo_duo_data["leaguePoints"]
    else:
        summoner_data["tier"] = "Unranked"
        summoner_data["rank"] = ""
        summoner_data["leaguePoints"] = 0

    return summoner_data


@bot.command(name="create_poll")
async def create_poll(ctx, question: str, *options: str):
    if len(options) < 2:
        await ctx.send("You must provide at least two options for the poll.")
        return

    poll_id = f"{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}"
    poll_options = {str(i): option for i, option in enumerate(options, 1)}

    polls[poll_id] = {
        "question": question,
        "options": poll_options,
        "votes": defaultdict(int)
    }

    options_text = "\n".join([f"{key}. {value}" for key, value in poll_options.items()])
    await ctx.send(f"Poll created with ID: {poll_id}\nQuestion: {question}\nOptions:\n{options_text}")

@bot.command(name="vote")
async def vote(ctx, poll_id: str, option: str):
    poll = polls.get(poll_id)
    if not poll:
        await ctx.send("Invalid poll ID.")
        return

    if option not in poll["options"]:
        await ctx.send("Invalid option.")
        return

    poll["votes"][option] += 1
    await ctx.send(f"Vote recorded for poll {poll_id}.")

@bot.command(name="poll_results")
async def poll_results(ctx, poll_id: str):
    poll = polls.get(poll_id)
    if not poll:
        await ctx.send("Invalid poll ID.")
        return

    results = "\n".join([f"{key}. {value}: {poll['votes'][key]}" for key, value in poll["options"].items()])
    await ctx.send(f"Poll results for {poll_id}:\nQuestion: {poll['question']}\n{results}")


async def fetch_song_data(query):
    url = f"http://api.genius.com/search?q={query}&access_token={GENIUS_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def fetch_lyrics(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            lyrics = re.search(r'<div class="lyrics">([\s\S]+?)<\/div>', html).group(1)
            return re.sub(r"<.*?>", "", lyrics).strip()

@bot.command(name="lyrics")
async def lyrics(ctx, *, song_title: str):
    song_data = await fetch_song_data(song_title)
    if song_data["response"]["hits"]:
        song_url = song_data["response"]["hits"][0]["result"]["url"]
        song_lyrics = await fetch_lyrics(song_url)
        await ctx.send(song_lyrics[:2000] + ("..." if len(song_lyrics) > 2000 else ""))
    else:
        await ctx.send("No lyrics found for that song.")

async def fetch_quote():
    url = "https://zenquotes.io/api/random"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="quote")
async def quote(ctx):
    quote_data = await fetch_quote()
    quote = quote_data[0]["q"]
    author = quote_data[0]["a"]
    await ctx.send(f"{quote}\n- {author}")


    # Define the gpt command
@bot.command(name="gpt")
async def gpt(ctx, *, prompt: str):
    # Set up the GPT API call parameters
    gpt_request = {
        "engine": "text-davinci-002",
        "prompt": prompt,
        "max_tokens": 100,
        "n": 1,
        "stop": None,
        "temperature": 0.5,
    }

    # Call the GPT API
    response = openai.Completion.create(**gpt_request)
    answer = response.choices[0].text.strip()

    # Send the generated response back to the Discord channel
    await ctx.send(answer)
    
async def fetch_youtube_video(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=25&q={query}&key={YOUTUBE_API_KEY}&type=video"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="youtube")
async def youtube(ctx, *, keyword: str):
    videos_data = await fetch_youtube_video(keyword)
    if videos_data["items"]:
        random_video = random.choice(videos_data["items"])
        video_id = random_video["id"]["videoId"]
        await ctx.send(f"https://www.youtube.com/watch?v={video_id}")
    else:
        await ctx.send("No videos found for that keyword.")

    # Ban command
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member_str: str, duration_str: str, *, reason=None):
    member = find_member(ctx, member_str)

    if member is None:
        await ctx.send(f"Member '{member_str}' not found.")
        return
    duration = parse_duration(duration_str)
    await ctx.guild.ban(member, reason=reason)
    await ctx.send(f"{member} has been banned for {duration} seconds. Reason: {reason}")
    await asyncio.sleep(duration)
    await ctx.guild.unban(member)
    await ctx.send(f"{member} has been unbanned after {duration} seconds.")

async def fetch_weather(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="weather")
async def weather(ctx, *, location: str):
    weather_data = await fetch_weather(location)
    if weather_data.get("message"):
        await ctx.send(weather_data["message"])
    else:
        temp = weather_data["main"]["temp"]
        conditions = ", ".join([weather["description"] for weather in weather_data["weather"]])
        await ctx.send(f"Weather in {location}:\nTemperature: {temp}°C\nConditions: {conditions}")

    # Unban command
@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanned {user.mention}")
            return

    # Mute command
@bot.command(name="mute")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member_str: str, duration_str: str, *, reason=None):
    member = find_member(ctx, member_str)

    if member is None:
        await ctx.send(f"Member '{member_str}' not found.")
        return
    duration = parse_duration(duration_str)
    guild = ctx.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")

    if not muted_role:
        muted_role = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)

    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"{member} has been muted for {duration} seconds. Reason: {reason}")
    await asyncio.sleep(duration)
    await member.remove_roles(muted_role)
    await ctx.send(f"{member} has been unmuted after {duration} seconds.")

# Unmute command
@bot.command(name="unmute")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f"{member} has been unmuted.")
    else:
        await ctx.send(f"{member} is not currently muted.")

    # Limit command
@bot.command(name="limit")
@commands.has_permissions(manage_roles=True)
async def limit(ctx, member_str: str, messages_per_interval: int, interval_str: str, *, reason=None):
    member = find_member(ctx, member_str)

    if member is None:
        await ctx.send(f"Member '{member_str}' not found.")
        return
    interval = parse_duration(interval_str)
    # Create a role with limited message permissions
    guild = ctx.guild
    limited_role = discord.utils.get(guild.roles, name="Limited")

    if not limited_role:
        limited_role = await guild.create_role(name="Limited")

        for channel in guild.channels:
            await channel.set_permissions(limited_role, send_messages=False)

    # Assign the limited role
    await member.add_roles(limited_role, reason=reason)
    await ctx.send(f"{member}'s messages have been limited to {messages_per_interval} per {interval} seconds. Reason: {reason}")

    # Remove the limited role after the specified interval
    while True:
        await asyncio.sleep(interval)
        message_count = 0
        async for message in ctx.channel.history(limit=messages_per_interval):
            if message.author == member:
                message_count += 1
                if message_count >= messages_per_interval:
                    await message.delete()

    # Kick command
@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, *, member_str: str, reason=None):
    member = find_member(ctx, member_str)

    if member is None:
        await ctx.send(f"Member '{member_str}' not found.")
        return

    await member.kick(reason=reason)
    await ctx.send(f"{member} has been kicked. Reason: {reason}")


    # Nickname command
@bot.command(name="nickname")
@commands.has_permissions(manage_nicknames=True)
async def nickname(ctx, member_str: str, *, new_nickname):
    member = find_member(ctx, member_str)

    if member is None:
        await ctx.send(f"Member '{member_str}' not found.")
        return

    await member.edit(nick=new_nickname)
    await ctx.send(f"{member}'s nickname has been changed to {new_nickname}")
    
    # Clear command
@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"{amount} messages have been cleared.")
    await asyncio.sleep(5)
    await msg.delete()

# Role command
@bot.command(name="role")
@commands.has_permissions(manage_roles=True)
async def role(ctx, member_str: str, role_name: str, action: str):
    member = find_member(ctx, member_str)

    if member is None:
        await ctx.send(f"Member '{member_str}' not found.")
        return

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        await ctx.send(f"Role '{role_name}' not found.")
        return

    if action.lower() == "give":
        await member.add_roles(role)
        await ctx.send(f"Role '{role_name}' has been given to {member}.")
    elif action.lower() == "take":
        await member.remove_roles(role)
        await ctx.send(f"Role '{role_name}' has been taken from {member}.")
    elif action.lower() == "change":
        await member.remove_roles(*member.roles[1:])
        await member.add_roles(role)
        await ctx.send(f"{member}'s role has been changed to '{role_name}'.")
    else:
        await ctx.send("Invalid action. Use 'give', 'take', or 'change'.")
        
async def fetch_joke():
    url = "https://v2.jokeapi.dev/joke/Any"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="joke")
async def joke(ctx):
    joke_data = await fetch_joke()

    if joke_data['type'] == 'single':
        await ctx.send(joke_data['joke'])
    else:
        await ctx.send(f"{joke_data['setup']}\n{joke_data['delivery']}")

translator = Translator()

@bot.command(name="translate")
async def translate(ctx, target_language: str, *, text: str):
    try:
        translated = translator.translate(text, dest=target_language)
        await ctx.send(translated.text)
    except ValueError:
        await ctx.send("Invalid target language.")

async def fetch_gif(query):
    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={query}&limit=25&offset=0&rating=g&lang=en"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command(name="gif")
async def gif(ctx, *, keyword: str):
    gifs_data = await fetch_gif(keyword)
    if gifs_data['data']:
        random_gif = random.choice(gifs_data['data'])
        await ctx.send(random_gif['url'])
    else:
        await ctx.send("No GIFs found for that keyword.")
        
@bot.command(name="help")
async def help_command(ctx):
    help_text1 = """
    
**!gpt [text]** - Sends a message to the GPT API and returns the response.
**!ban [user] [duration] [duration_unit]** - Bans a user for the specified duration. Duration units: 's' for seconds, 'm' for minutes, 'h' for hours, 'd' for days.
**!unban [user]** - Unbans a user.
**!mute [user] [duration] [duration_unit]** - Mutes a user for the specified duration. Duration units: 's' for seconds, 'm' for minutes, 'h' for hours, 'd' for days.
**!unmute [user]** - Unmutes a user.
**!limit [user] [number_of_messages] [duration] [duration_unit]** - Limits a user to send the specified number of messages within the specified duration. Duration units: 's' for seconds, 'm' for minutes, 'h' for hours, 'd' for days.
**!kick [user]** - Kicks a user from the server.
**!nickname [user] [new_nickname]** - Changes a user's nickname.
**!clear [number_of_messages]** - Clears the specified number of messages from the chat.
**!role [user] [role_name] [action]** - Gives, takes or changes a user's role. Actions: 'give', 'take', 'change'.
**!joke** - Fetches a random joke.
**!translate [text] [target_language]** - Translates the input text to the specified target language.
**!gif [keyword]** - Generates a random GIF based on the provided keyword.
**!weather [location]** - Fetches the weather forecast for the specified location.
**!youtube [keyword]** - Plays a random YouTube video based on the specified keyword.
"""
    help_text2 = """
    
**!lyrics [song_title] [artist_name]** - Fetches the lyrics for the specified song.
**!quote** - Retrieves a random inspirational quote or daily affirmation.
**!poll [question] [option1] [option2] [...]** - Creates a poll with the specified question and options.
**!trivia** - Generates a random trivia question.
**!prompt** - Generates a random writing prompt or exercise.
**!wikipedia [query]** - Searches for and retrieves information from Wikipedia based on the query.
**!fact** - Generates a random fact or interesting piece of trivia.
**!cat** - Generates a random cat picture.
**!dog** - Generates a random dog picture.
**!wine** - Generates a random wine recommendation.
**!news [query]** - Searches for and retrieves information from news sources based on the query.
**!workout** - Generates a random workout or exercise routine.
"""

    await ctx.send(help_text1)
    await ctx.send(help_text2)
  


# Error handlers
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument. Correct syntax: `!clear <amount>`")
    else:
        await ctx.send("An error occurred. Please try again.")

@role.error
async def role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument. Correct syntax: `!role <member_name> <role_name> <action>`")
    else:
        await ctx.send("An error occurred. Please try again.")
        
# Other commands and bot.run
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument. Correct syntax: `!ban <member_name> <duration> [reason]`")
    else:
        await ctx.send("An error occurred. Please try again.")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument. Correct syntax: `!mute <member_name> <duration> [reason]`")
    else:
        await ctx.send("An error occurred. Please try again.")

@limit.error
async def limit_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument. Correct syntax: `!limit <member_name> <messages_per_interval> <interval> [reason]`")
    else:
        await ctx.send("An error occurred. Please try again.")

@nickname.error
async def nickname_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument. Correct syntax: `!nickname <member_name> <new_nickname>`")
    else:
        await ctx.send("An error occurred. Please try again.")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument. Correct syntax: `!kick <member_name> [reason]`")
    else:
        await ctx.send("An error occurred. Please try again.")

# Run the bot
bot.run(DISCORD_TOKEN)

