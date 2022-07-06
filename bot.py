from email import message
from enum import unique
from sys import prefix
import discord
import idols
import wallet
import inventory
import aiosqlite
import PIL
from PIL import Image
import os

from idols import Idol, get_borderimage, get_rank, idol_gacha, parseToString

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

    rolledEmbed = Embed(title=f'{embed_title} - {ctx.author}', description=f'`-{cost}🪙`')
    
    rolledEmbed.add_field(name='SUCCESS!', value=f'{ctx.author.mention} found **{rolled.get_themename()}**!\n\n⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅', inline=False)
    rolledEmbed.add_field(name='Card Info', value=f'Group: **{rolled.get_group()}**\nCard ID: `{rolled.get_uniqueid()}`\nRarity: {rolled.get_rarity_as_emoji()}\nRank: {rolled.get_rank_as_emoji()}', inline=False)
    rolledEmbed.add_field(name='Card Stats', value=f'HP: `{rolled.gethp()}`\nATK: `{rolled.getatk()}`\nDEF: `{rolled.getdefnd()}`')
    rolledEmbed.add_field(name='_ _', value=f'Crit Rate: `{rolled.getcritr()}`\nCrit DMG: `{rolled.getcritdmg()}`')

    if (rolled.get_shiny() == True):
        rolledEmbed.add_field(name='This card shines a bit brighter than others...', value='Congrats! This card is **SHINY**!', inline=False)

    rolledEmbed.set_image(url="attachment://foundcard.png")

    return rolledEmbed

@bot.event
async def on_ready():
    print('Logged in as {0.user} using Pycord!'.format(bot))
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            #await cursor.execute('ALTER TABLE users ADD COLUMN inventory STRING')
            await cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, username STRING, wallet INTEGER, inventory STRING)')
            await cursor.execute('CREATE TABLE IF NOT EXISTS cards_numbers (id STRING , uniqueval INTEGER)')
            await cursor.execute('CREATE TABLE IF NOT EXISTS cards_details (uniqueid STRING , name STRING, groupname STRING, id STRING, rarity INTEGER, theme STRING, rank STRING, shiny INTEGER, hp INTEGER, atk INTEGER, defnd INTEGER, critr INTEGER, critdmg INTEGER, owner INTEGER, borderless INTEGER)')
        await db.commit()

@bot.event
async def on_member_join(member):
    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT id FROM users WHERE id = ?", [member.id])
    result = await cursor.fetchone()
    if result is None:
        await cursor.execute("INSERT INTO users(id, username, wallet, inventory) VALUES (?, ?, ?, ?)", (member.id, member.name, 5000, None))

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
        await cursor.execute("INSERT INTO users(id, username, wallet, inventory) VALUES (?, ?, ?, ?)", (user.id, user.name, 1000, None))

        await db.commit()
        await cursor.close()
        await db.close()

        await ctx.respond(f'Added {user} ({user.id}) to database!')
    else:
        await db.commit()
        await cursor.close()
        await db.close()

        await ctx.respond(f'{user} is already in the database!')

@testing.command(guild_ids=[979520985365639238], name='modifywallet', description='modifies user wallet')
@commands.has_role("Mod")
async def modifywallet(ctx,
    user: Option(discord.Member, 'The user to add',
            required = True),
    amount: Option(int, 'Amount to change wallet to',
            required = True)):

    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT id from users WHERE id = ?", [user.id])
    result = await cursor.fetchone()

    if result is None:
        await db.commit()
        await cursor.close()
        await db.close()

        await ctx.respond(f'Not in database')
    else:
        await cursor.execute("UPDATE users SET wallet = ? WHERE id = ?", (amount, user.id))

        await db.commit()
        await cursor.close()
        await db.close()

        await ctx.respond(f'{user} now has {amount} coins')

@testing.command(guild_ids=[979520985365639238], name='clearinv', description='clears inventory for testing')
@commands.has_role("Mod")
async def clearinv(ctx,
    user: Option(discord.Member, 'The user whose inventory to clear',
            required = False)):

    if (user == None):
        user = ctx.author

    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT id from users WHERE id = ?", [user.id])
    result = await cursor.fetchone()

    await cursor.execute("UPDATE users SET inventory = ? WHERE id = ?", ('', user.id))

    await db.commit()
    await cursor.close()
    await db.close()

    await ctx.respond(f'Cleared {user}\'s inventory')
    
