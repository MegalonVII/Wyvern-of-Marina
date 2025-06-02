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
from utils import assert_cooldown, shark_react, add_coins, reply, direct_to_bank, check_reaction_board, add_to_board, create_list, create_birthday_list, add_item # utils functions

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
            'crank',
            'kys'
        ]
        self.trigger_emojis = [
            '<:full:1028536660918550568>',
            '<:megalon:1078914494132129802>',
            '<:megalon:1078914494132129802>',
            '<:wednesday:798691076092198993>',
            '<:bulbous:1028536648922832956>',
            '<:vers:804766992644702238>',
            '🐍',
            '🔧',
            '⚡'
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
            "well shit, that happened.",
            "okay, not what i expected.",
            "alright then.",
            "kinda weird, but okay.",
            "i'm not mad, just confused.",
            "what the hell, man.",
            "you really went for it, huh.",
            "could've just... not done that.",
            "respectfully, what the fuck.",
            "i mean, sure. why not.",
            "you do you, i guess.",
            "honestly? not the worst thing i've seen.",
            "i have no idea how to respond to that.",
            "i'll pretend i didn't see that.",
            "yeah, that's a thing now.",
            "mildly concerning, but go off.",
            "sure, let's call that a win.",
            "i see what you did there. i don't like it, but i see it.",
            "that's one way to react.",
            "somehow, i expected worse.",
            "well. that's something.",
            "this feels like a cry for help.",
            "i'm just gonna quietly react now.",
            "mood, honestly.",
            "alright, moving on.",
            "can't tell if i love it or hate it.",
            "not sure if i should laugh or worry.",
            "that one caught me off guard.",
            "low-key kinda valid.",
            "fine. i reacted. you happy now?"
        ]
        self.wish_birthday.start(); self.set_game_presence.start() # loops

    @commands.Cog.listener()
    async def on_message(self, message):
        wom = next((member for member in message.guild.members if member.bot and member.name == "Wyvern of Marina" or member.name == "Neel of Marina"), None)
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
                if wom.nick and wom.nick.lower() == "wrok":
                    the_thing=compile(rf"<@!?{wom.id}>\s+is this true[\s\?\!\.\,]*$", IGNORECASE)
                    if the_thing.fullmatch(message.content.strip()):
                        if assert_cooldown("itt") != 0:
                            await shark_react(message)
                        else:
                            async with message.channel.typing():
                                await asyncio.sleep(1)
                                await message.reply(choice(self.reply_choices), mention_author=False)
                the_thing2=compile(rf"<@!?{wom.id}>\s+react please[\s\?\!\.\,]*$", IGNORECASE)
                if the_thing2.fullmatch(message.content.strip()):
                    if assert_cooldown("react") != 0:
                        await shark_react(message)
                    else:
                        async with message.channel.typing():
                            await asyncio.sleep(3)
                            await message.reply(choice(self.reactions), mention_author=False)
                    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not ctx.message.content.split()[1] in list(lists["commands"].keys()):
            await shark_react(ctx.message)    
            return await reply(ctx, f'Wups! Try "!w help"... ({error})')

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
