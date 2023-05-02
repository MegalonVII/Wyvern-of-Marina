# all imports
import discord
import os
import csv
from discord.ext import commands
from keep_alive import keep_alive
import random
import pandas as pd
import asyncio
import time
import datetime
import requests
import json
import urllib.parse

# bot instantiation
TOKEN=os.getenv('DISCORD_TOKEN')
files=["commands", "flairs", "coins"]
file_checks={file:False for file in files}
lists={file:{} for file in files}
snipe_data={"content":{}, "author":{}, "id":{}, "attachment":{}}
editsnipe_data={"content":{}, "author":{}, "id":{}}
cooldowns={"roulette":10.0, "howgay":10.0, "which":10.0, "rps":5.0, "8ball":5.0, "clear":5.0, "trivia":30.0, "slots":10.0}
last_executed={cooldown:time.time() for cooldown in cooldowns}
starboard_emoji='<:spuperman:670852114070634527>'
bot=commands.Bot(command_prefix = '!w ', intents=discord.Intents.all())
bot.remove_command('help')

# bot helper functions
def create_list(filename):
    global file_checks
    global lists
    file_checks[filename]=False
    if not os.path.exists(f'{filename}.csv'):
        with open(f'{filename}.csv'):
            pass
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

def assert_cooldown(command):
    global last_executed
    if last_executed[command] + cooldowns[command] < time.time():
        last_executed[command] = time.time()
        return 0
    return round(last_executed[command] + cooldowns[command] - time.time())

async def check_starboard(message):
    if message.reactions:
        for reaction in message.reactions:
            if str(reaction.emoji)==starboard_emoji and reaction.count>=4:
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


# bot help command redifined
# functions are created in order of placement in this list for ease of user reading
@bot.command(name='help')
async def help(ctx, page:int=0):
    embed = discord.Embed(color = discord.Color.purple())
    if page < 0 or page > 4:
        return await ctx.reply('Wups! Invalid page number...', mention_author=False)
      
    if page == 0:
        embed.title='Need help?'
        embed.add_field(name='!w help 1', value = 'All the fun commands for everyone to enjoy!', inline=False)
        embed.add_field(name='!w help 2', value = 'All the administrative commands.', inline=False)
        embed.add_field(name='!w help 3', value = 'All the flair commands.', inline=False)
        embed.add_field(name='!w help 4', value = 'All the miscellaneous commands.', inline=False)  
      
    elif page == 1:
        embed.title='Fun Commands'
        embed.add_field(name='!w say', value='Type something after the command for me to repeat it.', inline=False)
        embed.add_field(name='!w customcommands', value="Displays a list of the server's custom commands.", inline=False)
        embed.add_field(name='!w snipe', value='Snipes the last deleted message in that channel. Only the first media attachment will be sniped from the message. Keep in mind, you only have 60 seconds to snipe the deleted message!', inline=False)  
        embed.add_field(name='!w editsnipe', value='Acts just like !w snipe, only for messages that were edited instead of deleted.', inline=False)
        embed.add_field(name='!w choose (any number of options, separated by a space)', value='Chooses a random option from all the options that you give me.', inline=False)
        embed.add_field(name='!w who (remainder of question)', value='I\'ll tell you the name of a random member who fits this description.', inline=False)
        embed.add_field(name='!w howgay ([Optional] @member)', value='I\'ll tell you either how gay you are or how gay the user you mention is.', inline=False)
        embed.add_field(name='!w rps (your choice)', value='Play a simple game of Rock-Paper-Scissors with me!', inline=False)
        embed.add_field(name='!w 8ball (question)', value='I\'ll give you the magic response to your yes or no question!', inline=False)
        embed.add_field(name='!w roulette ([Admin Only] @member)', value='Try your luck... 😈', inline=False)
        embed.add_field(name='!w trivia', value='I\'ll give you a multiple-choice trivia question on either general knowledge or some form of entertainment media. You have 15 seconds to answer with the correct letter option!', inline=False)
        embed.add_field(name='!w slots', value='Win some Zenny! 🤑', inline=False)
        embed.add_field(name='!w balance', value='I\'ll tell you how much Zenny you have.', inline=False)
        embed.add_field(name='!w leaderboard', value='Displays the top 5 richest members in the server.', inline=False)
      
    elif page == 2:
        embed.title='Administrative Commands'
        embed.add_field(name='!w createcommand (name) (output)', value='Create your own commands that make me send custom text or links.', inline=False)
        embed.add_field(name='!w deletecommand (name)', value='Delete commands that have already been created.', inline=False)
        embed.add_field(name='!w clear (number of messages)', value='Deletes the last number you specify of messages from the specific chat. To avoid rate limits, please enter a number between 1 and 10.', inline=False)
        embed.add_field(name='!w kick (@member)', value='Kicks the mentioned member from the server.', inline=False)
        embed.add_field(name='!w ban (@member)', value='Bans the mentioned member from the server.', inline=False)
        embed.add_field(name='!w mute (@member) (time amount)(s, m, h, d, or w)', value='Mutes the mentioned member for the given time amount. \"s\" for seconds, \"m\" for minutes, \"h\" for hours, \"d\" for days, and \"w\" for weeks. No space in between the time amount and the letter!', inline=False)
        embed.add_field(name='!w unmute (@member)', value='Unmutes the mentioned member.', inline=False)
        embed.add_field(name='!w addflair (@role)', value='Adds this role as a flair to this server.', inline=False)
        embed.add_field(name='!w deleteflair (@role)', value='Removes this role as a flair from this server.', inline=False)
      
    elif page == 3:
        embed.title='Flair Commands'
        embed.add_field(name='!w listflairs', value='Lists all the flairs for this server.', inline=False)
        embed.add_field(name='!w im (role name)', value='Gives or removes the flair you ask for.', inline=False)
      
    elif page == 4:
        embed.title='Miscellaneous Commands'
        embed.add_field(name='!w ping', value='Returns my response time in milliseconds.', inline=False)
        embed.add_field(name='!w whomuted', value='Returns the name of every member who is currently muted.', inline=False)
        embed.add_field(name='!w avatar ([Optional] @member)', value='I\'ll send you the avatar of the given user. Defaults to yourself.', inline=False) 
      
    if page > 0:
        embed.set_footer(text=f'Viewing page {page}/4')
    return await ctx.reply(embed=embed, mention_author=False)