gacha = bot.create_group('gacha', 'Roll for your idols!')

@gacha.command(guild_ids=[979520985365639238], name='menu', description='Gacha menu')
async def menu(ctx):
    gacha_info_embed = Embed(title=f'Gacha Menu - {ctx.author}', description='Choose what gacha level')
    gacha_info_embed.add_field(name='Prices', value='Normal: 150\nPremium: 250\nEvent: 500', inline=False)
    gacha_info_embed.add_field(name='Drop Rates', value='**Normal**\n:star: - 95%\n:star::star: - 5.4%\n:star::star::star: - 0.1%\n\n**Premium**\n:star: - 80%\n:star::star: - 12.5%\n:star::star::star: - 7.5%\n**Event**\n:star: - 50%\n:star::star: - 30%\n:star::star::star: - 20%', inline=False)

    class gachaView(View):
        @discord.ui.button(style=discord.ButtonStyle.gray, label='150 | Normal', emoji=bot.get_emoji(992242623127490630), custom_id="normal")
        async def normal_button_calback(self, button, interaction):

            await wallet.gacha_spend(ctx.author.id, 1)

            rolled = await idol_gacha(1)
            pic = Image.open(rolled.get_image())

            idolRank = get_rank()
            rolled.set_rank(idolRank)
            file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

            rolledEmbed = rolledEmbedBuilder(ctx, rolled, 1)

            rolledEmbed.set_image(url="attachment://foundcard.png")

            normal_button = [x for x in self.children if x.custom_id == "normal"][0]
            premium_button = [x for x in self.children if x.custom_id == "premium"][0]
            event_button = [x for x in self.children if x.custom_id == "event"][0]

            if (await wallet.gacha_pricecheck(ctx.author.id, 1) == False):
                normal_button.disabled = True
                premium_button.disabled = True
                event_button.disabled = True
            elif (await wallet.gacha_pricecheck(ctx.author.id, 2) == False):
                premium_button.disabled = True
                event_button.disabled = True
            elif (await wallet.gacha_pricecheck(ctx.author.id, 3) == False):
                event_button.disabled = True

            rolledEmbed.set_footer(text=f'You now have {await wallet.get_wallet(ctx.author.id)} coins.')

            rolled.set_owner(ctx.author.id)

            idolcomp = parseToString(rolled)
            await inventory.addtoinv(ctx.author.id, idolcomp)

            await idols.add_idol_to_database(rolled)

            self.embed = rolledEmbed

            return await interaction.response.edit_message(embed=rolledEmbed, file=file, view=self)

        @discord.ui.button(style=discord.ButtonStyle.green, label='250 | Premium', emoji=bot.get_emoji(992242623127490630), custom_id="premium")
        async def premium_button_calback(self, button, interaction):

            await wallet.gacha_spend(ctx.author.id, 2)

            rolled = await idol_gacha(2)
            pic = Image.open(rolled.get_image())

            idolRank = get_rank()
            rolled.set_rank(idolRank)
            file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

            rolledEmbed = rolledEmbedBuilder(ctx, rolled, 2)

            rolledEmbed.set_image(url="attachment://foundcard.png")

            normal_button = [x for x in self.children if x.custom_id == "normal"][0]
            premium_button = [x for x in self.children if x.custom_id == "premium"][0]
            event_button = [x for x in self.children if x.custom_id == "event"][0]

            if (await wallet.gacha_pricecheck(ctx.author.id, 1) == False):
                normal_button.disabled = True
                premium_button.disabled = True
                event_button.disabled = True
            elif (await wallet.gacha_pricecheck(ctx.author.id, 2) == False):
                premium_button.disabled = True
                event_button.disabled = True
            elif (await wallet.gacha_pricecheck(ctx.author.id, 3) == False):
                event_button.disabled = True

            rolledEmbed.set_footer(text=f'You now have {await wallet.get_wallet(ctx.author.id)} coins.')

            rolled.set_owner(ctx.author.id)

            idolcomp = parseToString(rolled)
            await inventory.addtoinv(ctx.author.id, idolcomp)

            await idols.add_idol_to_database(rolled)

            self.embed = rolledEmbed

            return await interaction.response.edit_message(embed=rolledEmbed, file=file, view=self)

        @discord.ui.button(style=discord.ButtonStyle.blurple, label='500 | Event', emoji=bot.get_emoji(992242623127490630), custom_id="event")
        async def event_button_calback(self, button, interaction):

            await wallet.gacha_spend(ctx.author.id, 3)

            rolled = await idol_gacha(3)
            pic = Image.open(rolled.get_image())

            idolRank = get_rank()
            rolled.set_rank(idolRank)
            file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

            rolledEmbed = rolledEmbedBuilder(ctx, rolled, 3)

            rolledEmbed.set_image(url="attachment://foundcard.png")

            normal_button = [x for x in self.children if x.custom_id == "normal"][0]
            premium_button = [x for x in self.children if x.custom_id == "premium"][0]
            event_button = [x for x in self.children if x.custom_id == "event"][0]

            if (await wallet.gacha_pricecheck(ctx.author.id, 1) == False):
                normal_button.disabled = True
                premium_button.disabled = True
                event_button.disabled = True
            elif (await wallet.gacha_pricecheck(ctx.author.id, 2) == False):
                premium_button.disabled = True
                event_button.disabled = True
            elif (await wallet.gacha_pricecheck(ctx.author.id, 3) == False):
                event_button.disabled = True

            rolledEmbed.set_footer(text=f'You now have {await wallet.get_wallet(ctx.author.id)} coins.')

            rolled.set_owner(ctx.author.id)

            idolcomp = parseToString(rolled)
            await inventory.addtoinv(ctx.author.id, idolcomp)

            await idols.add_idol_to_database(rolled)

            self.embed = rolledEmbed

            return await interaction.response.edit_message(embed=rolledEmbed, file=file, view=self)

        async def on_timeout(self):
            normal_button = [x for x in self.children if x.custom_id == "normal"][0]
            premium_button = [x for x in self.children if x.custom_id == "premium"][0]
            event_button = [x for x in self.children if x.custom_id == "event"][0]

            normal_button.disabled = True
            premium_button.disabled = True
            event_button.disabled = True

            return await ctx.edit(embed=self.embed, view=self)

        def set_embed(self, embed):
            self.embed = embed

    view = gachaView(timeout=30)
    view.set_embed(gacha_info_embed)

    normal_button = [x for x in view.children if x.custom_id == "normal"][0]
    premium_button = [x for x in view.children if x.custom_id == "premium"][0]
    event_button = [x for x in view.children if x.custom_id == "event"][0]

    if (await wallet.gacha_pricecheck(ctx.author.id, 1) == False):
        normal_button.disabled = True
        premium_button.disabled = True
        event_button.disabled = True
    elif (await wallet.gacha_pricecheck(ctx.author.id, 2) == False):
        premium_button.disabled = True
        event_button.disabled = True
    elif (await wallet.gacha_pricecheck(ctx.author.id, 3) == False):
        event_button.disabled = True

    return await ctx.respond(embed=gacha_info_embed, view=view) 

