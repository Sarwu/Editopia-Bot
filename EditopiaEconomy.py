import discord
import os
import json
import random
import time
from discord.ext import commands
from discord.ext.commands import (CommandOnCooldown)
from discord.ui import Button,View
from discord_slash.utils.manage_commands import create_option, create_choice
from discord.commands import Option
import asyncio

#setting up the bot
bot = discord.Bot()
os.chdir("C:\\Users\\Josh\\Desktop\\Editing Center Bot")
guild_ids=[704894281466380358]

@bot.event
async def on_ready():
    print(f"Editopia Economy is online!")

#setting up a blacklist
#BlackList = [1234567890]
#def check_List(ctx):
#    if ctx.author.id in BlackList:
#        return ctx.author.id in Blacklist
        
#coin icon/emoji
coins="[$]"

#economy commands
@bot.slash_command(name="balance",description="Check your balance, or someone else's!",guild_ids=guild_ids)
#@commands.check(check_List)
async def balance(ctx, member: discord.Member=None):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    if member == None:
        member = ctx.author
        await open_account(ctx.author)
        user = ctx.author
        users = await get_bank_data()
    else:
        await open_account(member)
        user = member
        users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]
    total_amt = wallet_amt + bank_amt
    em = discord.Embed(title = f"{member.name}'s balance",color = discord.Color.green())
    em.add_field(name = "Wallet balance", value = f"{wallet_amt} {coins}")
    em.add_field(name = "Bank balance", value = f"{bank_amt} {coins}")
    em.add_field(name="Total balance", value = f"{total_amt} {coins}")
    await ctx.respond(embed = em, ephemeral = True)
    return

@bot.slash_command(name="highlow", description="Play the High-Low game for currency!", guild_ids=guild_ids)
async def highlow(ctx):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    #initiating the numbers
    hiddenNumber = random.randint(1,100)
    shownNumber = random.randint(1,100)

    winnings = hiddenNumber + shownNumber

    #creating the embed
    embed = discord.Embed(title = "***Higher or Lower?***", description ="use the buttons to choose!", color = discord.Color.gold())
    embed.add_field(name = "Shown Number", value = f"{shownNumber}", inline=False)
    embed.add_field(name = "Hidden Number", value = "|hidden|", inline=False)
    
    #creating buttons and interactions
    button = Button(label="Higher", style=discord.ButtonStyle.green, emoji="🔼")
    buttontwo = Button(label="Lower", style=discord.ButtonStyle.red, emoji="🔽")
    
    
    
    await ctx.defer()
    async def button_callback(interaction):
        if hiddenNumber < shownNumber:
            new_embed = discord.Embed(title = "***Higher or Lower?***", description ="You *lose!*", color = discord.Color.gold())
            new_embed.add_field(name = "Shown Number", value = f"{shownNumber}", inline=False)
            new_embed.add_field(name = "Hidden Number", value = f"{hiddenNumber}", inline=False)
            await interaction.response.edit_message(embed=new_embed,view=None)
            return
        if hiddenNumber >= shownNumber:
            new_embed = discord.Embed(title = "***Higher or Lower?***", description =f"You *win! {winnings} {coins}*", color = discord.Color.gold())
            new_embed.add_field(name = "Shown Number", value = f"{shownNumber}", inline=False)
            new_embed.add_field(name = "Hidden Number", value = f"{hiddenNumber}", inline=False)
            await update_bank(ctx.author, winnings, "wallet")
            await interaction.response.edit_message(embed=new_embed,view=None)
            return

    async def buttontwo_callback(interaction):
        if hiddenNumber > shownNumber:
            new_embed = discord.Embed(title = "***Higher or Lower?***", description ="You *lose!*", color = discord.Color.gold())
            new_embed.add_field(name = "Shown Number", value = f"{shownNumber}", inline=False)
            new_embed.add_field(name = "Hidden Number", value = f"{hiddenNumber}", inline=False)
            await interaction.response.edit_message(embed=new_embed,view=None)
            return
        if hiddenNumber <= shownNumber:
            new_embed = discord.Embed(title = "***Higher or Lower?***", description =f"You *win {winnings} {coins}!*", color = discord.Color.gold())
            new_embed.add_field(name = "Shown Number", value = f"{shownNumber}", inline=False)
            new_embed.add_field(name = "Hidden Number", value = f"{hiddenNumber}", inline=False)
            await update_bank(ctx.author, winnings, "wallet")
            await interaction.response.edit_message(embed=new_embed,view=None)
            return

    button.callback = button_callback
    buttontwo.callback = buttontwo_callback
    view = View()
    view.add_item(button)
    view.add_item(buttontwo)
    await ctx.respond(embed=embed, view=view, ephemeral = True)