# fun commands start here
# say, custc, snipe, esnipe, choose, who, howgay, rps, 8ball, roulette, trivia, slots, balance, leaderboard
@bot.command(name='say')
async def say(ctx, *args):
    try:
        await ctx.message.delete()
        return await ctx.channel.send(" ".join(args).replace('"', '\"').replace("'", "\'"), allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
    except:
        return await ctx.reply("Wups! You need something for me to say...", mention_author=False)
            
@bot.command(name='customcommands', aliases=['custc'])
async def customcommands(ctx):
    try:
        return await ctx.reply(', '.join(list(lists["commands"].keys())), mention_author=False)
    except:
        return await ctx.reply('Wups! There are no custom commands...', mention_author=False)

@bot.command(name='snipe')
async def snipe(ctx):
    channel = ctx.channel
    try:
        data = snipe_data[channel.id]
        if data["attachment"] and 'video' in data["attachment"].content_type:
            data["content"] += f"\n[Attached Video]({data['attachment'].url})"
        embed = discord.Embed(title=f"Last deleted message in #{channel.name}", color = discord.Color.purple(), description=data["content"])
        if data["attachment"] and 'image' in data["attachment"].content_type:
            embed.set_image(url=data["attachment"].url)
        embed.set_footer(text=f"This message was sent by {data['author']}")
        embed.set_thumbnail(url=data['author'].avatar.url)
        return await ctx.reply(embed=embed, mention_author=False)
    except KeyError:
        return await ctx.reply(f"Wups! There are no recently deleted messages in <#{channel.id}>...", mention_author=False)

@bot.command(name='editsnipe', aliases=['esnipe'])
async def editsnipe(ctx):
    channel = ctx.channel
    try:
        data = editsnipe_data[channel.id]
        embed = discord.Embed(title=f"Last edited message in #{channel.name}", color = discord.Color.purple(), description=data["content"])
        embed.set_footer(text=f"This message was sent by {data['author']}")
        embed.set_thumbnail(url=data["author"].avatar.url)
        return await ctx.reply(embed=embed, mention_author=False)
    except KeyError:
        return await ctx.reply(f"Wups! There are no recently edited messages in <#{channel.id}>...", mention_author=False)

@bot.command(name='choose')
async def choose(ctx, *args):
    if (len(args) < 2):
        return await ctx.reply("Wups! You need at least 2 arguments for me to choose from...", mention_author=False)
    return await ctx.reply(f"I choose `{random.choice(args)}`!", mention_author=False)

@bot.command(name='who')
async def who(ctx):
    return await ctx.reply(f"`{ctx.message.content[3:]}`? {random.choice([member.name for member in ctx.message.guild.members if not member.bot])}", mention_author=False)
      
@bot.command(name='howgay')
async def howgay(ctx, member:discord.Member=None):
    if assert_cooldown("howgay") != 0:
        await ctx.message.add_reaction('🦈')
        return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('howgay')} seconds...", mention_author=False)
      
    member = member or ctx.author
    percent = random.randint(0,100)
    responses = ['You\'re not into that mentally ill crap.', 'You\'re probably just going through a phase...', 'It\'s ok to be gay, buddy. We\'ll support you... unless you make it your entire personality.', 'You **LOVE** it up the rear end, don\'t you?']
    if percent >= 0 and percent <= 25:
        response = responses[0]
    elif percent >= 26 and percent <= 50:
        response = responses[1]
    elif percent >= 51 and percent <= 75:
        response = responses[2]
    elif percent >= 76 and percent <= 100:
        response = responses[3]
      
    return await ctx.reply(f"{member.name} is {percent}% gay. {response}",mention_author=False)

