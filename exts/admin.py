import discord
import csv
from discord.ext import commands
import pandas as pd
from datetime import timedelta

from utils import lists, file_checks # utils direct values
from utils import cog_check, wups, reply, assert_cooldown, create_list # utils functions

# administrative commands start here
# cc, dc, clear, kick, ban, mute, unmute, addf, delf
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='createcommand', aliases=['cc'])
    async def createcommand(self, ctx, name, *output):
        if await cog_check(ctx):
            try:
                if len(output) < 1:
                    return await wups(ctx, "You need to give me an output for your new command")
                elif not ctx.author.guild_permissions.manage_messages:
                    return await wups(ctx, "You do not have the required permissions")
                elif name in list(lists["commands"].keys()):
                    return await wups(ctx, "This command already exists")
                
                output = ' '.join(output).replace('"', '\"').replace("'", "\'")
                with open('csv/commands.csv', 'a', newline='') as csvfile:
                    fieldnames = ['command_name', 'command_output']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    if file_checks["commands"]:
                        writer.writeheader()
                    writer.writerow({'command_name': name, 'command_output': output})
                create_list("commands")
                return await reply(ctx, f"The command {name} has been created!")
            except:
                return await wups(ctx, "I don't have a name for a command")
                    
    @commands.command(name='deletecommand', aliases=['dc'])
    async def deletecommand(self, ctx, name):
        if await cog_check(ctx):
            if not ctx.author.guild_permissions.manage_messages:
                return await wups(ctx, "You do not have the required permissions")
            if not name in list(lists["commands"].keys()):
                return await wups(ctx, "This command does not exist")
            if len(list(lists["commands"].keys())) == 0:
                return await wups(ctx, "There are no commands to delete in the first place")
    
            commands = pd.read_csv('csv/commands.csv')
            commands = commands[commands.command_name != name]
            commands.to_csv('csv/commands.csv', index=False)
            create_list("commands")
            return await reply(ctx, f'The command {name} has been deleted!')

    @commands.command(name='clear')
    async def clear(self, ctx, num:int=None):
        if await cog_check(ctx):
            if not ctx.author.guild_permissions.manage_messages:
                return await wups(ctx, "You do not have the required permissions")
            if num is None or num < 1 or num > 10:
                return await wups(ctx, "Please enter a number between 1 and 10")
            if assert_cooldown("clear") != 0:
                return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('clear')} seconds")
    
            await ctx.message.add_reaction('✅')
            return await ctx.message.channel.purge(limit=num+1)

    @commands.command(name='kick')
    async def kick(self, ctx, member:discord.Member):  
        if await cog_check(ctx):
            if not ctx.author.guild_permissions.administrator:
                return await wups(ctx, "Only administrators are allowed to use this command")
            if member.guild_permissions.administrator and not member.bot:
                return await wups(ctx, "Administrators can\'t be kicked")
            
            await member.kick()
            await ctx.message.delete()
            return await ctx.guild.system_channel.send(f"{member.name} has been kicked! Hope you learn from your mistake... <:do_not:1077435360537223238>")

    @commands.command(name='ban')
    async def ban(self, ctx, member:discord.Member):
        if await cog_check(ctx):
            if not ctx.author.guild_permissions.administrator:
                return await wups(ctx, "Only administrators are allowed to use this command")
            if member.guild_permissions.administrator and not member.bot:
                return await wups(ctx, "Administrators can\'t be banned")
            
            await member.ban()
            return await ctx.message.delete()

    @commands.command(name='mute')
    async def mute(self, ctx, member:discord.Member, timelimit):
        if await cog_check(ctx):
            try:
                timelimitList = [timelimit[:-1], timelimit[-1]]
                timelimitList[0] = int(timelimitList[0])
            except:
                return await wups(ctx, "Invalid time amount")
            valid = False
            timelimit = timelimit.lower()
            timepossibilities = ['s', 'm', 'h', 'd', 'w']
            if timelimit[-1] in timepossibilities:
                valid = True
            current_time = discord.utils.utcnow()
        
            if not ctx.author.guild_permissions.administrator:
                return await wups(ctx, "Only administrators are allowed to use this command")
            if member.guild_permissions.administrator:
                return await wups(ctx, "Administrators can\'t be muted")
            if not valid:
                return await wups(ctx, "Invalid time amount")
            
            time_units = {
                's': (timedelta, 'seconds', 2419200),
                'm': (timedelta, 'minutes', 40320),
                'h': (timedelta, 'hours', 672),
                'd': (timedelta, 'days', 28),
                'w': (timedelta, 'weeks', 4)
            }

            for unit, (timedelta_type, attribute, limit) in time_units.items():
                if unit in timelimit:
                    gettime = int(timelimit.strip(unit))
                    if gettime > limit:
                        return await wups(ctx, "Cannot mute member for more than 4 weeks")
                    newtime = timedelta_type(**{attribute: gettime})
                    break
            
            await member.edit(timed_out_until=current_time+newtime)
            return await ctx.message.delete()

    @commands.command(name='unmute')
    async def unmute(self, ctx, member:discord.Member):
        if await cog_check(ctx):
            if not ctx.message.author.guild_permissions.administrator:
                return await wups(ctx, "Only administrators are allowed to use this command")
            if member.guild_permissions.administrator:
                return await wups(ctx, "Administrators can\'t be muted in the first place")
            if not member.is_timed_out():
                return await wups(ctx, "User is not muted in the first place")
    
            await member.edit(timed_out_until=None)
            return await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Admin(bot))
