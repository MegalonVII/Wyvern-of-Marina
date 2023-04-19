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

# bot instantiation
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix = '!w ', intents=discord.Intents.all())
bot.remove_command('help')

# all global bot variables here
empty_file=False
command_list={}
snipe_data={"content":{}, "author":{}, "id":{}, "attachment":{}}
editsnipe_data={"content":{}, "author":{}, "id":()}
cooldowns={"roulette":10.0, "howgay":10.0, "which":10.0, "rps":10.0, "8ball":5.0}
last_executed={key:time.time() for key in cooldowns}

# defines how to create command list
def create_command_list():
    global command_list
    global empty_file
    if not os.path.exists('commands.csv'):
        with open('commands.csv', 'w'): 
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

# defines the cooldown method
def assert_cooldown(command):
    global last_executed
    if last_executed[command] + cooldowns[command] < time.time():
        last_executed[command] = time.time()
        return False
    return True

# bot commands start here
@bot.command(name='ping')
async def ping(ctx):
    await ctx.message.delete()
    return await ctx.send(f'Pong! {round (bot.latency * 1000)}ms')

@bot.command(name='say')
async def say(ctx, *args):
    arr = [arg for arg in args]
    response = " ".join(arr)
    await ctx.message.delete()
    return await ctx.channel.send(response, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
    
@bot.command(name='createcommand', aliases=['cc'])
async def createcommand(ctx, name, *output):
    if not output:
        return await ctx.reply('Wups! Incorrect number of arguments! You need two arguments to create a new command...', mention_author = False)
    elif not ctx.author.guild_permissions.manage_messages:
        return await ctx.reply("Wups! You do not have the required permissions...", mention_author=False)
    elif name in list(command_list.keys()):
        return await ctx.reply('Wups, this command already exists...', mention_author=False)
    else:
        output = ' '.join(output)
        with open('commands.csv', 'a', newline='') as csvfile:
            fieldnames = ['command_name', 'command_output']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if empty_file:
                writer.writeheader()
            writer.writerow({'command_name': name, 'command_output': output})
        command_list[name] = output
        return await ctx.reply(f"The command {name} has been created!", mention_author=False)
                
@bot.command(name='deletecommand', aliases=['dc'])
async def deletecommand(ctx, name):
    global command_list
  
    if not ctx.author.guild_permissions.manage_messages:
        return await ctx.reply('Wups, you do not have the required permissions...', mention_author=False)
    else:
        if not name in list(command_list.keys()):
            return await ctx.reply('Wups! This command does not exist...', mention_author=False)
        elif len(list(command_list.keys())) == 0:
            return await ctx.reply('Wups! There are no commands to delete in the first place...', mention_author=False)
        else:
            commands = pd.read_csv('commands.csv')
            commands = commands[commands.command_name != name]
            commands.to_csv('commands.csv', index=False)
            create_command_list()
            return await ctx.reply(f'The command {name} has been deleted!', mention_author=False)
            
@bot.command(name='customcommands', aliases=['custc'])
async def customcommands(ctx):
    commandList = list(command_list.keys())
    commands = ', '.join(commandList) 
    if commands == '':
        return await ctx.reply('Wups! There are no custom commands...', mention_author=False)
    else:
        return await ctx.reply(commands, mention_author=False)

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
async def choose(ctx, *options):
    if (len(options) < 2):
        return await ctx.reply("Wups! You need at least 2 arguments for me to choose from...", mention_author=False)
    return await ctx.reply(f"I choose {random.choice(options)}!", mention_author=False)

@bot.command(name='roulette')
async def roulette(ctx, member:discord.Member=None):
    if assert_cooldown("roulette"):
        return await ctx.reply("Wups! Slow down there, bub! Command on cooldown...", mention_author=False)
  
    member = member or ctx.message.author
    if member == ctx.message.author: # if a member wants to roulette themselves
        if not member.guild_permissions.administrator:
            if random.randint(1,6) == 1:
                await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                return await ctx.reply("🔥🔫 You died! (muted for 1 hour)", mention_author=False)
            return await ctx.reply("🚬🔫 Looks like you\'re safe, for now...", mention_author=False)
        return await ctx.reply("❌🔫 Looks like you\'re safe, you filthy admin...", mention_author=False)

    else: # if an admin wants to roulette a member they specify
        if not ctx.message.author.guild_permissions.administrator:
            if member == ctx.message.author:
                if random.randint(1,6) == 1:
                    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                    return await ctx.reply("🔥🔫 You died! (muted for 1 hour)", mention_author=False)
                return await ctx.reply("🚬🔫 Looks like you\'re safe, for now...", mention_author=False)
            return await ctx.reply("❌🔫 Wups! A lowlife like you can\'t possibly fire the gun at someone else...", mention_author=False)
        elif member == ctx.message.author:
            return await ctx.reply("❌🔫 Wups! Admins are valued. Don\'t roulette an admin like yourself...", mention_author=False)
        elif member.is_timed_out():
            return await ctx.reply("❌🔫 Wups! Don\'t you think it\'d be overkill to shoot a dead body?", mention_author=False)
        else:
            if not member.guild_permissions.administrator:
                if random.randint(1,6) == 1:
                    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                    return await ctx.reply("🔥🔫 This user died! (muted for 1 hour)", mention_author=False)
                return await ctx.reply("🚬🔫 Looks like they\'re safe, for now...", mention_author=False)
            return await ctx.reply("❌🔫 Looks like they\'re safe, that filthy admin...", mention_author=False)
      
@bot.command(name='howgay')
async def howgay(ctx, member:discord.Member=None):
    if assert_cooldown("howgay"):
        return await ctx.reply("Wups! Slow down there, bub! Command on cooldown...", mention_author=False)
      
    member = member or ctx.message.author
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
        
@bot.command(name='who')
async def who(ctx):
    content = ctx.message.content[3:]
    members = [member for member in ctx.message.guild.members if not member.bot]
    return await ctx.reply(f"`{content}`? {random.choice(members)}", mention_author=False)

@bot.command(name='kick')
async def kick(ctx, member:discord.Member):
    if not ctx.message.author.guild_permissions.administrator:
        return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
    if member.guild_permissions.administrator:
        return await ctx.reply("Wups! Administrators can\'t be kicked...", mention_author=False)
      
    await member.kick()
    await ctx.message.delete()
    return await ctx.message.author.guild.system_channel.send(f"{member.name} has been kicked! Hope you learn from your mistake... <:do_not:1077435360537223238>")

@bot.command(name='ban')
async def ban(ctx, member:discord.Member):
    if not ctx.message.author.guild_permissions.administrator:
        return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
    if member.guild_permissions.administrator:
        return await ctx.reply("Wups! Administrators can\'t be banned...", mention_author=False)

    await member.ban()
    return await ctx.message.delete()

@bot.command(name='mute')
async def mute(ctx, member:discord.Member, timelimit):
    current_time = discord.utils.utcnow()
    valid = False
    timelimit = timelimit.lower()
    timepossibilities = ['s', 'm', 'h', 'd', 'w']
    if timelimit[-1] in timepossibilities:
        valid = True
  
    if not ctx.message.author.guild_permissions.administrator:
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

@bot.command(name='whomuted')
async def whomuted(ctx):
    muted = [member.name for member in ctx.guild.members if member.is_timed_out()]
    mutedNames = ", ".join(muted)
    if mutedNames == '':
        return await ctx.reply("Wups! No one is muted currently...", mention_author=False)
    else:
        return await ctx.reply(mutedNames, mention_author=False)

@bot.command(name='avatar', aliases=['avi'])
async def avatar(ctx, member:discord.Member=None):
    member = member or ctx.message.author
    e = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.purple())
    if member.display_avatar.url != member.avatar.url:
        e.set_image(url=member.display_avatar.url)
        e.set_thumbnail(url=member.avatar.url)
    else:
        e.set_image(url=member.display_avatar.url)
    e.set_footer(text=f"Requested by: {ctx.message.author.name}")
    return await ctx.reply(embed=e, mention_author=False)