@bot.command(name='rps')
async def rps(ctx, playerChoice: str=None):
    if assert_cooldown("rps") != 0 :
        await ctx.message.add_reaction('🦈')
        return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('rps')} seconds...", mention_author=False)
    if playerChoice is None:
        return await ctx.reply("Wups! You need to give me your choice...", mention_author=False)
      
    playerChoice = playerChoice.lower()
    choices = ['rock', 'paper', 'scissors']
    if playerChoice not in choices:
        return await ctx.reply("Wups! Invalid choice...", mention_author=False)
    else:
        botChoice = random.choice(choices)
        if playerChoice == botChoice: # tie
            return await ctx.reply(f"I chose `{botChoice}`.\nUgh! Boring! We tied...", mention_author=False)
        elif (playerChoice == choices[0] and botChoice == choices[1]) or \
            (playerChoice == choices[1] and botChoice == choices[2]) or \
            (playerChoice == choices[2] and botChoice == choices[0]): # win
                return await ctx.reply(f"I chose `{botChoice}`.\nHah! I win, sucker! Why'd you pick that one, stupid?", mention_author=False)
        else: # lose
            return await ctx.reply(f"I chose `{botChoice}`.\nWell played there. You have bested me...", mention_author=False)

@bot.command(name='8ball')
async def eightball(ctx):
    if assert_cooldown("8ball") != 0 :
        await ctx.message.add_reaction('🦈')
        return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('8ball')} seconds...", mention_author=False)
    if len(ctx.message.content) < 9:
        return await ctx.reply("Wups! You need to give me a question to respond to...", mention_author=False)
      
    responses = ['Hell yeah!', 'It is certain.', 'Without a doubt.', 'You may rely on it.', 'Yes, definitely.', 'It is decidedly so.', 'As I see it, yes.', 'Most likely.', 'Yes.', 'Outlook good.', 'Signs point to yes.', 'You already know the answer.', 'Reply hazy, try again.', 'Better not tell you now.', 'Ask again later.', 'Cannot predict now.', 'Concentrate and ask again.', 'Don\'t count on it.', 'Outlook not so good.', 'My sources say no.', 'Very doubtful.', 'My reply is no.', 'No.', 'Oh god, no.']
    return await ctx.reply(f"🎱 `{ctx.message.content[9:]}` 🎱\n{random.choice(responses)}", mention_author=False)

