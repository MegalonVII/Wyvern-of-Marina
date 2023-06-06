import discord
from discord.ext import commands
import random
import asyncio
import datetime
import requests
import json
import urllib.parse
from utils import *

# fun commands start here
# say, custc, snipe, esnipe, choose, who, howgay, rps, 8ball, roulette, trivia, quote, deathbattle
class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.actions = ["{} poisons {}'s drink!", "{} places a frag mine beneath {}'s feet!", "{} passes {} a blunt!", "{} burns down {}'s house!"]
        self.deaths = [" {} dies of dysentery!", " {} explodes!", " {} took one hit of the Blunt9000™️ and descends straight to Hell!", " {} got caught in the fire and burns down to a crisp!"]
        self.survivals = [" {} noticed this and gets another drink...", " {} quickly steps aside...", " {} kindly rejects the offer...", " {} quickly got out of the fire and finds shelter elsewhere..."]
        self.currentFight = False

    @commands.command(name='say')
    async def say(self, ctx, *args):
        try:
            await ctx.message.delete()
            return await ctx.channel.send(" ".join(args).replace('"', '\"').replace("'", "\'"), allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        except:
            await ctx.message.add_reaction('🦈')
            return await ctx.reply("Wups! You need something for me to say...", mention_author=False)
                
    @commands.command(name='customcommands', aliases=['custc'])
    async def customcommands(self, ctx):
        try:
            return await ctx.reply(', '.join(list(lists["commands"].keys())), mention_author=False)
        except:
            await ctx.message.add_reaction('🦈')
            return await ctx.reply('Wups! There are no custom commands...', mention_author=False)

    @commands.command(name='snipe')
    async def snipe(self, ctx):
        channel = ctx.channel
        try:
            data = snipe_data[channel.id]
            if data["attachment"] and 'video' in data["attachment"].content_type:
                data["content"] += f"\n[Attached Video]({data['attachment'].url})"
            embed = discord.Embed(title=f"Last deleted message in #{channel.name}", color = discord.Color.purple(), description=str(data["content"]))
            if data["attachment"] and 'image' in data["attachment"].content_type:
                embed.set_image(url=data["attachment"].url)
            embed.set_footer(text=f"This message was sent by {data['author']}")
            embed.set_thumbnail(url=data['author'].avatar.url)
            return await ctx.reply(embed=embed, mention_author=False)
        except KeyError:
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f"Wups! There are no recently deleted messages in <#{channel.id}>...", mention_author=False)

    @commands.command(name='editsnipe', aliases=['esnipe'])
    async def editsnipe(self, ctx):
        channel = ctx.channel
        try:
            data = editsnipe_data[channel.id]
            embed = discord.Embed(title=f"Last edited message in #{channel.name}", color = discord.Color.purple(), description=str(data["content"]))
            embed.set_footer(text=f"This message was sent by {data['author']}")
            embed.set_thumbnail(url=data["author"].avatar.url)
            return await ctx.reply(embed=embed, mention_author=False)
        except KeyError:
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f"Wups! There are no recently edited messages in <#{channel.id}>...", mention_author=False)

    @commands.command(name='choose')
    async def choose(self, ctx, *args):
        if (len(args) < 2):
            await ctx.message.add_reaction('🦈')
            return await ctx.reply("Wups! You need at least 2 arguments for me to choose from...", mention_author=False)
        return await ctx.reply(f"I choose `{random.choice(args)}`!", mention_author=False)

    @commands.command(name='who')
    async def who(self, ctx):
        return await ctx.reply(f"`{ctx.message.content[3:]}`? {random.choice([member.name for member in ctx.message.guild.members if not member.bot])}", mention_author=False)
        
    @commands.command(name='howgay')
    async def howgay(self, ctx, member:discord.Member=None):
        if assert_cooldown("howgay") != 0:
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('howgay')} seconds...", mention_author=False)
        
        member = member or ctx.author
        percent = random.randint(0,100)
        responses = ['You\'re not into that mentally ill crap.', 'You\'re probably just going through a phase...', 'It\'s ok to be gay, buddy. We\'ll support you... unless you make it your entire personality.', 'You **LOVE** it up the rear end, don\'t you?']
        if percent >= 0 and percent <= 25:
            response = responses[0]
        elif percent >= 26 and percent <= 50:
            response = responses[1]
        elif percent >= 51 and percent <= 75:
            response = responses[2]
        elif percent >= 76 and percent <= 100:
            response = responses[3]
        
        return await ctx.reply(f"{member.name} is {percent}% gay. {response}",mention_author=False)

    @commands.command(name='rps')
    async def rps(self, ctx, playerChoice: str=None):
        if await in_wom_shenanigans(ctx):
            if assert_cooldown("rps") != 0 :
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('rps')} seconds...", mention_author=False)
            if playerChoice is None:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! You need to give me your choice...", mention_author=False)
            
            playerChoice = playerChoice.lower()
            choices = ['rock', 'paper', 'scissors']
            if playerChoice not in choices:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Invalid choice...", mention_author=False)
            else:
                botChoice = random.choice(choices)
                if playerChoice == botChoice: # tie
                    return await ctx.reply(f"I chose `{botChoice}`.\nUgh! Boring! We tied...", mention_author=False)
                elif (playerChoice == choices[0] and botChoice == choices[1]) or \
                    (playerChoice == choices[1] and botChoice == choices[2]) or \
                    (playerChoice == choices[2] and botChoice == choices[0]): # win
                        return await ctx.reply(f"I chose `{botChoice}`.\nHah! I win, sucker! Why'd you pick that one, stupid?", mention_author=False)
                else: # lose
                    return await ctx.reply(f"I chose `{botChoice}`.\nWell played there. You have bested me...", mention_author=False)

    @commands.command(name='8ball')
    async def eightball(self, ctx):
        if assert_cooldown("8ball") != 0 :
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('8ball')} seconds...", mention_author=False)
        if len(ctx.message.content) < 9:
            await ctx.message.add_reaction('🦈')
            return await ctx.reply("Wups! You need to give me a question to respond to...", mention_author=False)
        
        responses = ['Hell yeah!', 'It is certain.', 'Without a doubt.', 'You may rely on it.', 'Yes, definitely.', 'It is decidedly so.', 'As I see it, yes.', 'Most likely.', 'Yes.', 'Outlook good.', 'Signs point to yes.', 'You already know the answer.', 'Reply hazy, try again.', 'Better not tell you now.', 'Ask again later.', 'Cannot predict now.', 'Concentrate and ask again.', 'Don\'t count on it.', 'Outlook not so good.', 'My sources say no.', 'Very doubtful.', 'My reply is no.', 'No.', 'Oh god, no.']
        return await ctx.reply(f"🎱 `{ctx.message.content[9:]}` 🎱\n{random.choice(responses)}", mention_author=False)

    @commands.command(name='roulette')
    async def roulette(self, ctx, member:discord.Member=None):
        if assert_cooldown("roulette") != 0:
            await ctx.message.add_reaction('🦈')
            return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('roulette')} seconds...", mention_author=False)
        
        member = member or ctx.author
        if member == ctx.author: # if a member wants to roulette themselves
            if not member.guild_permissions.administrator:
                if random.randint(1,6) == 1:
                    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                    return await ctx.reply("🔥🔫 You died! (muted for 1 hour)", mention_author=False)
                add_coins(member.id,1)
                return await ctx.reply(f"🚬🔫 Looks like you\'re safe, for now... You also won 1 {zenny}!", mention_author=False)
            return await ctx.reply("❌🔫 Looks like you\'re safe, you filthy admin...", mention_author=False)
        
        else: # if an admin wants to roulette a member they specify
            if not ctx.message.author.guild_permissions.administrator:
                if member == ctx.author:  # roulette themselves if not admin (pinged themself)
                    if random.randint(1,6) == 1:
                        await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                        return await ctx.reply("🔥🔫 You died! (muted for 1 hour)", mention_author=False)
                    add_coins(member.id,1)
                    return await ctx.reply(f"🚬🔫 Looks like you\'re safe, for now... You also won 1 {zenny}!", mention_author=False)
                return await ctx.reply("❌🔫 A lowlife like you can\'t possibly fire the gun at someone else...", mention_author=False)
            elif member == ctx.author: # admin tries rouletting themself
                return await ctx.reply("❌🔫 Admins are valued. Don\'t roulette an admin like yourself...", mention_author=False)
            elif member.is_timed_out() == True: # admin tries rouletting a "dead" server member
                return await ctx.reply("❌🔫 Don\'t you think it\'d be overkill to shoot a dead body?", mention_author=False)
            else:
                if not member.guild_permissions.administrator: # admin tries rouletting "alive" non admin
                    if random.randint(1,6) == 1:
                        await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=1), reason='roulette')
                        return await ctx.reply("🔥🔫 This user died! (muted for 1 hour)", mention_author=False)
                    add_coins(member.id,1)
                    return await ctx.reply(f"🚬🔫 Looks like they\'re safe, for now... They also won 1 {zenny}!", mention_author=False)
                return await ctx.reply("❌🔫 Looks like they\'re safe, that filthy admin...", mention_author=False)

    @commands.command(name='trivia')
    async def trivia(self, ctx, type:str = None):
        if await in_wom_shenanigans(ctx):
            types = ['general', 'film', 'music', 'tv', 'games', 'anime']
            categories = [9, 11, 12, 14, 15, 31]
            if assert_cooldown('trivia') != 0:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('trivia')} seconds...", mention_author=False)
            if not type is None and type.lower() not in types:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply("Wups! Invalid trivia type...", mention_author=False)
            
            async with ctx.typing():
                if type is None:
                    response = requests.get(f"https://opentdb.com/api.php?amount=1&category={random.choice(categories)}&type=multiple&encode=url3986")
                else:
                    for typing, category in zip(types, categories):
                        if type.lower() == typing:
                            response = requests.get(f"https://opentdb.com/api.php?amount=1&category={category}&type=multiple&encode=url3986")
                            break
                data = json.loads(response.text)
                correct_answer = urllib.parse.unquote(data['results'][0]['correct_answer'])
                incorrect_answers = data['results'][0]['incorrect_answers']
                options = [urllib.parse.unquote(answer) for answer in incorrect_answers] + [correct_answer]
            random.shuffle(options)
            quiz_embed = discord.Embed(title="❓ Trivia ❓", description=urllib.parse.unquote(data['results'][0]['question']), color=discord.Color.purple())
            quiz_embed.add_field(name="Options", value="\n".join(options), inline=False)
            quiz_embed.set_footer(text="You have 15 seconds to answer. Type the letter of your answer (A, B, C, D).")
            await ctx.reply(embed=quiz_embed, mention_author=False)
        
            def check_answer(message):
                return message.author == ctx.author and message.content.lower() in ['a', 'b', 'c', 'd'] and message.channel == ctx.message.channel
        
            try:
                answer_message = await self.bot.wait_for('message', timeout=15.0, check=check_answer)
            except asyncio.TimeoutError:
                return await ctx.reply(f"Time's up! The correct answer was **{correct_answer}**.", mention_author=False)
            else:
                if answer_message.content.lower() == 'a':
                    selected_answer = options[0]
                elif answer_message.content.lower() == 'b':
                    selected_answer = options[1]
                elif answer_message.content.lower() == 'c':
                    selected_answer = options[2]
                elif answer_message.content.lower() == 'd':
                    selected_answer = options[3]
        
                if selected_answer == correct_answer:
                    add_coins(ctx.author.id, 10)
                    return await answer_message.reply(f"Correct! The answer is **{correct_answer}**. 10 {zenny}!", mention_author=False)
                return await answer_message.reply(f"Sorry, that's incorrect. The correct answer is **{correct_answer}**.", mention_author=False)

    @commands.command(name='quote')
    async def quote(self, ctx):
        if await in_wom_shenanigans(ctx):
            if assert_cooldown('quote') != 0:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! Slow down there, bub! Command on cooldown for another {assert_cooldown('quote')} seconds...", mention_author=False)

            async with ctx.typing():
                response = requests.get(f'https://ultima.rest/api/quote?id={random.randint(1,552)}')
                data = json.loads(response.text)
            quote = data['quote']
            character = data['character']
            title = data['title']
            release = data['release']
            embed = discord.Embed(title="💬 Quote 💬", description=f'"{quote}"', color=discord.Color.purple())
            embed.set_footer(text=f"From: {character} - {title}, {release}")
            return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='deathbattle', aliases=['db'])
    async def deathbattle(self, ctx, member: discord.Member):
        if await in_wom_shenanigans(ctx):
            if self.currentFight:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! There is currently a fight going on...", mention_author=False)
            if member.bot:
                await ctx.message.add_reaction('🦈')
                return await ctx.reply(f"Wups! You can't fight a bot...", mention_author=False)
              
        self.currentFight = True
        players = [ctx.author, member] if random.choice([True, False]) else [member, ctx.author]
        turn = 0
        am = discord.AllowedMentions.none()
        msg = await ctx.reply(f"{ctx.author.name} challenges {member.name} to the death!", mention_author=False)
        await asyncio.sleep(3)
        while True:
            if turn % 2 == 0:
                actor = players[0]
                target = players[1]
            else:
                actor = players[1]
                target = players[0]
            choiceNum = random.randint(0, len(self.actions) - 1)
            action = self.actions[choiceNum]
            await msg.edit(content=action.format(actor.name, target.name), allowed_mentions=am)
            await asyncio.sleep(2)
            determinant = random.randint(1, 5)
            if determinant == 1:
                response = action + self.deaths[choiceNum]
            else:
                response = action + self.survivals[choiceNum]
            await msg.edit(content=response.format(actor.name, target.name, target.name), allowed_mentions=am)
            if determinant == 1:
                self.currentFight = False
                break
            else:
                turn += 1
                await asyncio.sleep(3)
        return None
                

async def setup(bot):
    await bot.add_cog(Fun(bot))