@bot.command(name='rps')
async def rps(ctx, playerChoice: str=None):
    if assert_cooldown("rps"):
        return await ctx.reply("Wups! Slow down there, bub! Command on cooldown...", mention_author=False)
    elif playerChoice is None:
        return await ctx.reply("Wups! You need to give me your choice...", mention_author=False)

    playerChoice = playerChoice.lower()
    choices = ['rock', 'paper', 'scissors']
    if playerChoice not in choices:
        return await ctx.reply("Wups! Invalid choice...", mention_author=False)
    else:
        botChoice = random.choice(choices)
    
        if playerChoice == botChoice:
            return await ctx.reply(f"I chose `{botChoice}`.\nUgh! Boring! We tied...", mention_author=False)
        elif (playerChoice == choices[0] and botChoice == choices[1]) or \
            (playerChoice == choices[1] and botChoice == choices[2]) or \
            (playerChoice == choices[2] and botChoice == choices[0]):
                return await ctx.reply(f"I chose `{botChoice}`.\nHah! I win, sucker! Why'd you pick that one, stupid?", mention_author=False)
        else:
            return await ctx.reply(f"I chose `{botChoice}`.\nWell played there. You have bested me...", mention_author=False)

@bot.command(name='8ball')
async def eightball(ctx):
    if assert_cooldown("8ball"):
        return await ctx.reply("Wups! Slow down there, bub! Command on cooldown...", mention_author=False)
  
    responses = ['Hell yeah!', 'It is certain.', 'Without a doubt.', 'You may rely on it.', 'Yes, definitely.', 'It is decidedly so.', 'As I see it, yes.', 'Most likely.', 'Yes.', 'Outlook good.', 'Signs point to yes.', 'You already know the answer.', 'Reply hazy, try again.', 'Better not tell you now.', 'Ask again later.', 'Cannot predict now.', 'Concentrate and ask again.', 'Don\'t count on it.', 'Outlook not so good.', 'My sources say no.', 'Very doubtful.', 'My reply is no.', 'No.', 'Oh god, no.']
    return await ctx.reply(f"🎱 `{ctx.message.content[9:]}` 🎱\n{random.choice(responses)}", mention_author=False)