@bot.command(name='roulette')
async def roulette(ctx, member:discord.Member=None):
    if assert_cooldown("roulette") != 0:
        await ctx.message.add_reaction('🦈')
        return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('roulette')} seconds...", mention_author=False)
      
    member = member or ctx.author
    if member == ctx.author: # if a member wants to roulette themselves
        if not member.guild_permissions.administrator:
            if random.randint(1,6) == 1:
                await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                return await ctx.reply("🔥🔫 You died! (muted for 1 hour)", mention_author=False)
            return await ctx.reply("🚬🔫 Looks like you\'re safe, for now...", mention_author=False)
        return await ctx.reply("❌🔫 Looks like you\'re safe, you filthy admin...", mention_author=False)
      
    else: # if an admin wants to roulette a member they specify
        if not ctx.message.author.guild_permissions.administrator:
            if member == ctx.author:  # roulette themselves if not admin (pinged themself)
                if random.randint(1,6) == 1:
                    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                    return await ctx.reply("🔥🔫 You died! (muted for 1 hour)", mention_author=False)
                return await ctx.reply("🚬🔫 Looks like you\'re safe, for now...", mention_author=False)
            return await ctx.reply("❌🔫 A lowlife like you can\'t possibly fire the gun at someone else...", mention_author=False)
        elif member == ctx.author: # admin tries rouletting themself
            return await ctx.reply("❌🔫 Admins are valued. Don\'t roulette an admin like yourself...", mention_author=False)
        elif member.is_timed_out() == True: # admin tries rouletting a "dead" server member
            return await ctx.reply("❌🔫 Don\'t you think it\'d be overkill to shoot a dead body?", mention_author=False)
        else:
            if not member.guild_permissions.administrator: # admin tries rouletting "alive" non admin
                if random.randint(1,6) == 1:
                    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                    return await ctx.reply("🔥🔫 This user died! (muted for 1 hour)", mention_author=False)
                return await ctx.reply("🚬🔫 Looks like they\'re safe, for now...", mention_author=False)
            return await ctx.reply("❌🔫 Looks like they\'re safe, that filthy admin...", mention_author=False)

@bot.command(name='trivia')
async def trivia(ctx):
    if assert_cooldown('trivia') != 0:
        await ctx.message.add_reaction('🦈')
        return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('trivia')} seconds...", mention_author=False)
    
    async with ctx.typing():
        response = requests.get(f"https://opentdb.com/api.php?amount=1&category={random.choice([9, 11, 12, 14, 15, 31])}&type=multiple&encode=url3986")
        data = json.loads(response.text)
        correct_answer = urllib.parse.unquote(data['results'][0]['correct_answer'])
        incorrect_answers = data['results'][0]['incorrect_answers']
        options = [urllib.parse.unquote(answer) for answer in incorrect_answers] + [correct_answer]
        random.shuffle(options)
        quiz_embed = discord.Embed(title="❓ Trivia ❓", description=urllib.parse.unquote(data['results'][0]['question']), color=discord.Color.purple())
        quiz_embed.add_field(name="Options", value="\n".join(options), inline=False)
        quiz_embed.set_footer(text="You have 15 seconds to answer. Type the letter of your answer (A, B, C, D).")
        await ctx.reply(embed=quiz_embed, mention_author=False)

    def check_answer(message):
        return message.author == ctx.author and message.content.lower() in ['a', 'b', 'c', 'd']

    try:
        answer_message = await bot.wait_for('message', timeout=15.0, check=check_answer)
    except asyncio.TimeoutError:
        return await ctx.reply(f"Time's up! The correct answer was **{correct_answer}**.", mention_author=False)
    else:
        if answer_message.content.lower() == 'a':
            selected_answer = options[0]
        elif answer_message.content.lower() == 'b':
            selected_answer = options[1]
        elif answer_message.content.lower() == 'c':
            selected_answer = options[2]
        elif answer_message.content.lower() == 'd':
            selected_answer = options[3]

        if selected_answer == correct_answer:
            return await answer_message.reply(f"Correct! The answer is **{correct_answer}**.", mention_author=False)
        return await answer_message.reply(f"Sorry, that's incorrect. The correct answer is **{correct_answer}**.", mention_author=False)

