import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from utils import *

# token instantiation
load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN')

# bot initialization
bot=commands.Bot(command_prefix = '!w ', intents=discord.Intents.all())
bot.remove_command('help')
extensions=['fun', 'economy', 'admin', 'flair', 'misc', 'events']

# bot help command redifined
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
        embed.add_field(name='!w pokedex (number between 1 and 1017)', value='Returns information about said Pokémon at the given index!', inline=False)
        embed.add_field(name='!w who (remainder of question)', value='I\'ll tell you the name of a random member who fits this description.', inline=False)
        embed.add_field(name='!w howgay ([Optional] @member)', value='I\'ll tell you either how gay you are or how gay the user you mention is.', inline=False)
        embed.add_field(name='!w rps (your choice)', value='Play a simple game of Rock-Paper-Scissors with me!', inline=False)
        embed.add_field(name='!w 8ball (question)', value='I\'ll give you the magic response to your yes or no question!', inline=False)
        embed.add_field(name='!w roulette ([Admin Only] @member)', value='Try your luck... 😈', inline=False)
        embed.add_field(name='!w trivia ([Optional] type)', value='I\'ll give you a multiple-choice trivia question. If you do not provide a type, it will be a random question on either general knowledge or some form of media. If you do, the types you may choose from are "general", "music", "film", "tv", "games", or "anime".', inline=False)
        embed.add_field(name='!w quote', value='Returns a random quote from a video game!', inline=False)
        embed.add_field(name='!w deathbattle (@user)', value='Fight someone... 🤠', inline=False)

    elif page == 2:
        embed.title='Economical Commands'
        embed.add_field(name='!w slots', value='Win some Zenny! 🤑', inline=False)
        embed.add_field(name='!w bet (amount)', value='Bet your Zenny for double that bet if you roll 2 dice and they both result to 7.', inline=False)
        embed.add_field(name='!w steal (@member)', value='Do a little bit of thievery... 😈', inline=False)
        embed.add_field(name='!w heist', value='Indulge in a life of crime... 🤠')
        embed.add_field(name='!w deposit (amount)', value='Deposit your Zenny to the bank!', inline=False)
        embed.add_field(name='!w withdraw (amount)', value='Withdraw the Zenny in your bank account!', inline=False)
        embed.add_field(name='!w balance ([Optional] @member)', value='I\'ll tell you how much Zenny you or the person you mention have. It will cost you to peer into someone else\'s balance!', inline=False)
        embed.add_field(name='!w bankbalance', value='I\'ll tell you how much Zenny you have in the bank.', inline=False)
        embed.add_field(name='!w paypal (@member) (amount)', value='Pay your pal some Zenny!', inline=False)
        embed.add_field(name='!w marketplace', value='I\'ll show you all the items that you can buy with Zenny!', inline=False)
        embed.add_field(name='!w buy (item name) ([Optional] number requested)', value='If you have enough Zenny, you may buy an item from the Marketplace! Number value defaults to 1.', inline=False)
        embed.add_field(name='!w sell (item name) ([Optional] number requested)', value='Sell an item in your inventory for half the price. Number value defaults to 1.', inline=False)
        embed.add_field(name='!w inventory', value='I\'ll tell you the items that you have!', inline=False)
        embed.add_field(name='!w use (item name)', value='If you purchased the item you give me, you may use it!', inline=False)
      
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
        embed.add_field(name='!w startpoll', value='Start a poll!', inline=False)
        embed.add_field(name='!w convert (number) (original unit) (new unit)', value='Convert a number of units to another unit! Supported units include F, C, m, ft, kg, lb, mi, km, in, and cm. Supported conversions include F <-> C, ft <-> m, lb <-> kg, mi <-> km, and in <-> cm.', inline=False)
      
    if page > 0:
        embed.set_footer(text=f'Viewing page {page}/5')
    return await ctx.reply(embed=embed, mention_author=False)

# on_ready
@bot.event
async def on_ready():
    print("Logging in...")
  
    for file in files: # creates all lists wom stores
        create_list(file)
      
    for extension in extensions: # loads extensions for other commands
        await bot.load_extension(f'exts.{extension}')

    print(f"\nLogged in as: {bot.user.name}\nID: {bot.user.id}\n" + get_login_time('US/Eastern')) # fully logged in with everything loaded in the backend. chose the timezone as pst because that's what blues is based in
    
# everything has finally been set up
# we can now run the bot
bot.run(TOKEN)