@bot.command(name='help')
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
        embed.add_field(name='!w rps (your choice)', value='Play a simple game of Rock-Paper-Scissors with me!', inline=False)
        embed.add_field(name='!w roulette ([Admin Only] @member)', value='Try your luck... 😈', inline=False)
        embed.add_field(name='!w 8ball (question)', value='Ask me a yes or no question for me to give a response to!', inline=False)
      
    elif page == 2:
        embed.add_field(name='!w createcommand (name) (output)', value='Create your own commands that make me send custom text or links.', inline=False)
        embed.add_field(name='!w deletecommand (name)', value='Delete commands that have already been created.', inline=False)
        embed.add_field(name='!w kick (@member)', value='Kicks the mentioned member from the server.', inline=False)
        embed.add_field(name='!w ban (@member)', value='Bans the mentioned member from the server.', inline=False)
        embed.add_field(name='!w mute (@member) (time amount)(s, m, h, d, or w)', value='Mutes the mentioned member for the given time amount. \"s\" for seconds, \"m\" for minutes, \"h\" for hours, \"d\" for days, and \"w\" for weeks. No space in between the time amount and the letter!', inline=False)
        embed.add_field(name='!w unmute (@member)', value='Unmutes the mentioned member.', inline=False)
      
    elif page == 3:
        embed.add_field(name='!w ping', value='Returns my response time in milliseconds.', inline=False)
        embed.add_field(name='!w whomuted', value='Returns the name of every member who is currently muted.', inline=False)
        embed.add_field(name='!w avatar ([Optional] @member)', value='I\'ll send you the avatar of the given user. Defaults to yourself.', inline=False)
    
    if page > 0:
        embed.set_footer(text=f'Viewing page {page}/{pages}')
    return await ctx.reply(embed=embed, mention_author=False)

