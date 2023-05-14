import discord
import os
import csv
from discord.ext import commands
from keep_alive import keep_alive
import random
import pandas as pd
import asyncio
import datetime
import requests
import json
import urllib.parse
from utils import *

# economy commands
# slots, balance, leaderboard, paypal, bet
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='slots')
    async def slots(self, ctx):
        if await in_wom_shenanigans(ctx):
            if assert_cooldown('slots') != 0:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('slots')} seconds...", mention_author=False)
            if not subtract_coins(ctx.author.id, 10):
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You don't have enough {zenny} to play...", mention_author=False)
        
            emojis = ["🍒", "🍇", "🍊", "🍋", "🍉","7️⃣"]
            reels = ["❓","❓","❓"]
            msg = await ctx.reply(f"{reels[0]} | {reels[1]} | {reels[2]}", mention_author=False)
            for i in range(0,3):
                await asyncio.sleep(1)
                reels[i] = random.choice(emojis)
                await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}", allowed_mentions=discord.AllowedMentions.none())
            if all(reel == "7️⃣" for reel in reels):
                add_coins(ctx.author.id,500)
                return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\n**Jackpot**! 500 {zenny}!", allowed_mentions=discord.AllowedMentions.none())
            elif len(set(reels)) == 1 and reels[0] != "7️⃣":
                add_coins(ctx.author.id,100)
                return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nSmall prize! 100 {zenny}!", allowed_mentions=discord.AllowedMentions.none())
            elif len(set(reels)) == 2:
                add_coins(ctx.author.id,25)
                return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nNice! 25 {zenny}!", allowed_mentions=discord.AllowedMentions.none())
            return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nBetter luck next time...", allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name='balance', aliases=['bal'])
    async def balance(self, ctx, member:discord.Member = None):
        member = member or ctx.author
        if not member == ctx.author:
            if subtract_coins(ctx.author.id, 10):
                add_coins(member.id, 10)
            else:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Insufficient funds...", mention_author=False)
        for userID in lists['coins'].keys():
            if str(member.id) == userID:
                if not member == ctx.author:
                    return await ctx.reply(f"{member.name} has {lists['coins'][str(member.id)]} {zenny}!", mention_author=False)
                return await ctx.reply(f"You have {lists['coins'][str(member.id)]} {zenny}!", mention_author=False)
        await ctx.message.add_reaction('🦈')
        return await ctx.reply("Wups! Get some bread, broke ass...", mention_author=False)

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx):
        async with ctx.typing():
            df = pd.read_csv("coins.csv")
            df_sorted = df.sort_values("coins", ascending=False)
            df_sorted.to_csv("coins.csv", index=False)
            create_list('coins')
        top_users = [(k, lists['coins'][k]) for k in list(lists['coins'])[:5]]
        embed = discord.Embed(title=f'Top {len(top_users)} Richest Users', color=discord.Color.purple())
        if len(top_users) == 1:
            embed.title='Richest User'
        elif len(top_users) == 0:
            return await ctx.reply('Wups! No one is in this economy...', mention_author=False)
        for i, (user_id, z) in enumerate(top_users):
            user = await self.bot.fetch_user(user_id)
            embed.add_field(name=f'#{i+1}: {user.name}', value=f'{z} {zenny}', inline=False)
            if i == 0:
                embed.set_thumbnail(url=user.avatar.url)
        return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='steal')
    async def steal(self, ctx, target: discord.Member):
        global prev_steal_targets, target_counts
        if await in_wom_shenanigans(ctx):
            if target.bot or target == ctx.author:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! You can't steal from a bot or from yourself...", mention_author=False)
            if prev_steal_targets.get(ctx.author.id) == target and target_counts.get(ctx.author.id, 0) < 2:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! You can't target this person again so soon. Choose a different target...", mention_author=False)
            if assert_cooldown('steal') != 0:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('steal')} seconds...", mention_author=False)
        
            if prev_steal_targets.get(ctx.author.id) != target:
                target_counts[ctx.author.id] = target_counts.get(ctx.author.id, 0) + 1
                prev_steal_targets[ctx.author.id] = target
            if target_counts.get(ctx.author.id, 0) >= 2:
                target_counts[ctx.author.id] = 0
            richest_person = discord.utils.get(ctx.guild.members, id=int(max(lists['coins'].keys(), key=(lambda k: lists['coins'][k]))))
            steal_chance = 6 if target == richest_person else 4
            
            if random.randint(1,10) <= steal_chance:
                random_steal = random.randint(1,100)
                if subtract_coins(target.id, random_steal):
                    add_coins(ctx.author.id, random_steal) # successful steal
                    return await ctx.reply(f"You successfully stole {random_steal} {zenny} from {target.name}!", mention_author=False)
                else:
                    return await ctx.reply(f"You tried stealing {random_steal} {zenny} from {target.name}, but they don't have enough {zenny}...", mention_author=False) # successful steal, but couldn't do it
            
            else: 
                lost_coins = random.randint(1, 100)
                if subtract_coins(ctx.author.id, lost_coins): # unsuccessful steal
                    add_coins(target.id, lost_coins)
                    return await ctx.reply(f"You got caught trying to steal {lost_coins} {zenny} from {target.name}! You were forced to pay them back instead...", mention_author=False)
                else:
                    return await ctx.reply(f"You got caught trying to steal {lost_coins} {zenny} from {target.name}! However, you weren't able to pay them back...", mention_author=False) # successful steal, couldn't pay back

    @commands.command(name='paypal')
    async def paypal(self, ctx, recipient:discord.Member, amount:int):
        if await in_wom_shenanigans(ctx):
            if amount <= 0:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Invalid payment amount...", mention_author=False)
            if recipient.bot or recipient.id == ctx.author.id:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! You can't pay a bot or yourself...", mention_author=False)
            if subtract_coins(ctx.author.id,amount):
                add_coins(recipient.id,amount)
                return await ctx.reply(f"{recipient.name} has received {amount} {zenny} from you!", mention_author=False)
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f"Wups! You don't have that much {zenny}...", mention_author=False)

    @commands.command(name='bet')
    async def bet(self, ctx, amount:int):
        if await in_wom_shenanigans(ctx):
            if assert_cooldown('bet'):
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('bet')} seconds...", mention_author=False)
            if subtract_coins(ctx.author.id, amount):
                roll = random.randint(1,6)
                roll2 = random.randint(1,6)
                result = roll + roll2
                if result == 7:
                    add_coins(ctx.author.id, 2*amount)
                    return await ctx.reply(f"You rolled a {result}! You win!", mention_author=False)
                return await ctx.reply(f"You rolled a {result}! Sorry, you lost...", mention_author=False)
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f"Wups! You can't bet that much {zenny} as you don't have that much...",mention_author=False)    

async def setup(bot):
    await bot.add_cog(Economy(bot))