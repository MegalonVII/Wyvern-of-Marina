import discord
import os
from platform import system
from discord.ext import commands
from dotenv import load_dotenv
from utils import *

# token instantiation
load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN')

# bot initialization
bot=commands.Bot(command_prefix = '!w ', intents=discord.Intents.all())
bot.remove_command('help')
extensions=['fun', 'economy', 'admin', 'flair', 'misc', 'birthday', 'music', 'events']

# bot help command redifined
@bot.command(name='help')
async def help(ctx, page:int=0):
    command_info = {
        0: ('Need help?', [
            ('!w help 1', 'All the fun commands for everyone to enjoy!'), 
            ('!w help 2', 'All the fun economy commands!'), 
            ('!w help 3', 'All the administrative commands.'), 
            ('!w help 4', 'All the flair commands.'), 
            ('!w help 5', 'All the birthday commands.'), 
            ('!w help 6', 'All the musical commands for voice chats!'), 
            ('!w help 7', 'All the miscellaneous commands.')
        ]),
        1: ('Fun Commands', [
            ('!w say', 'Type something after the command for me to repeat it.'),
            ('!w customcommands', 'Displays a list of the server\'s custom commands.'),
            ('!w snipe', 'Snipes the last deleted message in that channel. Only the first media attachment will be sniped from the message. Keep in mind, you only have 60 seconds to snipe the deleted message!'),
            ('!w editsnipe', 'Acts just like !w snipe, only for messages that were edited instead of deleted.'),
            ('!w choose (any number of options, separated by a space)', 'Chooses a random option from all the options that you give me.'),
            ('!w pokedex (number between 1 and 1017)', 'Returns information about said Pokémon at the given index!'),
            ('!w who (remainder of question)', 'I\'ll tell you the name of a random member who fits this description.'),
            ('!w howgay ([Optional] @member)', 'I\'ll tell you either how gay you are or how gay the user you mention is.'),
            ('!w rps (your choice)', 'Play a simple game of Rock-Paper-Scissors with me!'),
            ('!w 8ball (question)', 'I\'ll give you the magic response to your yes or no question!'),
            ('!w roulette ([Admin Only] @member)', 'Try your luck... 😈'),
            ('!w trivia ([Optional] type)', 'I\'ll give you a multiple-choice trivia question. If you do not provide a type, it will be a random question on either general knowledge or some form of media. If you do, the types you may choose from are "general", "music", "film", "tv", "games", or "anime".'),
            ('!w quote', 'Returns a random quote from a video game!'),
            ('!w deathbattle (@user)', 'Fight someone... 🤠'),
            ('!w ship (phrase1) (phrase2)', 'In the mood for some love? 😏')
        ]),
        2: ('Economical Commands', [
            ('!w slots', 'Win some Zenny! 🤑'),
            ('!w bet (amount)', 'Bet your Zenny for double that bet if you roll 2 dice and they both result to 7.'),
            ('!w steal (@member)', 'Do a little bit of thievery... 😈'),
            ('!w heist', 'Indulge in a life of crime... 🤠'),
            ('!w deposit (amount)', 'Deposit your Zenny to the bank!'),
            ('!w withdraw (amount)', 'Withdraw the Zenny in your bank account!'),
            ('!w balance ([Optional] @member)', 'I\'ll tell you how much Zenny you or the person you mention have. It will cost you to peer into someone else\'s balance!'),
            ('!w bankbalance', 'I\'ll tell you how much Zenny you have in the bank.'),
            ('!w paypal (@member) (amount)', 'Pay your pal some Zenny!'),
            ('!w marketplace', 'I\'ll show you all the items that you can buy with Zenny!'),
            ('!w buy (item name) ([Optional] number requested)', 'If you have enough Zenny, you may buy an item from the Marketplace! Number value defaults to 1.'),
            ('!w sell (item name) ([Optional] number requested)', 'Sell an item in your inventory for half the price. Number value defaults to 1.'),
            ('!w inventory', 'I\'ll tell you the items that you have!'),
            ('!w use (item name)', 'If you purchased the item you give me, you may use it!')
        ]),
        3: ('Administrative Commands', [
            ('!w createcommand (name) (output)', 'Create your own commands that make me send custom text or links.'),
            ('!w deletecommand (name)', 'Delete commands that have already been created.'),
            ('!w clear (number of messages)', 'Deletes the last number you specify of messages from the specific chat. To avoid rate limits, please enter a number between 1 and 10.'),
            ('!w kick (@member)', 'Kicks the mentioned member from the server.'),
            ('!w ban (@member)', 'Bans the mentioned member from the server.'),
            ('!w mute (@member) (time amount)(s, m, h, d, or w)', 'Mutes the mentioned member for the given time amount. \"s\" for seconds, \"m\" for minutes, \"h\" for hours, \"d\" for days, and \"w\" for weeks. No space in between the time amount and the letter!'),
            ('!w unmute (@member)', 'Unmutes the mentioned member.')
        ]), 
        4: ('Flair Commands', [
            ('!w addflair (@role) [Admin Only]', 'Adds this role as a flair to this server.'),
            ('!w deleteflair (@role) [Admin Only]', 'Removes this role as a flair from this server.'),
            ('!w listflairs', 'Lists all the flairs for this server.'),
            ('!w im (role name)', 'Gives or removes the flair you ask for.')
        ]),
        5: ('Birthday Commands', [
            ('!w birthday', 'Register your birthday with me so I can wish you a happy birthday!'),
            ('!w birthdaylist', 'See a list of all birthdays in the server!')
        ]),
        6: ('Musical Commands', [
            ('!w join', 'Joins the voice chat that you are in'),
            ('!w leave', 'Leaves the voice chat that I am in'),
            ('!w play (YouTube URL or search query)', 'While I\'m in voice call, I will play the song from the YouTube URL or search query you provide me.'),
            ('!w now', 'Displays the current song that I\'m playing'),
            ('!w queue (optional: page number)', 'Displays the queue of songs. Page value defaults to 1. Each page displays the first 10 songs in the queue'),
            ('!w shuffle', 'Shuffles the current queue. *[DJs/Admin Only]*'),
            ('!w remove (index)', 'Removes the song at the provided index from the queue'),
            ('!w pause', 'Pauses any music that I\'m playing'),
            ('!w resume', 'Resumes any paused music'),
            ('!w stop', 'Stops any playing music entirely'),
            ('!w skip', 'Skips the current playing song to the next one in the queue. Only the song requester can do this, though DJs and Admins are unaffected')
        ]),
        7: ('Miscellaneous Commands', [
            ('!w ping', 'Returns my response time in milliseconds.'),
            ('!w whomuted', 'Returns the name of every member who is currently muted.'),
            ('!w avatar ([Optional] @member)', 'I\'ll send you the avatar of the given user. Defaults to yourself.'),
            ('!w emote (emote from this server)', 'Returns information of the given emote. It MUST be from this server!'),
            ('!w startpoll', 'Start a poll!'),
            ('!w convert (number) (original unit) (new unit)', 'Convert a number of units to another unit! Supported units include F, C, m, ft, kg, lb, mi, km, in, and cm. Supported conversions include F <-> C, ft <-> m, lb <-> kg, mi <-> km, and in <-> cm.'),
            ('!w translate (phrase)', 'Translates any given phrase to English! Be weary that I might not be 100 percent accurate with my translations.'),
            ('!w grabber (platform) (query)', 'Yar har, me mateys! Sail the high seas and let me give you music from streaming platforms! 🏴‍☠️')
        ])
    }

    embed = discord.Embed(color = discord.Color.purple())
    if page < 0 or page > len(command_info) - 1:
        await shark_react(ctx.message)
        return await ctx.reply('Wups! Invalid page number...', mention_author=False)

    embed.title = command_info[page][0]
    for name, value in command_info[page][1]:
        embed.add_field(name=name, value=value, inline=False)

    if page > 0:
        embed.set_footer(text=f'Viewing page {page}/{len(command_info) - 1}')
    embed.set_thumbnail(url=bot.user.avatar.url)
    return await ctx.reply(embed=embed, mention_author=False)

# on_ready
@bot.event
async def on_ready():
    print("Logging in...")
  
    for file in files: # creates all lists wom stores
        create_list(file)
    create_birthday_list()
      
    try:
        for extension in extensions: # loads extensions for other commands
            await bot.load_extension(f'exts.{extension}')
    except:
        pass

    if not discord.opus.is_loaded() and system() == 'Darwin':
        discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.4/lib/libopus.0.dylib') # this if statement is for if i'm working from my mac and testing stuff locally

    return print(f"\nLogged in as: {bot.user.name}\nID: {bot.user.id}\n" + get_login_time('US/Pacific')) # fully logged in with everything loaded in the backend. chose the timezone as pst because that's what blues is based in
    
# everything has finally been set up
# we can now run the bot
bot.run(TOKEN)
