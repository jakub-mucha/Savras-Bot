import pandas as pd
import discord

CACHE = []

def initialize():
    df_unplayed = pd.read_excel("board games to play.xlsx", "To play V2", usecols="B:J")
    df_unplayed = df_unplayed[df_unplayed["TTS?"] == "Tak"]
    df_unplayed = df_unplayed[(df_unplayed["Best for players"] != "---") & (df_unplayed["Best for players"].notnull())]
    df_unplayed = df_unplayed[~(df_unplayed["Nazwa"].isin(CACHE))]
    return df_unplayed


def filter_player_num_ideal(row, no_players):
    result = False
    raw_string = row["Best for players"]
    substrings = raw_string.split(" ")
    if len(substrings) == 1:
        substrings.insert(0, "0")
    substrings[0] = substrings[0].replace("(", "").replace(")", "")
    if "-" in substrings[0]:
        players = substrings[0].split("-")
        if no_players == "low":
            if int(players[1]) <= 4:
                result = True
        else:
            if int(players[1]) > 4:
                result = True
    elif "," in substrings[0]:
        players = substrings[0].split(",")
        if no_players == "low":
            if int(players[0]) <= 4:
                result = True
        else:
            if int(players[0]) > 4:
                result = True
    else:
        if no_players == "low":
            if int(substrings[0]) <= 4:
                result = True
        else:
            if int(substrings[0]) > 4:
                result = True
    return result


def filter_player_num_backup(row, no_players):
    result = False
    raw_string = row["Best for players"]
    substrings = raw_string.split(" ")
    if len(substrings) == 1:
        substrings.insert(0, "0")
    substrings[1] = substrings[1].replace("(", "").replace(")", "")
    if "-" in substrings[1]:
        players = substrings[1].split("-")
        if no_players == "low":
            if int(players[1]) <= 4:
                result = True
        else:
            if int(players[1]) > 4:
                result = True
    elif "," in substrings[1]:
        players = substrings[1].split(",")
        if no_players == "low":
            if int(players[0]) <= 4:
                result = True
        else:
            if int(players[0]) > 4:
                result = True
    else:
        if no_players == "low":
            if int(substrings[1]) <= 4:
                result = True
        else:
            if int(substrings[1]) > 4:
                result = True
    return result


def select_games(dataframe, no_players):
    global CACHE
    dataframe_ideal = dataframe[dataframe.apply(filter_player_num_ideal, axis=1, no_players=no_players)]
    dataframe_ideal = dataframe_ideal[~(dataframe_ideal["Nazwa"].isin(CACHE))]
    if len(dataframe_ideal) < 4:
        dataframe_backup = dataframe[dataframe.apply(filter_player_num_backup, axis=1, no_players=no_players)]
        dataframe_backup = dataframe_backup.sample(4 - len(dataframe_ideal))
        result = pd.concat([dataframe_ideal, dataframe_backup])
    else:
        result = dataframe_ideal.sample(4)
    return result


intents = discord.Intents.all()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global CACHE
    if message.author == client.user:
        return

    if message.content.startswith('$ankieta'):
        dataframe = initialize()
        options = [":regional_indicator_a:", ":regional_indicator_b:", ":regional_indicator_c:", ":regional_indicator_d:"]
        selection = select_games(dataframe, "low")
        idx = 0
        ankieta = ""
        for ind in selection.index:
            ankieta += options[idx] + " " + selection["Nazwa"][ind] + "\n"
            idx += 1
        await message.channel.send("Selekcja gier dla 1-4 graczy:\n" + ankieta)
        selection_high = select_games(dataframe, "high")
        idx = 0
        ankieta = ""
        for ind in selection_high.index:
            ankieta += options[idx] + " " + selection_high["Nazwa"][ind] + "\n"
            idx += 1
        CACHE = []
        for ind in selection.index:
            CACHE.append(selection["Nazwa"][ind])
        for ind in selection_high.index:
            CACHE.append(selection_high["Nazwa"][ind])
        await message.channel.send("Selekcja gier dla 5+ graczy:\n" + ankieta)

client.run('MTAyMDM2NTY2MDkzMDQ2MTgyOA.GW2cYN.r1ZoTIUt9018-hHssGYKCzcnNx8Iv0c6UsYl0k')