@bot.command(name='slots')
async def slots(ctx):
    if assert_cooldown('slots') != 0:
        await ctx.message.add_reaction('🦈')
        return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('slots')} seconds...", mention_author=False)
      
    emojis = ["🍒", "🍇", "🍊", "🍋", "🍉","7️⃣"]
    reels = ["❓","❓","❓"]
    msg = await ctx.reply(f"{reels[0]} | {reels[1]} | {reels[2]}", mention_author=False)
    for i in range(0,3):
        await asyncio.sleep(1)
        reels[i] = random.choice(emojis)
        await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}", allowed_mentions=discord.AllowedMentions.none())
    if all(reel == "7️⃣" for reel in reels):
        add_coins(ctx.author.id,500)
        return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\n**Jackpot**! 500 Zenny!", allowed_mentions=discord.AllowedMentions.none())
    elif len(set(reels)) == 1 and reels[0] != "7️⃣":
        add_coins(ctx.author.id,100)
        return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nSmall prize! 100 Zenny!", allowed_mentions=discord.AllowedMentions.none())
    elif len(set(reels)) == 2:
        add_coins(ctx.author.id,25)
        return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nNice! 25 Zenny!", allowed_mentions=discord.AllowedMentions.none())
    return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nBetter luck next time...", allowed_mentions=discord.AllowedMentions.none())

@bot.command(name='balance', aliases=['bal'])
async def balance(ctx):
    for userID in lists['coins'].keys():
        if str(ctx.author.id) == userID:
            return await ctx.reply(f"You have {lists['coins'][str(ctx.author.id)]}z!", mention_author=False)
    return await ctx.reply("Wups! Get some bread, broke ass...", mention_author=False)

@bot.command(name='leaderboard', aliases=['lb'])
async def leaderboard(ctx):
    top_users = sorted(lists['coins'].items(), key=lambda x: x[1])[:5]
    embed = discord.Embed(title=f'Top {len(top_users)} Richest Users', color=discord.Color.purple())
    if len(top_users) == 1:
        embed.title='Richest User'
    elif len(top_users) == 0:
        return await ctx.reply('Wups! No one is in this economy...', mention_author=False)
    for i, (user_id, z) in enumerate(top_users):
        user = await bot.fetch_user(user_id)
        embed.add_field(name=f'#{i+1}: {user.name}', value=f'{z}z', inline=False)
        if i == 0:
            embed.set_thumbnail(url=user.avatar.url)
    return await ctx.reply(embed=embed, mention_author=False)

# administrative commands start here
# cc, dc, clear, kick, ban, mute, unmute, addf, delf
@bot.command(name='createcommand', aliases=['cc'])
async def createcommand(ctx, name, *output):
    try:
        if len(output) < 1:
            return await ctx.reply('Wups! You need to give me an output for your new command...', mention_author = False)
        elif not ctx.author.guild_permissions.manage_messages:
            return await ctx.reply("Wups! You do not have the required permissions...", mention_author=False)
        elif name in list(lists["commands"].keys()):
            return await ctx.reply('Wups, this command already exists...', mention_author=False)
          
        output = ' '.join(output).replace('"', '\"').replace("'", "\'")
        with open('commands.csv', 'a', newline='') as csvfile:
            fieldnames = ['command_name', 'command_output']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if file_checks["commands"]:
                writer.writeheader()
            writer.writerow({'command_name': name, 'command_output': output})
        create_list("commands")
        return await ctx.reply(f"The command {name} has been created!", mention_author=False)
    except:
        return await ctx.reply('Wups! I don\'t have a name for a command...', mention_author=False)
                
@bot.command(name='deletecommand', aliases=['dc'])
async def deletecommand(ctx, name):
    if not ctx.author.guild_permissions.manage_messages:
        return await ctx.reply('Wups, you do not have the required permissions...', mention_author=False)
    if not name in list(lists["commands"].keys()):
        return await ctx.reply('Wups! This command does not exist...', mention_author=False)
    if len(list(lists["commands"].keys())) == 0:
        return await ctx.reply('Wups! There are no commands to delete in the first place...', mention_author=False)

    commands = pd.read_csv('commands.csv')
    commands = commands[commands.command_name != name]
    commands.to_csv('commands.csv', index=False)
    create_list("commands")
    return await ctx.reply(f'The command {name} has been deleted!', mention_author=False)

