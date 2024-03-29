import discord
import csv
from discord.ext import commands
import pandas as pd
from datetime import timedelta
from utils import *

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
                    await shark_react(ctx.message)
                    return await ctx.reply('Wups! You need to give me an output for your new command...', mention_author = False)
                elif not ctx.author.guild_permissions.manage_messages:
                    await shark_react(ctx.message)
                    return await ctx.reply("Wups! You do not have the required permissions...", mention_author=False)
                elif name in list(lists["commands"].keys()):
                    await shark_react(ctx.message)
                    return await ctx.reply('Wups! This command already exists...', mention_author=False)
                
                output = ' '.join(output).replace('"', '\"').replace("'", "\'")
                with open('csv/commands.csv', 'a', newline='') as csvfile:
                    fieldnames = ['command_name', 'command_output']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    if file_checks["commands"]:
                        writer.writeheader()
                    writer.writerow({'command_name': name, 'command_output': output})
                create_list("commands")
                return await ctx.reply(f"The command {name} has been created!", mention_author=False)
            except:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! I don\'t have a name for a command...', mention_author=False)
                    
    @commands.command(name='deletecommand', aliases=['dc'])
    async def deletecommand(self, ctx, name):
        if await cog_check(ctx):
            if not ctx.author.guild_permissions.manage_messages:
                await shark_react(ctx.message)
                return await ctx.reply('Wups, you do not have the required permissions...', mention_author=False)
            if not name in list(lists["commands"].keys()):
                await shark_react(ctx.message)
                return await ctx.reply('Wups! This command does not exist...', mention_author=False)
            if len(list(lists["commands"].keys())) == 0:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! There are no commands to delete in the first place...', mention_author=False)
    
            commands = pd.read_csv('csv/commands.csv')
            commands = commands[commands.command_name != name]
            commands.to_csv('csv/commands.csv', index=False)
            create_list("commands")
            return await ctx.reply(f'The command {name} has been deleted!', mention_author=False)

    @commands.command(name='clear')
    async def clear(self, ctx, num:int=None):
        if await cog_check(ctx):
            if not ctx.author.guild_permissions.manage_messages:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! You do not have the required permissions...', mention_author=False)
            if num is None or num < 1 or num > 10:
                await shark_react(ctx.message)
                return await ctx.reply('Wups! Please enter a number between 1 and 10...', mention_author=False)
            if assert_cooldown("clear") != 0:
                await shark_react(ctx.message)
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('clear')} seconds...", mention_author=False)
    
            await ctx.message.add_reaction('✅')
            return await ctx.message.channel.purge(limit=num+1)

    @commands.command(name='kick')
    async def kick(self, ctx, member:discord.Member):  
        if await cog_check(ctx):
            if not ctx.author.guild_permissions.administrator:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
            if member.guild_permissions.administrator and not member.bot:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Administrators can\'t be kicked...", mention_author=False)
            
            await member.kick()
            await ctx.message.delete()
            return await ctx.guild.system_channel.send(f"{member.name} has been kicked! Hope you learn from your mistake... <:do_not:1077435360537223238>")

    @commands.command(name='ban')
    async def ban(self, ctx, member:discord.Member):
        if await cog_check(ctx):
            if not ctx.author.guild_permissions.administrator:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
            if member.guild_permissions.administrator and not member.bot:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Administrators can\'t be banned...", mention_author=False)
            
            await member.ban()
            return await ctx.message.delete()

    @commands.command(name='mute')
    async def mute(self, ctx, member:discord.Member, timelimit):
        if await cog_check(ctx):
            try:
                timelimitList = [timelimit[:-1], timelimit[-1]]
                timelimitList[0] = int(timelimitList[0])
            except:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Invalid time amount...", mention_author=False)
            valid = False
            timelimit = timelimit.lower()
            timepossibilities = ['s', 'm', 'h', 'd', 'w']
            if timelimit[-1] in timepossibilities:
                valid = True
            current_time = discord.utils.utcnow()
        
            if not ctx.author.guild_permissions.administrator:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
            if member.guild_permissions.administrator:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Administrators can\'t be muted...", mention_author=False)
            if not valid:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Invalid time amount...", mention_author=False)
            
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
                        await shark_react(ctx.message)
                        return await ctx.reply("Wups! Cannot mute member for more than 4 weeks...", mention_author=False)
                    newtime = timedelta_type(**{attribute: gettime})
                    break
            
            await member.edit(timed_out_until=current_time+newtime)
            return await ctx.message.delete()

    @commands.command(name='unmute')
    async def unmute(self, ctx, member:discord.Member):
        if await cog_check(ctx):
            if not ctx.message.author.guild_permissions.administrator:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Only administrators are allowed to use this command...", mention_author=False)
            if member.guild_permissions.administrator:
                await shark_react(ctx.message)
                return await ctx.reply("Wups! Administrators can\'t be muted in the first place...", mention_author=False)
            if not member.is_timed_out():
                await shark_react(ctx.message)
                return await ctx.reply("Wups! User is not muted in the first place...", mention_author=False)
    
            await member.edit(timed_out_until=None)
            return await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Admin(bot))
