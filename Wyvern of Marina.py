# all imports
import discord
import os
import csv
from dotenv import load_dotenv
from discord.ext import commands
from keep_alive import keep_alive
import random
import pandas as pd
import asyncio
import time
import datetime

# instantiation starts here
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '!w ', intents=intents)

say=print
command_list={}
empty_file=False
snipe_message_content={}
snipe_message_author={}
snipe_message_id={}
snipe_message_attachment={}
editsnipe_message_content={}
editsnipe_message_author={}
editsnipe_message_id={}
cooldown_amount=10.0
last_executed=time.time()
cooldown_trigger_count=0

def assert_cooldown():
    global last_executed
    if last_executed + cooldown_amount < time.time():
        last_executed = time.time()
        return False
    return True

if not os.path.exists('commands.csv'):
    with open('commands.csv', 'w') as creating_new_csv_file: 
        pass
with open('commands.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    rows = list(csv_reader)
    if len(rows)==0:
        empty_file=True
    else:
        command_list = {}
        for row in rows:
            dict = list(row.values())
            command_list[dict[0]]=dict[1]
            
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}\nID: {bot.user.id}')

# bot commands start here
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round (bot.latency * 1000)}ms')
    await ctx.message.delete()

@bot.command()
async def say(ctx, *args):
    response = ''
    for arg in args:
        response = response + ' ' + arg
    await ctx.channel.send(response)
    await ctx.message.delete()
    
@bot.command()
async def createcommand(ctx, *args):
    if len(args) < 2:
        return await ctx.reply('Wups! Incorrect number of arguments! You need two arguments to create a new command...', mention_author = False)
    elif not ctx.author.guild_permissions.manage_messages:
        return await ctx.reply("Wups! You do not have the required permissions...", mention_author=False)
    else:
        array = [arg for arg in args]
        name = array[0]
        array.remove(array[0])
        output = array[0]
        array.remove(array[0])
        for arg in array:
            output = output + ' ' + arg
        with open('commands.csv', 'a', newline='') as csvfile:
            fieldnames = ['command_name', 'command_output']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if empty_file:
                writer.writeheader()
            if name in list(command_list.keys()):
                return await ctx.reply('Wups, this command already exists...', mention_author=False)
            else:
                writer.writerow({'command_name': name, 'command_output': output})
                return await ctx.reply(f"The command {name} has been created!", mention_author=False)
                command_list[name] = output
                