@bot.command(name='clear')
async def clear(ctx, num:int=None):
    if not ctx.author.guild_permissions.manage_messages:
        return await ctx.reply('Wups! You do not have the required permissions...', mention_author=False)
    if num is None or num < 1 or num > 10:
        return await ctx.reply('Wups! Please enter a number between 1 and 10...', mention_author=False)
    if assert_cooldown("clear") != 0:
        await ctx.message.add_reaction('🦈')
        return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('clear')} seconds...", mention_author=False)

    await ctx.message.add_reaction('✅')
    return await ctx.message.channel.purge(limit=num+1)

@bot.command(name='kick')
async def kick(ctx, member:discord.Member):  
    if not ctx.author.guild_permissions.administrator:
        return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
    if member.guild_permissions.administrator and not member.bot:
        return await ctx.reply("Wups! Administrators can\'t be kicked...", mention_author=False)
      
    await member.kick()
    await ctx.message.delete()
    return await ctx.guild.system_channel.send(f"{member.name} has been kicked! Hope you learn from your mistake... <:do_not:1077435360537223238>")

@bot.command(name='ban')
async def ban(ctx, member:discord.Member):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
    if member.guild_permissions.administrator and not member.bot:
        return await ctx.reply("Wups! Administrators can\'t be banned...", mention_author=False)
      
    await member.ban()
    return await ctx.message.delete()

@bot.command(name='mute')
async def mute(ctx, member:discord.Member, timelimit):
    valid = False
    timelimit = timelimit.lower()
    timepossibilities = ['s', 'm', 'h', 'd', 'w']
    if timelimit[-1] in timepossibilities:
        valid = True
    current_time = discord.utils.utcnow()
  
    if not ctx.author.guild_permissions.administrator:
        return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
    if member.guild_permissions.administrator:
        return await ctx.reply("Wups! Administrators can\'t be muted...", mention_author=False)
    if not valid:
        return await ctx.reply("Wups! Invalid time amount...", mention_author=False)
      
    if 's' in timelimit:
        gettime = int(timelimit.strip('s'))
        if gettime > 2419200:
            return await ctx.reply("Wups! Cannot mute member for more than 4 weeks...", mention_author=False)
        newtime = datetime.timedelta(seconds=gettime)
    if 'm' in timelimit:
        gettime = int(timelimit.strip('m'))
        if gettime > 40320:
              return await ctx.reply("Wups! Cannot mute member for more than 4 weeks...", mention_author=False)
        newtime = datetime.timedelta(minutes=gettime)
    if 'h' in timelimit:
        gettime = int(timelimit.strip('h'))
        if gettime > 672:
              return await ctx.reply("Wups! Cannot mute member for more than 4 weeks...", mention_author=False)
        newtime = datetime.timedelta(hours=gettime)
    if 'd' in timelimit:
        gettime = int(timelimit.strip('d'))
        if gettime > 28:
              return await ctx.reply("Wups! Cannot mute member for more than 4 weeks...", mention_author=False)
        newtime = datetime.timedelta(days=gettime)
    if 'w' in timelimit:
        gettime = int(timelimit.strip('w'))
        if gettime > 4:
              return await ctx.reply("Wups! Cannot mute member for more than 4 weeks...", mention_author=False)
        newtime = datetime.timedelta(weeks=gettime)
      
    await member.edit(timed_out_until=current_time+newtime)
    return await ctx.message.delete()

@bot.command(name='unmute')
async def unmute(ctx, member:discord.Member):
    if not ctx.message.author.guild_permissions.administrator:
        return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
    if member.guild_permissions.administrator:
        return await ctx.reply("Wups! Administrators can\'t be muted in the first place...", mention_author=False)
    if not member.is_timed_out():
        return await ctx.reply("Wups! User is not muted in the first place...", mention_author=False)

    await member.edit(timed_out_until=None)
    return await ctx.message.delete()

