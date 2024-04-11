import discord
from asyncio import TimeoutError, subprocess, create_subprocess_exec
from discord.ext import commands
from googletrans import Translator
from colorama import Fore, Back, Style
from utils import *

# misc commands start here
# ping, whomuted, avi, emote, startpoll, convert, translate, grabber
class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
        self.emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        self.conversions = {
            ("c", "f"): lambda x: x * 9/5 + 32,
            ("f", "c"): lambda x: (x - 32) * 5/9,
            ("m", "ft"): lambda x: x * 3.28084,
            ("ft", "m"): lambda x: x * 0.3048,
            ("kg", "lb"): lambda x: x * 2.20462,
            ("lb", "kg"): lambda x: x * 0.453592,
            ("mi", "km"): lambda x: x * 1.60934,
            ("km", "mi"): lambda x: x * 0.621371,
            ("in", "cm"): lambda x: x * 2.54,
            ("cm", "in"): lambda x: x * 0.393701
        }
        self.platforms = ['spotify', 'youtube', 'soundcloud', 'emulation']
        self.consoles = {
            'nes': "[NES Emulator](<https://github.com/TASEmulators/fceux/releases>)\n[NES ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20Entertainment%20System%20%28Headerless%29/>)", 
            'snes': "[SNES Emulator](<https://bsnes.org/download>)\n[SNES ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Super%20Nintendo%20Entertainment%20System/>)", 
            'n64': "[N64 Emulator](<https://www.retroarch.com/?page=platforms>)\n[N64 ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%2064%20%28BigEndian%29/>)", 
            'gamecube': "[GameCube Emulator](<https://dolphin-emu.org/download/>)\n[GameCube ROMs](<https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/>)", 
            'wii': "[Wii Emulator](<https://dolphin-emu.org/download/>)\n[Wii ROMs](<https://myrient.erista.me/files/Redump/Nintendo%20-%20Wii%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/>)", 
            'wiiu': "[Wii U Emulator](<https://github.com/cemu-project/Cemu/releases>)\n[Wii U ROMs](<https://myrient.erista.me/files/Redump/Nintendo%20-%20Wii%20U%20-%20WUX/>)\n[Wii U Keys](<https://pastebin.com/GWApZVLa>)",
            'switch': "[Switch Emulator](<https://ryujinx.org/download>)\n[Switch ROMs](<https://www.ziperto.com/nintendo-switch-nsp-list/>)\n[Switch Firmware](<https://prodkeys.net/ryujinx-firmware/>)\n[Switch Keys](<https://prodkeys.net/ryujinx-prod-keys/>)",  
            'gb': "[Game Boy Emulator](<https://sameboy.github.io/downloads/>)\n[Game Boy ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy/>)", 
            'gbc': "[Game Boy Color Emulator](<https://sameboy.github.io/downloads/>)\n[Game Boy Color ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Color/>)",
            'gba': "[Game Boy Advance Emulator](<https://mgba.io/downloads.html>)\n[Game Boy Advance ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Advance/>)", 
            'ds': "[DS Emulator](<https://melonds.kuribo64.net/downloads.php>)\n[DS ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20DS%20%28Decrypted%29/>)", 
            '3ds': "[3DS Emulator](<https://github.com/Lime3DS/Lime3DS/releases>)\n[3DS ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%203DS%20%28Decrypted%29/>)", 
            'ps1': "[PS1 Emulator](<https://github.com/stenzek/duckstation/releases/tag/latest>)\n[PS1 ROMs](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation/>)\n[PS1 BIOS](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%20-%20BIOS%20Images/>)", 
            'ps2': "[PS2 Emulator](<https://pcsx2.net/>)\n[PS2 ROMs](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%202/>)\n[PS2 BIOS](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%202%20-%20BIOS%20Images/>)", 
            'ps3': "[PS3 Emulator](<https://rpcs3.net/download>)\n[PS3 ROMs](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%203/>)\n[PS3 BIOS](<https://www.playstation.com/en-us/support/hardware/ps3/system-software/>)", 
            'psp': "[PSP Emulator](<https://www.ppsspp.org/download/>)\n[PSP ROMs](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%20Portable/>)", 
            'psvita': "[PS Vita Emulator](<https://vita3k.org/>)\n[PS Vita Roms](<https://myrient.erista.me/files/No-Intro/Sony%20-%20PlayStation%20Vita%20%28PSN%29%20%28Content%29/>)"
        }

    @commands.command(name='ping')
    async def ping(self, ctx):
        if await cog_check(ctx):
            await ctx.message.delete()
            return await ctx.send(f'Pong! {round (self.bot.latency * 1000)}ms')
    
    @commands.command(name='whomuted')
    async def whomuted(self, ctx):
        if await cog_check(ctx):
            try:
                return await ctx.reply(", ".join([member.name for member in ctx.guild.members if member.is_timed_out()]), mention_author=False)
            except:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! No one is muted currently...", mention_author=False)
    
    @commands.command(name='avatar', aliases=['avi'])
    async def avatar(self, ctx, member:discord.Member=None):
        if await cog_check(ctx):
            member = member or ctx.author
            e = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.purple())
            if member.display_avatar.url != member.avatar.url:
                e.set_thumbnail(url=member.avatar.url)
            e.set_image(url=member.display_avatar.url)
            e.set_footer(text=f"Requested by: {ctx.message.author.name}")
            return await ctx.reply(embed=e, mention_author=False)
    
    @commands.command(name='emote')
    async def emote(self, ctx, emote:discord.Emoji):
        if await cog_check(ctx):
            embed = discord.Embed(color=discord.Color.purple())
            embed.description=f"**__Emote Information__**\n**URL**: {emote.url}\n**Name**: {emote.name}\n**ID**: {emote.id}"
            embed.set_image(url=emote.url)
            return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='startpoll')
    async def startpoll(self, ctx):
        if await cog_check(ctx):
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            def get_emoji(number):
                return self.emojis[number - 1]
    
            prompt = await ctx.reply('You have 30 seconds to give me the question to ask!', mention_author=False)
            try:
                question = await self.bot.wait_for('message', check=check, timeout=30)
            except TimeoutError:
                return await ctx.reply("Time's up! You didn't provide me with a question...", mention_author=False)
            await question.delete()
            prompt = await prompt.edit(content='You now have 1 minute to give me all the possible poll options! Remember, I cannot start a poll with less than 2 options and more than 10 options. Also, all options will be separated by a space.', allowed_mentions=discord.AllowedMentions.none())
            try:
                options = await self.bot.wait_for('message', check=check, timeout=60)
            except TimeoutError:
                return await ctx.reply("Time's up! You didn't provide me with any options...", mention_author=False)
            options_list = options.content.split()
            if len(options_list) < 2:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You can\'t have a poll with less than 2 options...', mention_author=False)
            elif len(options_list) > 10:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You can\'t have a poll with more than 10 options...', mention_author=False)
            await options.delete()
            await prompt.delete()
    
            poll_embed = discord.Embed(title=f"{ctx.author.name} started a poll!", description=f"**{question.content.upper()}**", color=discord.Color.purple())
            poll_embed.set_thumbnail(url=ctx.author.avatar.url)
            for i, option in enumerate(options_list, 1):
                emoji = get_emoji(i)
                poll_embed.add_field(name=f"{emoji} Option {i}", value=option, inline=False)
            poll_embed.set_footer(text="React to vote!")
            await ctx.message.delete()
            poll_message = await ctx.send(embed=poll_embed)
            for i in range(1, len(options_list) + 1):
                emoji = get_emoji(i)
                await poll_message.add_reaction(emoji)
            return None

    @commands.command(name='convert')
    async def convert(self, ctx, value: float, org_unit: str, new_unit: str):
        if await cog_check(ctx):
            org_unit = org_unit.lower()
            new_unit = new_unit.lower()
            unit_mapping = {"f": "F", "c": "C"}

            if (org_unit, new_unit) in self.conversions:
                result = self.conversions[(org_unit, new_unit)](value)
                org_unit = unit_mapping.get(org_unit, org_unit)
                new_unit = unit_mapping.get(new_unit, new_unit)
                return await ctx.reply(f"{value} {org_unit} is equal to {result:.2f} {new_unit}.", mention_author=False)
            else:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Invalid conversion...", mention_author=False)
            
    @commands.command(name='translate')
    async def translate(self, ctx, *, phrase):
        if await cog_check(ctx):
            try:
                detected_language = self.translator.detect(phrase)
                if detected_language.lang != 'en':
                    translated_text = self.translator.translate(phrase, src=detected_language.lang, dest='en')
                    return await ctx.reply(f"Translated: {translated_text.text}\n\n*Beware of some inaccuracies. I cannot be 100% accurate...*", mention_author=False)
                else:
                    await shark_react(ctx.message)
                    return await ctx.reply("Wups! Message is already in English...", mention_author=False)
            except Exception as e:
                return await ctx.reply(f"Wups! A translation error occurred... ({e})", mention_author=False)
    
    @commands.command(name='grabber')
    async def grabber(self, ctx, platform: str, *query):
        if await cog_check(ctx) and await in_wom_shenanigans(ctx):
            try:
                query = " ".join(query)
                if query[0] == '<' and query[-1] == '>':
                    query = query[1:-1]
                elif query[0] == '[' and query [-1] == ')':
                    await shark_react(ctx.message)
                    return await reply(ctx, "Wups! I couldn't download anything in an embedded link. Try again... ")
            except IndexError:
                await shark_react(ctx.message)
                return await reply(ctx, "Wups! I need a search query...")
            
            if platform.lower() not in self.platforms:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! Invalid platform choice! Must be either `Spotify`, `SoundCloud`, `YouTube`, or `Emulation`...')

            async with ctx.typing():
                if platform in self.platforms[0:3]:
                    msg = await ctx.reply('Hang tight! I\'ll try downloading your song. You\'ll be pinged with your song once I finish.', mention_author=False)

                    if platform == 'spotify':
                        if query.__contains__('/artist/') or query.__contains__('/album/') or query.__contains__('/playlist/'):
                            await msg.delete()
                            await shark_react(ctx.message)
                            return await reply(ctx, "Wups! I don't want to bombard you with pings! Try downloading songs individually...")
                        
                        print(f"{Style.BRIGHT}Downloading from {Fore.BLACK}{Back.GREEN}Spotify{Fore.RESET}{Back.RESET}{Style.RESET_ALL}...")
                        spotdl = await create_subprocess_exec('spotdl', 'download', query, '--lyrics', 'synced', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = await spotdl.communicate()
                        print(f"{Style.BRIGHT}Out{Style.RESET_ALL}:\n{stdout.decode()}{Style.BRIGHT}Err{Style.RESET_ALL}:\n{stderr.decode()}\n")
                        if "LookupError" in stdout.decode():
                            await msg.delete()
                            await shark_react(ctx.message)
                            return await reply(ctx, "Wups! I couldn't find a song on Spotify with that query. Try again... ")
                        if spotdl.returncode != 0:
                            await msg.delete()
                            await shark_react(ctx.message)
                            return await reply(ctx, "Wups! I couldn't download anything. Try again... ")
                        
                    elif platform == 'youtube':
                        print(f"{Style.BRIGHT}Downloading from {Fore.WHITE}{Back.RED}YouTube{Fore.RESET}{Back.RESET}{Style.RESET_ALL}...")
                        ytdl = await create_subprocess_exec('yt-dlp', f'ytsearch:"{query}"', '-x', '--audio-format', 'mp3', '--output', '%(title)s.%(ext)s', '--no-playlist', '--embed-metadata', '--embed-thumbnail', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = await ytdl.communicate()
                        print(f"{Style.BRIGHT}Out{Style.RESET_ALL}:\n{stdout.decode()}{Style.BRIGHT}Err{Style.RESET_ALL}:\n{stderr.decode()}")
                        if 'Downloading 0 items' in stdout.decode():
                            await msg.delete()
                            await shark_react(ctx.message)
                            return await ctx.reply("Wups! I couldn't download anything. Try again... (Most likely, your search query was invalid.)")
                        
                    elif platform == 'soundcloud':
                        if query[0:23] != 'https://soundcloud.com/':
                            await msg.delete()
                            await shark_react(ctx.message)
                            return await ctx.reply("Wups! I couldn't download anything. Try again... (Due to API requirements, you must make sure that you are providing a `https://soundcloud.com/` link as your query.)")
                        index = query.find("?in=")
                        if index != -1:
                            query = query[:index]
                        if query[-1] == '/':
                            query = query[:-1]
                        print(f"{Style.BRIGHT}Downloading from {Fore.WHITE}{Back.LIGHTRED_EX}SoundCloud{Fore.RESET}{Back.RESET}{Style.RESET_ALL}...")
                        scdl = await create_subprocess_exec('scdl', '-l', query, '--onlymp3', '--force-metadata', '--no-playlist', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = await scdl.communicate()
                        print(f"{Style.BRIGHT}Out{Style.RESET_ALL}:\n{stdout.decode()}\n{Style.BRIGHT}Err{Style.RESET_ALL}:\n{stderr.decode()[:-1]}")
                        if 'Found a playlist' in stderr.decode():
                            await msg.delete()
                            await shark_react(ctx.message)
                            return await reply(ctx, "Wups! I don't want to bombard you with pings! Try downloading songs individually...")
                        if 'URL is not valid' in stderr.decode():
                            await msg.delete()
                            await shark_react(ctx.message)
                            return await reply(ctx, "Wups! Invalid URL! Try again...")

                    new_files = [file for file in os.listdir('.') if file.endswith(".mp3")]
                    for file in new_files:
                        file_path = os.path.join('.', file)
                        try:
                            await ctx.reply(content='Here is your song!', file=discord.File(file_path))
                        except:
                            os.remove(file_path)
                            await msg.delete()
                            await shark_react(ctx.message)
                            return await reply(ctx, 'Wups! The file was too big for me to send...')
                        os.remove(file_path)
                    return await msg.delete()
                else:
                    if query.lower() not in self.consoles.keys():
                        consolesTemp = []
                        for console in self.consoles.keys():
                            console = f"`{console}`"
                            consolesTemp.append(console)
                        await shark_react(ctx.message)
                        return await reply(ctx, f"Wups! Invalid console choice! Must exactly one from the following list...\n{", ".join(consolesTemp)}")
                    for key, value in self.consoles.items():
                        if query.lower() == key:
                            if key == 'n64':
                                return await reply(ctx, value + "\n*Go hog wild.\nUse `Mupen64Plus-Next` core on the emulator.*")
                            elif key == 'switch':
                                return await reply(ctx, value + "\n*Go hog wild.\nUse an adblocker for the ROM site.\nIf using an emulator, it doesn't matter which file format you download, but Megalon personally prefers NSP files!\nDownload the latest keys needed from the Keys site, open Ryujinx, click `File > Open Ryujinx Folder`, navigate to the `system` folder, drop the key files there.\nFrom the Firmware site, download the latest firmware, open Ryujinx, click `Tools > Install Firmware > Install a firmware from XCI or ZIP`, and then select your firmware ZIP. Make sure you do NOT extract it!*")
                            elif key == 'wiiu':
                                return await reply(ctx, value + "\n*Go hog wild.\nOn the Keys site, copy everything in the Pastebin, open Cemu, click `File > Open Cemu Folder`, and replace everything in `keys.txt` with what you copied from the Pastebin.*")
                            elif key == 'ps1':
                                return await reply(ctx, value + "\n*Go hog wild.\nOn the Emulator, click `Settings > BIOS`. Under BIOS Directory, choose the folder where you downloaded your BIOS to.*")
                            elif key == 'psvita':
                                return await reply(ctx, value + "\n*Go hog wild.\nDo NOT extract the ZIP file of the ROM you downloaded!\nIn the Emulator, click `File > Install .zip, .vpk` and then select the ZIP of your ROM.*")
                            else:
                                return await reply(ctx, value + "\n*Go hog wild.*")

            
async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
