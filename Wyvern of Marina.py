import discord
import os
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands
from keep_alive import keep_alive

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix = '!w ')

say = print

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

@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(
        color = discord.Color.purple())

    embed.set_author(name='Commands available')

    embed.add_field(name='!w ping', value='Returns my respond time in milliseconds', inline=False)

    embed.add_field(name='!w say', value='Type something after the command for me to repeat it', inline=False)

    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.content == "me":
        await message.channel.send('<:WoM:836128658828558336>')
    else if message.content == "yoshi":
        await message.channel.send('<:full:1028536660918550568>')
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f'Wups, try "!w help" ({error})')

keep_alive()
bot.run(TOKEN)
