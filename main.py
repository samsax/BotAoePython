import discord
import os
import requests
import json
from requests.auth import HTTPBasicAuth
client = discord.Client()

def get_rank(player_name="TheSam"):
    url = """https://aoe2.net/api/leaderboard?game=aoe2de&leaderboard_id=3&search={player_name}""".format(
        player_name=player_name)
    response = requests.get(url)
    json_data = json.loads(response.text)
    json_data = json_data['leaderboard'][0]
    json_data['rating'] = int(
        (json_data['previous_rating'] + json_data['highest_rating']) / 2)
    return (json_data)


def set_register(name, username='', tournament_name=''):
    url = "https://api.challonge.com/v1/tournaments/{}/participants.json".format(tournament_name)
    payload = {"participant": {"name": name, "misc": username}}
    response = requests.post(url,
                             json=payload,
                             auth=HTTPBasicAuth(
                                 os.getenv('USERNAME'),
                                 os.getenv('APIKEY')))

    json_data = json.loads(response.text)
    return (json_data)


def get_participants(tournament_name):
    url = "https://api.challonge.com/v1/tournaments/{}/participants.json".format(tournament_name)
    
    response = requests.get(url,
                            auth=HTTPBasicAuth(
                                os.getenv('USERNAME'),
                                os.getenv('APIKEY')))
    json_data = json.loads(response.text)
    return (json_data)


def get_matches(tournament_name):
    url = "https://api.challonge.com/v1/tournaments/{}/matches.json".format(tournament_name)
    response = requests.get(url,
                            auth=HTTPBasicAuth(
                                os.getenv('USERNAME'),
                                os.getenv('APIKEY')))
    json_data = json.loads(response.text)
    return (json_data)


def update_match(match_id, match, tournament_name):
    url = "https://api.challonge.com/v1/tournaments/{}/matches/{}.json".format(
        tournament_name, match_id)
    response = requests.put(url,
                            json=match,
                            auth=HTTPBasicAuth(
                                os.getenv('USERNAME'),
                                os.getenv('APIKEY')))

    json_data = json.loads(response.text)
    return (json_data)

