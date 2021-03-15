import discord
import os
import requests
import json

client = discord.Client()

def get_rank(player_name = "TheSam"):
  url = """https://aoe2.net/api/leaderboard?game=aoe2de&leaderboard_id=3&search={player_name}""".format(player_name = player_name)
  response = requests.get(url)
  json_data = json.loads(response.text)
  json_data = json_data['leaderboard'][0]
  json_data['rating'] = int((json_data['previous_rating'] + json_data['highest_rating'] )/2)
  return(json_data)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    
    
    if message.content.startswith('!rank'):
      quote = get_rank()
      await message.channel.send(quote)

client.run(os.getenv('TOKEN'))