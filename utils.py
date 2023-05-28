import discord
import time
import os
import csv

files=["commands", "flairs", "coins", "bank", "delivery", "shell", "bomb", "ticket", "letter", "banana"]
file_checks={file:False for file in files}
lists={file:{} for file in files}
snipe_data={"content":{}, "author":{}, "id":{}, "attachment":{}}
editsnipe_data={"content":{}, "author":{}, "id":{}}
prev_steal_targets={}
target_counts={}
cooldowns={"roulette":10.0, "howgay":10.0, "which":10.0, "rps":5.0, "8ball":5.0, "clear":5.0, "trivia":25.0, "slots":10.0, "steal":30.0, 'bet':30.0, 'quote':45.0, "heist":300.0}
last_executed={cooldown:0 for cooldown in cooldowns}
starboard_emoji='<:spuperman:670852114070634527>'
starboard_count=4
zenny='<:zenny:1104179194780450906>'

# bot helper functions
# create_list, check_starboard, add_to_starboard, add_coins, subtract_coins, add_item, subtract_item, dep, wd, direct_to_bank, stolen_funds, in_wom_shenanigans, assert_cooldown
def create_list(filename):
    global file_checks
    global lists
    file_checks[filename]=False
    if not os.path.exists(f'{filename}.csv'):
        with open(f'{filename}.csv', 'w'):
            pass # creates csv file
    with open(f'{filename}.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        if len(rows)==0:
            file_checks[filename]=True
        else:
            lists[filename]={}
            for row in rows:
                dict = list(row.values())
                lists[filename][dict[0]]=dict[1]

async def check_starboard(message):
    if message.reactions:
        for reaction in message.reactions:
            if str(reaction.emoji)==starboard_emoji and reaction.count>=starboard_count:
                return True
    return False

async def add_to_starboard(message):
    channel = discord.utils.get(message.guild.channels, name='hot-seat')
    embed = discord.Embed(color=discord.Color.gold(), description=f'[Original Message]({message.jump_url})') # creates embed
    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
    embed.set_thumbnail(url=message.author.avatar.url)
    embed.add_field(name='Channel', value=f'<#{message.channel.id}>', inline=True)
    embed.add_field(name='Message', value=f'{str(message.content)}', inline=True)
    if message.attachments:
        embed.set_image(url=message.attachments[0].url)
    for reaction in message.reactions:
        if str(reaction.emoji) == starboard_emoji:
            star_reaction = reaction
            embed.set_footer(text=f'{star_reaction.count} ⭐')
            break
    async for star_msg in channel.history(): # edits embed in case of added reaction
        if star_msg.embeds and star_msg.embeds[0].description == f'[Original Message]({message.jump_url})':
            embed = star_msg.embeds[0]
            for reaction in message.reactions:
                if str(reaction.emoji) == starboard_emoji:
                    star_reaction = reaction
                    embed.set_footer(text=f'{star_reaction.count} ⭐')
                    break
            return await star_msg.edit(embed=embed)
    return await channel.send(embed=embed)

def add_coins(userID: int, coins: int):
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('coins.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                row = {'user_id': row['user_id'], 'coins': int(row['coins']) + coins}
                found = True
            rows.append(row)
    if not found:
        rows.append({'user_id': str(userID), 'coins': coins})
    with open('coins.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("coins")

def subtract_coins(userID: int, coins: int) -> bool:
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('coins.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                balance = int(row['coins'])
                if balance >= coins:
                    row = {'user_id': row['user_id'], 'coins': balance - coins}
                    found = True
                else:
                    return False
            rows.append(row)
    if not found:
        return False
    with open('coins.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("coins")
    return True

def add_item(itemName:str, userID:int, quantity:int):
    fieldnames = ['user_id', f'{itemName}s']
    found = False
    rows = []
    with open(f'{itemName}.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                row = {'user_id': str(userID), f'{itemName}s': int(row[f'{itemName}s']) + quantity}
                found = True
            rows.append(row)
    if not found:
        rows.append({'user_id': str(userID), f'{itemName}s': quantity})
    with open(f'{itemName}.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list(itemName)

def subtract_item(itemName:str, userID:int, quantity:int) -> bool:
    fieldnames = ['user_id', f'{itemName}s']
    found = False
    rows = []
    with open(f'{itemName}.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                balance = int(row[f'{itemName}s'])
                if balance >= quantity:
                    row = {'user_id': row['user_id'], f'{itemName}s': balance - quantity}
                    found = True
                else:
                    return False
            rows.append(row)
    if not found:
        return False
    with open(f'{itemName}.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list(itemName)
    return True

def dep(userID: int, coins: int) -> bool:
    if subtract_coins(userID, coins):
        fieldnames = ['user_id', 'coins']
        found = False
        rows = []
        with open('bank.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == str(userID):
                    row = {'user_id': row['user_id'], 'coins': int(row['coins']) + coins}
                    found = True
                rows.append(row)
        if not found:
            rows.append({'user_id': str(userID), 'coins': coins})
        with open('bank.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        create_list("bank")
        return True
    return False

def wd(userID: int, coins: int) -> bool:
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('bank.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                if int(row['coins']) >= coins:
                    row = {'user_id': row['user_id'], 'coins': int(row['coins']) - coins}
                    found = True
                else:
                    return False
            rows.append(row)
    if not found:
        return False
    with open('bank.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("bank")
    add_coins(userID, coins)
    return True

def direct_to_bank(userID: int, coins: int):
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('bank.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                row = {'user_id': row['user_id'], 'coins': int(row['coins']) + coins}
                found = True
            rows.append(row)
    if not found:
        rows.append({'user_id': str(userID), 'coins': coins})
    with open('bank.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("bank")

def stolen_funds(userID: int, coins: int) -> bool:
    fieldnames = ['user_id', 'coins']
    found = False
    rows = []
    with open('bank.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == str(userID):
                balance = int(row['coins'])
                if balance >= coins:
                    row = {'user_id': row['user_id'], 'coins': balance - coins}
                    found = True
                else:
                    return False
            rows.append(row)
    if not found:
        return False
    with open('bank.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    create_list("bank")
    return True

async def in_wom_shenanigans(ctx):
    wom_shenanigans = discord.utils.get(ctx.guild.channels, name='wom-shenanigans')
    if wom_shenanigans is None:
        await ctx.message.add_reaction('🦈')
        await ctx.reply("ask for or make a wom-shenanigans channel first, stupid", mention_author=False)
        return False
    if not ctx.message.channel.id == wom_shenanigans.id:
        await ctx.message.add_reaction('🦈')
        await ctx.reply(f"go to <#{wom_shenanigans.id}>, jackass", mention_author=False)
        return False
    return True

def assert_cooldown(command):
    global last_executed
    if last_executed[command] + cooldowns[command] < time.time():
        last_executed[command] = time.time()
        return 0
    return round(last_executed[command] + cooldowns[command] - time.time())