# bot events start here
@bot.event
async def on_ready():
    create_command_list()
    print(f'Logged in as: {bot.user.name}\nID: {bot.user.id}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
  
    if message.content[0:3] == "!w " and message.content.split()[1] in list(command_list.keys()):
        await message.channel.send(command_list[message.content.split()[1]])
    else:   
        if message.content.lower() == "me":
            await message.channel.send('<:WoM:836128658828558336>')
        if message.content.lower() == "which":
            if assert_cooldown("which"):
                await message.reply("Wups! Slow down there, bub! Command on cooldown...", mention_author=False)
            else:
                members = [member.name.lower() for member in message.guild.members if not member.bot]
                await message.channel.send(random.choice(members))

        if "yoshi" in message.content.lower().split(" "):
            await message.add_reaction('<:full:1028536660918550568>')
        if "3ds" in message.content.lower().split(" "):
            await message.add_reaction('<:megalon:1078914494132129802>')
        if "yuri" in message.content.lower().split(" "):
            await message.add_reaction('<:vers:804766992644702238>')
        if "verstie" in message.content.lower().split(" "):
            await message.add_reaction('🏳️‍⚧️')
        if "crank" in message.content.lower().split(" "):
            await message.add_reaction('🔧')

    await bot.process_commands(message)

    if random.randint(1,4096) == 1:  
        if random.randint(1,2) == 1:
            try:
                return await message.author.send(f"Hey {message.author.name}. Hope this finds you well.\n\nJust wanted to say that I know that this server might make some jabs at you or do some things that might rub you the wrong way, but that aside I wanted to personally tell you that I value that you\'re here. I think you\'re amazing and you deserve only good things coming to you. Hope you only succeed from here!\nIf you\'re ever feeling down, I hope you can look back at this message just to cheer you up. Also, this message might come back to you again so maybe you\'ll need it again?\n\nOh well. Been nice talking to ya! <3")
            except:
                return await message.channel.send(f"Wups! I tried sending {message.author.mention} top secret classified government information, but for some reason I couldn\'t...")
        else:
            with open("shiny.png", "rb") as f:
                return await message.channel.send(content="A wild Wyvern of Marina appeared! ✨", file=discord.File(f))

@bot.event
async def on_command_error(ctx, error):
    if not ctx.message.content.split()[1] in list(command_list.keys()):
        return await ctx.reply(f'Wups! try "!w help"... ({error})', mention_author=False)

@bot.event
async def on_message_delete(message):
    global snipe_data
    channel = message.channel.id
    if message.author.bot:
        return

    snipe_data[channel]={"content":message.content, "author":message.author, "id":message.id, "attachment":message.attachments[0] if message.attachments else None}
    await asyncio.sleep(60)
    if message.id == snipe_data[channel]["id"]:
        del snipe_data[channel]

@bot.event
async def on_message_edit(message_before, message_after):
    global editsnipe_data
    channel = message_after.channel.id
    if message_before.author.bot:
        return

    editsnipe_data[channel]={"content":message_before.content, "author":message_before.author, "id":message_before.id}
    await asyncio.sleep(60)
    if message_before.id == editsnipe_data[channel]["id"]:
        del editsnipe_data[channel]

@bot.event
async def on_member_join(member):
    if not member.bot:
        return await member.guild.system_channel.send(f"Welcome, {member.mention}, to **The Marina**! This is your one-way ticket to Hell. There\'s no going back from here...\nFor a grasp of the rules, however (yes, we have those), we do ask that you check <#822341695411847249>.\n*Remember to take breaks, nya?*")

@bot.event
async def on_member_update(before, after):
    if not before.is_timed_out() and after.is_timed_out():
        return await before.guild.system_channel.send(f"That fucking bozo {after.mention} got timed out! Point and laugh at this user! <:you:765067257008881715>")
    if before.is_timed_out() and not after.is_timed_out():
        return await before.guild.system_channel.send(f"Welcome back, {after.mention}. Don\'t do that again, idiot. <:do_not:1077435360537223238>")

@bot.event
async def on_member_ban(guild, user):
    return await guild.system_channel.send(f"{user.name} has been banned! Rest in fucking piss, bozo. <:kysNOW:896223569288241175>")
    
# set up to start the bot
keep_alive()
bot.run(TOKEN)
