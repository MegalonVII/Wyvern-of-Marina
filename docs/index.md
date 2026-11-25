!!! danger Danger
	This guide is meant to be read sequentially!

**This is a lengthy blob of documentation meant directly for developers for our Discord bot. Use this as needed for developing our bot.**

## Requirements
1. A UNIX based device that you are comfortable with leaving on 24/7. It **CANNOT** go to sleep **WHATSOEVER** *(ex. a Mac or a device running Linux. Something like a Raspberry Pi works perfectly, preferrably if you install the full Pi OS instead of just the CLI only version. In fact, this guide will be written under the assumption you are using the full OS version)*. If you are only looking to develop, the device does not need to be on 24/7 since you will not be hosting the bot.
2. The CLI tools I made. [1 (.env)](https://drive.google.com/file/d/1htVQKKKQkVwx-bPuQkk5E3eYB-Dbwh1y/view?usp=drive_link), [2 (womconf.sh)](https://drive.google.com/file/d/10I4aOdNgImAjimymyO3lF21XtvgEUVx-/view?usp=drive_link), [3 (wom) ((binary))](https://drive.google.com/file/d/1ybdpt6qtKXqR7DvY0N6WmYOXl0fyak0g/view?usp=sharing). Click on these links to download the files from my Google Drive. When downloading the ".env" file, it will try saving as just "env"; rename the file to ".env".

!!! warning Warnings
	1. This guide assumes you have never installed any of the specified requirements before! 
	2. The version of Python we will be installing will be compiled manually just so we have access to the direct list of `pip` libraries from PyPi!

## Steps
1. Copy/Paste the following gargantuan command in a terminal:
```
sudo apt update
sudo apt upgrade -y
sudo apt install -y git ffmpeg libopus-dev translate-shell make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev firefox
curl https://pyenv.run | bash
echo -e '\nexport PATH="$HOME/.pyenv/bin:$PATH"\neval "$(pyenv init --path)"\neval "$(pyenv init -)"\neval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc
pyenv install 3.14.7
pyenv global 3.14.7
```
	This will take a while and may require some user input from time to time for passwords and whatnot, but will install all necessary dependencies to your device. Grab a snack in the meantime.

2. Our executable relies on if you can use the `python3` command in your terminal. Try running `python3 --version`. and look for if it is running a version of Python that is in support but no later than 3.14. Support for Python 3.15 has not been tested yet.

3. Check if `pip3 --version` works. If it does, great. No need for a specific version of `pip3` but if you'd like you may upgrade it.

4. Create a GitHub account [here](https://github.com/signup) if you haven't already and sign into it. Then, go [here](https://github.com/settings/tokens/new) to create a new Personal Access Token. Make sure to choose the classic option, name it whatever you'd like, and to make it have no expiration! Also give this token all privileges. Once created copy this to a text file or somewhere you'll remember; we'll be needing it in a second.

5. Almost done with the scariest stuff! In your terminal enter:
```
git config --global user.name "(your github username)"
git config --global user.email "(your github email)"
git config --global credential.helper store
echo "https://(your github username):(your github token from earlier)@github.com" >> ~/.git-credentials
``` 
	Replace the items enclosed in parentheses with your appropriate values.

6. It should already be, but ensure that `/usr/local/bin` is in your PATH variable. This is done by doing `echo $PATH` and checking if `/usr/local/bin` is in the output. If not, do
```
echo "export PATH=\"/usr/local/bin:$PATH\"" >> ~/.bashrc
source ~/.bashrc
```
	This will be used for convenience later.

7. Download the CLI tools I made. Make sure that in your file explorer you have "Show hidden files" enabled. You can figure out how to do this.

8. Individually run
```
cd Downloads
nano womconf.sh
```
	This will open the `nano` text editor. This may look scary to newcomers but trust me it's pretty easy.

9. Edit the `EXPECTED_NAME`, `EXPECTED_EMAIL`, and the `WOM_DIR` variables with the name attached to your GitHub username, the email attached to your account, and the local directory you saved earlier respectfully. Do NOT get rid of the quotation marks before and after their values! Once done, press Ctrl+X, Y, then Enter to save the file. 

10. Enter `chmod +x wom`. This will make this file runnable through the terminal.

11. In your terminal run
```
sudo mv .env womconf.sh wom /usr/local/bin/
```

12. Run `wom`. This should display descriptions of commands and ASCII art of WoM itself. Also, it will be proof that we have the tools ready for now. We're not done quite yet, however.

13. If you are looking to host WoM, talk to the current host (at the time of writing, Neel) for WoM's token value. If you are just looking to develop, ignore the communication and get your own bot token from [here](https://discord.com/developers/applications).

14. `cd` into the directory where the repo cloned into earlier.

15. Run the following in the terminal:
```
mkdir csv
cp .env.example .env
nano .env
```
	Note that this `.env` file is DIFFERENT from the one we were originally working with!

16. Since we're back in the `nano` text editor, replace the string in quotes with your bot token you got earlier. Do NOT get rid of the quotes! Once done, press Ctrl+X, Y, then Enter to save the file.

17. Run `cd csv` in the terminal. 

18. If you are looking to host WoM, give Neel (yes, them in particular) your GitHub username. They will grant you access to a private GitHub repository containing a backup of WoM's CSV backend. This is so that there is a "cloud" based backup solution for these files, while also keeping them away from the public as they may contain sensitive personal information.

19. If you are looking to host WoM, once you've gotten access to that repository, back in the terminal `git clone` the link to the repository you gained access to.

20. Sign into your YouTube account on Firefox. This sounds random and oddly specific, but this is so that WoM can read your browser cookies for access to age-restricted videos to play in voice channels, and so Google's authentication server thinks you are human.

21. If you are looking to host WoM, ask the current host to stop running WoM. Once you've gotten confirmation that they've done that (WoM goes offline), you will run `cd` to go back to the $HOME folder and then `wom run`.

**WoM should now be online!**

## Expectations

If you only want to code for this bot and be able to test functionality, the set up process is largely the same. The only difference might be that when entering a token in step 16, it would be your test bot's token instead of WoM's direct token. Therefore, you will have direct access to all of WoM's functionality through your own bot instead of directly through WoM.

Additionally, if you run `wom` you will see a few developer specific inputs.

1. `wom edit (filename)`. This is for editing files tied to WoM.
2. `wom list`. This is to see all the valid filenames that can go with `wom edit`.
3. `wom add (filename) (0, 1, 2, or 3)`. This is to add a file to the list so that you might work on it through `wom edit`. Enter `0` as a parameter if you are adding a file to the root directory, `1` if you are adding it as an extension, `2` if you are adding it as a document, or `3` if you are adding it an image.
	- Extensions are where the categories for everything in `!w help` is found, and where all bot commands are programmed into. For example, `exts/admin.py` is where all administrative commands are coded and can be seen when entering `!w help admin`.
	- Documents are where you store external strings of information the bot makes use of. This is mainly implemented in the events extension, as there are just a lot of lists that the bot uses that were hogging up readable space to work in.
	- Images are self explanatory. However when adding the filename you are going to give the entire filepath instead. For example, `wom add /home/neel/Desktop/hi.png 3` will add the image to WoM's image directory for use in the project.
4. `wom remove (filename)`. This is to remove a file from the list so that in case it no longer becomes necessary you do not have to work on it.
!!! danger Requirements
	You are ***REQUIRED*** to post in the development thread whether or not you added or removed a file! This is so that the host and other testers can be notified of any changes so that they can `wom add` or `wom remove` that file from their `womconf.sh` setup!
5. `wom commit (message)`. This is to commit any changes you may have made directly to GitHub.
6. `wom status`. This is to check the status of the git repository.

You may notice I'm leaving out `wom run` and `wom pull`. This is because both the host and the testers are going to be using this. 

1. `wom run`'s use case is pretty self explanatory.
2. `wom pull` is to directly pull any changes to files from GitHub. However, it is important to note that if a tester had ran `wom add (a filename) (0, 1, 2, or 3)` or `wom remove (a filename)` you must also do so before running `wom pull`. This is to make sure there are no merge conflicts.

You are expected to not change anything in the `.env` file in `/usr/local/bin`, the `wom` executable, or get rid of the valid options originally set by me in `womconf.sh`. This is to make sure that everything is indeed set correctly through `wom add` or `wom remove` otherwise.

If you are looking to host WoM, every so often please make sure to commit these CSV files back to github! This is NOT covered by `wom commit`, so you will have to do this manually. `cd` into WoM's `csv` folder, `git add .`, `git commit -m "MM/DD/YY"`, `git push`. Replace MM with the number of the month, DD with the number of the day, and YY with the last 2 numbers of the year. This is to ensure that there is a semi recent backup of this information in the event that the host loses these files. Neel usually tries to do this once every month or so, but 2-3 weeks is also fine as well.

Developers, make sure that when making a new command **the function you'll be defining is no more than 20 lines of non-comment, non-empty code**! This seems like an impossible feat, but I will expand on this more in the section right below this mini-paragraph.

## utils.py

The `utils.py` file has a lot of helpful variables and functions that you most likely will use when developing functions for the bot. Think of this as if you could "`import wom"` to the top of the file you're working on, but instead you're doing `from utils import *`. Developers, if you make changes to this file **YOU ARE EXPECTED TO EDIT THIS DOCUMENTATION AND LET NEEL KNOW OF IT**! Speaking of, here's that documentation.

At the time of writing, the file is over 1600 lines of code long! it seems gargantuan, but the file is actually formatted very intentionally into separate categories.
- Global variables that may be useful when developing. more information on them below.
- One-off helper functions that are only really used when defining just a single command function. More often than not, in order to fit the arbitrary 20 line requirement for command functions, you'll most likely have to define a function in this category that contains all the processing logic for that command function.
- Class declarations that work in tandem with just one command function that require 3+ one-off helper functions.
- Class declarations that are used for playing music in vc. you will most likely ignore this, as vc implementation is largely complete.
- Reusable bot helper functions. more information on them below.

### Variables

#### files (list of strings)
This is a list of strings regarding all the `.csv` files in the `csv` folder with the exception of `birthday.csv` and `mix.csv`.

#### file_checks (dict of booleans)
This is a dict that is initially set to `False` for all values. This is used to check if a `.csv` file is empty or not.

#### lists (dict of dicts)
This is a dict that contains empty dicts inside of it. These inner dicts all will contain the information stored within a `.csv` file, as the bot will not be able to read directly from the `.csv` file.

#### user_info (dict)
This is an initial dict that will contain the information regarding users' birthdates and preferred timezones.

#### snipe_data (dict containing 4 dicts)
This is a dict that contains information about sniped messages from a channel.

#### editsnipe_data (dict containing 3 dicts)
This is a dict that contains information about edited messages from a channel, more specifically, what they were before being edited.

#### prev_steal_targets (dict)
This is a dict that contains information about who stole from somebody last.

#### target_counts (dict)
This is a dict that contains information about how many times somebody has to steal from another person before they can steal from someone else.

#### cooldowns (dict of floats)
This is a dict containing floats that mark how many seconds before a command can be used again globally.

#### last_executed (dict of ints)
This is a dict containing ints that mark how long ago in seconds a command that is affected by a cooldown was used.

#### starboard_emoji (str)
Self explanatory.

#### shame_emoji (str)
Self explanatory.

#### starboard_count (int)
Self explanatory. Used in both counts for hot seat and cold seat.

#### zenny (str)
Self explanatory.

#### starttime (None)
This gets changed into a datetime object upon starting the bot. This datetime object contains the information on the time the bot started up.

#### login_timezone (str)
Self explanatory.

#### tts_voice_aliases (dict containing 6 str key/value pairs)
For use when a user sets their TTS voice. It simply maps the library's voices with more human understandable options.

#### voice_id_to_alias (dict of 6 strs)
This dict contains a small for loop that maps voice IDs to aliases.

#### default_tts_voice (str)
Self explanatory.

#### MUTE_TIME_LIMITS (dict containing 5 str/tuple key/value pairs)
Self explanatory.

#### volume_adjustment (float)
This is used to indicate the volume level of music played in VC while a TTS message is playing over it. For example, if this value is 0.2, then music volume will be playing at 20% as a TTS message plays over the music. This value is read from a stored `.csv` file to maintain parity of the mix between downtimes.

#### tts_volume_adjustment (float)
This is used to indicate the volume level of a TTS message played in VC while music is playing over it. For example, if this value is 0.2, then TTS volume will be playing at 20% as a TTS message plays over the music. This value is read from a stored `.csv` file to maintain parity of the mix between downtimes.

### Reusable Functions

#### create_list(filename: str)
This is a function that stores the information from a `.csv` file in the `csv` folder to a dict in the lists variable. Be sure to pass a valid file from the files variable into the parameter, unless you are trying to create a new `.csv` file!
- filename refers to the name of the `.csv` file to read from, without the extension.

#### create_birthday_list()
This is a function that stores the information from `csv/birthday.csv` to the user_into dict.

#### update_birthday(user_id: int, birthdate: str, tz: str)
This is a function that updates information regarding birthdays to `csv/birthday.csv` and stores it into the bot's memory.
- user_id refers to a user's ID tied to their discord account.
- birthdate refers to a user's birthdate.
- tz refers to a user's preferred timezone.

#### check_reaction_board(message: discord.Message, reaction_type: str)
This is a function that checks if a message is eligible for either hot seat or cold seat.
- message refers to the exact message that we are trying to parse.
- reaction_type refers to whether we want to check for if a message is eligible for one of the seats. ("starboard" or "shameboard" in our case).

#### add_to_board(message: discord.Message, board_type: str)
This is a function that adds a deserving message to a board. Additionally, it also works to edit the "star" or "tomato" count of the message. This function also adds to or removes from a hidden "karma" value that each human member has, which dictates their chances of "success" in roulette.
- message refers to the exact message that we are trying to parse.
- board_type refers to the type of board (seat) we need to send the message to.

#### reply(ctx: discord.Context, content: str)
This is a function I made that simplifies the process of end output that the bot will display. Wholly unnecessary, and is just for convenience in development.
- ctx refers to the context in which the bot is responding to.
- content refers to the message's content.

#### prompt_for_message(bot: discord Bot object, ctx: discord.Context, prompt_text: str, timeout: float, timeout_text: str, timeout_wups: bool = True) -> Optional\[tuple\[discord.Message, discord.Message\]\]
This function is less complicated than it seems. It simply prompts a user to send a certain message within a certain amount of seconds.
- bot refers to the bot instance, typically `self.bot` since more often than not the function will run under an extension.
- ctx refers to the context in which the bot is responding to.
- prompt_text refers to the text that will display when the bot prompts a user for the message.
- timeout refers to how much time in seconds the user has to respond before timing out.
- timeout_text refers to the text that displays with the bot times out of the prompt.
- timeout_wups refers to whether or not the bot will return an error to the user if the prompt times out.

#### add_coins(userID: int, coins: int)
This is a function that adds coins (zenny) to `csv/coins.csv` for a specified user.
- userID refers to a user's ID tied to their discord account.
- coins refers to how much zenny you are adding to their balance.

#### subtract_coins(userID: int, coins: int)
This is a function that tries to subtract coins (zenny) from a specified user in their balance dictated in `csv/coins.csv`. This function returns a boolean value.
- userID refers to a user's ID tied to their discord account.
- coins refers to how much zenny you are subtracting from their balance.

#### dual_spend(userID: int, spending: int)
This is a function that tries to subtract coins (zenny) from both of a specified user's balance dictated in `csv/coins.csv` and `csv/bank.csv`. This function returns a boolean value.
- userID refers to a user's ID tied to their discord account.
- spending refers to how much zenny you are subtracting from their balances.

#### add_item(itemName: str, userID: int, quantity: int)
This is a function that adds the specified quantity of items to `csv/{itemName}.csv` for a specified user. Please use an itemName that exists in the files variable!
- itemName refers to the name item we are trying to add to.
- userID refers to a user's ID tied to their discord account.
- quantity refers to how much of said item you are adding to their inventory.

#### subtract_item(itemName: str, userID: int, quantity: int)
This is a function that tries to subtract the specified quantity of items to `csv/{itemName}.csv` for a specified user. This function returns a boolean value. Please use an itemName that exists in the files variable!
- itemName refers to the name item we are trying to subtract from.
- userID refers to a user's ID tied to their discord account.
- quantity refers to how much of said item you are subtracting from their inventory.

#### dep(userID: int, coins: int)
This is a function that tries to subtract coins (zenny) from a user's row in `csv/coins.csv` to add to the value to their row in `csv/bank.csv`. This function returns a boolean value.
- userID refers to a user's ID tied to their discord account.
- coins refers to how much zenny you are adding to their bank balance.

#### wd(userID: int, coins: int)
This is a function that tries to subtract coins (zenny) from a user's row in `csv/bank.csv` to add to the value to their row in `csv/coins.csv`. This function returns a boolean value.
- userID refers to a user's ID tied to their discord account.
- coins refers to how much zenny you are subtracting from their bank balance.

#### direct_to_bank(userID: int, coins: int)
This is a function that directly adds funds to a user's section in`csv/bank.csv`.
- userID refers to a user's ID tied to their discord account.
- coins refers to how much zenny you are adding to their bank balance.

#### stolen_funds(userID: int , coins: int)
This is a function that directly tries to remove funds from a user's section in `csv/bank.csv`.
- userID refers to a user's ID tied to their discord account.
- coins refers to how much zenny you are subtracting from their bank balance.

#### in_wom_shenanigans(ctx)
This is a function that checks if a command is being used in the #wom-shenanigans channel in the server. This function returns a boolean value.
- ctx refers to the context in which the bot is responding to.

#### in_channels(ctx, channels: list of strs, giveResponse: bool)
This is a function that checks if a command is being used in any of the specified channels in the channels list.
- ctx refers to the context in which the bot is responding to.
- channels refers to a list of channel names that use of the tied command is permitted in.
- giveResponse refers to whether the bot should rudely respond back with what channels to use the command in or not.

#### in_threads(ctx, channels: list of strs, giveResponse: bool)
This is a function that checks if a command is being used in any of the specified threads in the channels list.
- ctx refers to the context in which the bot is responding to.
- channels refers to a list of thread names that use of the tied command is permitted in.
- giveResponse refers to whether the bot should rudely respond back with what channels to use the command in or not.

#### assert_cooldown(command: str, user_id: int)
This is a function that checks to see if a command can be used again. Returns an integer value. Make sure to input the name of a command in the cooldowns variable!
- command refers to the name of the command that the cooldown is being asserted for.
- user_id refers to the user's user id, obtained from their profile.

#### cooldown_remaining(command: str, user_id: int) -> int
This is a function that returns how many more sections until a user can use a certain command again. Returns an integer value. Make sure to input the name of a command in the cooldowns variable!
- command refers to the name of the command that the cooldown is being asserted for.
- user_id refers to the user's user id, obtained from their profile.

#### capitalize_string(string: str)
This is a function that properly formats a string for a pokédex entry from its API output. No need for it in any other function. Returns a string.
- string refers to the string that needs to be formatted.

#### shark_react(message: discord.Message)
This is a function used whenever something goes wrong. The shark react is meant to tell the user that something went wrong with their processing. I only made this function to avoid having to manually input the unicode character for the shark emoji every time. More often than not, the parameter when coding is going to be `ctx.message`.
- message refers to the messabe object that will be reacted to.

#### wups(ctx, content: str)
This is a function used whenever you want to tell the end user when something went wrong. This is the function you're going to use more often than not instead of shark_react. The output message from wom would be "Wups! {content}..." so write the content accordingly.
- ctx refers to the context in which the bot is responding to.
- content refers to the message that the error sends to the user.

#### load_info(info: str)
This is a function used to load information from the `docs` folder stored as a `txt` file. Returns a list. Whatever info you want to load the `txt` file must be named the same thing. For example, if you want to load `self.triggers` in the `events.py` file, make sure `triggers.txt` exists in the `docs` folder.
- info refers to the name of the file to read from in the `docs` folder, without the extension.

### Important Note for Developers

The `load_emulation()` and `load_help()` functions found in `utils.py` are things that would take a while to explain, yet it is extremely important to understand how they work despite their status as one off helpers. This is because they work in tandem with manually tampered text files in the `docs` folder of the repository root.

#### load_emulation()
This is a function used to load all the information related to WoM's `emulation` command. The command doesn't take any inputs, yet it reads from 3 files in the `docs` folder: `consoles.txt`, `links.txt`, and `instructions.txt`. the reading from these files is hard coded into the function. If you'd like to add instructions, make sure that...
- In `consoles.txt`, you add the console's name in one word and in all lowercase. Numbers are okay. For example, in a new line you should write "ps4". Additionally, I've done my best to try to group consoles according to manufacturer and form factor. I have ordered them such that they go ...
	1. Nintendo home console
	2. Nintendo handheld console
	3. PlayStation home console
	4. PlayStation handheld console
	5. Sega console
	6. Xbox home console
	Make sure that if you're going to add, say, "ps4" to the list then it goes below "ps3" in the `consoles.txt` file.
- In `links.txt`, you format your links such that they appear formatted as covered and have embeds hidden. This means they follow the format of \[word(s) to display](<link from browser\>). also, each console's relevant links must be all in one line of the `.txt` file and separated by commas. Finally, there is an order that links follow when a user inputs a command: emulator, ROMs, BIOS, anything else after; make sure to adhere to this. Remember that if your console you're adding is in line, say, 15 of `consoles.txt` your links set should also be in line 15 of `links.txt`!
- In `instructions.txt`, you input all your instructions for that console in one line. Remember that if your console you're adding is in line, say, 15 of `consoles.txt` your instruction set should also be in line 15 of `instructions.txt`! Instructions are denoted by "1. " or "2. ", so on. They are NOT to be separated by pressing Enter on your keyboard but by simply typing "\n" as if this were MarkDown. Generally speaking your steps 1 and 2 can be copy pasted from other consoles, as they are going to most likely be the same regardless of console. You may notice that once instructions are finished there are 2-3 tidbits that WoM provides per console about how to reaccess an emulated game and how to add more games to the emulator's UI; Make sure to separate those by "\n\-" in the line of text. A final word of advice: try to keep your instruction set easy to understand but fitted within 1500 characters of text, as it is very easy to go off the rails and hit Discord's 2000 character per message limitation with this command!

#### load_help()
This is a function used to load all the information related to WoM's custom `help` command. The command doesn't take any inputs, yet it reads from very specific files in the `docs` folder. The reading from these files is hard coded into the function. if you'd like to add to the embed, make sure that...
- If you used `wom add` to add a new extension, in `help_pages.txt` make sure to add the name of this new extension to a new line. if not, don't worry about this.
- In the `docs` folder you will see `.txt` files that there are for commands and their descriptions sorted by extension name. For example, you will see `admin_commands.txt` and `admin_descriptions.txt`, and you'll see `music_commands.txt` and `music_descriptions.txt`. If you used `wom add` to add a new extension, make sure to also `wom add` the appropriate `.txt` files as documents. If not, just `wom edit` the appropriate `.txt` files as they should already be enlisted as documents.
- The relevant `commands.txt` files contain high level descriptions on how a member can use these commands. For example, `admin_commands.txt` includes `!w unmute (@member)` as a description of using the `unmute` command. If you added a new command to any extension, regardless of if you just made it or not, be sure to include it in a new line in the appropriate `commands.txt` file.
- The relevant `descriptions.txt` files contain short, high level descriptions on what commands do. For example, when talking about the `birthdaylist` command, `birthday_descriptions` contains a line that says "`See a list of all birthdays in the server!`". If you added a new command to any extension, regardless of if you just made it or not, be sure to include it in a new line in the appropriate `descriptions.txt` file.