@gacha.command(guild_ids=[979520985365639238], name='normal', description='Normal gacha, costs 150')
async def normal(ctx):

    canRoll = await wallet.gacha_pricecheck(ctx.author.id, 1)

    if (canRoll==True):
        await wallet.gacha_spend(ctx.author.id, 1)

        rolled = await idol_gacha(1)
        pic = Image.open(rolled.get_image())

        idolRank = get_rank()
        rolled.set_rank(idolRank)
        file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

        rolledEmbed = rolledEmbedBuilder(ctx, rolled)

        rolledEmbed.set_footer(text=f'You now have {await wallet.get_wallet(ctx.author.id)} coins.')

        rolled.set_owner(ctx.author.id)

        idolcomp = parseToString(rolled)
        await inventory.addtoinv(ctx.author.id, idolcomp)

        await idols.add_idol_to_database(rolled)

        return await ctx.respond(embed=rolledEmbed, file=file)
    else:
        return await ctx.respond("You don't have enough coins for this!")

@gacha.command(guild_ids=[979520985365639238], name='premium', description='Premium gacha, costs 250')
async def premium(ctx):

    canRoll = await wallet.gacha_pricecheck(ctx.author.id, 2)

    if (canRoll==True):
        await wallet.gacha_spend(ctx.author.id, 2)

        rolled = await idol_gacha(2)
        pic = Image.open(rolled.get_image())

        idolRank = get_rank()
        rolled.set_rank(idolRank)
        file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

        rolledEmbed = rolledEmbedBuilder(ctx, rolled, 2)

        rolledEmbed.set_footer(text=f'You now have {await wallet.get_wallet(ctx.author.id)} coins.')

        rolled.set_owner(ctx.author.id)

        idolcomp = parseToString(rolled)
        await inventory.addtoinv(ctx.author.id, idolcomp)

        await idols.add_idol_to_database(rolled)

        return await ctx.respond(embed=rolledEmbed, file=file)
    else:
        return await ctx.respond("You don't have enough coins for this!")

