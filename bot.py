from email import message
from sys import prefix
import discord
import idols
import wallet
import aiosqlite
import PIL
from PIL import Image
import os

from idols import Idol, get_borderimage, get_rank, idol_gacha

from discord.ui import Button, View
from discord.ext import commands, bridge
from discord import Bot, InteractionResponse, Option
from discord import Embed

intents = discord.Intents().all()
intents.members = True

bot = discord.Bot(debug_guilds=[979520985365639238], command_prefix='c!', intents=intents)

def rolledEmbedBuilder(ctx, rolled, level=1):
    match level:
        case (2):
            embed_title = 'Premium Gacha'
            cost = '250'
        case (3):
            embed_title = 'Event Gacha'
            cost = '500'
        case _:
            embed_title = 'Normal Gacha'
            cost = '150'

    rolledEmbed = Embed(title=f'{embed_title} - {ctx.author}', description=f'`-{cost}`:coin:')
    
    rolledEmbed.add_field(name='SUCCESS!', value=f'{ctx.author.mention} found **{rolled.get_themename()}**!\n\n⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅', inline=False)
    rolledEmbed.add_field(name='Info', value=f'Group: **{rolled.get_group()}**\nCard ID: `{rolled.get_uniqueid()}`\nRarity: {rolled.get_rarity()}\nRank: {rolled.get_rank()}', inline=False)

    if (rolled.get_shiny() == True):
        rolledEmbed.add_field(name='This card shines a bit brighter than others...', value='Congrats! This card is **SHINY**!', inline=False)

    rolledEmbed.set_image(url="attachment://foundcard.png")

    return rolledEmbed

@bot.event
async def on_ready():
    print('Logged in as {0.user} using Pycord!'.format(bot))
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            #await cursor.execute('DROP TABLE users')
            await cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, wallet INTEGER)')
            await cursor.execute('CREATE TABLE IF NOT EXISTS cards_numbers (id STRING , uniqueval INTEGER)')
        await db.commit()

@bot.event
async def on_member_join(member):
    print("joined")
    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT id FROM users WHERE id = ?", [member.id])
    result = await cursor.fetchone()
    print(member.id)
    if result is None:
        await cursor.execute("INSERT INTO users(id, wallet) VALUES (?, ?)", (member.id, 1000))

    await db.commit()
    await cursor.close()
    await db.close()

testing = bot.create_group('owner', 'owner commands')

@testing.command(guild_ids=[979520985365639238], name='addtodatabase', description='adds user to database')
@commands.has_role("Mod")
async def addtodatabase(ctx,
    user: Option(discord.Member, 'The user to add',
            required = True)):

    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT id from users WHERE id = ?", [user.id])
    result = await cursor.fetchone()

    if result is None:
        await cursor.execute("INSERT INTO users(id, wallet) VALUES (?, ?)", (user.id, 1000))

        await db.commit()
        await cursor.close()
        await db.close()

        await ctx.respond(f'Added {user} ({user.id}) to database!')
    else:
        await db.commit()
        await cursor.close()
        await db.close()

        await ctx.respond(f'{user} is already in the database!')

gacha = bot.create_group('gacha', 'Roll for your idols!')

@gacha.command(guild_ids=[979520985365639238], name='menu', description='Gacha menu')
async def menu(ctx):
    gacha_info_embed = Embed(title=f'Gacha Menu - {ctx.author}', description='Choose what gacha level')
    gacha_info_embed.add_field(name='Prices', value='Normal: 150\nPremium: 250\nEvent: 500', inline=False)
    gacha_info_embed.add_field(name='Drop Rates', value='**Normal**\n:star: - 95%\n:star::star: - 5.4%\n:star::star::star: - 0.1%\n\n**Premium**\n:star: - 80%\n:star::star: - 12.5%\n:star::star::star: - 7.5%\n**Event**\n:star: - 50%\n:star::star: - 30%\n:star::star::star: - 20%', inline=False)

    class gachaView(View):
        @discord.ui.button(style=discord.ButtonStyle.gray, label='150 | Normal', emoji=bot.get_emoji(992242623127490630), custom_id="normal")
        async def normal_button_calback(self, button, interaction):

            hasEnough = await wallet.gacha_pricecheck(ctx.author.id, 1)

            if (hasEnough == False):
                normal_button = [x for x in self.children if x.custom_id == "normal"][0]
                normal_button.disabled = True

            rolled = await idol_gacha(1)
            pic = Image.open(rolled.get_image())

            idolRank = get_rank()
            rolled.set_rank(idolRank)
            file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

            rolledEmbed = rolledEmbedBuilder(ctx, rolled, 3)

            rolledEmbed.set_image(url="attachment://foundcard.png")

            return await interaction.response.edit_message(embed=rolledEmbed, file=file)

        @discord.ui.button(style=discord.ButtonStyle.green, label='250 | Premium', emoji=bot.get_emoji(992242623127490630))
        async def premium_button_calback(self, button, interaction):

            rolled = await idol_gacha(2)
            pic = Image.open(rolled.get_image())

            idolRank = get_rank()
            rolled.set_rank(idolRank)
            file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

            rolledEmbed = rolledEmbedBuilder(ctx, rolled, 3)

            rolledEmbed.set_image(url="attachment://foundcard.png")

            return await interaction.response.edit_message(embed=rolledEmbed, file=file)

        @discord.ui.button(style=discord.ButtonStyle.blurple, label='500 | Event', emoji=bot.get_emoji(992242623127490630))
        async def event_button_calback(self, button, interaction):

            rolled = await idol_gacha(3)
            pic = Image.open(rolled.get_image())

            idolRank = get_rank()
            rolled.set_rank(idolRank)
            file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

            rolledEmbed = rolledEmbedBuilder(ctx, rolled, 3)

            rolledEmbed.set_image(url="attachment://foundcard.png")

            return await interaction.response.edit_message(embed=rolledEmbed, file=file)

    view = gachaView()

    return await ctx.respond(embed=gacha_info_embed, view=view) 

@gacha.command(guild_ids=[979520985365639238], name='normal', description='Normal gacha, costs 150')
async def normal(ctx):

    rolled = await idol_gacha(1)
    pic = Image.open(rolled.get_image())

    idolRank = get_rank()
    rolled.set_rank(idolRank)
    file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

    rolledEmbed = rolledEmbedBuilder(ctx, rolled)

    return await ctx.respond(embed=rolledEmbed, file=file)

@gacha.command(guild_ids=[979520985365639238], name='premium', description='Premium gacha, costs 250')
async def premium(ctx):

    rolled = await idol_gacha(2)
    pic = Image.open(rolled.get_image())

    idolRank = get_rank()
    rolled.set_rank(idolRank)
    file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

    rolledEmbed = rolledEmbedBuilder(ctx, rolled, 2)

    return await ctx.respond(embed=rolledEmbed, file=file)

@gacha.command(guild_ids=[979520985365639238], name='event', description='Event gacha, costs 500')
async def event(ctx):

    rolled = await idol_gacha(3)
    pic = Image.open(rolled.get_image())

    idolRank = get_rank()
    rolled.set_rank(idolRank)
    file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

    rolledEmbed = rolledEmbedBuilder(ctx, rolled, 3)

    return await ctx.respond(embed=rolledEmbed, file=file)

bot.run("OTc5MjY2NTk3NTc3NDM3MTg0.GLK7Uv.NzCax7nVubjfEiFwzO8oUh5BRLRP-6kv1crA-Y")