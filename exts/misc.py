import discord
from asyncio import subprocess, create_subprocess_exec
from discord.ext import commands
from googletrans import Translator
from colorama import Fore, Back, Style
from utils import *

# misc commands start here
# ping, whomuted, avi, emote, convert, translate, grabber
class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
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
            'nes': { # retroarch
                "links": "[Emulator](<https://www.retroarch.com/?page=platforms>), [ROMs](<https://vimm.net/vault/NES>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - NES / Famicom (Mesen)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply navigate through `Main Menu > Load Content > (the location of your ROM)`."
            },
            'snes': { # retroarch
                "links": "[Emulator](<https://www.retroarch.com/?page=platforms>), [ROMs](<https://vimm.net/vault/SNES>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - SNES / SFC (Snes9x 2010)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply navigate through `Main Menu > Load Content > (the location of your ROM)`."
            }, 
            'n64': { # retroarch
                "links": "[Emulator](<https://www.retroarch.com/?page=platforms>), [ROMs](<https://vimm.net/vault/N64>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - Nintendo 64 / Mupen64Plus-Next` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply navigate through `Main Menu > Load Content > (the location of your ROM)`."
            }, 
            'gamecube': { # dolphin
                "links": "[Emulator](<https://dolphin-emu.org/download/>), [ROMs](<https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/>)",
                "instructions": "1. Download the beta version of the emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In Dolphin, click `View > Grid View`.\n4. In the main window, click `Config > Interface > Download Game Covers from GameTDB.com for Use in Grid Mode`.\n5. Click on the `Paths` tab on top. Add the directory where you stored your ROM. Optionally, also tick off `Search Subfolders` as this looks for any ROMs inside any folders that are inside the path you added.\n6. Click on the `General` tab. In the `Auto Update Settings` portion, choose the `Beta` option. Close out of the `Config` window.\n7. Click `Controllers` in the main window. Configure controls as you need. Close out of the `Controllers` window.\n\\- From now on, whenever you open Dolphin quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up on Dolphin, simply add another ROM to the same folder (or any folders in that folder) that you listed in step 5."
            }, 
            'wii': { # dolphin
                "links": "[Emulator](<https://dolphin-emu.org/download/>), [ROMs](<https://myrient.erista.me/files/Redump/Nintendo%20-%20Wii%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/>)",
                "instructions": "1. Download the beta version of the emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In Dolphin, click `View > Grid View`.\n4. In the main window, click `Config > Interface > Download Game Covers from GameTDB.com for Use in Grid Mode`.\n5. Click on the `Paths` tab on top. Add the directory where you stored your ROM. Optionally, also tick off `Search Subfolders` as this looks for any ROMs inside any folders that are inside the path you added.\n6. Click on the `General` tab. In the `Auto Update Settings` portion, choose the `Beta` option. Close out of the `Config` window.\n7. Click `Controllers` in the main window. Configure controls as you need. Close out of the `Controllers` window.\n\\- From now on, whenever you open Dolphin quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up on Dolphin, simply add another ROM to the same folder (or any folders in that folder) that you listed in step 5."
            }, 
            'wiiu': { # cemu
                "links": "[Emulator](<https://github.com/cemu-project/Cemu/releases>), [ROMs](<https://myrient.erista.me/files/Redump/Nintendo%20-%20Wii%20U%20-%20WUX/>), [Keys](<https://pastebin.com/GWApZVLa>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In Cemu, click `File > Open Cemu folder`.\n4. You should see a `keys.txt` file. Open it. It should just have an example key in it.\n5. Open the link to the rest of the keys. Copy the entire Pastebin document and paste it into your `keys.txt` file. Save the document and close it and the Cemu folder.\n6. In the Cemu main window, click `Options > General settings`. In the `Game Paths` section, add the directory where you stored your ROM. It will automatically search recursively. Close out of the `General settings` window.\n7. Click `Options > Input settings`, and configure controls to your liking. Close out of the `Input settings` window.\n8. In the main window right click. It should open a menu. Click `Style: Icons` and then `Refresh game list`.\n\\- From now on, whenever you open Cemu quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up on Cemu, simply add another ROM to the same folder (or any folders in that folder) that you listed in step 6."
            },
            'switch': { # ryujinx
                "links": "[Emulator](<https://ryujinx.org/download>), [ROMs](<https://www.ziperto.com/nintendo-switch-nsp-list/>), [Firmware](<https://prodkeys.net/ryujinx-firmware/>), [Keys](<https://prodkeys.net/ryujinx-prod-keys/>)", 
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault by scrolling down to the downloads section. Use an adblocker when accessing the vault. If your ROM of choice has multiple parts, download all parts and extract them all at once. It doesn't matter whether you download a `.xci` or a `.nsp`. Use MegaUp if possible as your download client. Once you've extracted your ROM, store it to somewhere of your choosing.\n3. Download the latest `prod.keys` file from the keys site.\n4. Download the latest firmware from the firmware site. Do NOT extract this `.zip` file!\n5. A popup will appear on screen telling you to open their set up guide. Follow their guide to a tee, as they did my job for me!\n6. Below the `File` and `Options` buttons, there should be options for the view mode of their UI. Click the icons toggle right below `Options`.\n7. Adjust the `Icon Size` slider as much as you want. Optionally, also tick off `Show Names` right next to the slider.\n8. At the bottom left corner of the window, hit the refresh button.\n\\- From now on, whenever you open Ryujinx quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up on Ryujinx, simply add another ROM to the same folder (or any folders in that folder) that you listed when following the set up guide."
            },
            'gb': { # retroarch
                "links": "[Emulator](<https://www.retroarch.com/?page=platforms>), [ROMs](<https://vimm.net/vault/GB>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - Game Boy / Color (SameBoy)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply navigate through `Main Menu > Load Content > (the location of your ROM)`."
            }, 
            'gbc': { # retroarch
                "links": "[Emulator](<https://www.retroarch.com/?page=platforms>), [ROMs](<https://vimm.net/vault/GBC>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - Game Boy / Color (SameBoy)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply navigate through `Main Menu > Load Content > (the location of your ROM)`."
            },
            'gba': { # retroarch
                "links": "[Emulator](<https://www.retroarch.com/?page=platforms>), [ROMs](<https://vimm.net/vault/GBA>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - Game Boy Advance (mGBA)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply navigate through `Main Menu > Load Content > (the location of your ROM)`."
            }, 
            'ds': { # melonds
                "links": "[Emulator](<https://melonds.kuribo64.net/downloads.php>), [ROMs](<https://vimm.net/vault/DS>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. Near where you left your ROM, create `saves`, `states`, and `cheats` folders for reference later.\n4. Launch melonDS. Click `Config > Path settings`. Match each path you see on screen with the folders you created earlier. Click OK at the bottom.\n5. Click `Config > Input settings`. Edit the controls as you see fit. Optionally, click on the `General hotkeys` tab and adjust those. Click OK at the bottom.\n6. Click `File > Open ROM`. Locate where you stored your ROM and hit Open.\n\\- melonDS supports multiplayer through creating a second instance! Simply click `System > Multiplayer > Launch new instance`, then load your ROM by clicking on the new melonDS window and loading your ROM through `File > Open ROM`.\n\\- If that's not your thing, melonDS also supports Wi-Fi! In your game, enter the Wi-Fi settings, edit the DNS settings for `melonAP` by selecting `No` on `Auto-Obtain DNS`. Enter the primary DNS as `167.86.108.126` and the secondary as `1.1.1.1`.\n\\- From now on, your last 10 played DS ROMs are listed in `File > Open recent > (your ROM)`. Just click on your ROM from there.\n\\- To load more ROMs, simply click `File > Open ROM`."
            }, 
            '3ds': { # lime3ds / citra
                "links": "[Emulator](<https://github.com/Lime3DS/Lime3DS/releases/>), [ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%203DS%20%28Decrypted%29/>)",
                "instructions": "1. Download the `.7z` file for the emulator for your platform. Extract using 7-Zip.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. Open the `lime-qt` application. Do NOT open the version that just says `lime` or `lime-room`!\n4. Double click the Lime3DS main window to add the directory of where you stored your ROM.\n5. Once you've added your directory, do NOT click on your game just yet! Click on `Emulation > Configure` and then click on the `Controls` tab. Edit accordingly. Optionally, edit any hotkeys you want. Click OK at the bottom.\n7. On the Lime3DS main window above your game, you should see the folder location it is looking from. Right click it and click `Scan Subfolders`.\n\\- From now on, whenever you open Lime3DS quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up on Lime3DS, simply drag your other ROM into the same folder you specified in step 4."
            }, 
            'ps1': { # retroarch (different setup)
                "links": "[Emulator](<https://www.retroarch.com/?page=platforms>), [ROMs](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation/>), [BIOS](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%20-%20BIOS%20Images/>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice. The ROM should have both a `.bin` and a `.cue` file. They are both important. If your game has multiple discs, download and extract all the archives that contain each disc of your game.\n3. Follow [these instructions](<https://retrogamecorps.com/2023/02/06/the-ultimate-rom-file-compression-guide/#CHD>) for converting your ROM file(s) to `.chd` format for your OS. Once that's done, you can delete the original `.bin` and `.cue` file(s). If your game has multiple discs, follow [this tutorial](<https://youtu.be/1PZORGQU73c>) to consolidate your `.chd` files into a single ROM.\n4. Download `ps-41a.zip` and `ps-41e.zip` from the BIOS site. Extract both archives.\n5. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n6. Scroll down to `Sony - PlayStation (PCSX ReARMed)` and select it.\n7. Back out to the Main Menu, and go to the Settings section. Enter `Settings > Directory`. Look at where your `System/BIOS` directory is.\n8. In your file explorer, move your extracted BIOS files into that folder that RetroArch listed was for your BIOS files.\n9. Back in RetroArch, back out to the `Main Menu`, and select `Main Menu > Load Content > (location of your ROM)`.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply navigate through `Main Menu > Load Content > (the location of your ROM)`."
            }, 
            'ps2': { # pcsx2
                "links": "[Emulator](<https://pcsx2.net/>), [ROMs](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%202/>), [BIOS](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%202%20-%20BIOS%20Images/>), [Covers](<https://www.steamgriddb.com/>)",
                "instructions": "1. Download emulator for your platform. Either the stable or nightly work.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. Download the `ps2-0230a-20080220.zip`, `ps2-0230e-20080220.zip`, and `ps2-0230j-20080220.zip` archives from the BIOS site. Extract them all.\n4. Open PCSX2. Change the theme if you'd like, otherwise press `Next`.\n5. Click `Open BIOS Folder`. Drag and drop the BIOS `.bin` files you extracted earlier into the folder. Close the file explorer windows. Click `Refresh List` in PCSX2. Finally, select a BIOS. Click `Next`.\n6. Click `Add...` and add the directory in which your ROM is stored. Optionally, click `Yes` to scan recursively. Click `Next` twice and then `Finish`.\n7. In the main UI, click the icon that looks like 4 rectangles in the top left.\n8. Click `Settings > Controller > Controller Port 1`. Rebind as you'd like, and optionally bind any hotkeys. Click `Close`.\n9. If your game doesn't have cover art, go to the covers website and download some cover art for your game through search. Right click your game on PCSX2 and choose `Set Cover Image`. Select the image you downloaded from the website.\n\\- From now on, whenever you open PCSX2 quick access to your ROM will be available right in front of you. Just double click on your game.\n\\- To add more ROMs to PCSX2, simply add your ROM to the folder (or any subfolders of it) you specified in step 6. If the game does not automatically grab cover art, download some from the covers site and set the cover image of the game."
			},
            'ps3': { # rpcs3
                "links": "[Emulator](<https://rpcs3.net/download>), [ROMs](<https://vimm.net/vault/PS3>), [BIOS](<https://www.playstation.com/en-us/support/hardware/ps3/system-software/>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice. Your folder that you just extracted should look something like...\n```Game Name\n	- Game Name\n		- (game contents...)\n	- README\n```\nRename the folder in the first folder to anything else and move it out of that folder. Delete the original folder.\n3. Open RPCS3. Tick the two boxes on the bottom saying you've read the Qucikstart guide and to not show you this box again. Then click `Continue`.\n4. If you were flashed with a giant bright white window, click on `Config` in that window. Go to the GUI tab, and change the UI stylesheet to whatever you'd like and press `Apply` then `Save`.\n5. In the main window, press the `Grid` icon.\n6. Go to the BIOS site, scroll down to where it says `Update using a computer` and click that menu, then click `Download PS3 Update`. If your browser blocks the download calling it malicious, just tell it to continue the download.\n7. Once that's done, in RPCS3 click `File > Install Firmware`. Select the firmware you just downloaded. If you immediately booted into the firmware, close out of it for now.\n8. Remember the folder we just moved that had our game in it? *THAT* is your ROM! In RPCS3, click the `Open` icon on the top left. Select the folder with the game's contents in it. If the game opened up immediately after, just close it for now.\n9. In the main window, click on the `Pads` icon. Rebind controls as needed.\n10. Now you can launch your game!\n\\- From now on, whenever you open RPCS3 quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To add more ROMs to RPCS3, simply click `Open` and select the folder with your game's contents in it."
            }, 
            'psp': { # ppsspp
                "links": "[Emulator](<https://www.ppsspp.org/download/>), [ROMs](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%20Portable/>)",
                "instructions": "1. Download emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. Open PPSSPP. The UI is very easy to navigate with just your mouse. Scroll through your directories and find your game. Just click on it. Default controls are set to...\n```Arrow Keys - D-Pad\nZ - X\nX - O\nA - Triangle\nS - Square\nTab - Speed Up\nEnter/Return - Start```\n\\- From now on, whenever you open PPSSPP quick access to your ROM will be in the `Recent` tab of the UI, just click on your game from there.\n\\- To add more games to PPSSPP, click on the `Games` tab of the emulator UI and move your other ROM to the folder that is shown on the top left corner of PPSSPP. Then, just click the `Refresh` button at the top of the emulator window. (It looks like a curly arrow). Just click on your game from there."
            }, 
            'psvita': { # vita3k
                "links": "[Emulator](<https://vita3k.org/>), [ROMs](<https://nopaystation.com/>)",
                "instructions": "1. Download emulator for your platform.\n2. Download the NoPayStation client for your platform. In the NPS Browser, select `PSV Games` in whatever region and then search for your game. Click `Download` and your game should appear in your `Downloads` directory once complete. Do NOT extract the `.zip` file(s), as that is/those are the ROM(s)!\n3. Open Vita3k. Keep clicking `Next` until you see the option to download required files. Download both of them, then hit `Install Firmware File`. Select one of the files, and once that's done make sure to tick `Delete Archive?`. Do it again for the other firmware file. Click `Next` once done.\n4. Tick the box for `Grid Mode`, as it gives a more \"authentic\" Vita look to the UI. Click `Next` and then `OK`.\n5. In the next popup, untick `Show this again` and then click `OK`.\n6. Vita3k will prompt you to create a new user. Please do that. Once that's done, tick `Automatic User Login` at the bottom of the window and then click on your user.\n7. Click the screen to unlock your \"Vita\". From here, click `File > Install .zip, .vpk`. Select the ROM you downloaded earlier. Once that's done, tick `Delete Archive?`, as it's not necessary anymore.\n9. Optionally, configure any controls in the `Controls` panel.\n\\- From now on, whenever you open Vita3k quick access to your ROM will be available right in front of you. Just click on your game.\n\\- To add more ROMs to Vita3k, simply click `File > Install .zip, .vpk` and then select your ROM. Once finished, make sure to tick `Delete Archive?`."
            }
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
        if await cog_check(ctx):
            query = " ".join(query)
            try:
                if query[0] == '<' and query[-1] == '>':
                    query = query[1:-1]
                elif query [0] == '[' and query[-1] == ')':
                    await shark_react(ctx.message)
                    return await reply(ctx, "Wups! I couldn't download anything in an embedded link. Try again... ")
            except IndexError:
                await shark_react(ctx.message)
                return await reply(ctx, "Wups! I need a search query... ")
            if platform.lower() in self.platforms[0:3]: # music
                if await in_wom_shenanigans(ctx):

                    async with ctx.typing():
                        msg = await ctx.reply('Hang tight! I\'ll try downloading your song. You\'ll be pinged with your song once I finish.', mention_author=False)

                        if platform.lower() == 'spotify': # spotify
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
                            
                        elif platform.lower() == 'youtube': # youtube
                            print(f"{Style.BRIGHT}Downloading from {Fore.WHITE}{Back.RED}YouTube{Fore.RESET}{Back.RESET}{Style.RESET_ALL}...")
                            ytdl = await create_subprocess_exec('yt-dlp', f'ytsearch:"{query}"', '-x', '--audio-format', 'mp3', '--output', '%(title)s.%(ext)s', '--no-playlist', '--embed-metadata', '--embed-thumbnail', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            stdout, stderr = await ytdl.communicate()
                            print(f"{Style.BRIGHT}Out{Style.RESET_ALL}:\n{stdout.decode()}{Style.BRIGHT}Err{Style.RESET_ALL}:\n{stderr.decode()}")
                            if 'Downloading 0 items' in stdout.decode():
                                await msg.delete()
                                await shark_react(ctx.message)
                                return await ctx.reply("Wups! I couldn't download anything. Try again... (Most likely, your search query was invalid.)")
                            
                        elif platform.lower() == 'soundcloud': # soundcloud
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

            elif platform.lower() == self.platforms[3]: # emulation
                if await in_channels(ctx, ["gamig", "gamig-2-coming-soon", "wom-shenanigans"], False):
                    if query.lower() not in self.consoles.keys():
                        consolesTemp = []
                        for console in self.consoles.keys():
                            console = f"`{console}`"
                            consolesTemp.append(console)
                        await shark_react(ctx.message)
                        return await reply(ctx, f"Wups! Invalid console choice! Must exactly one from the following list...\n{", ".join(consolesTemp)}")
                    for key, value in self.consoles.items():
                        if query.lower() == key:
                            return await reply(ctx, f"# {value['links']}\n{value['instructions']}\n\n*Go hog wild.*")
                elif await in_threads(ctx, ['Rip-bozotendo'], False):
                    if query.lower() not in self.consoles.keys():
                        consolesTemp = []
                        for console in self.consoles.keys():
                            console = f"`{console}`"
                            consolesTemp.append(console)
                        await shark_react(ctx.message)
                        return await reply(ctx, f"Wups! Invalid console choice! Must exactly one from the following list...\n{", ".join(consolesTemp)}")
                    for key, value in self.consoles.items():
                        if query.lower() == key:
                            return await reply(ctx, f"# {value['links']}\n{value['instructions']}\n\n*Go hog wild.*")
                else:
                    ids = []
                    for channel in ["gamig", "gamig-2-coming-soon", "wom-shenanigans"]:
                        ids.append(f"<#{discord.utils.get(ctx.guild.channels, name=channel).id}>")
                    for thread in ["Rip-bozotendo"]:
                        ids.append(f"<#{discord.utils.get(ctx.guild.threads, name=thread).id}>")
                    await shark_react(ctx.message)
                    return await reply(ctx, f"this command can only be used in the following channels: {", ".join(ids)}. go to one of those channels, jackass")
            else:
                await shark_react(ctx.message)
                return await reply(ctx, 'Wups! Invalid platform choice! Must be either `Spotify`, `YouTube`, `SoundCloud`, or `Emulation`...')    

            
async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))