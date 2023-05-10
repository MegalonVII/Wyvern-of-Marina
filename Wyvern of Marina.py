# all imports
import discord
import os
import csv
from discord.ext import commands
from keep_alive import keep_alive
import random
import pandas as pd
import asyncio
import datetime
import requests
import json
import urllib.parse
from utils import *

# bot instantiation
TOKEN=os.getenv('DISCORD_TOKEN')
bot=commands.Bot(command_prefix = '!w ', intents=discord.Intents.all())
bot.remove_command('help')
extensions=['fun', 'economy', 'admin', 'flair', 'misc']

# bot help command redifined
# functions are created in order of placement in this list for ease of user reading
@bot.command(name='help')
async def help(ctx, page:int=0):
    embed = discord.Embed(color = discord.Color.purple())
    if page < 0 or page > 5:
        return await ctx.reply('Wups! Invalid page number...', mention_author=False)
      
    if page == 0:
        embed.title='Need help?'
        embed.add_field(name='!w help 1', value = 'All the fun commands for everyone to enjoy!', inline=False)
        embed.add_field(name='!w help 2', value = 'All the fun economy commands!', inline=False)
        embed.add_field(name='!w help 3', value = 'All the administrative commands.', inline=False)
        embed.add_field(name='!w help 4', value = 'All the flair commands.', inline=False)
        embed.add_field(name='!w help 5', value = 'All the miscellaneous commands.', inline=False)  
      
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
        embed.add_field(name='!w trivia ([Optional] type)', value='I\'ll give you a multiple-choice trivia question. If you do not provide a type, it will be a random question on either general knowledge or some form of media. If you do, the types you may choose from are "general", "music", "film", "tv", "games", or "anime".', inline=False)
        embed.add_field(name='!w quote', value='Returns a random quote from a video game!', inline=False)

    elif page == 2:
        embed.title='Economical Commands'
        embed.add_field(name='!w slots', value='Win some Zenny! 🤑', inline=False)
        embed.add_field(name='!w balance ([Optional] @member)', value='I\'ll tell you how much Zenny you or the person you mention have. It will cost you to peer into someone else\'s balance!', inline=False)
        embed.add_field(name='!w leaderboard', value='Displays the top 5 richest members in the server.', inline=False)
        embed.add_field(name='!w steal (@member)', value='Do a little bit of thievery... 😈', inline=False)
        embed.add_field(name='!w paypal (@member) (amount)', value='Pay your pal some Zenny!', inline=False)
        embed.add_field(name='!w bet (amount)', value='Bet your Zenny for double that bet if you roll 2 dice and they both result to 7.', inline=False)
      
    elif page == 3:
        embed.title='Administrative Commands'
        embed.add_field(name='!w createcommand (name) (output)', value='Create your own commands that make me send custom text or links.', inline=False)
        embed.add_field(name='!w deletecommand (name)', value='Delete commands that have already been created.', inline=False)
        embed.add_field(name='!w clear (number of messages)', value='Deletes the last number you specify of messages from the specific chat. To avoid rate limits, please enter a number between 1 and 10.', inline=False)
        embed.add_field(name='!w kick (@member)', value='Kicks the mentioned member from the server.', inline=False)
        embed.add_field(name='!w ban (@member)', value='Bans the mentioned member from the server.', inline=False)
        embed.add_field(name='!w mute (@member) (time amount)(s, m, h, d, or w)', value='Mutes the mentioned member for the given time amount. \"s\" for seconds, \"m\" for minutes, \"h\" for hours, \"d\" for days, and \"w\" for weeks. No space in between the time amount and the letter!', inline=False)
        embed.add_field(name='!w unmute (@member)', value='Unmutes the mentioned member.', inline=False)
      
    elif page == 4:
        embed.title='Flair Commands'
        embed.add_field(name='!w addflair (@role) [Admin Only]', value='Adds this role as a flair to this server.', inline=False)
        embed.add_field(name='!w deleteflair (@role) [Admin Only]', value='Removes this role as a flair from this server.', inline=False)
        embed.add_field(name='!w listflairs', value='Lists all the flairs for this server.', inline=False)
        embed.add_field(name='!w im (role name)', value='Gives or removes the flair you ask for.', inline=False)
      
    elif page == 5:
        embed.title='Miscellaneous Commands'
        embed.add_field(name='!w ping', value='Returns my response time in milliseconds.', inline=False)
        embed.add_field(name='!w whomuted', value='Returns the name of every member who is currently muted.', inline=False)
        embed.add_field(name='!w avatar ([Optional] @member)', value='I\'ll send you the avatar of the given user. Defaults to yourself.', inline=False) 
        embed.add_field(name='!w emote (emote from this server)', value='Returns information of the given emote. It MUST be from this server!', inline=False)
      
    if page > 0:
        embed.set_footer(text=f'Viewing page {page}/5')
    return await ctx.reply(embed=embed, mention_author=False)

# on_ready

@bot.event
async def on_ready():
    for file in files:
        create_list(file)
    print(f'Logged in as: {bot.user.name}\nID: {bot.user.id}')
    for extension in extensions:
        print(extension)
        await bot.load_extension(extension)


# bot events start here
# on_message, on_command_error, on_message_delete, on_message_edit, on_member_join, on_member_update, on_member_ban, on_reaction_add, on_member_remove
# TODO move to a cog
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
        triggers = ['yoshi','3ds','wednesday','yuri','yaoi','crank','kys','chan']
        trigger_emojis = ['<:full:1028536660918550568>','<:megalon:1078914494132129802>','<:wednesday:798691076092198993>','<:vers:804766992644702238>','🐍','🔧','⚡','🦄']
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
            add_coins(message.author.id,500)
            with open("shiny.png", "rb") as f:
                file = discord.File(f)
                return await message.channel.send(content=f"{message.author.name} stumbled across 500 {zenny} and a wild Wyvern of Marina! ✨", file=file)

@bot.event
async def on_command_error(ctx, error):
    if not ctx.message.content.split()[1] in list(lists["commands"].keys()):
        await ctx.message.add_reaction('🦈')
        return await ctx.reply(f'Wups! try "!w help"... ({error})', mention_author=False)

@bot.event
async def on_message_delete(message):
    if not message.content[0:3] == '!w ' or message.author.bot:
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
    if not message_after.author.bot:
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
        try:
            peep_role = discord.utils.get(member.guild.roles, name="Peep")
            await member.add_roles(peep_role)
        except:
            pass
        add_coins(member.id,100)
        return await member.guild.system_channel.send(f"Welcome, {member.mention}, to **The Marina**! This is your one-way ticket to Hell. There\'s no going back from here...\nFor a grasp of the rules, however (yes, we have those), we do ask that you check <#822341695411847249>.\n*Remember to take breaks, nya?*")
    else:
        try:
            beep = discord.utils.get(member.guild.roles, name="beep")
            return await member.add_roles(beep)
        except:
            pass

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