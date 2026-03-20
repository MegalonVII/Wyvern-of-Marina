import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone

from utils import user_info # utils direct values
from utils import in_wom_shenanigans, update_birthday, reply, wups, prompt_for_message # utils functions

# birthday commands start here
# birthday, bdl
class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='birthday')
    async def birthday(self, ctx):
        if await in_wom_shenanigans(ctx):
            prompt_data = await prompt_for_message(self.bot, ctx, 'In the next 30 seconds, give me your birthday in the format "MM-DD"!', 30, "Time's up! You didn't provide me with your birthday in time...")
            if prompt_data is None:
                return
            prompt, bday_message = prompt_data

            try:
                bday = datetime.strptime(bday_message.content, '%m-%d').date().strftime('%m-%d')
                await bday_message.delete()
            except Exception:
                await bday_message.delete()
                await prompt.delete()
                return await wups(ctx, 'Invalid birthday input')
            
            await prompt.delete()
            prompt_data = await prompt_for_message(self.bot, ctx, 'Now, you have 5 minutes to give me the timezone you are based in. Make sure it is one from [this list](<https://gist.githubusercontent.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568/raw/daacf0e4496ccc60a36e493f0252b7988bceb143/pytz-time-zones.py>)!', 300, "Time's up! You didn't provide me with your timezone in time...")
            if prompt_data is None:
                return
            prompt, tz_message = prompt_data
            try:
                tz = timezone(tz_message.content)
            except Exception:
                await tz_message.delete()
                await prompt.delete()
                return await wups(ctx, 'Invalid timezone. Refer to [this list](<https://gist.githubusercontent.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568/raw/daacf0e4496ccc60a36e493f0252b7988bceb143/pytz-time-zones.py>)')
            await tz_message.delete()
            await prompt.delete()
            
            update_birthday(ctx.author.id, bday, tz_message.content)
            return await reply(ctx, f'Birthday set for {bday} in {tz}!')
            
    @commands.command(name='birthdaylist', aliases=['bdaylist', 'bdl'])
    async def birthday_list(self, ctx):
        if await in_wom_shenanigans(ctx):
            temp_data = []
            for key in user_info.keys():
                member = discord.utils.get(ctx.message.guild.members, id=key)
                temp_data.append({'user': member, 'birthday': datetime.strptime(user_info[key]['birthdate'], '%m-%d').date().strftime('%B %d')})
            temp_data = sorted(temp_data, key=lambda x: datetime.strptime(x['birthday'], '%B %d').date())
            embed = discord.Embed(title='Marina Birthdays', color=discord.Color.blue())
            desc = ''
            for data in temp_data:
                desc += f'{data['user'].mention}: **{data['birthday']}**\n\n'
            embed.description = desc
            embed.set_thumbnail(url=self.bot.guilds[0].icon.url)
            return await ctx.reply(embed=embed, mention_author=False)
        

async def setup(bot):
    await bot.add_cog(Birthday(bot))