@bot.command(name='addflair', aliases=['addf'])
async def addflair(ctx, role: discord.Role):
    try:
        if not ctx.author.guild_permissions.administrator:
            return await ctx.reply('Wups! Only administrators can use this command...', mention_author=False)
        if role.position >= ctx.me.top_role.position:
            return await ctx.reply("Wups! I can't add this role as a flair because it is above my highest role...", mention_author=False)
        if role.name in lists["flairs"].keys():
            return await ctx.reply(f"Wups! '{role.name}' is already a flair...", mention_author=False)
          
        with open('flairs.csv', 'a', newline='') as csvfile:
            fieldnames = ['role_name', 'role_id']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames) 
            if file_checks["flairs"]:
                writer.writeheader()
            writer.writerow({'role_name': role.name, 'role_id': role.id})
        create_list("flairs")
        await ctx.message.add_reaction('✅')
        await asyncio.sleep(3)
        return await ctx.message.delete()
    except:
        return await ctx.reply('Wups! Something went wrong. Try doing `!w addflair @Role`...', mention_author=False)

@bot.command(name='deleteflair', aliases=['delf'])
async def deleteflair(ctx, role:discord.Role):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.reply('Wups, you do not have the required permissions...', mention_author=False)
    if not role.name in list(lists["flairs"].keys()):
        return await ctx.reply('Wups! This role is not a flair...', mention_author=False)
    if len(list(lists["flairs"].keys())) == 0:
        return await ctx.reply('Wups! There are no flairs to delete in the first place...', mention_author=False)
      
    flairs = pd.read_csv('flairs.csv')
    flairs = flairs[flairs.role_name != role.name]
    flairs.to_csv('flairs.csv', index=False)
    create_list("flairs")
    await ctx.message.add_reaction('✅')
    await asyncio.sleep(3)
    return await ctx.message.delete()
  

# flair commands start here
# lf, im
@bot.command(name='listflairs', aliases=['lf'])
async def listflairs(ctx):
    try:
        await ctx.send('\n'.join(list(lists["flairs"].keys())))
        return await ctx.message.delete()
    except:
        return await ctx.reply('Wups! There are no self-assignable roles in this server...', mention_author=False)

@bot.command(name='im')
async def im(ctx, *roleName:str):
    roleName = ' '.join(roleName) # finds the role from the name given
    role = discord.utils.get(ctx.guild.roles, name=roleName)
    if role is None:
        return await ctx.reply("Wups! Invalid role...", mention_author=False)
    if role.name not in list(lists["flairs"].keys()): # checks if it is a flair
        return await ctx.reply("Wups! That is not a self-assignable role...", mention_author=False)
      
    hasRole = False # checks if the user already has the role
    for userRole in ctx.author.roles:
        if userRole.id == role.id:
            hasRole = True
            break
          
    if hasRole: # gives or removes role
        await ctx.author.remove_roles(role)
    else:
        await ctx.author.add_roles(role)
    await ctx.message.add_reaction('✅')
    await asyncio.sleep(3)
    return await ctx.message.delete()
  

# misc commands start here
# ping, whomuted, avi
@bot.command(name='ping')
async def ping(ctx):
    await ctx.message.delete()
    return await ctx.send(f'Pong! {round (bot.latency * 1000)}ms')

@bot.command(name='whomuted')
async def whomuted(ctx):
    try:
        return await ctx.reply(", ".join([member.name for member in ctx.guild.members if member.is_timed_out()]), mention_author=False)
    except:
        return await ctx.reply("Wups! No one is muted currently...", mention_author=False)

@bot.command(name='avatar', aliases=['avi'])
async def avatar(ctx, member:discord.Member=None):
    member = member or ctx.author
    e = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.purple())
    if member.display_avatar.url != member.avatar.url:
        e.set_thumbnail(url=member.avatar.url)
    e.set_image(url=member.display_avatar.url)
    e.set_footer(text=f"Requested by: {ctx.message.author.name}")
    return await ctx.reply(embed=e, mention_author=False)
  