@bot.slash_command(name="fish",description="go fishing and sell your bounties!", guild_ids = guild_ids)
async def fish(ctx):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    #opening the account
    await open_account(ctx.author)
    bal = await update_bank(ctx.author)
    #fish lists by rarity
    commonFish = ["sunfish","shrimp","salmon","clownfish","bluefish","coral"]
    uncommonFish = ["globefish","goldfish","seaweed"]
    rareFish = ["angelfish","crab","lobster"]
    legendaryFish = ["swordfish","whale","shark"]
    #Fish lines for the description
    fishQuips=["that's a nice catch!",
            "ew it's kinda slimey",
            "*high fives* that's a pog-worthy catch",
            "smaller than I thought it would be...",
            "this obviously isn't your first rodeo",
            "ever considered going pro?",
            "yummy",
            "mmm tasty",
            f"not bad for someone with the name {ctx.author.mention}"]
    #attributes for the fish
    length = round(random.uniform(2,20),2)
    #getting the list
    fishType = random.randint(1,200)
    if fishType <= 100:
        fishName = random.choice(commonFish)
        value = random.randint(1,40)
    if fishType > 100 and fishType <= 175:
        fishName = random.choice(uncommonFish)
        value = random.randint(40,80)
    if fishType > 175 and fishType <= 195:
        fishName = random.choice(rareFish)
        value = random.randint(80,120)
    if fishType > 195 and fishType <=200:
        fishName = random.choice(legendaryFish)
        value = random.randint(120,160)
    price = round(((length * 0.2)* value),0)

    price = int(price)

    await update_bank(ctx.author,price, "wallet")
    embed = discord.Embed(title=f"You caught a {fishName}!", description=f"Value: {price} {coins}")
    embed.add_field(name=f"{length} inches long!", value=f"{random.choice(fishQuips)}")
    file = discord.File(f"F:/discord/fish/{fishName}.png", filename=f"{fishName}.png")
    embed.set_image(url=f"attachment://{fishName}.png")
    await ctx.respond(file=file, embed=embed)

@bot.slash_command(name="deposit", desciption="deposit to your bank!", guild_ids=guild_ids)
async def deposit(ctx,amount = str):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    await open_account(ctx.author)
    
    bal = await update_bank(ctx.author)

    users = await get_bank_data()
    user=ctx.author
    bank_amt = users[str(user.id)]["bank"]
    
    if amount == "all":
        amount = bal[0]
    new_balance = int(bank_amt) + int(amount)
    amount = int(amount)
    if amount>bal[0]:
        await ctx.respond("You don't have enough to do that.")
        return
    await update_bank(ctx.author,-1*amount,"wallet")
    await update_bank(ctx.author,amount,"bank")
    embed=discord.Embed(title=f"You deposited {amount} {coins}",description=f"Your new balance is {new_balance}")
    await ctx.respond(embed=embed)

@bot.slash_command(name="withdraw", desciption="withdraw from your bank!", guild_ids=guild_ids)
async def withdraw(ctx,amount: str):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    await open_account(ctx.author)

    bal = await update_bank(ctx.author)
    if amount == "all":
            amount = bal[1]
    amount = int(amount)
    if amount>bal[1]:
        await ctx.respond("You don't have enough to do that.")
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount,"bank")
    await ctx.respond(f"You withdrew {amount} {coins} from your bank account.")

