# Wyvern of Marina
Proprietary Discord bot for the server called "The Marina" written in Discord.py. While the code may be open-source, **it is NOT intended for distribution or reproduction!** The open-source nature is for people in the server to see the inner workings of the bot and join in on the coding if they so choose. 

# Commands
This is also viewable from the `main.py` file in this repo, and also in our Discord server via `!w help`.

## Fun
1. `!w say (output)` *Repeats the output given.*
2. `!w customcommands` *Returns a list of custom commands created by the moderation.*
3. `!w snipe` *Returns the last deleted message in a given channel. Note that you only have 60 seconds to do this!*
4. `!w editsnipe` *Same thing as the snipe command, just for edited messages.*
5. `!w choose (options, separated by a space)` *Chooses between certain options given.*
6. `!w pokedex (national dex number)` *Returns information about the Pokémon.*
7. `!w who (remainder of question)` *Returns a random name from the list of all human members to answer your question.*
8. `!w howgay ([Optional] @member)` *As a joke, returns a random percentage of how gay the user is.*
9. `!w rps (choice)` *Play a game of Rock-Paper-Scissors with the bot.*
10. `!w 8ball (question)` *Have a magic 8-Ball answer your question.*
11. `!w roulette ([Admin Only] @member)` *Play a game of Russian Roulette with the bot. Moderation can roulette members for them.*
12. `!w trivia ([Optional] type)` *Answer trivia questions given by the bot.*
13. `!w quote` *Returns a quote from a video game character from an API.*
14. `!w deathbattle (@user)` *Bot creates an imaginary scenario where 2 users fight to the death.*

## Economical
1. `!w slots` *Simulates a slot machine.*
2. `!w bet (amount)` *Play a betting game with the bot.* 
3. `!w steal (@member)` *Steal Zenny from another member.* 
4. `!w heist` *Steal from the bank.*
5. `!w deposit (amount)` *Deposit your Zenny to the bank.* 
6. `!w withdraw (amount)` *Withdraw Zenny from your bank account.* 
7. `!w balance ([Optional] @member)` *Returns the amount of Zenny you have on hand. May peer into wallets of others for a cost of 10 Zenny*  
8. `!w bankbalance` *Returns the amount of Zenny you have in the bank.*  
9. `!w paypal (@member) (amount)` *Pay Zenny to a server member.*  
10. `!w marketplace` *Returns a board of items that you may purchase with your Zenny.*  
11. `!w buy (item name) ([Optional] number requested)` *Purchase an item from the marketplace with your Zenny. Number requested defaults to 1.*  
12. `!w sell (item name) ([Optional] number requested)` *Sell an item in your inventory for half the price. Number value defaults to 1.*  
13. `!w inventory` *Returns the items you have on hand.*  
14. `!w use (item name)` *Use an item from your inventory.*

## Administrative
1. `!w createcommand (name) (output)` *Creates a custom macro.*
2. `!w deletecommand (name)` *Deletes a custom macro.*
3. `!w clear (number of messages)` *Deletes a number of messages from a chat. Ranges from 1-10 to avoid API rate limits.*
4. `!w kick (@member)` *Kicks a member from the server.*
5. `!w ban (@member)` *Bans a member from the server.*
6. `!w mute (@member) (time amount)(s, m, h, d, or w)` *Mutes mentioned member for specified time. "s" for seconds, "m" for minutes, "h" for hours, "d" for days, and "w" for weeks. No space in between the time amount and the letter!*
7. `!w unmute (@member)` *Unmutes mentioned member.*

## Flair
1. `!w addflair (@role) [Admin Only]` *Adds a role to the list of self-assignable flairs.*
2. `!w deleteflair (@role) [Admin Only]` *Deletes a role from the list of self-assignable flairs.*
3. `!w listflairs` *Lists all self-assignable flairs.*
4. `!w im (role name)` *Gives/removes specified flair from user.*

## Birthday
1. `!w birthday` *Allows member to register their birthday with the bot following on screen prompts.*
2. `!w birthdaylist` *Displays a list of all the birthdays of each server member registered with the bot.*

## Musical
1. `!w join` *Joins the asker's voice call.*
2. `!w leave` *Leave the asker's voice call.*
3. `!w play (YouTube URL or search query)` *Plays the tracks requested from the query in the voice call.*
4. `!w now` *Displays currently playing track in text channel.*
5. `!w queue (optional: page number)` *Displays the queue of songs incoming to the voice call.*
6. `!w shuffle` *Shuffles queue. DJs or Admins only.*
7. `!w remove (index)` *Removes song at index of queue. DJs, Admins, or song requester only.*
8. `!w pause` *Pauses current song.*
9. `!w resume` *Resumes paused song.*
10. `!w stop` *Clears queue and stops currently playing song.*
11. `!w skip` *Skips to next song in queue. DJs, Admins, or song requester only.*

## Miscellaneous
1. `!w ping` *Returns bot response time in milliseconds.*
2. `!w whomuted` *Returns a list of all muted members.*
3. `!w avatar ([Optional] @member)` *Returns the profile picture of either the user or the specified member.*
4. `!w emote (emoji from the server)` *Returns information about the emoji in our server.*
5. `!w startpoll` *Start a poll within a specified channel.*
6. `!w convert (number) (original unit) (new unit)` *Converts the number of original units to the same amount in the new unit. Supported units are F, C, m, ft, kg, lb, mi, km, in, and cm. Supported conversions are F <-> C, ft <-> m, lb <-> kg, mi <-> km, and in <-> cm.*