@gacha.command(guild_ids=[979520985365639238], name='event', description='Event gacha, costs 500')
async def event(ctx):

    canRoll = await wallet.gacha_pricecheck(ctx.author.id, 3)

    if (canRoll==True):
        await wallet.gacha_spend(ctx.author.id, 3)

        rolled = await idol_gacha(3)
        pic = Image.open(rolled.get_image())

        idolRank = get_rank()
        rolled.set_rank(idolRank)
        file = get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

        rolledEmbed = rolledEmbedBuilder(ctx, rolled, 3)

        rolledEmbed.set_footer(text=f'You now have {await wallet.get_wallet(ctx.author.id)} coins.')

        rolled.set_owner(ctx.author.id)

        idolcomp = parseToString(rolled)
        await inventory.addtoinv(ctx.author.id, idolcomp)

        await idols.add_idol_to_database(rolled)

        return await ctx.respond(embed=rolledEmbed, file=file)
    else:
        return await ctx.respond("You don't have enough coins for this!")

view = bot.create_group('view', 'view cards, inventories, wallets, etc')

@view.command(guild_ids=[979520985365639238], name='inv', description='see your or someones inventory')
async def view_inv(ctx,
        user: Option(discord.Member, 'Whose inventory to view, yours by default',
            required = False),
        pagenumber: Option(int, 'Inventory page to view, first page by default',
            required = False),
        group: Option(str, 'filter inventory by specific group', required=False, choices=idols.card_groups, default=None),
        rarity: Option(str, 'filter inventory by specific rarity', required=False, choices=idols.rarities, default=None),
        rank: Option(str, 'filter inventory by specific rank', required=False, choices=idols.ranks, default=None),
        toggle_only_shiny: Option(str, 'filter by only shiny cards', required=False, choices=idols.toggle_shiny, default='')
            ):

    if (user == None):
        user = ctx.author
    if (pagenumber == None):
        pagenumber = 1

    groupf = str(group or 'ALL')
    rarityf = str(rarity or 'ALL')
    rankf = str(rank or 'ALL')
    shinyf = bool(toggle_only_shiny)

    filters = f'***Filters:***\nGroup = **{groupf}** | Rarity = **{rarityf}**\nRank = **{rankf}** | Toggle Shiny Only = **{str(shinyf)}**'

    pagenumber -= 1

    inv = await inventory.getinvfromdb(user.id)

    inv = await inventory.filter_inv(inv, group, rarity, rank, toggle_only_shiny)

    amount_of_pages = len(await inventory.get_pages(inv))
    listed_inv = await inventory.print_inv(ctx, inv, pagenumber, filters)

    class invView(View):
        @discord.ui.button(style=discord.ButtonStyle.red, label='Back', emoji='⬅️', custom_id="back")
        async def back_button_calback(self, button, interaction):
            self.pagenumber -= 1
            pagenumber = self.pagenumber
            back_button = [x for x in self.children if x.custom_id == "back"][0]
            next_button = [x for x in self.children if x.custom_id == "next"][0]

            inv = await inventory.getinvfromdb(user.id)
            inv = await inventory.filter_inv(inv, group, rarity, rank, toggle_only_shiny)
            amount_of_pages = len(await inventory.get_pages(inv))

            if pagenumber not in range(1, amount_of_pages):
                back_button.disabled = True
            else:
                back_button.disabled = False

            if pagenumber not in range(0, amount_of_pages - 1):
                next_button.disabled = True
            else:
                next_button.disabled = False
            
            listed_inv = await inventory.print_inv(ctx, inv, pagenumber, filters)
            self.embed = listed_inv

            return await interaction.response.edit_message(embed=self.embed, view=self)

        @discord.ui.button(style=discord.ButtonStyle.green, label='Next', emoji='➡️', custom_id="next")
        async def next_button_calback(self, button, interaction):
            self.pagenumber += 1
            pagenumber = self.pagenumber
            back_button = [x for x in self.children if x.custom_id == "back"][0]
            next_button = [x for x in self.children if x.custom_id == "next"][0]

            inv = await inventory.getinvfromdb(user.id)
            inv = await inventory.filter_inv(inv, group, rarity, rank, toggle_only_shiny)
            amount_of_pages = len(await inventory.get_pages(inv))

            if pagenumber not in range(1, amount_of_pages):
                back_button.disabled = True
            else:
                back_button.disabled = False

            if pagenumber not in range(0, amount_of_pages - 1):
                next_button.disabled = True
            else:
                next_button.disabled = False

            listed_inv = await inventory.print_inv(ctx, inv, pagenumber, filters)
            self.embed = listed_inv

            return await interaction.response.edit_message(embed=self.embed, view=self)
        
        async def on_timeout(self):
            back_button = [x for x in self.children if x.custom_id == "back"][0]
            next_button = [x for x in self.children if x.custom_id == "next"][0]

            back_button.disabled = True
            next_button.disabled = True

            return await ctx.edit(embed=self.embed, view=self)
        
        def set_pagenum(self, pagenumber):
            self.pagenumber = pagenumber
        def get_pagenum(self):
            return self.pagenumber
        def set_embed(self, embed):
            self.embed = embed
    
    view = invView(timeout=30)
    view.set_pagenum(pagenumber)
    view.set_embed(listed_inv)

    back_button = [x for x in view.children if x.custom_id == "back"][0]
    next_button = [x for x in view.children if x.custom_id == "next"][0]

    if pagenumber not in range(1, amount_of_pages):
        back_button.disabled = True
    else:
        back_button.disabled = False

    if pagenumber not in range(0, amount_of_pages - 1):
        next_button.disabled = True
    else:
        next_button.disabled = False

    await ctx.respond(embed=listed_inv, view=view)