@bot.slash_command(name="leaderboard",description="take a look at the top earners!", guild_ids=guild_ids)
async def leaderboard(ctx):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    x = 10
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)

    em = discord.Embed(title = f"Top {x} Richest People" , description = "use /buy to check the shop!",color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = await bot.fetch_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.respond(embed = em)

@bot.slash_command(name="rob",description="pick-pocket a pal's pennies or pounds!", guild_ids=guild_ids)
async def rob(ctx,member:discord.Member):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    await open_account(ctx.author)
    await open_account(member)

    bal = await update_bank(member)

    if bal[0]<250:
        await ctx.respond("They do not have enough to be robbed!")
        return

    earnings = random.randrange(0, bal[0])

    await update_bank(ctx.author,earnings)
    await update_bank(member,-1*earnings)
    await ctx.respond(f"You robbed {member} of {earnings} coins!")

@bot.slash_command(name="beg", description="beg for coins!", guild_ids=guild_ids)
async def beg(ctx):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randint(1,300)

    await ctx.respond(f"You begged for {earnings} {coins}")

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json","w") as f:
        json.dump(users,f)

@bot.slash_command()
async def bigslots(ctx,amount = None):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount")
        return 

    bal = await update_bank(ctx.author)
    if amount == "all":
            amount = bal[0]
    amount = int(amount)
    if amount>bal[0]:
        await ctx.respond("You don't have enough to do that.")
        return
    if amount<=2499:
        await ctx.respond("You must bet at least 2500 coins.")
        return
    amount = int(amount)
    final = []
    for i in range(5):
        a = random.choice([":apple:",":tangerine:",":strawberry:",":grapes:",":cherries:",":kiwifruit:"])

        final.append(a)

    #await ctx.send((final))
    embed = discord.Embed(title="Big Slot Machine")
    embed.add_field(name="OUTCOME:", value = f"{final}")
    await ctx.send(embed=embed)
    await update_bank(ctx.author,-1*amount)
    if (final[0] == final[1]) and (final[0] == final[2]) and (final[0] == final[3]) and (final[0] == final[4]):
        await update_bank(ctx.author,10*amount)
        earnings = (10*amount)
        await ctx.respond(f"YOU GOT ALL FIVE AND WON {earnings} COINS!")
        return
    elif ((final[0] == final[1] and final[0] == final[2]) or (final[0] == final[1] and final[0] == final[3]) or (final[0] == final[1] and final[0] == final[4]) or (final[0] == final[2] and final[0] == final[3]) or (final[0] == final[2] and final[0] == final[4]) or (final[0] == final[3] and final[0] == final[4]) or (final[1] == final[2] and final[1] == final[3]) or (final[1] == final[2] and final[1] == final[4]) or (final[1] == final[3] and final[1] == final[4]) or (final[2] == final[3] and final[2] == final[4])):
        await update_bank(ctx.author,3*amount)
        earnings = (3*amount)
        await ctx.respond(f"You won {earnings} coins!")
        return
    elif ((final[0] == final[1] and final[0] == final[2] and final[0] == final[3]) or (final[0] == final[1] and final[0] == final[2] and final[0] == final[4]) or (final[0] == final[1] and final[0] == final[3] and final[0] == final[4]) or (final[0] == final[2] and final[0] == final[3] and final[0] == final[4]) or (final[1] == final[2] and final[1] == final[3] and final[1] == final[4])):
        await update_bank(ctx.author,4*amount)
        earnings = (4*amount)
        await ctx.respond(f"You won {earnings} coins!")
        return
    else:
        await ctx.respond(f"You lost {amount} coins!")
        await update_banker(920703288087834625,1*amount)
        return

@bot.slash_command()
async def slots(ctx,amount = None):
    if ctx.channel.id != 919624913529212988:
        await ctx.respond("This is an economy command, please go to the #economy channel!")
        return
    await open_account(ctx.author)

    if amount == None:
        await ctx.respond("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    if amount == "all":
            amount = bal[0]
    amount = int(amount)
    if amount>bal[0]:
        await ctx.respond("You don't have enough to do that.")
        return
    if amount<=99:
        await ctx.respond("You must bet at least 100 coins.")
        return
        
    final = []
    for i in range(3):
        a = random.choice([":apple:",":tangerine:",":pineapple:",":strawberry:",":grapes:",":cherries:"])

        final.append(a)

    #await ctx.send((final))
    embed = discord.Embed(title="Slot Machine")
    embed.add_field(name="OUTCOME:", value = f"{final}")
    await ctx.send(embed=embed)
    await update_bank(ctx.author,-1*amount)
    if (final[0] == final[1]) and (final[0] == final[2]) and (final[1] == final[2]):
        await update_bank(ctx.author,3*amount)
        earnings = (3*amount)
        await ctx.respond(f"You won {earnings} coins!")
        return
    elif (final[0] == final[1]) or (final[0] == final[2]) or (final[1] == final[2]):
        await update_bank(ctx.author,2*amount)
        earnings = (2*amount)
        await ctx.respond(f"You won {earnings} coins!")
        return
    else:
        await ctx.respond(f"You lost {amount} coins!")
        await update_banker(920703288087834625,1*amount)
        return

#setting up the economy
async def get_bank_data():
    with open("EditopiaBank.json","r") as f:
        users = json.load(f)

    return users

async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("EditopiaBank.json","w") as f:
        json.dump(users,f)
    return True

async def update_banker(user = 920703288087834625,change = 0,mode = "bank"):
    users = await get_bank_data()

    users[str(user)][mode] += change

    with open("EditopiaBank.json","w") as f:
        json.dump(users,f)
    
    bal = [users[str(user)]["wallet"],users[str(user)]["bank"]]
    return bal

async def update_bank(user,change = 0,mode = "wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("EditopiaBank.json","w") as f:
        json.dump(users,f)
    
    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return bal

with open("EditopiaToken.txt","r", encoding="utf-8") as f:
    bottoken = f.read()
bot.run(bottoken)