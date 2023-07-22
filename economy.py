import discord
from discord.ext import commands
import random
import datetime
import asyncio
from math import ceil
from utils import *

# economy commands
# slots, bet, steal, heist, dep, wd, bal, bankbal, paypal, mp, buy, sell, inv, use
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.items = ['delivery', 'bomb','ticket', 'letter', 'shell', 'banana']
        self.prices = [100000, 10000, 2500, 1000, 500, 10]
        self.priceStrs = ['100,000', '10,000', '2,500', '1,000', '500', '10']
        self.descs = ['Have Blues personally deliver their WoM plushie to you!', 'Siphon half of the Zenny from a random that they have in the bank!', 'Redeem this ticket for a custom role!', 'Send a letter to anyone in this server!', 'Siphon half of the Zenny from a random person that they have on hand!', 'Grab this illusive, mysterious banana!']
  
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
                if reels.count("7️⃣") == 2:
                    add_coins(ctx.author.id,50)
                    return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nTwo lucky 7's! 50 {zenny}!", allowed_mentions=discord.AllowedMentions.none())
                add_coins(ctx.author.id,25)
                return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nNice! 25 {zenny}!", allowed_mentions=discord.AllowedMentions.none())
            return await msg.edit(content=f"{reels[0]} | {reels[1]} | {reels[2]}\nBetter luck next time...", allowed_mentions=discord.AllowedMentions.none())

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

    @commands.command(name='steal')
    async def steal(self, ctx, target: discord.Member):
        global prev_steal_targets, target_counts
        if await in_wom_shenanigans(ctx):
            if target.bot or target == ctx.author:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! You can't steal from a bot or from yourself...", mention_author=False)
            if prev_steal_targets.get(ctx.author.id) == target and target_counts.get(ctx.author.id, 0) <= 2:
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
            
            if random.randint(1,10) <= 5:
                random_steal = random.randint(1,100)
                if subtract_coins(target.id, random_steal):
                    add_coins(ctx.author.id, random_steal) # successful steal
                    return await ctx.reply(f"You successfully stole {random_steal} {zenny} from {target.name}!", mention_author=False)
                else:
                    return await ctx.reply(f"You tried stealing {random_steal} {zenny} from {target.name}, but they don't have enough {zenny} on hand...", mention_author=False) # successful steal, but couldn't do it
            
            else: 
                lost_coins = random.randint(1, 100)
                if subtract_coins(ctx.author.id, lost_coins): # unsuccessful steal
                    add_coins(target.id, lost_coins)
                    return await ctx.reply(f"You got caught trying to steal {lost_coins} {zenny} from {target.name}! You were forced to pay them back instead...", mention_author=False)
                else:
                    return await ctx.reply(f"You got caught trying to steal {lost_coins} {zenny} from {target.name}! However, you weren't able to pay them back...", mention_author=False) # successful steal, couldn't pay back

    @commands.command(name='heist')
    async def heist(self, ctx):
        if await in_wom_shenanigans(ctx):
            if assert_cooldown("heist") != 0:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('heist')} seconds...", mention_author=False)
            if random.randint(1, 100) == 1: # successful heist
                total = 0
                for key in lists['bank'].keys():
                    amount = int(lists['bank'][key])
                    if stolen_funds(int(key), amount):
                        total += amount
                        add_coins(ctx.author.id, amount)
                return await ctx.reply(f"Successful heist! {total} {zenny}!", mention_author=False)
            else: # unsuccesful heist
                handBal = int(lists['coins'][str(ctx.author.id)])
                bankBal = int(lists['bank'][str(ctx.author.id)])
                if handBal != 0: # check if can take from hand
                    bail = ceil(handBal * 0.2)
                    if subtract_coins(ctx.author.id, bail):
                        return await ctx.reply(f"Unsuccessful heist! <:PoM:888677251615449158> arrested you! You paid {bail} {zenny} as bail...", mention_author=False)
                elif handBal == 0 and bankBal != 0: # can't take from hand, takes from bank instead
                    bail = ceil(bankBal * 0.2)
                    if stolen_funds(ctx.author.id, bail):
                        return await ctx.reply(f"Unsuccessful heist! <:PoM:888677251615449158> arrested you! You paid {bail} {zenny} from the bank as bail...", mention_author=False)
                else: # can't take from either
                    return await ctx.reply("Unsuccessful heist! <:PoM:888677251615449158> arrested you! You couldn't pay a bail, however, so you spent the night in jail...", mention_author=False)

    @commands.command(name='deposit', aliases=['dep'])
    async def deposit(self, ctx, amt:int):
        if await in_wom_shenanigans(ctx):
            if dep(ctx.author.id, amt):
                return await ctx.reply(f"Successfully deposited {amt} {zenny}!", mention_author=False)
            await ctx.message.add_reaction('🦈')
            return await ctx.reply("Wups! Insufficient funds...", mention_author=False)

    @commands.command(name='withdraw', aliases=['wd'])
    async def withdraw(self, ctx, amt:int):
        if await in_wom_shenanigans(ctx):
            if wd(ctx.author.id, amt):
                return await ctx.reply(f"Successfully withdrew {amt} {zenny}!", mention_author=False)
            await ctx.message.add_reaction('🦈')
            return await ctx.reply("Wups! Insufficient funds...", mention_author=False)

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

    @commands.command(name='bankbalance', aliases=['bankbal'])
    async def bankbalance(self, ctx):
        for userID in lists['bank'].keys():
            if str(ctx.author.id) == userID:
                return await ctx.reply(f"You have {lists['bank'][str(ctx.author.id)]} {zenny} in the bank!", mention_author=False)
        await ctx.message.add_reaction('🦈')
        return await ctx.reply("Wups! Get some bread, broke ass...", mention_author=False)

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

    @commands.command(name='marketplace', aliases=['mp'])
    async def marketplace(self, ctx):
        embed = discord.Embed(title='Marketplace', color=discord.Color.green())
        for i in range(0, len(self.items)):
            embed.add_field(name=f'{self.items[i]}, {self.priceStrs[i]} {zenny}', value=f'{self.descs[i]}', inline=False)
        embed.set_footer(text='If you want to purchase any of these items, use !w buy (item name). The item name is exactly as you see it in this marketplace!')
        return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='buy')
    async def buy(self, ctx, item:str, number:int = 1):
        if await in_wom_shenanigans(ctx):
            if number < 1:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Invalid number requested...", mention_author=False)
            item = item.lower()
            for item_name, item_price in zip(self.items, self.prices):
                if item.lower() == item_name:
                    if not subtract_coins(ctx.author.id, number * item_price):
                        await ctx.message.add_reaction('🦈')
                        return await ctx.reply(f"Wups! You don't have enough {zenny}...", mention_author=False)
                    add_item(item, ctx.author.id, number)
                    if number > 1:
                        return await ctx.reply(f"You have successfully purchased {number} {item_name}s!", mention_author=False)
                    else:
                        return await ctx.reply(f"You have successfully purchased {number} {item_name}!", mention_author=False)
            await ctx.message.add_reaction('🦈')
            return await ctx.reply("Wups! Invalid item...", mention_author=False)

    @commands.command(name='sell')
    async def sell(self, ctx, item:str, number:int = 1):
        if await in_wom_shenanigans(ctx):
            if number < 1:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Invalid number requested...", mention_author=False)
            item = item.lower()
            for name, price in zip(self.items, self.prices):
                sell = price // 2
                if item == name:
                    if subtract_item(item, ctx.author.id, number):
                        add_coins(ctx.author.id, number * sell)
                        if number == 1:
                            return await ctx.reply(f'Successfully sold {number} {item}! {sell} {zenny}!', mention_author=False)
                        else:
                            return await ctx.reply(f'Successfully sold {number} {item}s! {sell} {zenny}!', mention_author=False)
                    await ctx.message.add_reaction('🦈')
                    return await ctx.reply(f"Wups! You don't have that many {item}s...", mention_author=False) 
            await ctx.message.add_reaction('🦈')
            return await ctx.reply("Wups! Invalid item...", mention_author=False)
  
    @commands.command(name='inventory', aliases=['inv'])
    async def inventory(self, ctx):
        if await in_wom_shenanigans(ctx):
            inventorySTR = "You have...\n\n"
            async with ctx.typing():
                for item in self.items:
                    inventorySTR += f'{int(lists[item].get(str(ctx.author.id), 0))} {item}s\n'
            return await ctx.reply(inventorySTR, mention_author=False)

    @commands.command(name='use')
    async def use(self, ctx, item:str):
        if await in_wom_shenanigans(ctx):
            item = item.lower()
            if item not in self.items:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Invalid item...", mention_author=False)

            if item == 'delivery':
                if subtract_item(item, ctx.author.id, 1):
                    blues = 232041680017031168
                    moddery = discord.utils.get(ctx.guild.channels, name='moddery')
                    await moddery.send(f"<@{blues}>, {ctx.author.name} has purchased a delivery. You are now obligated to personally deliver your plushie of me to them! Don't back out of it now...")
                    return await ctx.reply("Blues has been notified, you gambling-addicted bastard...", mention_author=False)
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You don't have a {item}...", mention_author=False)

            elif item == 'bomb':
                if subtract_item(item, ctx.author.id, 1):
                    id = random.choice([key for key in lists['bank'].keys() if not key == str(ctx.author.id)])
                    balance = int(lists['bank'][id])
                    id = int(id)
                    stolen = balance // 2
                    member = discord.utils.get(ctx.guild.members, id=id)
                    if stolen_funds(id, stolen):
                        direct_to_bank(ctx.author.id, stolen)
                        return await ctx.reply(f"Stole {stolen} {zenny} from {member.name}'s bank account! That {zenny} has been deposited into your bank account!", mention_author=False)
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You don't have a {item}...", mention_author=False)

            elif item == 'ticket':
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                if subtract_item(item, ctx.author.id, 1):
                    await ctx.reply("You have 60 seconds to name your new custom role! This can be done by simply sending the name of that role in this channel. Be aware, however, that the next message you send will be the role name...", mention_author=False)
                    try:
                        msg = await self.bot.wait_for('message', check=check, timeout=60)
                    except asyncio.TimeoutError:
                        add_item(item, ctx.author.id, 1)
                        return await ctx.reply("Time's up! You didn't provide me with a role name, so I've given you your ticket back. Try again later...", mention_author=False)
                    name = msg.content
                    role = await ctx.guild.create_role(name=name)
                    await ctx.author.add_roles(role)
                    return await msg.reply("Congrats on your new role!", mention_author=False)
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You don't have a {item}...", mention_author=False)

            elif item == 'letter':
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                if subtract_item(item, ctx.author.id, 1):
                    await ctx.reply('You have 30 seconds to give me the name of a member you want to send a letter to! Your next message in this channel is what I will use to find the member\'s name!', mention_author=False)
                    try:
                        msg = await self.bot.wait_for('message', check=check, timeout=30)
                    except asyncio.TimeoutError:
                        add_item(item, ctx.author.id, 1)
                        return await ctx.reply(f"Time's up! You didn't provide me with anyone's name, so I've given you back your {item}...", mention_author=False)
                    recipient = discord.utils.get(ctx.guild.members, name=str(msg.content))
                    if recipient is None or recipient.bot or recipient == ctx.author:
                        add_item(item, ctx.author.id, 1)
                        await msg.delete()
                        await ctx.message.add_reaction('🦈')
                        return await ctx.reply(f"Wups! Invalid member name. I've refunded you your {item}...", mention_author=False)
                      
                    await msg.reply("Great! Now you have 2 minutes to cook up your letter to this person. Your next message in this channel will dictate that!", mention_author=False)
                    try:
                        content = await self.bot.wait_for('message', check=check, timeout=120)
                    except asyncio.TimeoutError:
                        add_item(item, ctx.author.id, 1)
                        await msg.reply(f"Time's up! You didn't provide me with any content, so I've given you back your {item}...", mention_author=False)
                        return await msg.delete()
                    contentReplaced = str(content.content).replace("'", "\'").replace('"','\"')
                  
                    await msg.delete()
                    try:
                        await recipient.send(f"__{ctx.author.name} sent you the following letter!__\n'{contentReplaced}'")
                    except:
                        await ctx.guild.system_channel.send(f"Since {recipient.mention} won't allow me to DM them, I guess I'll just have to air out to the entire world their letter from {ctx.author.name}...\n\n'{contentReplaced}'")
                    await content.reply("Message sent!", mention_author=False)
                    return await content.delete()

            elif item == 'shell':
                if subtract_item(item, ctx.author.id, 1):
                    target = random.choice([member for member in ctx.guild.members if not member.bot and not member == ctx.author])
                    balance = int(lists['coins'][str(target.id)])
                    if balance % 2 == 1:
                        add_coins(target.id, 1)
                        balance = int(lists['coins'][str(target.id)])
                    if subtract_coins(target.id, int(balance // 2)):
                        add_coins(ctx.author.id, int(balance // 2))
                        return await ctx.reply(f"{target.name} got hit by a {item}! You received {balance // 2} {zenny} from them!", mention_author=False)
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You don't have a {item}...", mention_author=False)

            elif item == 'banana':
                if subtract_item(item, ctx.author.id, 1):
                    msg = await ctx.reply("You ate a banana! You feel something funny inside your body...", mention_author=False)
                    await asyncio.sleep(3)
                    return await msg.edit(content="Turns out that was just your stomach growling. The banana you just ate was a regular old banana...", allowed_mentions=discord.AllowedMentions.none())

async def setup(bot):
    await bot.add_cog(Economy(bot))
