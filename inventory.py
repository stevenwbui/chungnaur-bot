import array
from asyncio.windows_events import NULL
import idols
import aiosqlite
import discord

async def addtoinv(user_id, compressedcard):
    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT inventory FROM users WHERE id = ?", [user_id])

    result = await cursor.fetchone()
    inv = result[0]

    if (inv == None or inv == NULL or inv == "None" or inv == ""):
        inv = compressedcard
    else:
        invArray = inv.split("+")
        invArray.append(compressedcard)
        inv = "+".join(invArray)

    await cursor.execute("UPDATE users SET inventory = ? WHERE id = ?", (inv, user_id))

    await db.commit()
    await cursor.close()
    await db.close()

async def removefrominv(user_id, idol:idols.Idol):
    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT inventory FROM users WHERE id = ?", [user_id])

    result = await cursor.fetchone()
    inv = result[0]

    invArray = inv.split("+")

    removeidolstr = idols.parseToString(idol)

    invArray.remove(removeidolstr)

    inv = "+".join(invArray)

    await cursor.execute("UPDATE users SET inventory = ? WHERE id = ?", (inv, user_id))

    await cursor.execute("DELETE FROM cards_details WHERE uniqueid = ?", [user_id])

    await db.commit()
    await cursor.close()
    await db.close()

async def has_idol(user_id, uniqueval):
    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT owner FROM cards_details WHERE uniqueid = ?", [uniqueval])

    result = await cursor.fetchone()
    owner = result[0]

    await db.commit()
    await cursor.close()
    await db.close()
    
    if (owner != user_id):
        return None
    else:
        idol = await idols.get_idol_from_database(uniqueval)

        return idol

async def filter_inv(inv:array, group=None, rarity=None, rank=None, toggle_shiny=''):
    if group is not None:
        filteredbygroup = []
        for idol in inv:
            if (idol.get_group()==group):
                filteredbygroup.append(idol)
        inv = filteredbygroup
    
    if rarity is not None:
        filteredbyrarity = []
        for idol in inv:
            if (idol.get_rarity()==int(rarity)):
                filteredbyrarity.append(idol)
        inv = filteredbyrarity

    if rank is not None:
        filteredbyrank = []
        for idol in inv:
            if (idol.get_rank()==rank):
                filteredbyrank.append(idol)
        inv = filteredbyrank

    if bool(toggle_shiny) is True:
        filteredbyshiny = []
        for idol in inv:
            if (idol.get_shiny()==True):
                filteredbyshiny.append(idol)
        inv = filteredbyshiny

    return inv

async def getinvfromdb(user_id):
    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT inventory FROM users WHERE id = ?", [user_id])

    result = await cursor.fetchone()
    invraw = result[0]

    if (invraw != None and invraw != ''):
        inv = invraw.split("+")

        total_inv = []

        for i in inv:
            total_inv.append(idols.parseToIdol(i))
    else:
        total_inv = []

    return total_inv

async def print_inv(ctx, inv, page=0, filters=None):
    inv = await get_pages(inv)

    if (page >= len(inv) or page < 0):
        page = 0

    embed = discord.Embed(title=f'Inventory - {ctx.author}', description=filters)
    str = ''

    if (len(inv)==0):
        str = 'You have no idols!'
    else:
        for i in inv[page]:
            str += f'{i.toString()}\n'

    embed.add_field(name='Cards', value=str, inline=False)
    embed.set_footer(text=f'Page {page + 1} of {len(inv)}')

    return embed

async def get_pages(inv:array):
    if not inv:
        return []

    pages, remainder = divmod(len(inv), 10)
    pages += 1

    split_inv = []
    inv_page = []
    i = 0
    j = 0

    while i < pages:
        if (i == (pages - 1)):
            limit = remainder
        else:
            limit = 10

        while j < limit:
            inv_page.append(inv[j + (i * 10)])
            j += 1

        split_inv.append(inv_page)

        j = 0
        inv_page = []
        i += 1

    return split_inv