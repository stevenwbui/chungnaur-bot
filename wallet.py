from unicodedata import decimal
import aiosqlite
import random
import discord
import idols
import inventory
from PIL import Image

async def gacha_pricecheck(user_id, level=1):

    match level:
        case (1): 
            price = 150
        case (2):
            price = 250
        case (3):
            price = 500

    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT wallet FROM users WHERE id = ?", [user_id])

    result = await cursor.fetchone()
    wallet = result[0]

    if (wallet >= price):
        # wallet -= price
        # await cursor.execute("UPDATE users SET wallet = ? WHERE id = ?", (wallet, user_id))

        answer = True

    else:
        answer = False

    await db.commit()
    await cursor.close()
    await db.close()
    return answer

async def gacha_spend(user_id, level=1):

    match level:
        case (1): 
            price = 150
        case (2):
            price = 250
        case (3):
            price = 500

    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT wallet FROM users WHERE id = ?", [user_id])

    result = await cursor.fetchone()
    wallet = result[0]

    if (wallet >= price):
        wallet -= price
        await cursor.execute("UPDATE users SET wallet = ? WHERE id = ?", (wallet, user_id))

    await db.commit()
    await cursor.close()
    await db.close()

async def get_wallet(user_id):

    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT wallet FROM users WHERE id = ?", [user_id])

    result = await cursor.fetchone()
    wallet = result[0]

    await db.commit()
    await cursor.close()
    await db.close()

    return wallet

async def get_busk(ctx):

    busk_msg = [
                'Someone stole your tips...', 'Tough crowd today...', 'Pretty decent outcome today!', 'Now you can buy dinner!',
                'Was this worth the hour of work?'
                ]

    result = random.randrange(10, 501, 1)

    busk_embed = discord.Embed(title=f'Busk - {ctx.author}', description=random.choice(busk_msg))
    busk_embed.add_field(name='Result:', value=f'Your hard work totaled to `{result}🪙`!')

    await add_to_wallet(ctx, result)

    new_wallet = await get_wallet(ctx.author.id)

    busk_embed.set_footer(text=f'You now have {new_wallet} coins.')

    return busk_embed

async def add_to_wallet(ctx, amount):
    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT wallet FROM users WHERE id = ?", [ctx.author.id])

    result = await cursor.fetchone()
    wallet = result[0]

    wallet += amount

    await cursor.execute("UPDATE users SET wallet = ? WHERE id = ?", (wallet, ctx.author.id))

    await db.commit()
    await cursor.close()
    await db.close()

    return wallet

async def get_stocks(ctx, amount):
    busk_msg = [
                'JYP', 'SM', 'YG', 'Cube', 'HYBE', 'Jellyfish', 'Pledis', 'Starship', 'Fantagio', 'Blockberry Creative',
                'Woollim', 'WakeOne', 'Mnet', 'KakaoM', 'CJ ENM'
                ]

    result = random.choice([0, 0.5, 1, 1.5, 2])

    jackpot = random.randrange(0, 1001)
    if (jackpot < 1):
        result = 10

    bal = await get_wallet(ctx.author.id)
    bal -= amount
    new_amt = int(result * amount)

    match result:
        case (0):
            title = 'MARKET CRASH!'
            msg = f'Oh no!!! The stock crashed and you lost all your investments...'
        case (0.5):
            title = 'Price drop!'
            msg = f'Yikes... The stock price dropped and you lost some money. Better luck next time!'
        case (1):
            title = 'Nothing happened?'
            msg = f'Hmm. I guess the stock market is dry this time around. At least you didn\'t lose anything!'
        case (1.5):
            title = 'Profit rose!'
            msg = f'Yes! Your stock rose in price a little and you made some quick cash! Talk about luck!'
        case (2):
            title = 'DOUBLED PROFITS!'
            msg = f'WOW!!! The stock rose exponentially and you gained double what you invested!'
        case (10):
            title = 'JACKPOT!!!'
            msg = f'YOU JUST HIT THE **JACKPOT!!!!!** YOU GAINED 10 TIMES WHAT YOU INVESTED!'

    busk_embed = discord.Embed(title=f'Busk - {ctx.author}', description=f'You decided to invest `{amount}🪙` into **{random.choice(busk_msg)}**')
    busk_embed.add_field(name=title, value=msg, inline=False)
    busk_embed.add_field(name='Result:', value=f'You have gained `{new_amt}🪙`!', inline=False)

    new_bal = bal + new_amt

    await add_to_wallet(ctx, new_amt - amount)

    busk_embed.set_footer(text=f'You now have {new_bal} coins.')

    return busk_embed

async def daily_claims(ctx):
    result = 5000

    rolled = await idols.idol_gacha(level=1)
    pic = Image.open(rolled.get_image())

    idolRank = idols.get_rank()
    rolled.set_rank(idolRank)
    file = idols.get_borderimage(idolRank, pic, rolled.get_shiny(), rolled.get_rarity())

    embed = discord.Embed(title=f'Daily - {ctx.author}', description='Welcome back!')
    embed.add_field(name='Daily Cash Claim!', value=f'You have been granted `{result}🪙` for your loyalty!', inline=False)

    embed.add_field(name='Daily Card Result!', value=f'{ctx.author.mention} found **{rolled.get_themename()}**!\n\n⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅', inline=False)
    embed.add_field(name='Card Info', value=f'Group: **{rolled.get_group()}**\nCard ID: `{rolled.get_uniqueid()}`\nRarity: {rolled.get_rarity_as_emoji()}\nRank: {rolled.get_rank_as_emoji()}', inline=False)
    embed.add_field(name='Card Stats', value=f'HP: `{rolled.gethp()}`\nATK: `{rolled.getatk()}`\nDEF: `{rolled.getdefnd()}`')
    embed.add_field(name='_ _', value=f'Crit Rate: `{rolled.getcritr()}`\nCrit DMG: `{rolled.getcritdmg()}`')

    if (rolled.get_shiny() == True):
        embed.add_field(name='This card shines a bit brighter than others...', value='Congrats! This card is **SHINY**!', inline=False)

    embed.set_image(url="attachment://foundcard.png")

    await add_to_wallet(ctx, result)

    new_wallet = await get_wallet(ctx.author.id)

    embed.set_footer(text=f'You now have {new_wallet} coins.')

    rolled.set_owner(ctx.author.id)
    idolcomp = idols.parseToString(rolled)
    await inventory.addtoinv(ctx.author.id, idolcomp)

    embedandfile = [embed, file]

    return embedandfile