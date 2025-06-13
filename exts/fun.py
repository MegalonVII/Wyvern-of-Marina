import discord
from discord.ext import commands
import random
import asyncio
from datetime import timedelta
import requests
import json
import urllib.parse
import pypokedex as dex

from utils import lists, snipe_data, editsnipe_data, zenny # utils direct values
from utils import cog_check, shark_react, reply, wups, capitalize_string, assert_cooldown, in_wom_shenanigans, add_coins, in_channels, in_threads # utils functions

# fun commands start here
# say, custc, snipe, esnipe, choose, pokedex, who, howgay, rps, 8ball, roulette, trivia, emulation, quote, deathbattle, ship
class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.actions = ["{} poisons {}'s drink!", "{} places a frag mine beneath {}'s feet!", "{} passes {} a blunt!", "{} burns down {}'s house!"]
        self.deaths = [" {} dies of dysentery!", " {} explodes!", " {} took one hit of the Blunt9000™️ and descends straight to Hell!", " {} got caught in the fire and burns down to a crisp!"]
        self.survivals = [" {} noticed this and gets another drink...", " {} quickly steps aside...", " {} kindly rejects the offer...", " {} quickly got out of the fire and finds shelter elsewhere..."]
        self.shipNotes = ["Ugh! How did you two even become friends in the first place?", "You two are just better off as friends...", "Don't ruin your friendship over this...", "Take it easy now...", "Something might be sparking...", "I could potentially see it happening.", "Maybe it could work!", "You two should try going out on casual dates!", "Give it a shot!", "It's a match made in Heaven!", "I don't think it's possible to create a better pairing!"]
        self.consoles = {
            'nes': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20Entertainment%20System%20%28Headered%29/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - NES / Famicom (Mesen)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            },
            'snes': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Super%20Nintendo%20Entertainment%20System/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - SNES / SFC (Snes9x 2010)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            }, 
            'n64': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%2064%20%28BigEndian%29/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - Nintendo 64 / Mupen64Plus-Next` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            }, 
            'gamecube': { # dolphin
                "links": ["[Dolphin](<https://dolphin-emu.org/download/>)", "[ROMs](<https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In Dolphin, click `View > Grid View`.\n4. In the main window, click `Config > Interface > Download Game Covers from GameTDB.com for Use in Grid Mode`.\n5. Click on the `Paths` tab on top. Add the directory where you stored your ROM. Optionally, also tick off `Search Subfolders` as this looks for any ROMs inside any folders that are inside the path you added.\n6. Click on the `General` tab. In the `Auto Update Settings` portion, choose the `Beta` option. Close out of the `Config` window.\n7. Click `Controllers` in the main window. Configure controls as you need. Close out of the `Controllers` window.\n\\- From now on, whenever you open Dolphin quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up on Dolphin, simply repeat step 2. Extract to the folder you listed in step 5."
            }, 
            'wii': { # dolphin
                "links": ["[Dolphin](<https://dolphin-emu.org/download/>)", "[ROMs](<https://myrient.erista.me/files/Redump/Nintendo%20-%20Wii%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In Dolphin, click `View > Grid View`.\n4. In the main window, click `Config > Interface > Download Game Covers from GameTDB.com for Use in Grid Mode`.\n5. Click on the `Paths` tab on top. Add the directory where you stored your ROM. Optionally, also tick off `Search Subfolders` as this looks for any ROMs inside any folders that are inside the path you added.\n6. Click on the `General` tab. In the `Auto Update Settings` portion, choose the `Beta` option. Close out of the `Config` window.\n7. Click `Controllers` in the main window. Configure controls as you need. Close out of the `Controllers` window.\n\\- From now on, whenever you open Dolphin quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up on Dolphin, simply repeat step 2. Extract to the folder you listed in step 5."
            }, 
            'wiiu': { # cemu
                "links": ["[Cemu](<https://github.com/cemu-project/Cemu/releases>)", "[ROMs](<https://github.com/Xpl0itU/WiiUDownloader/releases>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download and open the WiiUDownloader client for your platform. Follow onscreen prompts for region and platform (Cemu).\n3. Search for the desired game/update/DLC. Check `Decrypt contents` and `Delete encrypted contents after decryption`. Finally, check whatever game/update/DLC you want then click on `Download queue`. Download to a directory of choice.\n4. Open Cemu, then go to `File > Install game title, update, or DLC...`. Click `Open` on any of the folders that you downloaded. Delete these folders after installation.\n5. Go to `Tools > Title manager`. Right click on the game base and select on `Convert to compressed Wii U archive (.wua)`. Save the ROM to a new location, and keep this location in mind. Delete the original folders after conversion. Close out of the title manager.\n6. Right click on the Cemu main UI and select `Refresh game list`.\n7. Go to `Options > General settings`. Add the directory where you stored your `.wua` file(s) in the `Game Paths` box. Close out of the `General settings` window.\n8. Configure controls in `Options > Input settings`. Close out of the `Input settings` window.\n9. Right click on the main window. Click `Style: Icons` and then `Refresh game list`.\n\\- From now on, whenever you open Cemu quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up on Cemu, simply repeat steps 3-9. Place `.wua` file(s) in the same folder that you listed in step 7."
            },
            'gb': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - Game Boy / Color (SameBoy)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            }, 
            'gbc': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Color/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - Game Boy / Color (SameBoy)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            },
            'gba': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Advance/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Nintendo - Game Boy Advance (mGBA)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            }, 
            'ds': { # melonds
                "links": ["[melonDS](<https://melonds.kuribo64.net/downloads.php>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20DS%20%28Decrypted%29/>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. Near where you left your ROM, create `saves`, `states`, and `cheats` folders for reference later.\n4. Launch melonDS. Click `Config > Path settings`. Match each path you see on screen with the folders you created earlier. Click OK at the bottom.\n5. Click `Config > Input settings`. Edit the controls as you see fit. Optionally, click on the `General hotkeys` tab and adjust those. Click OK at the bottom.\n6. Click `File > Open ROM`. Locate where you stored your ROM and hit Open.\n\\- melonDS supports multiplayer through creating a second instance! Simply click `System > Multiplayer > Launch new instance`, then load your ROM by clicking on the new melonDS window and loading your ROM through `File > Open ROM`.\n\\- If that's not your thing, melonDS also supports Wi-Fi! In your game, enter the Wi-Fi settings, edit the DNS settings for `melonAP` by selecting `No` on `Auto-Obtain DNS`. Enter the primary DNS as `167.235.229.36` and the secondary as `1.1.1.1`.\n\\- From now on, your last 10 played DS ROMs are listed in `File > Open recent > (your ROM)`. Just click on your ROM from there.\n\\- To load more ROMs, simply repeat steps 2 and 6."
            }, 
            '3ds': { # azahar
                "links": ["[Azahar](<https://github.com/azahar-emu/azahar/releases>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%203DS%20%28Decrypted%29/>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. Open the `azahar` application. Do NOT open the version that says `azahar-room`!\n4. Double click the Azahar main window to add the directory of where you stored your ROM.\n5. Once you've added your directory, do NOT click on your game just yet! Click on `Emulation > Configure` and then click on the `Controls` tab. Edit accordingly. Optionally, edit any hotkeys you want. Click OK at the bottom.\n7. On the Azahar main window above your game, you should see the folder location it is looking from. Right click it and click `Scan Subfolders`.\n\\- From now on, whenever you open Azahar quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up on Azahar, simply repeat step 2. Extract to the same folder you specified in step 4."
            },
            'switch': { # greemdev ryujinx
                "links": ["[Ryubing](<https://sor.bz/iFSur>)", "[ROMs](<https://sor.bz/7FbLS>)", "[Firmware](<https://prodkeys.net/ryujinx-firmware/>)", "[Keys](<https://prodkeys.net/ryujinx-prod-keys/>)", "[Ad blocker](<https://ublockorigin.com/>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download your ROM of choice from the vault by scrolling down to the downloads section. Use an adblocker when accessing the vault. Once you've extracted your ROM, store it to somewhere of your choosing. Be sure to download any update and/or DLC as well!\n3. Download the latest key files from the keys site. Extract the `.zip` file but do NOT delete it!\n4. Follow [this guide](<https://youtu.be/FkrYCXtiVI4>) in case your game has (an) `.nsp` file(s) for an update and/or DLC.\n5. Download the latest firmware from the firmware site. Do NOT extract this `.zip` file!\n6. In Ryujinx, go to `Actions > Install Keys` and `Install Firmware`, then choose `Install from ZIP` for both and select your earlier `.zip` files.\n7. Click on `Options > Settings > User Interface`. In the \"Game Directories\" section, click on `Add`. Select the folder where you extracted (and/or merged) your `.nsp` file from earlier and select it. Click `Apply` then `OK`.\n8. Below the `File and Options` buttons, there should be options for the view mode of their UI. Click the icons toggle right below Options.\n9. Adjust the `Icon Size` slider as much as you want. Optionally, also tick off `Show Names` right next to the slider.\n10. Click on `Options > Settings > Input`. Configure controls as you like. Click `Apply` then `OK`.\n11. At the bottom left corner of the window, hit the refresh button.\n\\- From now on, whenever you open Ryujinx quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To make more ROMs show up in Ryujinx, simply repeat steps 2 and 4 if needed. Extract to the same folder that you listed in step 7."
            },
            'ps1': { # duckstation
                "links": ["[DuckStation](<https://www.duckstation.org/>)", "[ROMs](<https://bit.ly/4gdjfkV>)", "[BIOS](<https://bit.ly/4cWoNh2>)", "[Covers](<https://bit.ly/3z0b8aV>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download and extract your ROM to a location of your choice. For multiple disc games, do this for each disc.\n3. Follow [this guide](<https://bit.ly/3TnHEuh>) to convert your file(s) to `.chd` format. Delete the original `.bin` and `.cue` file(s) once done. For multiple disc games, follow [this video](<https://youtu.be/1PZORGQU73c>) to put your `.chd` files into a playlist.\n4. Download `ps-41a.zip` and `ps-41e.zip` from the BIOS site. Extract both archives.\n5. Open DuckStation. Change the theme if need be. Press `Next`.\n6. Click `Open in Explorer`. Drag and drop the `.bin` files you extracted earlier into the folder. Close the explorer window. Click `Refresh List` then `Next`.\n7. Click `Add...` and add the folder where you stored your ROM. Click `Yes` to scan recursively. Click `Next` twice and then `Finish`.\n8. In the main UI, click the icon that looks like 4 rectangles in the top left.\n9. Click `Settings > Controller > Controller Port 1`. Rebind as needed, including any hotkeys. Click `Close`.\n10. Click the `Covers` link in this message. Follow the on screen instructions for downloading covers with the first link.\n\\- From now on, whenever you open DuckStation quick access to your ROM will be available right in front of you. Just double click on your game. For multiple disc games each disc will show up, so on DuckStation right click each disc and click `Exclude from List`. Only the `.m3u` file should be listed then.\n\\- To add more ROMs to DuckStation, repeat steps 2, 3, and 10. Extract to the same folder as the one in step 7."
            }, 
            'ps2': { # pcsx2
                "links": ["[PCSX2](<https://pcsx2.net/>)", "[ROMs](<https://bit.ly/4gsD8oq>)", "[BIOS](<https://bit.ly/4gl7lpp>)", "[Covers](<https://bit.ly/4g9LmS2>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. Follow [this guide](<https://bit.ly/3TnHEuh>) to convert your file to `.chd` format. Delete the original `.iso` file once done.\n4. Download the `ps2-0230a-20080220.zip`, `ps2-0230e-20080220.zip`, and `ps2-0230j-20080220.zip` archives from the BIOS site. Extract them all.\n5. Open PCSX2. Change the theme if you'd like, otherwise press `Next`.\n6. Click `Open BIOS Folder`. Drag and drop the BIOS `.bin` files you extracted earlier into the folder. Close the file explorer windows. Click `Refresh List` in PCSX2. Finally, select a BIOS. Click `Next`.\n7. Click `Add...` and add the directory in which your ROM is stored. Optionally, click `Yes` to scan recursively. Click `Next` twice and then `Finish`.\n8. In the main UI, click the icon that looks like 4 rectangles in the top left.\n9. Click `Settings > Controller > Controller Port 1`. Rebind as you'd like, and optionally bind any hotkeys. Click `Close`.\n10. Click the `Covers` link in this message. Follow the on screen instructions for downloading covers with the first link.\n\\- From now on, whenever you open PCSX2 quick access to your ROM will be available right in front of you. Just double click on your game.\n\\- To add more ROMs to PCSX2, repeat steps 2, 3, and 10. Extract to the same folder as the one in step 7."
			},
            'ps3': { # rpcs3
                "links": ["[RPCS3](<https://rpcs3.net/download>)", "[ROMs](<https://nopaystation.com/>)", "[BIOS](<https://www.playstation.com/en-us/support/hardware/ps3/system-software/>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download the NoPayStation client for your platform. In the NPS Browser, select `PS3 Games` in whatever region and then search for your game. Click `Download` and your game should appear in your `Downloads` directory once complete.\n3. Open RPCS3. Tick the two boxes on the bottom saying you've read the Quickstart guide and to not show you this box again. Then click `Continue`.\n4. If you were flashed with a giant bright white window, click on `Config` in that window. Go to the GUI tab, and change the UI stylesheet to whatever you'd like and press `Apply` then `Save`.\n5. In the main window, press the `Grid` icon.\n6. Go to the BIOS site, scroll down to where it says `Update using a computer` and click that menu, then click `Download PS3 Update`. If your browser blocks the download calling it malicious, just tell it to continue the download.\n7. Once that's done, in RPCS3 click `File > Install Firmware`. Select the firmware you just downloaded. If you immediately booted into the firmware, close out of it for now.\n8. In the main window, click on the `Pads` icon. Rebind controls as needed. Click `Save` when finished.\n9. Click `File > Install Packages/Raps/EDATS`. Navigate to the location of your download from the NPS Browser. Once it's finished installing that `.pkg`, you can delete the raw file as it is no longer needed.\n10. Now you can launch your game!\n\\- From now on, whenever you open RPCS3 quick access to your ROM will be located right in front of you. Just double click your game.\n\\- To add more ROMs to RPCS3, simply repeat steps 2 and 9."
            }, 
            'psp': { # ppsspp
                "links": ["[PPSSPP](<https://www.ppsspp.org/download>)", "[ROMs](<https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%20Portable/>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. Open PPSSPP. The UI is very easy to navigate with just your mouse. Scroll through your directories and find your game. Just click on it. Default controls are set to...\n```Arrow Keys - D-Pad\nZ - X\nX - O\nA - Triangle\nS - Square\nTab - Speed Up\nEnter/Return - Start```\n\\- From now on, whenever you open PPSSPP quick access to your ROM will be in the `Recent` tab of the UI, just click on your game from there.\n\\- To add more games to PPSSPP, simply repeat steps 2 and 3."
            }, 
            'psvita': { # vita3k
                "links": ["[Vita3k](<https://vita3k.org>)", "[ROMs](<https://nopaystation.com/>)"],
                "instructions": "1. Download the latest release of the emulator for your platform.\n2. Download the NoPayStation client for your platform. In the NPS Browser, select `PSV Games` in whatever region and then search for your game. Click `Download` and your game should appear in your `Downloads` directory once complete. Do NOT extract the `.zip` file(s), as that is/those are the ROM(s)!\n3. Open Vita3k. Keep clicking `Next` until you see the option to download required files. Download both of them, then hit `Install Firmware File`. Select one of the files, and once that's done make sure to tick `Delete Archive?`. Do it again for the other firmware file. Click `Next` once done.\n4. Tick the box for `Grid Mode`, as it gives a more \"authentic\" Vita look to the UI. Click `Next` and then `OK`.\n5. In the next popup, untick `Show this again` and then click `OK`.\n6. Vita3k will prompt you to create a new user. Please do that. Once that's done, tick `Automatic User Login` at the bottom of the window and then click on your user.\n7. Click the screen to unlock your \"Vita\". From here, click `File > Install .zip, .vpk`. Select the ROM you downloaded earlier. Once that's done, tick `Delete Archive?`, as it's not necessary anymore.\n8. Configure any controls in the `Controls` panel. Close out of that window when finished.\n9. Now you can enjoy your game!\n\\- From now on, whenever you open Vita3k quick access to your ROM will be available right in front of you. Just click on your game.\n\\- To add more ROMs to Vita3k, simply repeat steps 2 and 7."
            },
            'mastersystem': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Sega%20-%20Master%20System%20-%20Mark%20III/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Sega - MS/GG/MD/CD (Genesis Plus GX)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            },
            'genesis': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/No-Intro/Sega%20-%20Mega%20Drive%20-%20Genesis/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Sega - MS/GG/MD/CD (Genesis Plus GX)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            },
            'saturn': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/Redump/Sega%20-%20Saturn/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Sega - Saturn (Beetle Saturn)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            },
            'dreamcast': { # retroarch
                "links": ["[RetroArch](<https://www.retroarch.com/?page=platforms>)", "[ROMs](<https://myrient.erista.me/files/Redump/Sega%20-%20Dreamcast/>)"],
                "instructions": "1. Download the emulator for your platform. Do NOT download from Steam!\n2. Download your ROM of choice from the vault. Extract the ROM from the archive to a location of your choice.\n3. In RetroArch, navigate to `Main Menu > Online Updater > Core Downloader`. On a computer, the arrow keys are navigator, the Z key is to back out, and the X key is to advance.\n4. Scroll down to `Sega - Dreamcast/Naomi (Flycast)` and select it.\n5. Back out to the `Main Menu`, select `Load Content`. Select the appropriate drive where you stored your ROM. (i.e. the C:// drive).\n6. Navigate to the location of your ROM. Select your ROM.\n\\- If you need to, press `F1` (or `fn + F1`) on your keyboard to open the quick menu. Scroll down to `Controls` and reconfigure `Port 1 Controls` as you need.\n\\- From now on, whenever you open RetroArch quick access to your ROM will be located in the `History` section at the start. In that section, just select the ROM from the list and then hit `Play`.\n\\- To add more ROMs to your history, simply repeat steps 2, 5, and 6."
            }
            # add xbox, so this command can finally be finished
        }
        self.currentFight = False

    @commands.command(name='say')
    async def say(self, ctx, *args):
        if await cog_check(ctx):
            try:
                await ctx.message.delete()
                return await ctx.channel.send(" ".join(args).replace('"', '\"').replace("'", "\'"), allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
            except:
                return await wups(ctx, "You need something for me to say")
                
    @commands.command(name='customcommands', aliases=['custc'])
    async def customcommands(self, ctx):
        if await cog_check(ctx):
            try:
                return await reply(ctx, ', '.join(list(lists["commands"].keys())))
            except:
                return await wups(ctx, 'There are no custom commands')

    @commands.command(name='snipe')
    async def snipe(self, ctx):
        if await cog_check(ctx):
            channel = ctx.channel
            try:
                data = snipe_data[channel.id]
                if data["attachment"] and 'video' in data["attachment"].content_type:
                    data["content"] += f"\n[Attached Video]({data['attachment'].url})"
                embed = discord.Embed(title=f"Last deleted message in #{channel.name}", color = discord.Color.purple(), description=str(data["content"]))
                if data["attachment"] and 'image' in data["attachment"].content_type:
                    embed.set_image(url=data["attachment"].url)
                embed.set_footer(text=f"This message was sent by {data['author']}")
                embed.set_thumbnail(url=data['author'].avatar.url)
                return await ctx.reply(embed=embed, mention_author=False)
            except KeyError:
                return await wups(ctx, f"There are no recently deleted messages in <#{channel.id}>")

    @commands.command(name='editsnipe', aliases=['esnipe'])
    async def editsnipe(self, ctx):
        if await cog_check(ctx):
            channel = ctx.channel
            try:
                data = editsnipe_data[channel.id]
                embed = discord.Embed(title=f"Last edited message in #{channel.name}", color = discord.Color.purple(), description=str(data["content"]))
                embed.set_footer(text=f"This message was sent by {data['author']}")
                embed.set_thumbnail(url=data["author"].avatar.url)
                return await ctx.reply(embed=embed, mention_author=False)
            except KeyError:
                return await wups(ctx, f"There are no recently edited messages in <#{channel.id}>")

    @commands.command(name='choose')
    async def choose(self, ctx, *args):
        if await cog_check(ctx):
            if (len(args) < 2):
                return await wups(ctx, "You need at least 2 arguments for me to choose from")
            return await reply(ctx, f"I choose `{random.choice(args)}`!")

    @commands.command(name='pokedex')
    async def pokedex(self, ctx, index: int):
        if await cog_check(ctx):
            if index > 1017 or index < 1:
                return await wups(ctx, "Invalid index")
              
            async with ctx.typing():
                # data collections
                pokemon = dex.get(dex=index)
                res = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{index}')
                encRes = requests.get(f'https://pokeapi.co/api/v2/pokemon/{index}/encounters')
                pokRes = requests.get(f'https://pokeapi.co/api/v2/pokemon/{index}/')
                data = res.json()
                encData = encRes.json()
                pokData = pokRes.json()

                # random vars
                shinyInt = random.randint(1,512)
                name = [entry for entry in data["names"] if entry["language"]["name"] == "en"][0]["name"]

                # gender ratio calc
                if data['gender_rate'] == -1:
                    gender_ratio = "Genderless"
                elif data['gender_rate'] == 8:
                    gender_ratio = "100% Female"
                else:
                    female_percentage = (data['gender_rate'] / 8) * 100
                    male_percentage = 100 - female_percentage
                    gender_ratio = f"{male_percentage}% Male / {female_percentage}% Female"

                # location data calc
                locations = []
                for entry in encData:
                    locations.append(capitalize_string(entry['location_area']['name']))

                # moves data calc
                moves = []
                for entry in pokData['moves']:
                    moves.append(capitalize_string(entry['move']['name']))

                # make embed
                embed = discord.Embed(title=f'{name}, #{index}', color=discord.Color.red())
                embed.description = ''
                for i, type in enumerate(pokemon.types, 1):
                    embed.description += f'**Type {i}**: {capitalize_string(type)}\n'
                embed.description += '\n'
                for i, ability in enumerate(pokemon.abilities, 1):
                    embed.description += f'**Ability {i}**: {capitalize_string(ability.name)}{" *(Hidden)*" if ability.is_hidden else ""}\n'
                embed.description += '\n'
                embed.description += f'**Base HP**: {pokemon.base_stats.hp}\n'
                embed.description += f'**Base Attack**: {pokemon.base_stats.attack}\n'
                embed.description += f'**Base Defense**: {pokemon.base_stats.defense}\n'
                embed.description += f'**Base Special Attack**: {pokemon.base_stats.sp_atk}\n'
                embed.description += f'**Base Special Defense**: {pokemon.base_stats.sp_def}\n'
                embed.description += f'**Base Speed**: {pokemon.base_stats.speed}\n'
                embed.description += f'**Base Stat Total**: {pokemon.base_stats.hp + pokemon.base_stats.attack + pokemon.base_stats.defense + pokemon.base_stats.sp_atk + pokemon.base_stats.sp_def + pokemon.base_stats.speed}\n\n'
                embed.description += f'**Base Experience**: {pokemon.base_experience if pokemon.base_experience is not None else 0}\n'
                embed.description += f'**Base Happiness**: {data["base_happiness"]}\n'
                embed.description += f'**Capture Rate**: {data["capture_rate"]}\n\n'
                embed.description += f"**Egg Groups**: {', '.join(capitalize_string(name['name']) for name in [entry for entry in data['egg_groups']])}\n"
                embed.description += f"**Gender Ratio**: {gender_ratio}\n\n"
                embed.description += f"**Found At**: {', '.join(str(location) for location in locations) if len(locations) != 0 else 'No Location Data'}\n"
                embed.description += f"**Moves Learned**: {', '.join(str(move) for move in moves) if index != 151 else 'Every Move'}"

                try:
                    embed.set_thumbnail(url=pokemon.sprites.front.get('shiny')) if shinyInt == 1 else embed.set_thumbnail(url=pokemon.sprites.front.get('default'))
                    embed.set_footer(text=[entry for entry in data['flavor_text_entries'] if entry['language']['name'] == 'en'][0]['flavor_text'])
                except:
                    pass

                if shinyInt != 1:
                    return await ctx.reply(embed=embed, mention_author=False)
                else:
                    return await ctx.reply(content=f'Woah! A Shiny {name}! ✨', embed=embed, mention_author=False)

    @commands.command(name='who')
    async def who(self, ctx):
        if await cog_check(ctx):
            return await reply(ctx, f"`{ctx.message.content[3:]}`? {random.choice([member.name for member in ctx.message.guild.members if not member.bot])}")
        
    @commands.command(name='howgay')
    async def howgay(self, ctx, member:discord.Member=None):
        if await cog_check(ctx):
            if assert_cooldown("howgay") != 0:
                return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('howgay')} seconds")
        
            member = member or ctx.author
            percent = random.randint(0,100)
            responses = ['You\'re not into that mentally ill crap.', 'You\'re probably just going through a phase...', 'It\'s ok to be gay, buddy. We\'ll support you... unless you make it your entire personality.', 'You **LOVE** it up the rear end, don\'t you?']
            if percent >= 0 and percent <= 25:
                response = responses[0]
            elif percent >= 26 and percent <= 50:
                response = responses[1]
            elif percent >= 51 and percent <= 75:
                response = responses[2]
            elif percent >= 76 and percent <= 100:
                response = responses[3]
            
            return await reply(ctx, f"{member.name} is {percent}% gay. {response}")

    @commands.command(name='rps')
    async def rps(self, ctx, playerChoice: str=None):
        if await cog_check(ctx) and await in_wom_shenanigans(ctx):
            if assert_cooldown("rps") != 0 :
                return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('rps')} seconds")
            if playerChoice is None:
                return await wups(ctx, "You need to give me your choice")
            
            playerChoice = playerChoice.lower()
            choices = ['rock', 'paper', 'scissors']
            if playerChoice not in choices:
                return await wups(ctx, "Invalid choice")
            else:
                botChoice = random.choice(choices)
                if playerChoice == botChoice: # both tie
                    return await reply(ctx, f"I chose `{botChoice}`.\nUgh! Boring! We tied...")
                elif (playerChoice == choices[0] and botChoice == choices[1]) or \
                    (playerChoice == choices[1] and botChoice == choices[2]) or \
                    (playerChoice == choices[2] and botChoice == choices[0]): # bot wins
                        return await reply(ctx, f"I chose `{botChoice}`.\nHah! I win, sucker! Why'd you pick that one, stupid?")
                else: # bot loses
                    return await reply(ctx, f"I chose `{botChoice}`.\nWell played there. You have bested me...")

    @commands.command(name='8ball')
    async def eightball(self, ctx):
        if await cog_check(ctx):
            if assert_cooldown("8ball") != 0 :
                return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('8ball')} seconds")
            if len(ctx.message.content) < 9:
                return await wups(ctx, "You need to give me a question to respond to")
            
            responses = ['Hell yeah!', 'It is certain.', 'Without a doubt.', 'You may rely on it.', 'Yes, definitely.', 'It is decidedly so.', 'As I see it, yes.', 'Most likely.', 'Yes.', 'Outlook good.', 'Signs point to yes.', 'You already know the answer.', 'Reply hazy, try again.', 'Better not tell you now.', 'Ask again later.', 'Cannot predict now.', 'Concentrate and ask again.', 'Don\'t count on it.', 'Outlook not so good.', 'My sources say no.', 'Very doubtful.', 'My reply is no.', 'No.', 'Oh god, no.']
            return await reply(ctx, f"🎱 `{ctx.message.content[9:]}` 🎱\n{random.choice(responses)}")

    @commands.command(name='roulette')
    async def roulette(self, ctx, member:discord.Member=None):
        if await cog_check(ctx):
            if assert_cooldown("roulette") != 0:
                return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('roulette')} seconds")
            
            member = member or ctx.author
            chance = int(lists["karma"][str(member.id)])
            if member == ctx.author: # if a member wants to roulette themselves
                if not member.guild_permissions.administrator:
                    if random.randint(1,chance) == 1:
                        await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(hours=1), reason='roulette')
                        return await reply(ctx, "🔥🔫 You died! (muted for 1 hour)")
                    add_coins(member.id,1)
                    return await reply(ctx, f"🚬🔫 Looks like you\'re safe, for now... Here's 1 {zenny} as a pity prize...")
                return await reply(ctx, "❌🔫 Looks like you\'re safe, you filthy admin...")
            
            else: # if an admin wants to roulette a member they specify
                if not ctx.message.author.guild_permissions.administrator:
                    if member == ctx.author:  # roulette themselves if not admin (pinged themself)
                        if random.randint(1,chance) == 1:
                            await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(hours=1), reason='roulette')
                            return await reply(ctx, "🔥🔫 You died! (muted for 1 hour)")
                        add_coins(member.id,1)
                        return await reply(ctx, f"🚬🔫 Looks like you\'re safe, for now... Here's 1 {zenny} as a pity prize...")
                    return await reply(ctx, "❌🔫 A lowlife like you can\'t possibly fire the gun at someone else...")
                elif member == ctx.author: # admin tries rouletting themself
                    return await reply(ctx, "❌🔫 Admins are valued. Don\'t roulette an admin like yourself...")
                elif member.is_timed_out() == True: # admin tries rouletting a "dead" server member
                    return await reply(ctx, "❌🔫 Don\'t you think it\'d be overkill to shoot a dead body?")
                else:
                    if not member.guild_permissions.administrator: # admin tries rouletting "alive" non admin
                        if random.randint(1,chance) == 1:
                            await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(hours=1), reason='roulette')
                            return await reply(ctx, "🔥🔫 This user died! (muted for 1 hour)")
                        add_coins(member.id,1)
                        return await reply(ctx, f"🚬🔫 Looks like they\'re safe, for now... I gave them 1 {zenny} as a pity prize...")
                    return await reply(ctx, "❌🔫 Looks like they\'re safe, that filthy admin...")

    @commands.command(name='trivia')
    async def trivia(self, ctx, type:str = None):
        if await cog_check(ctx) and await in_wom_shenanigans(ctx):
            types = ['general', 'film', 'music', 'tv', 'games', 'anime']
            categories = [9, 11, 12, 14, 15, 31]
            if assert_cooldown('trivia') != 0:
                return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('trivia')} seconds")
            if not type is None and type.lower() not in types:
                return await wups(ctx, "Invalid trivia type")
            
            async with ctx.typing():
                if type is None:
                    response = requests.get(f"https://opentdb.com/api.php?amount=1&category={random.choice(categories)}&type=multiple&encode=url3986")
                else:
                    for typing, category in zip(types, categories):
                        if type.lower() == typing:
                            response = requests.get(f"https://opentdb.com/api.php?amount=1&category={category}&type=multiple&encode=url3986")
                            break
                data = json.loads(response.text)
                correct_answer = urllib.parse.unquote(data['results'][0]['correct_answer'])
                incorrect_answers = data['results'][0]['incorrect_answers']
                options = [urllib.parse.unquote(answer) for answer in incorrect_answers] + [correct_answer]
            random.shuffle(options)
            quiz_embed = discord.Embed(title="❓ Trivia ❓", description=urllib.parse.unquote(data['results'][0]['question']), color=discord.Color.purple())
            quiz_embed.add_field(name="Options", value="\n".join(options), inline=False)
            quiz_embed.set_footer(text="You have 15 seconds to answer. Type the letter of your answer (A, B, C, D).")
            await ctx.reply(embed=quiz_embed, mention_author=False)
        
            def check_answer(message):
                return message.author == ctx.author and message.content.lower() in ['a', 'b', 'c', 'd'] and message.channel == ctx.message.channel
        
            try:
                answer_message = await self.bot.wait_for('message', timeout=15.0, check=check_answer)
            except asyncio.TimeoutError:
                return await reply(ctx, f"Time's up! The correct answer was **{correct_answer}**.")
            else:
                if answer_message.content.lower() == 'a':
                    selected_answer = options[0]
                elif answer_message.content.lower() == 'b':
                    selected_answer = options[1]
                elif answer_message.content.lower() == 'c':
                    selected_answer = options[2]
                elif answer_message.content.lower() == 'd':
                    selected_answer = options[3]
        
                if selected_answer == correct_answer:
                    add_coins(ctx.author.id, 10)
                    return await answer_message.reply(f"Correct! The answer is **{correct_answer}**. 10 {zenny}!", mention_author=False)
                return await answer_message.reply(f"Sorry, that's incorrect. The correct answer is **{correct_answer}**.", mention_author=False)
            
    @commands.command(name='emulation')
    async def emulation(self, ctx, console: str = "guide"):
        if await cog_check(ctx) and (await in_channels(ctx, ["gamig", "gamig-2-coming-soon", "wom-shenanigans"], False) or await in_threads(ctx, ['Rip-bozotendo'], False)):
            if console == "guide":
                return await reply(ctx, "# __Emulation Wiki__\n\n## This is a wiki on how to get emulators for various systems set up on a PC!\n\n__**List of Valid Consoles**__ (enter as `!w emulation (console name)`)\n- NES\n- SNES\n- N64\n- GameCube\n- Wii\n- Wii U (enter as \"WiiU\")\n- GameBoy (enter as \"GB\")\n- GameBoy Color (enter as \"GBC\")\n- GameBoy Advance (enter as \"GBA\")\n- DS\n- 3DS\n- Switch\n- PS1\n- PS2\n- PS3\n- PSP\n- PS Vita (enter as \"PSVita\")\n- Master System (enter as \"MasterSystem\")\n- Genesis\n- Saturn\n- Dreamcast")
            elif console.lower() not in self.consoles.keys():
                return await wups(ctx, "You entered a console that isn't on the list of valid consoles. Please refer to the list by entering `!w emulation`")

            for key, value in self.consoles.items():
                if console.lower() == key:
                    return await reply(ctx, f"# {", ".join(value['links'])}\n{value['instructions']}\n\n*Go hog wild.*")
        else:
            ids = []
            for channel in ["gamig", "gamig-2-coming-soon", "wom-shenanigans"]:
                ids.append(f"<#{discord.utils.get(ctx.guild.channels, name=channel).id}>")
            ids.append(f"<#{discord.utils.get(ctx.guild.threads, name="Rip-bozotendo").id}>")
            await shark_react(ctx.message)
            return await reply(ctx, f"this command can only be used in the following channels: {", ".join(ids)}. go to one of those channels, jackass")

    @commands.command(name='quote')
    async def quote(self, ctx):
        if await cog_check(ctx):
            if await in_wom_shenanigans(ctx):
                if assert_cooldown('quote') != 0:
                    return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('quote')} seconds")
    
                async with ctx.typing():
                    response = requests.get(f'https://ultima.rest/api/quote?id={random.randint(1,560)}')
                    data = json.loads(response.text)
                quote = data['quote']
                character = data['character']
                title = data['title']
                release = data['release']
                embed = discord.Embed(title="💬 Quote 💬", description=f'"{quote}"', color=discord.Color.purple())
                embed.set_footer(text=f"From: {character} - {title}, {release}")
                return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='deathbattle', aliases=['db'])
    async def deathbattle(self, ctx, member: discord.Member):
        if await cog_check(ctx):
            if await in_wom_shenanigans(ctx):
                if self.currentFight:
                    return await wups(ctx, f"There is currently a fight going on")
                if member.bot:
                    return await wups(ctx, f"You can't fight a bot")
                  
                self.currentFight = True
                players = [ctx.author, member] if random.choice([True, False]) else [member, ctx.author]
                turn = 0
                am = discord.AllowedMentions.none()
                msg = await reply(ctx, f"{ctx.author.name} challenges {member.name} to the death!")
                await asyncio.sleep(3)
                while True:
                    actor, target = (players[0], players[1]) if turn % 2 == 0 else (players[1], players[0])
                    choiceNum = random.randint(0, len(self.actions) - 1)
                    action = self.actions[choiceNum]
                    await msg.edit(content=action.format(actor.name, target.name), allowed_mentions=am)
                    await asyncio.sleep(2)
                    determinant = random.randint(1, 5)
                    if determinant == 1:
                        response = action + self.deaths[choiceNum]
                    else:
                        response = action + self.survivals[choiceNum]
                    await msg.edit(content=response.format(actor.name, target.name, target.name), allowed_mentions=am)
                    if determinant == 1:
                        self.currentFight = False
                        break
                    else:
                        turn += 1
                        await asyncio.sleep(3)
                return None
            
    @commands.command(name='ship')
    async def ship(self, ctx: commands.Context, str1: str, str2: str):
        if await cog_check(ctx) and await in_wom_shenanigans(ctx):
            half_str1 = str1[:len(str1) // 2 + 1] if len(str1) % 2 == 1 else str1[:len(str1) // 2]
            half_str2 = str2[len(str2) // 2 + 1:] if len(str2) % 2 == 1 else str2[len(str2) // 2:]
            merged_string = half_str1 + half_str2
            embed = discord.Embed()
            bar = [':black_medium_square:' for _ in range(10)]
            shipPercent = random.randint(0, 100)
            shipBar = shipPercent // 10
            for i in range(0, shipBar):
                bar[i] = ':red_square:'

            finalStr = f":heartpulse: **MATCHMAKING** :heartpulse:\n:small_red_triangle_down: `{str1}`\n:small_red_triangle: `{str2}`"
            embed.color = discord.Color.pink()
            embed.title = f'**{merged_string}**'
            embed.description = f"**{shipPercent}%** {str(bar).replace(", ", "").replace("'", "")}{f" PERFECT! ❤" if shipPercent == 100 else ""}"
            embed.set_footer(text=f"*{self.shipNotes[shipBar]}*")
            return await ctx.reply(finalStr, embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(Fun(bot))