@view.command(guild_ids=[979520985365639238], name='wallet', description='see how many coins you have or someone has')
async def view_wallet(ctx,
        user: Option(discord.Member, 'Whose wallet to view, yours by default',
            required = False)):

    if (user == None):
        user = ctx.author
    
    amount = await wallet.get_wallet(user.id)

    await ctx.respond(f'{user} has **{amount}**:coin:')

@view.command(guild_ids=[979520985365639238], name='card', description='view a card using the unique id')
async def view_card(ctx,
        uniqueid: Option(str, 'the card\'s unique id',
            required = True)):
    
    rolled = await idols.get_idol_from_database(uniqueid)

    rolledEmbed = Embed(title=f'View - {ctx.author}', description=f'Viewing card: `{uniqueid}`')
    
    rolledEmbed.add_field(name='Card Info', value=f'Group: **{rolled.get_group()}**\nCard ID: `{rolled.get_uniqueid()}`\nRarity: {rolled.get_rarity_as_emoji()}\nRank: {rolled.get_rank_as_emoji()}\nOwner: <@{rolled.get_owner()}>', inline=False)
    rolledEmbed.add_field(name='Card Stats', value=f'HP: `{rolled.gethp()}`\nATK: `{rolled.getatk()}`\nDEF: `{rolled.getdefnd()}`')
    rolledEmbed.add_field(name='_ _', value=f'Crit Rate: `{rolled.getcritr()}`\nCrit DMG: `{rolled.getcritdmg()}`')

    file = get_borderimage(rolled.get_rank(), Image.open(rolled.get_image()), rolled.get_shiny(), rolled.get_rarity())

    if (rolled.get_shiny() == True):
        rolledEmbed.add_field(name='This card shines a bit brighter than others...', value='This card is **SHINY**!', inline=False)

    rolledEmbed.set_image(url="attachment://foundcard.png")

    await ctx.respond(embed=rolledEmbed, file=file)