def print_message(title, description, color, additional_data = []):
  embedVar = discord.Embed(title=title, description=description, color=color)

  for data in additional_data:
    embedVar.add_field(name=data['name'], value=data['value'], inline=False)

  return embedVar

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # if message.content.startswith('!hello'):
    #     username = '{}#{}'.format(message.author.name,
    #                               message.author.discriminator)
    #     embedVar = print_message("Hello", "Hello", 0x00ff00, [dict(name="hello", value=username), dict(name="hello2", value="Baneados todos")])
    #     await message.channel.send(embed=embedVar)
        #await message.reply('Hello! {}'.format(username))

    # if message.content.startswith('!register'):
    #     #TODO register with mentions
    #     username = '{}#{}'.format(message.author.name,
    #                               message.author.discriminator)

    #     tournament_name = message.channel.name.split("-")
    #     if(len(tournament_name)!=2):
    #       await message.channel.send("canal equivocado")
    #     tournament_name = tournament_name[1]

    #     set_register(message.author.name, username, tournament_name)
    #     await message.channel.send('Success {}'.format(username))

    if message.content.startswith('!pavel'):
        await message.channel.send(':clown: :eggplant:')




    if message.content.startswith('!result'):
        username = '{}#{}'.format(message.author.name,
                                   message.author.discriminator)
        mentions = message.mentions

        message_split = message.content.split(" ")
        message_split = list(filter(None, message_split))
        if ((not message_split[2].isdigit()) or (not message_split[4].isdigit())):
          embedVar = print_message("Los puntos de los jugadores deben ser un número", "Recuerda que el formato es: !result @jugador1 puntos @jugador2 puntos", 0xff0000)
          await message.channel.send(embed=embedVar)
          return

        if(len(message_split) != 5 or len(mentions) != 2):
          embedVar = print_message("Te faltan datos para actualizar el resultado", "Recuerda que el formato es: !result @jugador1 puntos @jugador2 puntos", 0xff0000)
          await message.channel.send(embed=embedVar)
          return
        if((str(mentions[0]) != username) and (str(mentions[1]) != username)):
          embedVar = print_message("Solos los jugadores pueden actualizar su resultado", "Recuerda que el formato es: !result @jugador1 puntos @jugador2 puntos", 0xff0000)
          await message.channel.send(embed=embedVar)
          return
        tournament_name = message.channel.name.split("-")
        if(len(tournament_name) != 2):
          embedVar = print_message("Publica tu resultado en el canal correcto", "", 0xff0000)
          await message.channel.send(embed=embedVar)
          return
        
        tournament_name = tournament_name[1]
        scores = list()
        scores.append(message_split[2])
        scores.append(message_split[4])
        ids_paticipants = list()
        unique_ids = list()
        participants = get_participants(tournament_name)
        iter = 0
        for mention in mentions:
            for participant in participants:
                if (participant['participant']['misc'] == str(mention)):
                    unique_ids.append(
                        dict(id=participant['participant']['id'],
                             misc=str(mention),
                             score=scores[iter]))
                    ids_paticipants.append(participant['participant']['id'])
            iter = iter + 1


        matches = get_matches(tournament_name)
        
        found_match = False
        for match in matches:
            if ((match['match']['player1_id'] in ids_paticipants)
                    and (match['match']['player2_id'] in ids_paticipants)):
                match['match']['winner_id'] = unique_ids[0][
                    'id'] if unique_ids[0]['score'] > unique_ids[1][
                        'score'] else unique_ids[1]['id']
                score_format = "{}-{}"
                match['match']['scores_csv'] = score_format.format(
                    unique_ids[0]['score'],
                    unique_ids[1]['score']) if unique_ids[0]['id'] == match[
                        'match']['player1_id'] else score_format.format(
                            unique_ids[1]['score'], unique_ids[0]['score'])
                match['match']['player1_votes'] = unique_ids[0][
                    'score'] if unique_ids[0]['id'] == match['match'][
                        'player1_id'] else unique_ids[1]['score']
                match['match']['player2_votes'] = unique_ids[0][
                    'score'] if unique_ids[0]['id'] == match['match'][
                        'player2_id'] else unique_ids[1]['score']
                found_match = True
                update_match(match['match']['id'], match, tournament_name)
                

        if(not found_match):
          embedVar = print_message("No se encontró una partida asociada.", "Revisa que te encuentes en el canal de tu categoría", 0xff0000)
          await message.channel.send(embed=embedVar)
          return

        embedVar = print_message("Resultado actualizado", "Categoria {}".format(tournament_name), 0x00ff00, [
          dict(name=unique_ids[0]['misc'], value=unique_ids[0]['score']),
          dict(name=unique_ids[1]['misc'], value=unique_ids[1]['score'])
        ])
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!match'):
        mentions = message.mentions

        if(len(mentions) > 0):
          username = str(mentions[0])
        else: 
          username = '{}#{}'.format(message.author.name, message.author.discriminator)
        
        tournament_name = message.channel.name.split("-")
        if(len(tournament_name) != 2):
          embedVar = print_message("Canal equivocado", "", 0xff0000)
          await message.channel.send(embed=embedVar)
          return
        tournament_name = tournament_name[1]

        participants = get_participants(tournament_name)
        participant_id = None
        actual_participant = None
        for participant in participants:
          if (participant['participant']['misc'] == str(username)):
            participant_id = participant['participant']['id']
            actual_participant = participant['participant']
            break

        if(participant_id is None):
          embedVar = print_message("No existe una partida", "", 0xff0000)
          await message.channel.send(embed=embedVar)
          return

        matches = get_matches(tournament_name)
        actual_match = None
        actual_round = 0
        participant_enemy = None

        for match in matches:
          if ((match['match']['player1_id'] == participant_id) or (match['match']['player2_id'] == participant_id)):
            
            if(match['match']['round'] > actual_round):
              actual_match = match['match']
              actual_round = match['match']['round']
              actual_enemy = match['match'][
                      'player2_id'] if participant_id == match['match'][
                      'player1_id'] else match['match'][
                      'player1_id']
            
        if(actual_match):
          for participant in participants:
            if (participant['participant']['id'] == actual_enemy):
              participant_enemy = participant['participant']
              break
        else:
          embedVar = print_message("No existe una partida", "", 0xff0000)
          await message.channel.send(embed=embedVar)
          return
        data_participants = []
        if(participant_enemy):
          data_participants = [
            dict(name=actual_participant['name'], value=actual_participant['misc']),
            dict(name=participant_enemy['name'], value=participant_enemy['misc'])
          ]
        else:
          data_participants = [
            dict(name=actual_participant['name'], value=actual_participant['misc']),
            dict(name="Rival", value="Por confirmar")
          ]
        if(actual_match['winner_id']):
          title = "Ultima partida jugada"
          data_participants.append(dict(name="Resultado:",value=actual_match['scores_csv'] ))
          winner = actual_participant[
                    'misc'] if actual_match['winner_id'] == actual_participant['id'] else participant_enemy['misc']
          data_participants.append(dict(name="Ganador:",value=winner ))
        else:
          title = "Próxima partida"
        embedVar = print_message(title, "Categoria {}".format(tournament_name), 0x00ff00, data_participants)
        await message.channel.send(embed=embedVar)

client.run(os.getenv('TOKEN'))
  