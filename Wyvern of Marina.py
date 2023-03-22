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

# instantiation starts here
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '!w ', intents = intents)

say = print
command_list={}
empty_file=False
snipe_message_content = {}
snipe_message_author = {}

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
    guild = discord.utils.get(bot.guilds)
    botname = '{0.user.name}'.format(bot)
    members = '\n - '.join(member.name for member in guild.members if not member.bot)
    print(f'{botname} is connected to the following guild:\n{guild.name} (ID: {guild.id})\nMembers:\n - {members}')

# bot commands start here
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round (bot.latency * 1000)}ms ')
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
        await ctx.reply('Wups! Incorrect number of arguments! You need two arguments to create a new command...', mention_author = False)
    elif not ctx.author.guild_permissions.manage_messages:
        await ctx.reply("Wups! You do not have the required permissions...", mention_author=False)
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
                await ctx.reply('Wups, this command already exists...', mention_author=False)
            else:
                writer.writerow({'command_name': name, 'command_output': output})
                await ctx.reply(f"The command {name} has been created!", mention_author=False)
                command_list[name] = output
                
@bot.command()
async def deletecommand(ctx, *args):
    global command_list
  
    if len(args) != 1:
        await ctx.reply('Wups! Incorrect number of arguments! You need one argument to delete a command...', mention_author=False)
    elif not ctx.author.guild_permissions.manage_messages:
        await ctx.reply('Wups, you do not have the required permissions...', mention_author=False)
    else:
        array = [arg for arg in args]
        name = array[0]
        if not name in list(command_list.keys()):
            await ctx.reply('Wups! This command does not exist...', mention_author=False)
        elif len(list(command_list.keys())) == 0:
            await ctx.reply('Wups! There are no commands to delete in the first place...', mention_author=False)
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
            await ctx.reply(f'The command {name} has been deleted!', mention_author=False)
            
@bot.command()
async def customcommands(ctx):
    commandList = list(command_list.keys())
    commands = ', '.join(commandList) 
    if commands == '':
        await ctx.reply('Wups! There are no custom commands...', mention_author=False)
    else:
        await ctx.reply(commands, mention_author=False)

@bot.command()
async def snipe(ctx):
    channel = ctx.channel
    try:
        embed = discord.Embed(color = discord.Color.purple(), description=snipe_message_content[channel.id])
        embed.set_author(name=f"Last deleted message in #{channel.name}")
        embed.set_footer(text=f"This message was sent by {snipe_message_author[channel.id]}")
        embed.set_thumbnail(url=snipe_message_author[channel.id].avatar)
        await ctx.reply(embed=embed, mention_author=False)
    except KeyError:
        await ctx.reply(f"Wups! There are no recently deleted messages in <#{channel.id}>...", mention_author=False)

@bot.command()
async def help(ctx):
    embed = discord.Embed(color = discord.Color.purple())
    embed.set_author(name='Commands available')

    embed.add_field(name='!w ping', value='Returns my respond time in milliseconds.', inline=False)
    embed.add_field(name='!w say', value='Type something after the command for me to repeat it.', inline=False)
    embed.add_field(name='!w createcommand', value='Create your own commands that make me send custom text or links. [Admin Only]', inline=False)
    embed.add_field(name='!w deletecommand', value='Delete commands that have already been created. [Admin Only]', inline=False)
    embed.add_field(name='!w customcommands', value="Displays a list of the server's custom commands.", inline=False)
    embed.add_field(name='!w snipe', value='Snipes the last deleted message in that channel. Keep in mind, you only have 60 seconds to snipe the deleted message!', inline=False)
    
    await ctx.reply(embed=embed, mention_author=False)

# bot events start here
@bot.event
async def on_message(message):
    if message.content[0:3] == "!w " and message.content.split()[1] in list(command_list.keys()):
        await message.channel.send(command_list[message.content.split()[1]])
    else:   
        if message.content.lower() == "me":
            await message.channel.send('<:WoM:836128658828558336>')
        if message.content.lower() == "which":
            guild = discord.utils.get(bot.guilds)
            members = []
            for member in guild.members:
                if member.bot == False:
                    members.append(member.name.lower())
            memberNum = random.randint(0, len(members) - 1)
            await message.channel.send(members[memberNum])

        if "yoshi" in message.content.lower().split(" "):
            await message.add_reaction('<:full:1028536660918550568>')
        if "3ds" in message.content.lower().split(" "):
            await message.add_reaction('<:megalon:1078914494132129802>')
        if "yuri" in message.content.lower().split(" "):
            await message.add_reaction('<:vers:804766992644702238>')
        if "verstie" in message.content.lower().split(" "):
            await message.add_reaction('<:verstie:1078929624429498430>')
            
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if not ctx.message.content.split()[1] in list(command_list.keys()):
        await ctx.reply(f'Wups! try "!w help"... ({error})', mention_author=False)

@bot.event
async def on_message_delete(message):
    global snipe_message_content
    global snipe_message_author

    snipe_message_author[message.channel.id] = message.author
    snipe_message_content[message.channel.id] = message.content
    await asyncio.sleep(60)
    del snipe_message_author[message.channel.id]
    del snipe_message_content[message.channel.id]
    
# set up to start the bot
keep_alive()
bot.run(TOKEN)