@view.command(guild_ids=[979520985365639238], name='cooldowns', description='view your cooldowns')
async def view_cooldowns(ctx):
    def isOnCooldown(cmd:commands.Command):

        if (cmd.is_on_cooldown(ctx)):
            m, s = divmod(cmd.get_cooldown_retry_after(ctx), 60)
            h, m = divmod(m, 60)

            if (h > 0):
                time = f'{h:.0f} hour(s)'
            elif (m > 0):
                time = f'{m:.0f} minute(s) and {s:.2f} second(s)'
            else:
                time = f'{s:.2f} second(s)'

            msg = f'`⏰` | **{time}** remaining'
        else:
            msg = '`✅` | Ready'

        return msg

    daily = bot.get_command('daily')
    busk = bot.get_command('busk')
    stocks = bot.get_command('stocks')

    embed = discord.Embed(title=f'Cooldowns - {ctx.author}', description=f'\n**Daily**: {isOnCooldown(daily)}\n**Busk**: {isOnCooldown(busk)}\n**Stocks**: {isOnCooldown(stocks)}')

    await ctx.respond(embed=embed)

card = bot.create_group('card', 'card commands')

@card.command(guild_ids=[979520985365639238], name='sell', description='sell a card')
async def sell_card(ctx,
        uniqueid: Option(str, 'the unique id of the card to sell', required=True)):
    
    to_remove = await inventory.has_idol(ctx.author.id, uniqueid)

    if to_remove is None:
        ctx.respond(f'You dont own `{uniqueid}`!')
    else:
        price = to_remove.get_sellprice()

        await inventory.removefrominv(ctx.author.id, to_remove)

        await wallet.add_to_wallet(ctx, price)

        await ctx.respond(f'Successfully sold `{uniqueid}` for `{price}🪙`.')

@bot.command(guild_ids=[979520985365639238], name='stocks', description='invest wisely... or not')
@commands.cooldown(1, 5, commands.cooldowns.BucketType.user)
async def stocks(ctx,
        amount: Option(int, 'the amount to invest', required=True)):
    
    if (amount <= 0):
        await ctx.respond('You can\'t invest nothing!')
    elif (amount > await wallet.get_wallet(ctx.author.id)):
        await ctx.respond('You can\'t invest more than what you have!')
    else:
        embed = await wallet.get_stocks(ctx, amount)

        await ctx.respond(embed=embed)

@bot.command(guild_ids=[979520985365639238], name='busk', description='gain some quick coins')
@commands.cooldown(1, 600, commands.cooldowns.BucketType.user)
async def busk(ctx):
    embed = await wallet.get_busk(ctx)

    await ctx.respond(embed=embed)

@bot.command(guild_ids=[979520985365639238], name='daily', description='daily claim')
@commands.cooldown(1, 86400, commands.cooldowns.BucketType.user)
async def daily(ctx):
    embedandfile = await wallet.daily_claims(ctx)

    embed = embedandfile[0]
    file = embedandfile[1]

    await ctx.respond(embed=embed, file=file)

@busk.error
async def error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)

        if (m > 0):
            time = f'{m:.0f} minute(s) and {s:.2f} second(s)'
        else:
            time = f'{s:.2f} second(s)'

        msg = f'You\'re too tired to head out again! Try again in **{time}**.'

        await ctx.respond(msg)

@stocks.error
async def error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = f'Woah there! The stock market is a treacherous place. Try again in **{error.retry_after:.2f} second(s)**.'

        await ctx.respond(msg)

@daily.error
async def error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)

        if (h > 0):
            time = f'{h:.0f} hour(s)'
        else:
            time = f'{m:.0f} minute(s) and {s:.2f} second(s)'

        msg = f'Not yet! **{time}** remaining.'

        await ctx.respond(msg)

@addtodatabase.error
async def error(ctx, error):
    if isinstance(error, commands.errors.MissingRole):
        await ctx.respond('You do not have permission to use this command!')

@clearinv.error
async def error(ctx, error):
    if isinstance(error, commands.errors.MissingRole):
        await ctx.respond('You do not have permission to use this command!')

@modifywallet.error
async def error(ctx, error):
    if isinstance(error, commands.errors.MissingRole):
        await ctx.respond('You do not have permission to use this command!')


bot.run(os.environ["DISCORD_TOKEN"])