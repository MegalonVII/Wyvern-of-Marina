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
from utils import assert_cooldown, shark_react, wups, add_coins, reply, direct_to_bank, check_reaction_board, add_to_board, create_list, create_birthday_list, add_item, load_info # utils functions

# bot events start here
# on_message, on_command_error, on_message_delete, on_message_edit, on_member_join, on_member_update, on_member_ban, on_reaction_add, on_member_remove, wish_birthday
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.information = ["triggers", "trigger_emojis", "games", "messages", "reply_choices", "reactions"]
        
        for item in self.information:
            setattr(self, item, load_info(item))

        # loops
        self.wish_birthday.start()
        self.set_game_presence.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        # variable decs for ping triggers
        wom = next((member for member in message.guild.members if member.bot and member.name == "Wyvern of Marina"), None)
        try:
            the_thing = compile(rf"<@!?{wom.id}>\s+is this true[\s\?\!\.\,]*$", IGNORECASE)
            the_thing2 = compile(rf"<@!?{wom.id}>\s+.+", IGNORECASE)
            # this is just so your test bots don't give on you on_message ignorances in console
        except:
            pass
        content = message.content.strip()

        if message.guild: # must be in server
            if message.author.bot: # must be human
                return
            else:
                 # custom commands
                if message.content[0:3] == "!w " and message.content.split()[1] in list(lists["commands"].keys()): 
                    await message.reply(lists["commands"][message.content.split()[1]], mention_author=False)

                # message phrase triggers
                if content.lower() == "skill issue":
                    await message.channel.send(file=discord.File("img/skill-issue.gif"))
                if content.lower() == "me":
                    await message.channel.send('<:WoM:836128658828558336>')
                if content.lower() == "which":
                    if assert_cooldown("which") != 0:
                        await shark_react(message)
                    else:
                        await message.channel.send(choice([member.name.lower() for member in message.guild.members if not member.bot]))
                if content.lower() == "hi guys":
                    try:
                        await message.add_reaction("🍅")
                    except:
                        pass

                # phrase trigger reactions
                for trigger, emoji in zip(self.triggers, self.trigger_emojis):
                    pattern = r'\b' + escape(trigger) + r'\b'
                    if search(pattern, message.content.lower()):
                        if trigger == "persona" and message.channel.name == "the-velvet-room":
                            continue
                        try:
                            await message.add_reaction(emoji)
                        except:
                            pass
            
                # shiny
                if randint(1,8192) == 1:  
                    if not message.channel.name in ['venting', 'serious-talk']:
                        direct_to_bank(message.author.id,500)
                        with open("img/shiny.png", "rb") as f:
                            file = discord.File(f)
                            return await message.channel.send(content=f"{message.author.name} stumbled across 500 {zenny} and a wild Wyvern of Marina! ✨", file=file)
                        
                # is this true + react
                try:
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
                except:
                    pass # probably a test bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not ctx.message.content.split()[1] in list(lists["commands"].keys()):
            return await wups(ctx, f'Try "!w help" ({error})')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or (message.content and message.content.startswith('!w ')):
            return

        channel = message.channel.id
        snipe_data[channel] = {
            "content": str(message.content) if message.content else "",
            "author": message.author,
            "id": message.id,
            "attachment": message.attachments[0] if message.attachments else None
        }

        await asyncio.sleep(60)
        if snipe_data.get(channel) and snipe_data[channel]["id"] == message.id:
            del snipe_data[channel]

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if message_after.author.bot:
            return

        channel = message_after.channel.id
        editsnipe_data[channel] = {
            "content": str(message_before.content) if message_before.content else "",
            "author": message_after.author,
            "id": message_after.id
        }

        await asyncio.sleep(60)
        if editsnipe_data.get(channel) and editsnipe_data[channel]["id"] == message_after.id:
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
        marina = self.bot.guilds[0]
        role = discord.utils.get(marina.roles, name="B-day")

        for key in user_info.keys():
            time_person = datetime.now(timezone(user_info[key]['timezone']))
            time_person_date = time_person.strftime('%m-%d')
            time_person_exact = [int(time_person.strftime('%H')), int(time_person.strftime('%M')), int(time_person.strftime('%S'))]

            if time_person_date == user_info[key]['birthdate'] and time_person_exact == [0,0,0]:
                member = marina.get_member(int(key))
                if member:
                    await marina.system_channel.send(
                        content=f'<:luv:765073937645305896> 🎉 Happy Birthday, <@{member.id}>! {choice(self.messages)} 🎂 <:luv:765073937645305896>',
                        file=discord.File("img/mario-birthday.gif")
                    )

                    if role and role not in member.roles:
                        await member.add_roles(role, reason=f"it is {member.name}'s birthday")

                        async def remove_role_later(m, r):
                            await asyncio.sleep(86400)  # 24h in seconds
                            if r in m.roles:
                                await m.remove_roles(r, reason=f"it is no longer {m.name}'s birthday")

                        self.bot.loop.create_task(remove_role_later(member, role))

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