@bot.command()
async def deletecommand(ctx, *args):
    global command_list
  
    if len(args) != 1:
        return await ctx.reply('Wups! Incorrect number of arguments! You need one argument to delete a command...', mention_author=False)
    elif not ctx.author.guild_permissions.manage_messages:
        return await ctx.reply('Wups, you do not have the required permissions...', mention_author=False)
    else:
        array = [arg for arg in args]
        name = array[0]
        if not name in list(command_list.keys()):
            return await ctx.reply('Wups! This command does not exist...', mention_author=False)
        elif len(list(command_list.keys())) == 0:
            return await ctx.reply('Wups! There are no commands to delete in the first place...', mention_author=False)
        else:
            commands = pd.read_csv('commands.csv')
            commands = commands[commands.command_name != name]
            commands.to_csv('commands.csv', index=False)
            with open('commands.csv', mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                rows = list(csv_reader)
                command_list = {}
                for row in rows:
                    dict = list(row.values())
                    command_list[dict[0]]=dict[1]
            return await ctx.reply(f'The command {name} has been deleted!', mention_author=False)
            
@bot.command()
async def customcommands(ctx):
    commandList = list(command_list.keys())
    commands = ', '.join(commandList) 
    if commands == '':
        return await ctx.reply('Wups! There are no custom commands...', mention_author=False)
    else:
        return await ctx.reply(commands, mention_author=False)

@bot.command()
async def snipe(ctx):
    channel = ctx.channel
    try:
        if len(snipe_message_attachment) != 0:
            if 'video' in snipe_message_attachment[channel.id].content_type:
                video = snipe_message_attachment[channel.id]
                snipe_message_content[channel.id] += f"\n[Attached Video]({video.url})"
        embed = discord.Embed(title=f"Last deleted message in <#{channel.name}>", color = discord.Color.purple(), description=snipe_message_content[channel.id])
        if len(snipe_message_attachment) != 0:
            if 'image' in snipe_message_attachment[channel.id].content_type:
                embed.set_image(url=snipe_message_attachment[channel.id].url)
        embed.set_footer(text=f"This message was sent by {snipe_message_author[channel.id]}")
        embed.set_thumbnail(url=snipe_message_author[channel.id].avatar.url)
        return await ctx.reply(embed=embed, mention_author=False)
    except KeyError:
        return await ctx.reply(f"Wups! There are no recently deleted messages in <#{channel.id}>...", mention_author=False)

@bot.command()
async def editsnipe(ctx):
    channel = ctx.channel
    try:
        embed = discord.Embed(title=f"Last edited message in <#{channel.name}>", color = discord.Color.purple(), description=editsnipe_message_content[channel.id])
        embed.set_footer(text=f"This message was sent by {editsnipe_message_author[channel.id]}")
        embed.set_thumbnail(url=editsnipe_message_author[channel.id].avatar.url)
        return await ctx.reply(embed=embed, mention_author=False)
    except KeyError:
        return await ctx.reply(f"Wups! There are no recently edited messages in <#{channel.id}>...", mention_author=False)

@bot.command()
async def choose(ctx, *args):
    if (len(args) < 2):
        return await ctx.reply("Wups! You need at least 2 arguments for me to choose from...", mention_author=False)
    options = [arg for arg in args]
    choose = random.randint(0, len(options) - 1)
    return await ctx.reply(f"I choose {options[choose]}!", mention_author=False)

@bot.command()
async def roulette(ctx, member:discord.Member=None):
    if member == None: # if a member wants to roulette themselves
        member = ctx.message.author
        if not member.guild_permissions.administrator:
            gunshot = random.randint(1,6)
            if gunshot == 1:
                await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                return await ctx.reply("🔥🔫 You died! (muted for 1 hour)", mention_author=False)
            else:
                return await ctx.reply("🚬🔫 Looks like you\'re safe, for now...", mention_author=False)
        else:
            return await ctx.reply("❌🔫 Looks like you\'re safe, you filthy admin...", mention_author=False)

    else: # if an admin wants to roulette a member they specify
        if not ctx.message.author.guild_permissions.administrator:
            if member == ctx.message.author:
                gunshot = random.randint(1,6)
                if gunshot == 1:
                    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                    return await ctx.reply("🔥🔫 You died! (muted for 1 hour)", mention_author=False)
                else:
                    return await ctx.reply("🚬🔫 Looks like you\'re safe, for now...", mention_author=False)
            return await ctx.reply("❌🔫 Wups! A lowlife like you can\'t possibly fire the gun at someone else...", mention_author=False)
        elif member == ctx.message.author:
            return await ctx.reply("❌🔫 Wups! Admins are valued. Don\'t roulette an admin like yourself...", mention_author=False)
        elif member.timed_out_until != None:
            return await ctx.reply("❌🔫 Wups! Don\'t you think it\'d be overkill to shoot a dead body?", mention_author=False)
        else:
            if not member.guild_permissions.administrator:
                gunshot = random.randint(1,6)
                if gunshot == 1:
                    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1))
                    return await ctx.reply("🔥🔫 This user died! (muted for 1 hour)", mention_author=False)
                else:
                    return await ctx.reply("🚬🔫 Looks like they\'re safe, for now...", mention_author=False)
            else:
                return await ctx.reply("❌🔫 Looks like they\'re safe, that filthy admin...", mention_author=False)
      
@bot.command()
async def howgay(ctx, member:discord.Member=None):
    if member == None:
        member = ctx.message.author
    percent = random.randint(0,100)
    responses = ['You\'re not into that mentally ill crap.',
                 'You\'re probably just going through a phase...',
                 'It\'s ok to be gay, buddy. We\'ll support you... unless you make it your entire personality.',
                 'You **LOVE** it up the rear end, don\'t you?']
    if percent >= 0 and percent <= 25:
        response = responses[0]
    elif percent >= 26 and percent <= 50:
        response = responses[1]
    elif percent >= 51 and percent <= 75:
        response = responses[2]
    elif percent >= 76 and percent <= 100:
        response = responses[3]

    return await ctx.reply(f"{member.name} is {percent}% gay. {response}",mention_author=False)
        
