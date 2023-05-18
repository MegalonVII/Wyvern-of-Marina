import discord
from discord.ext import commands
import random
import pandas as pd
import asyncio
from utils import *

# bot events start here
# on_message, on_command_error, on_message_delete, on_message_edit, on_member_join, on_member_update, on_member_ban, on_reaction_add, on_member_remove
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
          
        if message.content[0:3] == "!w " and message.content.split()[1] in list(lists["commands"].keys()): # custom commands
            await message.channel.send(lists["commands"][message.content.split()[1]])
        else:   # any specific word triggers
            if message.content.lower() == "me":
                await message.channel.send('<:WoM:836128658828558336>')
            if message.content.lower() == "which":
                if assert_cooldown("which") != 0:
                    await message.add_reaction('🦈')
                else:
                    await message.channel.send(random.choice([member.name.lower() for member in message.guild.members if not member.bot]))
    
            # trigger reactions
            triggers = ['yoshi','3ds','wednesday','yuri','yaoi','crank','kys','chan']
            trigger_emojis = ['<:full:1028536660918550568>','<:megalon:1078914494132129802>','<:wednesday:798691076092198993>','<:vers:804766992644702238>','🐍','🔧','⚡','🦄']
            for trigger, emoji in zip(triggers, trigger_emojis):
                if trigger in message.content.lower().split(" "):
                    await message.add_reaction(emoji)
      
        if random.randint(1,4096) == 1:  
            if random.randint(1,2) == 1:
                try:
                    return await message.author.send(f"Hey {message.author.name}. Hope this finds you well.\n\nJust wanted to say that I know that this server might make some jabs at you or do some things that might rub you the wrong way, but that aside I wanted to personally tell you that I value that you\'re here. I think you\'re amazing and you deserve only good things coming to you. Hope you only succeed from here!\nIf you\'re ever feeling down, I hope you can look back at this message just to cheer you up. Also, this message might come back to you again so maybe you\'ll need it again?\n\nOh well. Been nice talking to ya! <3")
                except:
                    return await message.channel.send(f"I tried sending {message.author.mention} top secret classified government information, but for some reason I couldn\'t...")
            else:
                add_coins(message.author.id,500)
                with open("shiny.png", "rb") as f:
                    file = discord.File(f)
                    return await message.channel.send(content=f"{message.author.name} stumbled across 500 {zenny} and a wild Wyvern of Marina! ✨", file=file)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not ctx.message.content.split()[1] in list(lists["commands"].keys()):
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f'Wups! try "!w help"... ({error})', mention_author=False)

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
          
        if str(reaction.emoji) == starboard_emoji:
            if await check_starboard(reaction.message):
                return await add_to_starboard(reaction.message)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        coins = pd.read_csv('coins.csv')
        coins = coins[coins['user_id'] != member.id]
        coins.to_csv('coins.csv', index=False)
        create_list("coins")

async def setup(bot):
    await bot.add_cog(Events(bot))
