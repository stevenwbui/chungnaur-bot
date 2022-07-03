import aiosqlite

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
    await cursor.execute("SELECT id FROM users WHERE id = ?", [user_id])

    result = await cursor.fetchone()
    wallet = result[0]

    if (wallet >= result):
        wallet -= price
        await cursor.execute("UPDATE users SET wallet = ? WHERE id = ?", (wallet, user_id))

        answer = True

    else:
        answer = False

    db.commit()
    cursor.close()
    db.close()
    return answer