@bot.command()
async def who(ctx):
    message = ctx.message
    content = message.content[3:]
    members = [member for member in message.guild.members if not member.bot]
    memberNum = random.randint(0, len(members) - 1)
    return await ctx.reply(f"`{content}`? {members[memberNum].name}", mention_author=False)

@bot.command()
async def kick(ctx, member:discord.Member):
    author = ctx.message.author
    admin = author.guild_permissions.administrator
    channel = author.guild.system_channel
  
    if not admin:
        return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
    if member.guild_permissions.administrator:
        return await ctx.reply("Wups! Administrators can\'t be kicked...", mention_author=False)
      
    await member.kick()
    await ctx.message.delete()
    return await channel.send(f"{member.name} has been kicked! Hope you learn from your mistake... <:do_not:1077435360537223238>")

@bot.command()
async def ban(ctx, member:discord.Member):
    author = ctx.message.author
    admin = author.guild_permissions.administrator
  
    if not admin:
        return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
    if member.guild_permissions.administrator:
        return await ctx.reply("Wups! Administrators can\'t be banned...", mention_author=False)

    await member.ban()
    return await ctx.message.delete()

@bot.command()
async def mute(ctx, member:discord.Member, timelimit):
    valid = False
    author = ctx.message.author
    admin = author.guild_permissions.administrator
    timelimit = timelimit.lower()
    timeamount = timelimit[-1]
    timepossibilities = ['s', 'm', 'h', 'd', 'w']
    if timeamount in timepossibilities:
        valid = True
    current_time = discord.utils.utcnow()
  
    if not admin:
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

@bot.command()
async def unmute(ctx, member:discord.Member):
    author = ctx.message.author
    admin = author.guild_permissions.administrator

    if not admin:
        return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
    if member.guild_permissions.administrator:
        return await ctx.reply("Wups! Administrators can\'t be muted in the first place...", mention_author=False)
    if member.timed_out_until == None:
        return await ctx.reply("Wups! User is not muted in the first place...", mention_author=False)

    await member.edit(timed_out_until=None)
    return await ctx.message.delete()

@bot.command()
async def help(ctx, page:int=0):
    embed = discord.Embed(title='Commands available', color = discord.Color.purple())
    pages = 3
    if page < 0 or page > pages:
        return await ctx.reply('Wups! Invalid page number...', mention_author=False)
      
    if page == 0:
        embed.title='Need help?'
        embed.add_field(name='!w help 1', value = 'All the fun commands for everyone to enjoy!', inline=False)
        embed.add_field(name='!w help 2', value = 'All the administrative commands.', inline=False)
        embed.add_field(name='!w help 3', value = 'All the miscellaneous commands.', inline=False)
      
    elif page == 1:
        embed.add_field(name='!w say', value='Type something after the command for me to repeat it.', inline=False)
        embed.add_field(name='!w customcommands', value="Displays a list of the server's custom commands.", inline=False)
        embed.add_field(name='!w snipe', value='Snipes the last deleted message in that channel. Only the first media attachment will be sniped from the message. Keep in mind, you only have 60 seconds to snipe the deleted message!', inline=False)
        embed.add_field(name='!w editsnipe', value='Acts just like !w snipe, only for messages that were edited instead of deleted.', inline=False)
        embed.add_field(name='!w choose (any number of options, separated by a space)', value='Chooses a random option from all the options that you give me.', inline=False)
        embed.add_field(name='!w who (remainder of question)', value='I\'ll tell you the name of a random member who fits this description.', inline=False)
        embed.add_field(name='!w howgay ([Optional] @member)', value='I\'ll tell you either how gay you are or how gay the user you mention is.', inline=False)
        embed.add_field(name='!w roulette ([Admin Only] @member)', value='Try your luck... 😈', inline=False)
      
    elif page == 2:
        embed.add_field(name='!w createcommand (name) (output)', value='Create your own commands that make me send custom text or links.', inline=False)
        embed.add_field(name='!w deletecommand (name)', value='Delete commands that have already been created.', inline=False)
        embed.add_field(name='!w kick (@member)', value='Kicks the mentioned member from the server.', inline=False)
        embed.add_field(name='!w ban (@member)', value='Bans the mentioned member from the server.', inline=False)
        embed.add_field(name='!w mute (@member) (time amount)(s, m, h, d, or w)', value='Mutes the mentioned member for the given time amount. \"s\" for seconds, \"m\" for minutes, \"h\" for hours, \"d\" for days, and \"w\" for weeks. No space in between the time amount and the letter!', inline=False)
        embed.add_field(name='!w unmute (@member)', value='Unmutes the mentioned member.', inline=False)
      
    elif page == 3:
        embed.add_field(name='!w ping', value='Returns my response time in milliseconds.', inline=False)
    
    embed.set_footer(text=f'Viewing page {page}/{pages}')
    return await ctx.reply(embed=embed, mention_author=False)

