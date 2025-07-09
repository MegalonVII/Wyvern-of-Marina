import discord
from os import getenv
from discord.ext import commands
from dotenv import load_dotenv
from sys import exit

from utils import files, lists # utils direct values
from utils import create_list, create_birthday_list, get_login_time, wups, add_item # utils functions

# token instantiation
load_dotenv()
TOKEN=getenv('DISCORD_TOKEN')

# bot initialization
bot=commands.Bot(command_prefix = '!w ', intents=discord.Intents.all())
bot.remove_command('help')
extensions=['fun', 'economy', 'admin', 'flair', 'misc', 'birthday', 'music', 'events']

# bot help command
@bot.command(name='help')
async def help(ctx, page: str = "home"):
    page = page.lower()

    command_info = {
        "home": ('Need help?', [
            ('!w help fun', 'All the fun commands for everyone to enjoy!'), 
            ('!w help economy', 'All the fun economy commands!'), 
            ('!w help admin', 'All the administrative commands.'), 
            ('!w help flair', 'All the flair commands.'), 
            ('!w help birthday', 'All the birthday commands.'), 
            ('!w help music', 'All the musical commands.'), 
            ('!w help misc', 'All the miscellaneous commands.')
        ]),
        "fun": ('Fun Commands', [
            ('!w say', 'Type something after the command for me to repeat it.'),
            ('!w customcommands', 'Displays a list of the server\'s custom commands.'),
            ('!w snipe', 'Snipes the last deleted message in that channel...'),
            ('!w editsnipe', 'Acts just like !w snipe, only for messages that were edited instead of deleted.'),
            ('!w choose (any number of options, separated by a space)', 'Chooses a random option...'),
            ('!w pokedex (number between 1 and 1017)', 'Returns information about said Pokémon...'),
            ('!w who (remainder of question)', 'I\'ll tell you the name of a random member...'),
            ('!w howgay ([Optional] @member)', 'I\'ll tell you either how gay you are...'),
            ('!w rps (your choice)', 'Play a simple game of Rock-Paper-Scissors with me!'),
            ('!w 8ball (question)', 'I\'ll give you the magic response...'),
            ('!w roulette ([Admin Only] @member)', 'Try your luck... 😈'),
            ('!w trivia ([Optional] type)', 'I\'ll give you a multiple-choice trivia question...'),
            ('!w emulation', 'A wiki for how to set up emulators...'),
            ('!w quote', 'Returns a random quote from a video game!'),
            ('!w deathbattle (@user)', 'Fight someone... 🤠'),
            ('!w ship (phrase1) (phrase2)', 'In the mood for some love? 😏')
        ]),
        "economy": ('Economical Commands', [
            ('!w slots', 'Win some Zenny! 🤑'),
            ('!w bet (amount)', 'Bet your Zenny for double...'),
            ('!w steal (@member)', 'Do a little bit of thievery... 😈'),
            ('!w heist', 'Indulge in a life of crime... 🤠'),
            ('!w deposit (amount)', 'Deposit your Zenny to the bank!'),
            ('!w withdraw (amount)', 'Withdraw the Zenny in your bank account!'),
            ('!w balance ([Optional] @member)', 'I\'ll tell you how much Zenny you or the person you mention have...'),
            ('!w bankbalance', 'I\'ll tell you how much Zenny you have in the bank.'),
            ('!w paypal (@member) (amount)', 'Pay your pal some Zenny!'),
            ('!w marketplace', 'I\'ll show you all the items that you can buy with Zenny!'),
            ('!w buy (item name) ([Optional] number requested)', 'If you have enough Zenny...'),
            ('!w sell (item name) ([Optional] number requested)', 'Sell an item in your inventory...'),
            ('!w inventory', 'I\'ll tell you the items that you have!'),
            ('!w use (item name)', 'If you purchased the item... you may use it!')
        ]),
        "admin": ('Administrative Commands', [
            ('!w createcommand (name) (output)', 'Create your own commands...'),
            ('!w deletecommand (name)', 'Delete commands that have already been created.'),
            ('!w clear (number of messages)', 'Deletes the last number you specify of messages...'),
            ('!w kick (@member)', 'Kicks the mentioned member...'),
            ('!w ban (@member)', 'Bans the mentioned member...'),
            ('!w mute (@member) (time amount)(s, m, h, d, or w)', 'Mutes the mentioned member...'),
            ('!w unmute (@member)', 'Unmutes the mentioned member.')
        ]),
        "flair": ('Flair Commands', [
            ('!w addflair (@role) [Admin Only]', 'Adds this role as a flair to this server.'),
            ('!w deleteflair (@role) [Admin Only]', 'Removes this role as a flair...'),
            ('!w listflairs', 'Lists all the flairs for this server.'),
            ('!w im (role name)', 'Gives or removes the flair you ask for.')
        ]),
        "birthday": ('Birthday Commands', [
            ('!w birthday', 'Register your birthday...'),
            ('!w birthdaylist', 'See a list of all birthdays in the server!')
        ]),
        "music": ('Musical Commands', [
            ('!w join', 'Joins the voice chat...'),
            ('!w leave', 'Leaves the voice chat...'),
            ('!w play (YouTube URL or search query)', 'While I\'m in voice call, I will play the song...'),
            ('!w now', 'Displays the current song...'),
            ('!w queue (optional: page number)', 'Displays the queue of songs...'),
            ('!w shuffle', 'Shuffles the current queue...'),
            ('!w remove (index)', 'Removes the song at the provided index...'),
            ('!w pause', 'Pauses any music...'),
            ('!w resume', 'Resumes any paused music...'),
            ('!w stop', 'Stops any playing music...'),
            ('!w skip', 'Skips the current playing song...'),
            ('!w grabber (platform) (song name)', 'Yar har, me mateys!...')
        ]),
        "misc": ('Miscellaneous Commands', [
            ('!w ping', 'Returns my response time...'),
            ('!w whomuted', 'Returns the name of every member...'),
            ('!w avatar ([Optional] @member)', 'I\'ll send you the avatar...'),
            ('!w emote (emote from this server)', 'Returns information of the given emote...'),
            ('!w convert (number) (original unit) (new unit)', 'Convert a number of units...'),
            ('!w translate (phrase)', 'Translates any given phrase...')
        ])
    }

    if page not in command_info:
        options = ", ".join(f"`{key}`" for key in list(command_info.keys())[1:])
        return await wups(ctx, f'Invalid page name. Try one of: {options}')

    embed = discord.Embed(color=discord.Color.purple())
    embed.title = command_info[page][0]

    for name, value in command_info[page][1]:
        embed.add_field(name=name, value=value, inline=False)

    if page != "home":
        embed.set_footer(text=f'Viewing page: {page}')
    
    embed.set_thumbnail(url=bot.user.avatar.url)
    return await ctx.reply(embed=embed, mention_author=False)

# on_ready
@bot.event
async def on_ready():
    print("\nLogging in...")
  
    for file in files: # creates all lists wom stores
        create_list(file)
    create_birthday_list()
      
    try:
        for extension in extensions: # loads extensions for other commands
            await bot.load_extension(f'exts.{extension}')
    except Exception as e:
        print(e)
        exit(1)

    for member in bot.guilds[0].members: # mandates user has karma for roulette
        if not member.bot:
            if not str(member.id) in lists["karma"].keys():
                add_item("karma", member.id, 2)

    return print(f"\nLogged in as: {bot.user.name}\nID: {bot.user.id}\n" + get_login_time('America/Los_Angeles')) # fully logged in with everything loaded in the backend. chose the timezone as cest because that's where i am based in

# everything has finally been set up
# we can now run the bot
bot.run(TOKEN)
