import discord
import discord as ds
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import itertools
import random
import os

token = os.getenv("TOKEN")

intents = discord.Intents.all()
activities = itertools.cycle([
    discord.Game("Pytools.moderate"),
    discord.Activity(type=discord.ActivityType.watching, name="Pytools.ban"),
    discord.Activity(type=discord.ActivityType.listening, name="Pytools.kick")
])

bot = commands.Bot(command_prefix='!', intents=intents)

kick_time = timedelta(minutes=10)
ban_time = timedelta(days=1)

kicked_users = {}
verification_codes = {}  # To store 8-digit codes for users
verification_role_id = 1272179253315768351  # Role ID of the "User" role
bad_words = []
report_id = 1305553377022705675
# Load bad words from JSON file
def load_bad_words():
    global bad_words
    with open('bad_words.json', 'r') as file:
        data = json.load(file)
        bad_words = data.get('bad_words', [])

load_bad_words()

@tasks.loop(seconds=10)
async def change_status():
    current_activity = next(activities)
    await bot.change_presence(activity=current_activity)

# When a new member joins
@bot.event
async def on_member_join(member):
    if member.bot:
        return

    try:
        verification_code = str(random.randint(1000000000, 9999999999))  # Generate 10-digit random number
        verification_codes[member.id] = verification_code
        dm_channel = await member.create_dm()

        embed = discord.Embed(
            title="Welcome to the Server!",
            description=f"To gain access to the server, please reply with this 10-digit code: **{verification_code}**",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Thank you for joining!")
        await dm_channel.send(embed=embed)
    except discord.Forbidden:
        print(f"Couldn't send DM to {member.name}")

# When a user sends a message
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Handle private message for verification
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id in verification_codes and message.content == verification_codes[message.author.id]:
            guild = discord.utils.get(bot.guilds)  # Get the guild
            role = discord.utils.get(guild.roles, id=verification_role_id)  # Get the "User" role
            if role:
                member = guild.get_member(message.author.id)
                await member.add_roles(role)

                embed = discord.Embed(
                    title="Verification Complete!",
                    description="You have been verified and given access to the server.",
                    color=discord.Color.green()
                )
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Error",
                    description="Verification role not found.",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)

            del verification_codes[message.author.id]  # Remove the code after verification
        else:
            embed = discord.Embed(
                title="Incorrect Code",
                description="The code you entered is incorrect. Please try again.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)

    # Bad word checking
    if any(word in message.content.lower() for word in bad_words):
        if message.author.id in kicked_users:
            author = message.author
            emb = discord.Embed(
                title="You are Banned!",
                description=f"{message.author.mention},You have been banned for using a bad word. To appeal, go to <https://bit.ly/appeal_ban>",
                color=discord.Color.blue()
            )
            await author.send(embed=emb)
            await message.guild.ban(message.author, reason="Used a bad word again")
            embed = discord.Embed(
                title="User Banned",
                description=f"{message.author.mention} has been banned for using a bad word.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed, ephemeral=True)
        else:
            kicked_users[message.author.id] = datetime.now()
            await message.guild.kick(message.author, reason="Used a bad word")
            embed = discord.Embed(
                title="User Kicked",
                description=f"{message.author.mention} has been kicked for using a bad word. They will be banned if it happens again.",
                color=discord.Color.orange()
            )
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

@tasks.loop(minutes=1)
async def check_kicked_users():
    now = datetime.now()
    to_remove = []
    
    for user_id, kicked_at in kicked_users.items():
        if now - kicked_at >= kick_time:
            to_remove.append(user_id)
    
    for user_id in to_remove:
        del kicked_users[user_id]

class report_modal(ds.ui.Modal,title="Submit a report"):
    usr=ds.ui.TextInput(label="Type the Username",style=ds.TextStyle.short,placeholder="Eg:-win11_real",required=True)
    rsn=ds.ui.TextInput(label="Enter a reason",style=ds.TextStyle.long,placeholder="Reason here",required=True)
    async def on_submit(self,ctx:ds.Interaction):
        await ctx.response.send_message("Processed your report", ephemeral=True)
        a_usr, a_rsn, r_usr=self.usr, self.rsn, ctx.user
        white = 0xeeffee
        emb=ds.Embed(title=f"Report of {r_usr}",description=f"Username:{a_usr} \n---------- \nReason:{a_rsn}",colour = white)
        chl=bot.get_channel(report_id)
        await chl.send(embed=emb)

@bot.tree.context_menu(name="Report")
async def report(ctx:ds.Interaction,member:ds.Member):
    membr=member
    await ctx.response.send_modal(report_modal())

@bot.event
async def on_ready():
    change_status.start()
    sync=await bot.tree.sync()
    print(f'Logged in as {bot.user.name}')
    print(f"Synced {len(sync)}")
    check_kicked_users.start()

bot.run(token)
