import discord
from discord.ext import commands, tasks
import random
import pandas as pd
import asyncio
from pytz import timezone
import random
from utils import *

# bot events start here
# on_message, on_command_error, on_message_delete, on_message_edit, on_member_join, on_member_update, on_member_ban, on_reaction_add, on_member_remove, wish_birthday
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = [
            'Monster Hunter 4 Ultimate', 
            'Rain World', 
            'Final Fantasy Tactics', 
            'Baldur\'s Gate 3', 
            'Terraria', 
            'FINAL FANTASY XIV Online', 
            'Persona 4 Golden', 
            'Fire Emblem Echoes: Shadows of Valentia', 
            'Xenogears', 
            'Chrono Trigger',
            'Quake',
            'Dead Space',
            'NieR: Automata',
            'Hi-Fi Rush'
        ]
        self.messages = [
            "Try not to die of dysentery today!",
            "I hope you don't get AFK Corrin'd today!"
        ]
        self.wish_birthday.start(); self.set_game_presence.start() # loops

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild: # must be in server
            if message.author.bot: # must be human
                return
            else:
                 # custom commands
                if message.content[0:3] == "!w " and message.content.split()[1] in list(lists["commands"].keys()): 
                    await message.channel.send(lists["commands"][message.content.split()[1]])

                # message phrase triggers
                if message.content.lower() == "skill issue":
                    await message.channel.send(file=discord.File("skill issue.gif"))
                if message.content.lower() == "me":
                    await message.channel.send('<:WoM:836128658828558336>')
                if message.content.lower() == "which":
                    if assert_cooldown("which") != 0:
                        await shark_react(message)
                    else:
                        await message.channel.send(random.choice([member.name.lower() for member in message.guild.members if not member.bot]))
            
                    # word trigger reactions
                    triggers = ['yoshi','3ds','wednesday','fat','yuri','yaoi','crank','kys']
                    trigger_emojis = ['<:full:1028536660918550568>','<:megalon:1078914494132129802>','<:wednesday:798691076092198993>','<:bulbous:1028536648922832956>','<:vers:804766992644702238>','🐍','🔧','⚡']
                    for trigger, emoji in zip(triggers, trigger_emojis):
                        if trigger in message.content.lower().split(" "):
                            try:
                                await message.add_reaction(emoji)
                            except:
                                pass
            
                # shiny
                if random.randint(1,8192) == 1:  
                    if not message.channel.name in ['venting', 'serious-talk']:
                        add_coins(message.author.id,500)
                        with open("shiny.png", "rb") as f:
                            file = discord.File(f)
                            return await message.channel.send(content=f"{message.author.name} stumbled across 500 {zenny} and a wild Wyvern of Marina! ✨", file=file)

                    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not ctx.message.content.split()[1] in list(lists["commands"].keys()):
            await shark_react(ctx.message)
            return await reply(ctx, f'Wups! try "!w help"... ({error})')

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
            return await before.guild.system_channel.send(f"That fucking bozo {after.mention} got timed out! Point and laugh at this user! <:you:765067257008881715>")
          
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
        listsToCheck = ["coins", "bank", "delivery", "shell", "bomb", "ticket", "letter", "banana"]
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
                await self.bot.guilds[0].system_channel.send(content=f'<:luv:765073937645305896> 🎉 Happy Birthday, <@{int(key)}>! {random.choice(self.messages)} 🎂 <:luv:765073937645305896>', file=discord.File("mario-birthday.gif"))

    @tasks.loop(hours=3)
    async def set_game_presence(self):
        await self.bot.change_presence(activity=discord.Game(name=random.choice(self.games)))

    @set_game_presence.before_loop
    @wish_birthday.before_loop
    async def before_looping(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.wish_birthday.cancel()


async def setup(bot):
    await bot.add_cog(Events(bot))
