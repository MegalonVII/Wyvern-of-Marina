import discord
import os
import csv
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands
from keep_alive import keep_alive

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix = '!w ')

say = print
command_list={}
empty_file=False

#Creates csv file if it doesn't exist
if not os.path.exists('commands.csv'):
    with open('commands.csv', 'w') as creating_new_csv_file: 
        pass
#Reads the csv file and adds every command to a dictionary
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
    if len(args) < 2:
        await ctx.send(f'Wups, too few arguments! You need two arguments to create a new command.')
    #Note that the code only asks for the user to have the permission to manage messages
    if not ctx.author.guild_permissions.manage_messages:
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
            writer.writerow({'command_name': name, 'command_output': output})
            await ctx.send(f"The command " + name + " has been created!")
            command_list[name] = output

@bot.command(pass_context=True)
async def customcommands(ctx):
    await ctx.send(list(command_list.keys()))

async def help(ctx):
    embed = discord.Embed(
        color = discord.Color.purple())

    embed.set_author(name='Commands available')

    embed.add_field(name='!w ping', value='Returns my respond time in milliseconds', inline=False)

    embed.add_field(name='!w say', value='Type something after the command for me to repeat it', inline=False)
    
    embed.add_field(name='!w createcommand', value='Currently in Beta! Create your own commands that send custom text or links! [Admin Only]', inline=False)
    
    embed.add_field(name='!w customcommands', value="Displays a list of the server's custom commands", inline=False)
    
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.content == "me":
        await message.channel.send('<:WoM:836128658828558336>')
    elif " yoshi " in message.content.lower():
        await message.channel.send('<:full:1028536660918550568>')
    elif " yuri " in message.content.lower():
        await bot.add_reaction(message, '<:vers:804766992644702238>')
    elif message.content[0:3] == "!w " and message.content.split()[1] in list(command_list.keys()):
        await message.channel.send(command_list[message.content.split()[1]])
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    #This looks very fucking dumb but I can't think of anything else
    if not ctx.message.content.split()[1] in list(command_list.keys()):
        await ctx.send(f'Wups, try "!w help" ({error})')
    
keep_alive()
bot.run(TOKEN)
