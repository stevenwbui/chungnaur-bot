from cgitb import reset
from random import randrange
import random
import aiosqlite
import discord
from PIL import Image
from io import BytesIO

class Idol:
    def __init__(self, name, group, id, rarity=1, theme='No Theme', rank=None, shiny=False, unique_id=None):
        self.name = name
        self.group = group
        self.id = id
        self.rarity = rarity
        self.theme = theme
        self.rank = rank
        self.shiny = shiny
        self.unique_id = unique_id

    def get_name(self):
        return self.name

    def get_group(self):
        return self.group

    def get_id(self):
        return self.id

    def get_rarity(self):
        return self.rarity

    def get_theme(self):
        return self.theme

    def get_image(self):
        return "cardpics\\" + self.group + "\\" + str(self.rarity) + "\\" + self.id + ".png"

    def set_shiny(self):
        self.shiny = True

    def get_shiny(self):
        return self.shiny

    def get_themename(self):
        if (self.theme == 'No Theme'):
            return self.name
        else:
            return f'`{self.theme}` {self.name}'

    def set_rank(self, rank):
        self.rank = rank

    def get_rank(self):
        return self.rank

    def set_uniqueid(self, value):
        self.unique_id = f"{self.id}.{value}"

    def get_uniqueid(self):
        return self.unique_id

IdolsList_One = [Idol('Nayeon', 'TWICE', 'twinyn101'),
            Idol('Jeongyeon', 'TWICE', 'twijyn101'),
            Idol('Momo', 'TWICE', 'twimmo101')
            ]

IdolsList_Two = [Idol('Nayeon', 'TWICE', 'twinyn201', 2, 'The Story Begins'),
            Idol('Nayeon', 'TWICE', 'twinyn202', 2, 'Page Two'),
            Idol('Nayeon', 'TWICE', 'twinyn203', 2, 'Feel Special')
            ]

IdolsList_Three = [Idol('Nayeon', 'TWICE', 'twinyn301', 3, 'Do It Again'),
            Idol('Nayeon', 'TWICE', 'twinyn302', 3, 'Cheer Up'),
            Idol('Nayeon', 'SOLO', 'solnyn301', 3, 'POP!')
            ]

IdolsList = [IdolsList_One, IdolsList_Two, IdolsList_Three]

async def idol_gacha(level=1):

    match level:
        case 1:
            max_one = 950
            max_two = 994
        case 2:
            max_one = 800
            max_two = 925
        case 3:
            max_one = 500
            max_two = 800

    rolled = randrange(0, 1001, 1)

    rolledrarity = 3

    if (rolled < max_one):
        rolledrarity = 1
    elif (rolled < max_two):
        rolledrarity = 2

    rolledindex = rolledrarity - 1

    rarity_array = IdolsList[rolledindex]

    idol_rolled = random.choice(rarity_array)

    shiny = randrange(0, 101, 1)
    if (shiny < 6):
        idol_rolled.set_shiny()

    card_db = await aiosqlite.connect("main.db")
    card_cursor = await card_db.cursor()
    await card_cursor.execute(f"SELECT uniqueval FROM cards_numbers WHERE id = ?", [idol_rolled.get_id()])
    result = await card_cursor.fetchone()
    
    if result is None:
        await card_cursor.execute("INSERT INTO cards_numbers(id, uniqueval) VALUES (?, ?)", (idol_rolled.get_id(), 1))
        result = 1
    else:
        result = result[0]
    
    current_uniqueval = result

    result = int(result)
    result += 1
    await card_cursor.execute(f"UPDATE cards_numbers SET uniqueval =  ? WHERE id = ?", (result, idol_rolled.get_id()))

    await card_db.commit()
    await card_cursor.close()
    await card_db.commit()

    idol_rolled.set_uniqueid(current_uniqueval)

    return idol_rolled

def get_rank():
    rarity = randrange(0, 10001, 1)

    if (rarity < 5000):

        return 'F'
    elif (rarity < 8500):
        return 'B'
    elif (rarity < 9750):
        return 'A'
    elif (rarity < 9930):
        return 'S'
    else:
        return 'U'

def get_borderimage(rank, image, shiny=False, rarity=1):
    match rank:
        case ('B'):
            border = Image.open(r"cardpics\BORDERS\Bborder.png")
        case ('A'):
            border = Image.open(r"cardpics\BORDERS\Aborder.png")
        case ('S'):
            border = Image.open(r"cardpics\BORDERS\Sborder.png")
        case ('U'):
            if (shiny==True):
                border = Image.open(r"cardpics\BORDERS\ShinyUborder.png")
            else:
                border = Image.open(r"cardpics\BORDERS\Uborder.png")
        case _:
            border = Image.open(r"cardpics\BORDERS\Fborder.png")

    if (shiny==True):
        shinystars = Image.open(r"cardpics\\SHINYSTARS\\" + str(rarity) + "shinystar.png")
        shinyImg = Image.alpha_composite(image, shinystars)
        image = shinyImg

    final_img = Image.alpha_composite(image, border)
    bytes = BytesIO()
    final_img.save(bytes, format="PNG")
    bytes.seek(0)
    dfile = discord.File(bytes, filename="foundcard.png")
    return dfile