# bot events start here
# on_ready, on_message, on_command_error, on_message_delete, on_message_edit, on_member_join, on_member_update, on_member_ban, on_reaction_add, on_member_remove
@bot.event
async def on_ready():
    for file in files:
        create_list(file)
    print(f'Logged in as: {bot.user.name}\nID: {bot.user.id}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
      
    if message.content[0:3] == "!w " and message.content.split()[1] in list(lists["commands"].keys()): # custom commands
        await message.channel.send(lists["commands"][message.content.split()[1]])
    else:   # any specific word triggers
        if message.content.lower() == "me":
            await message.channel.send('<:WoM:836128658828558336>')
        if message.content.lower() == "which":
            if assert_cooldown("which") != 0:
                await message.add_reaction('🦈')
            else:
                await message.channel.send(random.choice([member.name.lower() for member in message.guild.members if not member.bot]))

        # trigger reactions
        triggers = ['yoshi','3ds','yuri','yaoi','crank','kys','chan']
        trigger_emojis = ['<:full:1028536660918550568>','<:megalon:1078914494132129802>','<:vers:804766992644702238>','🐍','🔧','⚡','🦄']
        for trigger, emoji in zip(triggers, trigger_emojis):
            if trigger in message.content.lower().split(" "):
                await message.add_reaction(emoji)
          
    await bot.process_commands(message)
  
    if random.randint(1,4096) == 1:  
        if random.randint(1,2) == 1:
            try:
                return await message.author.send(f"Hey {message.author.name}. Hope this finds you well.\n\nJust wanted to say that I know that this server might make some jabs at you or do some things that might rub you the wrong way, but that aside I wanted to personally tell you that I value that you\'re here. I think you\'re amazing and you deserve only good things coming to you. Hope you only succeed from here!\nIf you\'re ever feeling down, I hope you can look back at this message just to cheer you up. Also, this message might come back to you again so maybe you\'ll need it again?\n\nOh well. Been nice talking to ya! <3")
            except:
                return await message.channel.send(f"Wups! I tried sending {message.author.mention} top secret classified government information, but for some reason I couldn\'t...")
        else:
            with open("shiny.png", "rb") as f:
                file = discord.File(f)
                return await message.channel.send(content="A wild Wyvern of Marina appeared! ✨", file=file)

@bot.event
async def on_command_error(ctx, error):
    if not ctx.message.content.split()[1] in list(lists["commands"].keys()):
        return await ctx.reply(f'Wups! try "!w help"... ({error})', mention_author=False)

@bot.event
async def on_message_delete(message):
    if not message.content[0:7] == '!w say ' or message.author.bot:
        global snipe_data
        channel = message.channel.id
        if message.author.bot:
            return
          
        snipe_data[channel]={"content":str(message.content), "author":message.author, "id":message.id, "attachment":message.attachments[0] if message.attachments else None}
      
        await asyncio.sleep(60)
        if message.id == snipe_data[channel]["id"]:
            del snipe_data[channel]

@bot.event
async def on_message_edit(message_before, message_after):
    global editsnipe_data
    channel = message_after.channel.id
    if message_before.author.bot:
        return
      
    editsnipe_data[channel]={"content":str(message_before.content), "author":message_before.author, "id":message_before.id}
  
    await asyncio.sleep(60)
    if message_before.id == editsnipe_data[channel]["id"]:
        del editsnipe_data[channel]

@bot.event
async def on_member_join(member):
    if not member.bot:
        return await member.guild.system_channel.send(f"Welcome, {member.mention}, to **The Marina**! This is your one-way ticket to Hell. There\'s no going back from here...\nFor a grasp of the rules, however (yes, we have those), we do ask that you check <#822341695411847249>.\n*Remember to take breaks, nya?*")

@bot.event
async def on_member_update(before, after):
    if after.is_timed_out() == True and before.is_timed_out() == False:
        return await before.guild.system_channel.send(f"That fucking bozo {after.mention} got timed out! Point and laugh at this user! <:you:765067257008881715>")
      
    if after.is_timed_out() == False and before.is_timed_out() == True:
        return await before.guild.system_channel.send(f"Welcome back, {after.mention}. Don\'t do that again, idiot. <:do_not:1077435360537223238>")

@bot.event
async def on_member_ban(guild, user):
    return await guild.system_channel.send(f"{user.name} has been banned! Rest in fucking piss, bozo. <:kysNOW:896223569288241175>")

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == user or user.bot:
        return
      
    if str(reaction.emoji) == starboard_emoji:
        if await check_starboard(reaction.message):
            return await add_to_starboard(reaction.message)

@bot.event
async def on_member_remove(member):
    coins = pd.read_csv('coins.csv')
    coins = coins[coins['user_id'] != member.id]
    coins.to_csv('coins.csv', index=False)
    create_list("coins")
          
    
# everything has finally been set up
# we can now run the bot
keep_alive()
bot.run(TOKEN)
