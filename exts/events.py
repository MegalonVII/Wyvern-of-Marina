import discord
from discord.ext import commands, tasks
import pandas as pd
import asyncio
from pytz import timezone
from datetime import datetime
from re import escape, search, compile
from re import IGNORECASE
from random import randint, choice

from utils import lists, zenny, starboard_emoji, shame_emoji, user_info, snipe_data, editsnipe_data # utils direct values
from utils import assert_cooldown, shark_react, wups, add_coins, reply, direct_to_bank, check_reaction_board, add_to_board, create_list, create_birthday_list, add_item # utils functions

# bot events start here
# on_message, on_command_error, on_message_delete, on_message_edit, on_member_join, on_member_update, on_member_ban, on_reaction_add, on_member_remove, wish_birthday
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.triggers = [
            'yoshi',
            '3ds',
            'steam deck',
            'wednesday',
            'fat',
            'yuri',
            'yaoi',
            'ffxiv',
            'chud',
            'crank',
            'kys',
            'persona'
        ]
        self.trigger_emojis = [
            '<:full:1028536660918550568>',
            '<:megalon:1078914494132129802>',
            '<:megalon2:1395668583643615295>',
            '<:wednesday:798691076092198993>',
            '<:bulbous:1028536648922832956>',
            '<:vers:804766992644702238>',
            '<:packrat:1094890437099143198>',
            '<:vinesound1:808037201525866496>',
            '<:nothingeverhappens:1384703408509947934>',
            '🔧',
            '⚡',
            '🚿'
        ]
        self.games = [
            "Monster Hunter 4 Ultimate", 
            "Rain World", 
            "FINAL FANTASY TACTICS",
            "FINAL FANTASY VII", 
            "Baldur's Gate 3", 
            "Terraria", 
            "FINAL FANTASY XIV Online", 
            "Persona 4 Golden", 
            "Fire Emblem Echoes: Shadows of Valentia", 
            "Xenogears", 
            "Chrono Trigger",
            "Quake",
            "Dead Space",
            "NieR: Automata",
            "Hi-Fi Rush",
            "Shin Megami Tensei: Nocturne",
            "DOOM",
            "Katawa Shoujo",
            "Overwatch 2"
        ]
        self.messages = [
            "Try not to die of dysentery today!",
            "I hope you don't get AFK Corrin'd today!",
            "Hopefully something happens on this not-so-chuddy day!"
        ]
        self.reply_choices = [
            "yes",
            "no",
            "maybe",
            "absolutely",
            "not really",
            "definitely",
            "nah",
            "probably",
            "doubt it",
            "100%",
            "never",
            "ask again later",
            "without a doubt",
            "highly unlikely",
            "yep",
            "nope",
            "could be",
            "certainly not",
            "think so",
            "who knows?"
        ]
        self.reactions = [
            "damn thats crazy",
            "yea okay",
            "well thats time ill never get back",
            "how do i delete someone elses video",
            "im feeling a light 7 here",
            "and im giving this a 7 out of 10",
            "lets give it up for the real heroes reactors",
            "wiggling my toesies right now",
            "whoever made this i hope you become rich and successful",
            "transformative commentary",
            "sorry i wasnt paying attention",
            "sorry i zoned out",
            "oh wow thats really interesting",
            "lets watch that again",
            "burp",
            "cmon guys lets get this video trending",
            "cmon guys lets upvote this on reddit",
            "banger alert",
            "we are so back",
            "it is so over",
            "videos like this are why i love my country",
            "bro went sicko mode",
            "methinks this didnt really happen",
            "scratches chin",
            "its giving thanks",
            "its giving rizz",
            "its giving zest",
            "its giving staged",
            "its giving cringe",
            "its giving girlboss",
            "its giving sigma",
            "what year is it",
            "this couldnt be made today",
            "erm someone call the woke police",
            "and be sure to like and subscribe",
            "cant do that anymore because of woke",
            "bro just lost the woke contest",
            "bro just won the woke contest",
            "bro really thinks hes woke",
            "bro really thinks hes smooth",
            "methinks i just soiled me undies",
            "erm did they just say what i think they said",
            "bro really wants us to think hes funny",
            "bro not this again",
            "when you see it youll shit bricks",
            "yo can we roll that back",
            "if youre enjoying this video please subscribe and hit that bell",
            "not me laughing at this",
            "not me nose exhaling",
            "not me giggling and kicking my feet",
            "dude what whhhaaaaat",
            "next video",
            "next tiktok",
            "okay next one",
            "like this if youre watching in 2014",
            "edit thanks for the likes",
            "i like this one",
            "leave a comment telling me what your favorite part is",
            "i dont like this one",
            "i dont get this one",
            "this is my reacting face 🙂",
            "this is my reacting face 😲",
            "this is my reacting face 🤨",
            "yup its official this videos epic",
            "literally obsessed with their hair",
            "this is so barbie coded",
            "this is giving major gemini energy",
            "this video makes my tummy hurt",
            "like this video if your agree",
            "if you criticize me ill come straight to your home",
            "i dont know what those big words mean",
            "my commentary makes this transformative",
            "you guys are all my friends",
            "whoa woah",
            "checkmate atheists",
            "im literally dead",
            "certified banger",
            "only virgos can relate",
            "this is so capricorn coded",
            "did you know that most of my viewers arent subscribed to me",
            "the scorpio energys insane",
            "this is something only my fellow girlies will get",
            "methinks you should pound that like button",
            "videos like this are why i could never have kids",
            "obsessed with these vibes",
            "dudes going goblin mode",
            "this video makes me wanna hug my doggo",
            "bro has no life",
            "no way bro is real",
            "cant believe he did that",
            "now this is epic",
            "whoa what is bro doing",
            "look at all these confident leos",
            "now this is content",
            "uhhhhh uh meow",
            "omegalol omegalul",
            "nah ima do my own thang",
            "rate 5 stars if you like this video",
            "oh yea thats cute",
            "now this is for real mulch eaters",
            "it is what it is",
            "now thats what i call music",
            "erm so theres that",
            "wow i have no words",
            "uh yeah so thats a thing",
            "this is giving off woke vibes",
            "what the grimace shake",
            "skibidi dibidi doo dahh",
            "not with that attitude",
            "erm no comment",
            "its joever",
            "why would bro do that",
            "bro is wrong for that one",
            "poggers",
            "this is so millennial humor",
            "this is so millennial coded",
            "hubba hubba",
            "this is so gen z pilled",
            "hupty dupty",
            "only 90s kids can relate",
            "if you can relate to this congrats your childhood was epic",
            "check your privilege",
            "my timbers shivered",
            "chatgpt what do i say next",
            "thank you very cool",
            "yo bro im so confused",
            "nostalgia maxxing",
            "oh alright",
            "jelqmaxxing",
            "the math isnt mathing",
            "oof",
            "oh boy oh boy",
            "lol me too",
            "couldnt be me",
            "storytime",
            "is this what our founding fathers wanted",
            "erm this makes my head hurt",
            "damn daniel",
            "goonin with the boys",
            "well said",
            "now this is a libra moment",
            "zoo wee mama",
            "really makes you think huh",
            "this",
            "aha sir this is a wendys",
            "ruh-roh raggy",
            "psalm 69 those who hate me",
            "man thats tough",
            "bazinga",
            "thats so funny",
            "the lord answered bring me a heifer genesis 15 9",
            "old",
            "ezekiel 23 20 there she lusted",
            "none of these words are in the bible",
            "i do my own research",
            "what is this the united states of woke",
            "free thinkers unite",
            "john 11 35 jesus wept",
            "ah bro is killing me",
            "i love freebooting",
            "this really shows how oppressed gamers are",
            "no flesh shall be spared matthew 24 22",
            "erm check please",
            "ill have what shes having",
            "its giving awesomesauce",
            "slay slaaaayyy",
            "their vibe checked",
            "chat whats this guys address",
            "wildin",
            "bruh im so done bruh",
            "what the what",
            "what the skibidi rizz is up with that guy",
            "god is dead and we killed him",
            "god is alive and will cleanse this world of sin",
            "pussy in bio",
            "eat the rich",
            "thats totally me",
            "this is actual brainrot",
            "totes magotes",
            "was that the bite of 87",
            "duuuuude",
            "this feels like liberal propaganda",
            "amazeballs",
            "i bet bro is vaccinated",
            "can we give a shoutout to working moms",
            "this wins the internet",
            "only true fans will like and share this",
            "feeling old yet",
            "such a samantha thing to say",
            "she thinks shes a carrie but shes really a miranda",
            "some real hufflepuff energy",
            "erm did that just happen",
            "its giving slytherin",
            "thats so michael scott coded",
            "its giving child of divorce",
            "that really rustles my jimmies",
            "im gonna say my angry word",
            "thanks i hate it",
            "does he know",
            "the gaslighting is insane",
            "and they were roommates",
            "is he stupid",
            "hes right behind me isnt he",
            "im telling the subreddit about this",
            "mic drop",
            "hahaha i do that",
            "looks like we got ourselves a sticky situation",
            "oh she ate",
            "erm what the sigma",
            "consider that tea spilled",
            "whats all this then",
            "now thats some good tea",
            "they fell off hard",
            "that sounded a lot better in my head",
            "thanks for the gold kind stranger",
            "now they understood the assignment",
            "they went full send never go full send",
            "fax no printer",
            "on god no cap",
            "thats cap",
            "uhoh uh oh stinky",
            "holy crap lois",
            "no god on cap",
            "scratch that reverse it",
            "bro has no chill",
            "heh yea OH kay",
            "they did the thing",
            "as an ai language model i am unable to react to this",
            "make it make sense",
            "this has vine energy",
            "hey guys very excited for todays video",
            "that wasnt on my bingo card",
            "im done adulting for the day",
            "more of this please",
            "win",
            "fail",
            "erm exqueeze me sauce",
            "cute",
            "this aint it chief",
            "wait was that markiplier",
            "dont talk to me until ive had my morning coffee",
            "oo hot take",
            "my dogs are barking",
            "let him cook",
            "challenge accepted",
            "thats enough internet for today",
            "they need to touch grass",
            "if you like what youre seeing go ahead and subscribe",
            "i heckin love science",
            "heckin chonker",
            "absolute unit",
            "we stan a queen",
            "we stan a queen",
            "if you know you know",
            "im on that weird side of youtube",
            "and i oop",
            "those who get it get it and those who dont dont",
            "like this if youre watching this in 2024",
            "can we just applaud this",
            "bro who even did this",
            "catch my upvote",
            "credit to whoever made this",
            "friendzoned",
            "we stan a short king",
            "chad energy",
            "that took balls",
            "unironically the coolest thing i_ve ever seen in my life",
            "chat can we get their social security number",
            "my jaw on the floor",
            "ah the classic switcheroo",
            "bro thinks theyre sigma",
            "nice",
            "not my president",
            "okay this next one is insane",
            "ok this next one is gonna break your brain",
            "give this video a like if your parents are still divorced",
            "flawless skin",
            "i need a shower after that",
            "only 1 percent of you will get this one",
            "my pronouns are wom wrok",
            "bro looks like cocomelon",
            "leave a comment telling me what you ate today",
            "unbothered and thriving",
            "wish i could rate this 5 stars still",
            "dyou guys hear trump died",
            "hit that subscribe button and join the wom army",
            "guys we can all agree that abstinence rules right",
            "yup its mukbang time",
            "look at this chungus",
            "bro how do they do that",
            "i love this song",
            "this is giving me goose pimples",
            "smash that like button if you agree",
            "its true what they say girls get it done",
            "this got me feeling a type of way",
            "i dedicate this video to the troops",
            "yea you really cant say that word anymore",
            "i was today years old when i found this out",
            "bruh moment",
            "they should retire after this",
            "women are so powerful",
            "can they say that",
            "they should be in jail",
            "thats what i call a vibe",
            "yo this ones for the guys",
            "yo this ones for the boys",
            "i felt that",
            "catch my downvote",
            "man this video feels illegal",
            "this vid would put a victorian child in a coma",
            "i dont know what i expected",
            "ah the classic razzle dazzle",
            "ok maybe the one piece is real",
            "that looked like it hurt",
            "this is why blue lives matter",
            "chat is this real",
            "rip bozo",
            "bro really said mmmmmm",
            "bro is lookin crusty musty",
            "i need a drink after that",
            "this makes me so mad",
            "blink twice if youre being held hostage",
            "and tell me which hogwarts house you belong to",
            "this video is why i have a peanut allergy",
            "this video gave me a migraine",
            "what the sigma",
            "man thats wild bro",
            "we must protect them at all costs",
            "hmm im gonna need a mini wom for this one it stinks",
            "the human body has over 60000 miles of blood vessels",
            "i dont have an opinion on this",
            "i fail to see the humor here",
            "this next ones for the fellas",
            "is this a liveleak video",
            "bros straight up mogging me",
            "can we gatekeep this from the normies",
            "this is so sad",
            "im bored",
            "bro thats wild man",
            "chad detected",
            "if you know what i mean wink",
            "its giving girl dinner",
            "would",
            "no comment",
            "yea im not touching that one",
            "i wanna shake this persons hand",
            "im a sucker for a cute lil doggo",
            "bro lowkey cookin",
            "if this gets 5000 likes ill swallow my own tongue",
            "erm what the scallop",
            "if this gets 10000 likes nothing will happen",
            "mmm i dont know about that",
            "bro thought they were slick",
            "bro thought they they bro though glitch next tiktok",
            "impossible is nothing",
            "we are the dream makers",
            "hold on shut up im trying to think of something to say",
            "now thats a spicy meatball",
            "whoa woah what did i just witness",
            "shut up and witness me",
            "yea its official im shooketh",
            "maybe the real video was in here",
            "haha yes so true",
            "so true mhmm",
            "nodders",
            "rizztacular",
            "based af",
            "thats actually really offensive",
            "theres nothing funny about 911",
            "this is so true you guys",
            "real",
            "thats crazy but okay",
            "nahh thats crazy",
            "for real thats crazy",
            "im watching this and i still dont believe it",
            "pathetic you can do better",
            "aw hell naw",
            "thats gross",
            "uh yea instant like",
            "nahhh thats the joker",
            "bro is getting it done",
            "man it always be like that",
            "mmm alrighty then",
            "go girl give us nothing",
            "bro is lying",
            "youre a real one for that",
            "uh actions meet consequences",
            "thats what you get",
            "thats a bowl fulla sauce",
            "this just be the harsh reality",
            "erm this is giving me an existential crisis",
            "im gonna feed you guys good today",
            "leave a comment if you thought that was crazy",
            "guys i literally cant with this",
            "uh language haha",
            "thats a bingo",
            "erm mods crush this guys skull",
            "not really that impressive",
            "this videos kind of a nothing burger",
            "bro let the intrusive thoughts win",
            "gonna show this to my meemaw",
            "gonna show this to gamgam",
            "wow they look like they work out",
            "i dont wanna say what im thinking right now",
            "whoa thats intense",
            "white ppl be like",
            "this just feels wrong",
            "feeling some huge libra vibes",
            "thats kinda cringe bruh",
            "they got that dog in em",
            "yippee",
            "this is me when i go to a starbucks",
            "subscribe to join the wom family",
            "i dont consider you guys my subscribers i consider you all my friends",
            "that didnt age well",
            "are you flipping kidding me",
            "cool video",
            "wake me when its virgo season",
            "instant karma",
            "they dont make em like they used to",
            "shakes head uhuh",
            "nods uh huh",
            "this isnt nearly as epic as BACON",
            "i cant react until ive had my coffee",
            "this feels racist but i cant explain why",
            "this video is proof that we live in the matrix",
            "oof thats cringe bro",
            "this is why i hate children",
            "showing this to my doggo",
            "i love fluffer pupper doggos",
            "bro lookin like an ipad kid",
            "this gave me second hand embarrassment",
            "this is making me uncomfortable",
            "someone wasnt hugged enough as a kid",
            "im gonna pin the craziest comment",
            "hi im wom",
            "im wom",
            "yup",
            "uhhh talk about a twist ending",
            "true",
            "only gamers will get that",
            "subscribe to me because i curate only the best stuff",
            "i just wanna say to the haters its not stealing its reacting",
            "i hate to bring gender into this but women deserve to be respected",
            "using ai ive determined that this video is epic sauce",
            "i just wanna say to the haters stay mad and stay broke",
            "i just wanna say to the haters its not my fault you have bacne",
            "straight vibin",
            "kinda waluigi coded",
            "damn",
            "bro i did not expect that",
            "this is garfield coded",
            "that got messy",
            "now that was an epic gamer moment",
            "insert reaction here",
            "not me vibing with the rizz",
            "this is slop",
            "i give it a two out of five",
            "i give this a D-",
            "this is a bop",
            "classic",
            "yuh if that were me i wouldve done things a little differently",
            "i bet their pronouns are epic sauce",
            "to all my haters look how smooth my skin is",
            "this reminds me of mr beast",
            "bro is straight up yapping",
            "yes",
            "yes",
            "NO",
            "this reminds me of epic meal time",
            "has RWJ seen this one yet",
            "this reminds me of ijustine rip",
            "im bored lets watch family guy funnies",
            "vroom vroom",
            "i cant focus can you put on some subway surfers",
            "okay yea this deserves some reddit gold",
            "what cant women do",
            "this aspect ratio rocks",
            "this is giving some freak energy",
            "this is a video",
            "well that just happened",
            "shazaam",
            "relatable",
            "this is a moment",
            "im literally speechless",
            "what just happened",
            "ruh roh",
            "did you guys see that",
            "bro is speakin truth",
            "now this is more like it",
            "my diaper full",
            "aw thats cute",
            "my flabbers ghasted",
            "behavior on both sides",
            "F to pay respects",
            "totally",
            "guhhhh noise when pulling tugging on shirt collar",
            "chuckling and shaking head",
            "this reminds me of something",
            "this is why i love america",
            "you can say that again",
            "bro is the michael jordan of basketball",
            "like this if youre watching in 2025",
            "bro is spitting straight facts",
            "they hate us cause they aint us",
            "i hope everyone watching is having a great day",
            "obsessed",
            "10 out of 10",
            "perfect no notes",
            "3 out of 10",
            "7 out of 10",
            "thats a 5 out of 10 for me",
            "its a no for me",
            "i think ive seen this before",
            "consider their goose cooked",
            "chat is this fact or cap",
            "who let bro cook",
            "vibe is crazy",
            "uhhhhh whos gonna tell em",
            "ok hear me out",
            "oh fuck censored bleeped",
            "is this satire",
            "this is lowkey bridgerton coded",
            "zoinks scoob",
            "oooo right in the feels",
            "oooo right in the childhood",
            "is this 8 minutes yet",
            "im reacting so hard right now",
            "what am i even watching",
            "emotional damage",
            "this doin numbers",
            "SUS",
            "this big guy eatin all the lil guys",
            "username checks out",
            "that makes sense",
            "how is this not viral",
            "the vibe i bring to the function",
            "i dont get it",
            "i dont get it",
            "not funny didnt laugh",
            "im on the weird side of youtube",
            "what part of me asked",
            "ahaha thats wild",
            "my hungry ass could not",
            "my sleepy ass could never",
            "this is peak",
            "this is peak",
            "what did i walk into",
            "the gooooaaaat goat",
            "the old one was better",
            "ahhh the good old days",
            "is that a jojo reference",
            "yup its official im on the weird side of youtube",
            "thats gonna leave a mark",
            "thats crazy",
            "that took a turn",
            "ermmm plot twist",
            "oh how the turn tables",
            "is that even legal",
            "aint no way",
            "stonks",
            "legit mood",
            "worldstar",
            "why i oughta",
            "i just failed my try not to laugh challenge",
            "this hits different now",
            "you had one job",
            "is that the guy from fortnite",
            "im not crying you are",
            "thats the straw that broke the camels back",
            "dont mind if i do",
            "what IS that",
            "what is THAT",
            "i need an adult",
            "ugh i hate the word moist",
            "bussin",
            "erm that was unexpected",
            "ugh i hate adulting",
            "bros giving me the ick",
            "we love a redemption arc",
            "we love to see it",
            "red flag",
            "instant red flag",
            "green flag",
            "thisll get me demonetized",
            "tips fedora",
            "bro let the demons win",
            "i cant even",
            "bombastic side eye",
            "hit em with the side eye",
            "yes speak your truth",
            "what are the odds",
            "go off king",
            "pop off sis",
            "yassss queen",
            "aw they ate with that",
            "ate and left no crumbs",
            "clearly edited",
            "thats actually really funny",
            "im in this vid and i dont like it",
            "clearly ai",
            "haters will say its fake",
            "oh ew you can see the rotoscoping",
            "bro has receipts",
            "looks photoshopped",
            "animators get on it",
            "NPC behavior",
            "uhhh in english please",
            "straight to jail",
            "agree to disagree",
            "caught in 4k",
            "someone send this to mr beast",
            "elon wont like this one",
            "not the asshole",
            "that looks like it hurt",
            "wait theyre banning tiktok",
            "this is literally 1984",
            "i can smell this video",
            "bureaucracy is inherently kafkaesque",
            "this is my fight song",
            "dude thats lowkey wild",
            "bro is on to nothing",
            "somebody call the whambulance",
            "this is my 13th reason",
            "i dont wanna get political but this is obama coded",
            "you need a high iq for this one",
            "new fear unlocked",
            "is he okay",
            "how did they do that",
            "this video right here officer",
            "500 IQ moment",
            "bet",
            "what a bozo",
            "big dick energy",
            "mmm a man of culture i see",
            "shut up and take my money",
            "mommy step on me",
            "mommy knows best",
            "mom can you pick me up im scared",
            "cant show this one to mom",
            "mother is mothering",
            "thats rough buddy",
            "facts",
            "me when the doom music kicks in",
            "i support the death penalty",
            "talk about a life hack",
            "this drama is spicy",
            "haha work smarter not harder",
            "who won whos next you decide",
            "i miss the old smosh",
            "my skinny ass could never",
            "oo thats a freudian slip",
            "more proof that video games lead to violence",
            "its kinda mid",
            "this says a lot about society",
            "hellll yea",
            "press x to doubt",
            "i dunno i just didnt find it that funny",
            "this is the best thing ive seen all year",
            "jarvis remove their legs",
            "this is literally my weakness",
            "this is literally my weakness",
            "hashtag not all men",
            "a for effort",
            "☝️🤓<:vinesound1:808037201525866496>",
            "chat can we skip this part",
            "😩<:vinesound1:808037201525866496>",
            "💀<:vinesound1:808037201525866496>",
            "awkward awkwarrrrrrd",
            "my pants pissed",
            "yikes",
            "yuckyyy",
            "chat can i get a kiss",
            "im feeling really ugly today can someone in the comments give me a lil boost",
            "gawrsh",
            "meesa like what im seeing",
            "mm hahaha",
            "thats certainly a choice",
            "this actually happened to my cousin",
            "welcome to crazytown population this video",
            "still wont heal our broken country",
            "i dont like that",
            "i dont like that",
            "okay",
            "pop pop pop pop pop",
            "my life be like oooo ahhhh",
            "chat can we cancel them",
            "hey can we get a USA in the chat",
            "this is cinema",
            "this a whole mood right here",
            "buzzer sound shakes head wrong",
            "ding ding ding correct sound nods head",
            "dont ask me where i was on the night of october 13th 2023",
            "this is giving me all the feels",
            "talk about a giant W",
            "talk about a giant L",
            "this video is giving epic sauce",
            "your honor i plead the fifth",
            "womp womp",
            "leviticus",
            "got me feeling a certain type of way",
            "proverbs",
            "the current time is 453 pm",
            "merry christmas",
            "this video gets a 4 out of 5",
            "whoever made this video deserves a big ol spanking",
            "whoever made this video definitely voted for trump",
            "i find that joke a little offensive",
            "i find that joke highly offensive",
            "be sure to credit the creators when reacting to content",
            "doxxing is a misdemeanor",
            "bro is literally me",
            "giving that an A+",
            "gonna grade this one a B-",
            "that is such a gemini move",
            "skibidi go to the polls",
            "love the aesthetic",
            "but doctor i am pagliacci",
            "bro left no crumbs",
            "bro who did this",
            "wishin my meemaw were still alive to see this",
            "bro i wish i could unsee that",
        ]
        self.wish_birthday.start(); self.set_game_presence.start() # loops

    @commands.Cog.listener()
    async def on_message(self, message):
        # variable decs for ping triggers
        wom = next((member for member in message.guild.members if member.bot and member.name == "Wyvern of Marina" or member.name == "Neel of Marina"), None)
        the_thing = compile(rf"<@!?{wom.id}>\s+is this true[\s\?\!\.\,]*$", IGNORECASE)
        the_thing2 = compile(rf"<@!?{wom.id}>\s+.+", IGNORECASE)
        content = message.content.strip()

        if message.guild: # must be in server
            if message.author.bot: # must be human
                return
            else:
                 # custom commands
                if message.content[0:3] == "!w " and message.content.split()[1] in list(lists["commands"].keys()): 
                    await message.reply(lists["commands"][message.content.split()[1]], mention_author=False)

                # message phrase triggers
                if message.content.lower() == "skill issue":
                    await message.channel.send(file=discord.File("skill issue.gif"))
                if message.content.lower() == "me":
                    await message.channel.send('<:WoM:836128658828558336>')
                if message.content.lower() == "which":
                    if assert_cooldown("which") != 0:
                        await shark_react(message)
                    else:
                        await message.channel.send(choice([member.name.lower() for member in message.guild.members if not member.bot]))
            
                # phrase trigger reactions
                for trigger, emoji in zip(self.triggers, self.trigger_emojis):
                    pattern = r'\b' + escape(trigger) + r'\b'
                    if search(pattern, message.content.lower()):
                        try:
                            await message.add_reaction(emoji)
                        except:
                            pass
            
                # shiny
                if randint(1,8192) == 1:  
                    if not message.channel.name in ['venting', 'serious-talk']:
                        direct_to_bank(message.author.id,500)
                        with open("shiny.png", "rb") as f:
                            file = discord.File(f)
                            return await message.channel.send(content=f"{message.author.name} stumbled across 500 {zenny} and a wild Wyvern of Marina! ✨", file=file)
                        
                # is this true + react
                if the_thing.fullmatch(content):
                    if wom.nick and wom.nick.lower() == "wrok":
                        if assert_cooldown("itt") != 0:
                            await shark_react(message)
                        else:
                            async with message.channel.typing():
                                await asyncio.sleep(1)
                                await message.reply(choice(self.reply_choices), mention_author=False)
                    else:
                        await shark_react(message)
                        await message.reply("Wups! I need to be nicknamed \"Wrok\" for this to work...", mention_author=False)
                elif the_thing2.fullmatch(content):
                    if assert_cooldown("react") != 0:
                        await shark_react(message)
                    else:
                        async with message.channel.typing():
                            await asyncio.sleep(3)
                            await message.reply(choice(self.reactions), mention_author=False)
                    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not ctx.message.content.split()[1] in list(lists["commands"].keys()):
            return await wups(ctx, f'Try "!w help" ({error})')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.content[0:3] == '!w ' or message.author.bot:
            global snipe_data
            channel = message.channel.id
            if message.author.bot:
                return
              
            snipe_data[channel]={"content":str(message.content), "author":message.author, "id":message.id, "attachment":message.attachments[0] if message.attachments else None}
          
            await asyncio.sleep(60)
            if message.id == snipe_data[channel]["id"]:
                del snipe_data[channel]

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if not message_after.author.bot:
            global editsnipe_data
            channel = message_after.channel.id
            if message_before.author.bot:
                return
              
            editsnipe_data[channel]={"content":str(message_before.content), "author":message_before.author, "id":message_before.id}
          
            await asyncio.sleep(60)
            if message_before.id == editsnipe_data[channel]["id"]:
                del editsnipe_data[channel]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            try:
                peep_role = discord.utils.get(member.guild.roles, name="Peep")
                await member.add_roles(peep_role)
            except:
                pass
            add_coins(member.id,100)
            direct_to_bank(member.id, 0)
            add_item("karma", member.id, 2)
            return await member.guild.system_channel.send(f"Welcome, {member.mention}, to **The Marina**! This is your one-way ticket to Hell. There\'s no going back from here...\nFor a grasp of the rules, however (yes, we have those), we do ask that you check <#822341695411847249>.\n*Remember to take breaks, nya?*")
        else:
            try:
                beep = discord.utils.get(member.guild.roles, name="beep")
                return await member.add_roles(beep)
            except:
                pass
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.is_timed_out() == True and before.is_timed_out() == False:
            return await before.guild.system_channel.send(f"{after.mention} got timed out... for whatever reason... <:villainy:915009093662556170>")
          
        if after.is_timed_out() == False and before.is_timed_out() == True:
            return await before.guild.system_channel.send(f"Welcome back, {after.mention}. Don\'t do that again, idiot. <:do_not:1077435360537223238>")
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        return await guild.system_channel.send(f"{user.name} has been banned! Rest in fucking piss, bozo. <:kysNOW:896223569288241175>")
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.author == user or user.bot:
            return
        
        if str(reaction.emoji) == starboard_emoji or str(reaction.emoji) == shame_emoji:
            board_type = "starboard" if str(reaction.emoji) == starboard_emoji else "shameboard"
            if await check_reaction_board(reaction.message, board_type):
                return await add_to_board(reaction.message, board_type)

    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        listsToCheck = lists[2:]
        for list in listsToCheck:
            csv = pd.read_csv(f'csv/{list}.csv')
            csv = csv[csv['user_id'] != member.id]
            csv.to_csv(f'csv/{list}.csv', index=False)
            create_list(list)
        csv = pd.read_csv(f'csv/birthdays.csv')
        csv = csv[csv['user_id'] != member.id]
        csv.to_csv(f'csv/{list}.csv', index=False)
        create_birthday_list()

    @tasks.loop(seconds=1)
    async def wish_birthday(self):
        for key in user_info.keys():
            time_person = datetime.now(timezone(user_info[key]['timezone']))
            time_person_date = time_person.strftime('%m-%d')
            time_person_exact = [int(time_person.strftime('%H')), int(time_person.strftime('%M')), int(time_person.strftime('%S'))]

            if time_person_date == user_info[key]['birthdate'] and time_person_exact == [0,0,0]:
                await self.bot.guilds[0].system_channel.send(content=f'<:luv:765073937645305896> 🎉 Happy Birthday, <@{int(key)}>! {choice(self.messages)} 🎂 <:luv:765073937645305896>', file=discord.File("mario-birthday.gif"))

    @tasks.loop(hours=3)
    async def set_game_presence(self):
        await self.bot.change_presence(activity=discord.Game(name=choice(self.games)))

    @set_game_presence.before_loop
    @wish_birthday.before_loop
    async def before_looping(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.wish_birthday.cancel()


async def setup(bot):
    await bot.add_cog(Events(bot))
