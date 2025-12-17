import discord
from discord.ext import commands
import random
import asyncio
from datetime import timedelta
import requests
import json
import urllib.parse
import pypokedex as dex

from utils import lists, snipe_data, editsnipe_data, zenny # utils direct values
from utils import shark_react, reply, wups, capitalize_string, assert_cooldown, in_wom_shenanigans, add_coins, in_channels, in_threads, load_info, load_emulation # utils functions

# fun commands start here
# say, custc, snipe, esnipe, choose, pokedex, who, howgay, rps, 8ball, roulette, trivia, emulation, deathbattle, ship
class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.info = ["actions", "deaths", "survivals", "shipNotes"]
        for item in self.info:
            setattr(self, item, load_info(item))
        self.consoles = load_emulation()
        self.currentFight = False

    @commands.command(name='say')
    async def say(self, ctx, *args):
        try:
            await ctx.message.delete()
            return await ctx.channel.send(" ".join(args).replace('"', '\"').replace("'", "\'"), allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        except:
            return await wups(ctx, "You need something for me to say")
                
    @commands.command(name='customcommands', aliases=['custc'])
    async def customcommands(self, ctx):
        try:
            return await reply(ctx, ', '.join(list(lists["commands"].keys())))
        except:
            return await wups(ctx, 'There are no custom commands')

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
            return await wups(ctx, f"There are no recently deleted messages in <#{channel.id}>")

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
            return await wups(ctx, f"There are no recently edited messages in <#{channel.id}>")

    @commands.command(name='choose')
    async def choose(self, ctx, *args):
        if (len(args) < 2):
            return await wups(ctx, "You need at least 2 arguments for me to choose from")
        return await reply(ctx, f"I choose `{random.choice(args)}`!")

    @commands.command(name='pokedex')
    async def pokedex(self, ctx, index: int):
        if index > 1017 or index < 1:
            return await wups(ctx, "Invalid index")
          
        async with ctx.typing():
            # data collections
            pokemon = dex.get(dex=index)
            res = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{index}')
            encRes = requests.get(f'https://pokeapi.co/api/v2/pokemon/{index}/encounters')
            pokRes = requests.get(f'https://pokeapi.co/api/v2/pokemon/{index}/')
            data = res.json()
            encData = encRes.json()
            pokData = pokRes.json()

            # random vars
            shinyInt = random.randint(1,512)
            name = [entry for entry in data["names"] if entry["language"]["name"] == "en"][0]["name"]

            # gender ratio calc
            if data['gender_rate'] == -1:
                gender_ratio = "Genderless"
            elif data['gender_rate'] == 8:
                gender_ratio = "100% Female"
            else:
                female_percentage = (data['gender_rate'] / 8) * 100
                male_percentage = 100 - female_percentage
                gender_ratio = f"{male_percentage}% Male / {female_percentage}% Female"

            # location data calc
            locations = []
            for entry in encData:
                locations.append(capitalize_string(entry['location_area']['name']))

            # moves data calc
            moves = []
            for entry in pokData['moves']:
                moves.append(capitalize_string(entry['move']['name']))

            # make embed
            embed = discord.Embed(title=f'{name}, #{index}', color=discord.Color.red())
            embed.description = ''
            for i, type in enumerate(pokemon.types, 1):
                embed.description += f'**Type {i}**: {capitalize_string(type)}\n'
            embed.description += '\n'
            for i, ability in enumerate(pokemon.abilities, 1):
                embed.description += f'**Ability {i}**: {capitalize_string(ability.name)}{" *(Hidden)*" if ability.is_hidden else ""}\n'
            embed.description += '\n'
            embed.description += f'**Base HP**: {pokemon.base_stats.hp}\n'
            embed.description += f'**Base Attack**: {pokemon.base_stats.attack}\n'
            embed.description += f'**Base Defense**: {pokemon.base_stats.defense}\n'
            embed.description += f'**Base Special Attack**: {pokemon.base_stats.sp_atk}\n'
            embed.description += f'**Base Special Defense**: {pokemon.base_stats.sp_def}\n'
            embed.description += f'**Base Speed**: {pokemon.base_stats.speed}\n'
            embed.description += f'**Base Stat Total**: {pokemon.base_stats.hp + pokemon.base_stats.attack + pokemon.base_stats.defense + pokemon.base_stats.sp_atk + pokemon.base_stats.sp_def + pokemon.base_stats.speed}\n\n'
            embed.description += f'**Base Experience**: {pokemon.base_experience if pokemon.base_experience is not None else 0}\n'
            embed.description += f'**Base Happiness**: {data["base_happiness"]}\n'
            embed.description += f'**Capture Rate**: {data["capture_rate"]}\n\n'
            embed.description += f"**Egg Groups**: {', '.join(capitalize_string(name['name']) for name in [entry for entry in data['egg_groups']])}\n"
            embed.description += f"**Gender Ratio**: {gender_ratio}\n\n"
            embed.description += f"**Found At**: {', '.join(str(location) for location in locations) if len(locations) != 0 else 'No Location Data'}\n"
            embed.description += f"**Moves Learned**: {', '.join(str(move) for move in moves) if index != 151 else 'Every Move'}"

            try:
                embed.set_thumbnail(url=pokemon.sprites.front.get('shiny')) if shinyInt == 1 else embed.set_thumbnail(url=pokemon.sprites.front.get('default'))
                embed.set_footer(text=[entry for entry in data['flavor_text_entries'] if entry['language']['name'] == 'en'][0]['flavor_text'])
            except:
                pass

            if shinyInt != 1:
                return await ctx.reply(embed=embed, mention_author=False)
            else:
                return await ctx.reply(content=f'Woah! A Shiny {name}! ✨', embed=embed, mention_author=False)

    @commands.command(name='who')
    async def who(self, ctx):
        return await reply(ctx, f"`{ctx.message.content[3:]}`? {random.choice([member.display_name for member in ctx.message.guild.members if not member.bot])}")
        
    @commands.command(name='howgay')
    async def howgay(self, ctx, member:discord.Member=None):
        if assert_cooldown("howgay", ctx.author.id) != 0:
            return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('howgay', ctx.author.id)} seconds")
    
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
        
        return await reply(ctx, f"{member.name} is {percent}% gay. {response}")

    @commands.command(name='rps')
    async def rps(self, ctx, playerChoice: str=None):
        if await in_wom_shenanigans(ctx):
            if assert_cooldown("rps", ctx.author.id) != 0 :
                return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('rps', ctx.author.id)} seconds")
            if playerChoice is None:
                return await wups(ctx, "You need to give me your choice")
            
            playerChoice = playerChoice.lower()
            choices = ['rock', 'paper', 'scissors']
            if playerChoice not in choices:
                return await wups(ctx, "Invalid choice")
            else:
                botChoice = random.choice(choices)
                if playerChoice == botChoice: # both tie
                    return await reply(ctx, f"I chose `{botChoice}`.\nUgh! Boring! We tied...")
                elif (playerChoice == choices[0] and botChoice == choices[1]) or \
                    (playerChoice == choices[1] and botChoice == choices[2]) or \
                    (playerChoice == choices[2] and botChoice == choices[0]): # bot wins
                        return await reply(ctx, f"I chose `{botChoice}`.\nHah! I win, sucker! Why'd you pick that one, stupid?")
                else: # bot loses
                    return await reply(ctx, f"I chose `{botChoice}`.\nWell played there. You have bested me...")

    @commands.command(name='8ball')
    async def eightball(self, ctx):
        if assert_cooldown("8ball", ctx.author.id) != 0 :
            return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('8ball', ctx.author.id)} seconds")
        if len(ctx.message.content) < 9:
            return await wups(ctx, "You need to give me a question to respond to")
        
        responses = ['Hell yeah!', 'It is certain.', 'Without a doubt.', 'You may rely on it.', 'Yes, definitely.', 'It is decidedly so.', 'As I see it, yes.', 'Most likely.', 'Yes.', 'Outlook good.', 'Signs point to yes.', 'You already know the answer.', 'Reply hazy, try again.', 'Better not tell you now.', 'Ask again later.', 'Cannot predict now.', 'Concentrate and ask again.', 'Don\'t count on it.', 'Outlook not so good.', 'My sources say no.', 'Very doubtful.', 'My reply is no.', 'No.', 'Oh god, no.']
        return await reply(ctx, f"🎱 `{ctx.message.content[9:]}` 🎱\n{random.choice(responses)}")

    @commands.command(name='roulette')
    async def roulette(self, ctx, member:discord.Member=None):
        if assert_cooldown("roulette", ctx.author.id) != 0:
            return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('roulette', ctx.author.id)} seconds")

        if member.bot:
            return await wups(ctx, "❌🔫 You can\'t shoot the one with the bullets")

        member = member or ctx.author
        chance = int(lists["karma"][str(member.id)])
        if member == ctx.author: # if a member wants to roulette themselves
            if not member.guild_permissions.administrator:
                if random.randint(1,chance) == 1:
                    await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(hours=1), reason='roulette')
                    return await reply(ctx, "🔥🔫 You died! (muted for 1 hour)")
                add_coins(member.id,1)
                return await reply(ctx, f"🚬🔫 Looks like you\'re safe, for now... Here's 1 {zenny} as a pity prize...")
            return await reply(ctx, "❌🔫 Looks like you\'re safe, you filthy admin...")
        
        else: # if an admin wants to roulette a member they specify
            if not ctx.message.author.guild_permissions.administrator:
                if member == ctx.author:  # roulette themselves if not admin (pinged themself)
                    if random.randint(1,chance) == 1:
                        await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(hours=1), reason='roulette')
                        return await reply(ctx, "🔥🔫 You died! (muted for 1 hour)")
                    add_coins(member.id,1)
                    return await reply(ctx, f"🚬🔫 Looks like you\'re safe, for now... Here's 1 {zenny} as a pity prize...")
                return await reply(ctx, "❌🔫 A lowlife like you can\'t possibly fire the gun at someone else...")
            elif member == ctx.author: # admin tries rouletting themself
                return await reply(ctx, "❌🔫 Admins are valued. Don\'t roulette an admin like yourself...")
            elif member.is_timed_out() == True: # admin tries rouletting a "dead" server member
                return await reply(ctx, "❌🔫 Don\'t you think it\'d be overkill to shoot a dead body?")
            else:
                if not member.guild_permissions.administrator: # admin tries rouletting "alive" non admin
                    if random.randint(1,chance) == 1:
                        await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(hours=1), reason='roulette')
                        return await reply(ctx, "🔥🔫 This user died! (muted for 1 hour)")
                    add_coins(member.id,1)
                    return await reply(ctx, f"🚬🔫 Looks like they\'re safe, for now... I gave them 1 {zenny} as a pity prize...")
                return await reply(ctx, "❌🔫 Looks like they\'re safe, that filthy admin...")

    @commands.command(name='trivia')
    async def trivia(self, ctx, type:str = None):
        if await in_wom_shenanigans(ctx):
            types = ['general', 'film', 'music', 'tv', 'games', 'anime']
            categories = [9, 11, 12, 14, 15, 31]
            if assert_cooldown('trivia', ctx.author.id) != 0:
                return await wups(ctx, f"Slow down there, bub! Command on cooldown for another {assert_cooldown('trivia', ctx.author.id)} seconds")
            if not type is None and type.lower() not in types:
                return await wups(ctx, "Invalid trivia type")
            
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
                return await reply(ctx, f"Time's up! The correct answer was **{correct_answer}**.")
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
            
    @commands.command(name='emulation')
    async def emulation(self, ctx, console: str = "guide"):
        if await in_channels(ctx, ["gamig", "gamig-2-coming-soon", "wom-shenanigans"], False) or await in_threads(ctx, ['Rip-bozotendo'], False):
            if console == "guide":
                return await reply(ctx, "# __Emulation Wiki__\n\n## This is a wiki on how to get emulators for various systems set up on a PC!\n\n__**List of Valid Consoles**__ (enter as `!w emulation (console name)`)\n- NES\n- SNES\n- N64\n- GameCube\n- Wii\n- Wii U (enter as \"WiiU\")\n- GameBoy (enter as \"GB\")\n- GameBoy Color (enter as \"GBC\")\n- GameBoy Advance (enter as \"GBA\")\n- DS\n- 3DS\n- Switch\n- PS1\n- PS2\n- PS3\n- PSP\n- PS Vita (enter as \"PSVita\")\n- Master System (enter as \"MasterSystem\")\n- Genesis\n- Saturn\n- Dreamcast\n- Xbox")
            elif console.lower() not in self.consoles.keys():
                return await wups(ctx, "You entered a console that isn't on the list of valid consoles. Please refer to the list by entering `!w emulation`")

            for key, value in self.consoles.items():
                if console.lower() == key:
                    return await reply(ctx, f"# {", ".join(value['links'])}\n{value['instructions']}\n\n*Go hog wild.*")
        else:
            ids = []
            for channel in ["gamig", "gamig-2-coming-soon", "wom-shenanigans"]:
                ids.append(f"<#{discord.utils.get(ctx.guild.channels, name=channel).id}>")
            ids.append(f"<#{discord.utils.get(ctx.guild.threads, name="Rip-bozotendo").id}>")
            await shark_react(ctx.message)
            return await reply(ctx, f"this command can only be used in the following channels: {", ".join(ids)}. go to one of those channels, jackass")

    @commands.command(name='deathbattle', aliases=['db'])
    async def deathbattle(self, ctx, member: discord.Member):
        if await in_wom_shenanigans(ctx):
            if self.currentFight:
                return await wups(ctx, f"There is currently a fight going on")
            if member.bot:
                return await wups(ctx, f"You can't fight a bot")
              
            self.currentFight = True
            players = [ctx.author, member] if random.choice([True, False]) else [member, ctx.author]
            turn = 0
            am = discord.AllowedMentions.none()
            msg = await reply(ctx, f"{ctx.author.name} challenges {member.name} to the death!")
            await asyncio.sleep(3)
            while True:
                actor, target = (players[0], players[1]) if turn % 2 == 0 else (players[1], players[0])
                choiceNum = random.randint(0, len(self.actions) - 1)
                action = self.actions[choiceNum]
                await msg.edit(content=action.format(actor.name, target.name), allowed_mentions=am)
                await asyncio.sleep(2)
                determinant = random.randint(1, 5)
                if determinant == 1:
                    response = action + f" {self.deaths[choiceNum]}"
                else:
                    response = action + f" {self.survivals[choiceNum]}"
                await msg.edit(content=response.format(actor.name, target.name, target.name), allowed_mentions=am)
                if determinant == 1:
                    self.currentFight = False
                    break
                else:
                    turn += 1
                    await asyncio.sleep(3)
            return None
            

    @commands.command(name='ship')
    async def ship(self, ctx: commands.Context, str1: str, str2: str):
        if await in_wom_shenanigans(ctx):
            half_str1 = str1[:len(str1) // 2 + 1] if len(str1) % 2 == 1 else str1[:len(str1) // 2]
            half_str2 = str2[len(str2) // 2 + 1:] if len(str2) % 2 == 1 else str2[len(str2) // 2:]
            merged_string = half_str1 + half_str2

            embed = discord.Embed()
            bar = [':black_medium_square:' for _ in range(10)]
            shipPercent = random.randint(0, 100)
            shipBar = shipPercent // 10

            for i in range(shipBar):
                bar[i] = ':red_square:'

            finalStr = (
                f":heartpulse: **MATCHMAKING** :heartpulse:\n"
                f":small_red_triangle_down: `{str1}`\n"
                f":small_red_triangle: `{str2}`"
            )

            embed.color = discord.Color.pink()
            embed.title = f"**{merged_string}**"

            # Fixed f-string quotes and simplified string join
            embed.description = (
                f"**{shipPercent}%** "
                f"{''.join(bar)}"
                f"{' PERFECT! ❤' if shipPercent == 100 else ''}"
            )

            embed.set_footer(text=f"*{self.shipNotes[shipBar]}*")
            return await ctx.reply(finalStr, embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(Fun(bot))