# bot events start here
@bot.event
async def on_message(message):
    if message.content[0:3] == "!w " and message.content.split()[1] in list(command_list.keys()):
        await message.channel.send(command_list[message.content.split()[1]])
    else:   
        if message.content.lower() == "me":
            await message.channel.send('<:WoM:836128658828558336>')
        if message.content.lower() == "which":
            if message.author.id == bot.user.id:
                return
            if assert_cooldown():
                global cooldown_trigger_count
                cooldown_trigger_count += 1;
                if cooldown_trigger_count == 3:
                    await message.channel.send("Wups! Slow down there, bub! Command on cooldown...")
                    cooldown_trigger_count = 0
                return
            guild = message.guild
            members = [member.name.lower() for member in guild.members if not member.bot]
            memberNum = random.randint(0, len(members) - 1)
            cooldown_trigger_count = 0
            await message.channel.send(members[memberNum])

        if "yoshi" in message.content.lower().split(" "):
            await message.add_reaction('<:full:1028536660918550568>')
        if "3ds" in message.content.lower().split(" "):
            await message.add_reaction('<:megalon:1078914494132129802>')
        if "yuri" in message.content.lower().split(" "):
            await message.add_reaction('<:vers:804766992644702238>')
        if "verstie" in message.content.lower().split(" "):
            await message.add_reaction('🏳️‍⚧️')
            
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if not ctx.message.content.split()[1] in list(command_list.keys()):
        return await ctx.reply(f'Wups! try "!w help"... ({error})', mention_author=False)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    global snipe_message_content
    global snipe_message_author
    global snipe_message_id
    global snipe_message_attachment
    channel = message.channel.id

    snipe_message_author[channel] = message.author
    snipe_message_content[channel] = message.content
    if message.attachments:
        attachment = message.attachments[0]
        snipe_message_attachment[channel] = attachment
    snipe_message_id[channel] = message.id
  
    await asyncio.sleep(60)
    if message.id == snipe_message_id[channel]:
        del snipe_message_author[channel]
        del snipe_message_content[channel]
        if len(snipe_message_attachment) != 0:
            del snipe_message_attachment[channel]
        del snipe_message_id[channel]

@bot.event
async def on_message_edit(message_before, message_after):
    if message_before.author.bot:
        return
  
    global editsnipe_message_content
    global editsnipe_message_author
    global editsnipe_message_id
    channel = message_after.channel.id

    editsnipe_message_content[channel] = message_before.content
    editsnipe_message_author[channel] = message_before.author
    editsnipe_message_id[channel] = message_before.id

    await asyncio.sleep(60)
    if message_before.id == editsnipe_message_id[channel]:
        del editsnipe_message_content[channel]
        del editsnipe_message_author[channel]
        del editsnipe_message_id[channel]

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if not member.bot:
        return await channel.send(f"Welcome, {member.mention}, to **The Marina**! This is your one-way ticket to Hell. There\'s no going back from here...\nFor a grasp of the rules, however (yes, we have those), we do ask that you check <#822341695411847249>.\n*Remember to take breaks, nya?*")

@bot.event
async def on_member_update(before, after):
    channel = before.guild.system_channel
    if before.is_timed_out() == False:
        if after.is_timed_out() == True:
            return await channel.send(f"That fucking bozo {after.mention} got timed out! Point and laugh at this user! <:you:765067257008881715>")

@bot.event
async def on_member_ban(guild, user):
    channel = guild.system_channel
    return await channel.send(f"{user.name} has been banned! Rest in fucking piss, bozo. <:kysNOW:896223569288241175>")
    
# set up to start the bot
keep_alive()
bot.run(TOKEN)
