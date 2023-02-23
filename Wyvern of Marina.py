import discord
import os
import csv
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands
from keep_alive import keep_alive
import pandas as pd # Make sure Sky installs this on his PC with "pip install pandas" in the terminal

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix = '!w ')

say = print
command_list={}
empty_file=False

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
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})')

    members = 'n\ - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

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
    if len(args) != 2:
        await ctx.send(f'Wups, not the correct number of arguments! You need two arguments to create a new command.')
        # This just rules out the edge case that some moron might just do "!w createcommand".
    elif not ctx.author.guild_permissions.manage_messages:
        await ctx.send(f"Wups, you do not have the required permissions!")
    else:
        array = [arg for arg in args]
        name = array[0]
        output = array[1]
        with open('commands.csv', 'a', newline='') as csvfile:
            fieldnames = ['command_name', 'command_output']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if empty_file:
                writer.writeheader()
            if name in list(command_list.keys()):
                await ctx.send(f'Wups, this command already exists...')
            else:
                writer.writerow({'command_name': name, 'command_output': output})
                await ctx.send(f"The command " + name + " has been created!")
                command_list[name] = output
                
@bot.command()
async def deletecommand(ctx, *args):
    if len(args) != 1:
        await ctx.send(f'Wups, not the correct number of arguments! You need one argument to delete a command.')
        # This also rules out the edge case that some moron might just do "!w deletecommand".
    elif not ctx.author.guild_permissions.manage_messages:
        await ctx.send(f'Wups, you do not have the required permissions!')
    else:
        # This is very buggy, I need to work with Pich on this.
        array = [arg for arg in args]
        name = array[0]
        with open('commands.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            if empty_file or not name in list(command_list.keys()):
                await ctx.send(f'Wups, this command does not exist...')
            else:
                commands = pd.read_csv('commands.csv')
                commands = commands[commands.command_name != name]
                commands.to_csv('commands.csv', index=False)
                await ctx.send(f'The command ' + name + ' has been deleted!')
        # The main bug that I found was that even though it deletes the command from the CSV file, it
        # does not remove it from command_list until WoM restarts.
        # 
        # Another bug I found was that sometimes running this will create a new command with 'command_name' as 
        # the name and 'command_output' as the output. I sometimes had to delete my commands.csv to get it to 
        # reset.
        # 
        # I'm writing this at like almost 3 am in the morning so I'm gonna go to bed. Hopefully Pich can find some
        # other bugs if she looks at this branch and fix them if possible.

@bot.command(pass_context=True)
async def customcommands(ctx):
    await ctx.send(list(command_list.keys()))

@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(
        color = discord.Color.purple())

    embed.set_author(name='Commands available')

    embed.add_field(name='!w ping', value='Returns my respond time in milliseconds', inline=False)

    embed.add_field(name='!w say', value='Type something after the command for me to repeat it', inline=False)
    
    embed.add_field(name='!w createcommand', value='Create your own commands that make me send custom text or links [Admin Only]', inline=False)
    
    # This is just there because we have the basis for this. Just so that we don't have to do this later.
    embed.add_field(name='!w deletecommand', value='Delete commands that have already been created [Admin Only]', inline=False)
    
    embed.add_field(name='!w customcommands', value="Displays a list of the server's custom commands", inline=False)
    
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.content[0:3] == "!w " and message.content.split()[1] in list(command_list.keys()):
        await message.channel.send(command_list[message.content.split()[1]])
    else:   
        if message.content.lower() == "me":
            await message.channel.send('<:WoM:836128658828558336>')
        if "yoshi" in message.content.lower().split(" "):
            await message.channel.send('<:full:1028536660918550568>')
        if "yuri" in message.content.lower().split(" "):
            await message.add_reaction('<:vers:804766992644702238>')
        if "3ds" in message.content.lower.split(" "):
            await message.channel.send('hey guys did you know hacking your nintendo 3ds is super easy?')
            # Sorry just felt like doing this :)
            
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if not ctx.message.content.split()[1] in list(command_list.keys()):
        await ctx.send(f'Wups, try "!w help" ({error})')
    
keep_alive()
bot.run(TOKEN)
