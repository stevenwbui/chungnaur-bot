from cgitb import reset
from random import randrange
import random
import aiosqlite
import discord
from PIL import Image
from io import BytesIO

card_groups = [
            discord.OptionChoice(name="AESPA", value="AESPA"),
            discord.OptionChoice(name="BLACKPINK", value="BLACKPINK"),
            discord.OptionChoice(name="BTS", value="BTS"),
            discord.OptionChoice(name="FROMIS_9", value="FROMIS_9"),
            discord.OptionChoice(name="GOLDEN CHILD", value="GOLDEN CHILD"),
            discord.OptionChoice(name="KEP1ER", value="KEP1ER"),
            discord.OptionChoice(name="SOLO", value="SOLO"),
            discord.OptionChoice(name="TWICE", value="TWICE")
            ]

rarities = [
        discord.OptionChoice(name="★☆☆", value='1'),
        discord.OptionChoice(name="★★☆", value='2'),
        discord.OptionChoice(name="★★★", value='3')
        ]

ranks = [
        discord.OptionChoice(name="F", value="F"),
        discord.OptionChoice(name="B", value="B"),
        discord.OptionChoice(name="A", value="A"),
        discord.OptionChoice(name="S", value="S"),
        discord.OptionChoice(name="U", value="U"),
        ]

toggle_shiny = [
        discord.OptionChoice(name="Only show SHINY cards", value='True'),
        discord.OptionChoice(name="Show both SHINY and NONSHINY cards", value='')
        ]

class Idol:
    def __init__(self, name, group, id, rarity=1, theme='No Theme', rank=None, shiny=False, unique_id=None, hp=1000, atk=150, defnd=15, critr=5, critdmg=100, owner=None, borderless=False):
        self.name = name
        self.group = group
        self.id = id
        self.rarity = rarity
        self.theme = theme
        self.rank = rank
        self.shiny = shiny
        self.unique_id = unique_id

        self.hp = hp
        self.atk = atk
        self.defnd = defnd
        self.critr = critr
        self.critdmg = critdmg

        self.owner = owner

        self.borderless = borderless

    def get_name(self):
        return self.name

    def get_group(self):
        return self.group

    def get_id(self):
        return self.id

    def get_rarity(self):
        return self.rarity

    def get_rarity_as_emoji(self):
        filledstar = '★'
        unfilledstar = '☆'

        if (self.shiny == True):
            filledstar = '✦'
            unfilledstar = '✧'

        emojis = ''
        i = 0
        while i < self.rarity:
            emojis += filledstar
            i += 1

        other_stars = 2 - (self.rarity - 1)
        i = 0
        while i < other_stars:
            emojis += unfilledstar
            i += 1
        
        return emojis

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

    def get_rank_as_emoji(self):
        match (self.rank):
            case ('F'):
                str = '<:F_:993746687145283595>'
            case ('B'):
                str = '<:B_:993746686226735197>'
            case ('A'):
                str = '<:A_:993746684637089793>'
            case ('S'):
                str = '<:S_:993746688676208650>'
            case ('U'):
                str = '<:U_:993746689456349235>'

        return str

    def set_uniqueid(self, value):
        self.unique_id = f"{self.id}.{value}"

    def get_uniqueid(self):
        return self.unique_id

    def gethp(self):
        return self.hp

    def getatk(self):
        return self.atk

    def getdefnd(self):
        return self.defnd

    def getcritr(self):
        return self.critr

    def getcritdmg(self):
        return self.critdmg

    def sethp(self, hp):
        self.hp = hp

    def setatk(self, atk):
        self.atk = atk

    def setdefnd(self, hp):
        self.defnd = hp

    def setcritr(self, hp):
        self.critr = hp

    def setcritdmg(self, hp):
        self.critdmg = hp

    def set_owner(self, id):
        self.owner = id

    def get_owner(self):
        return self.owner
    
    def get_borderless(self):
        return self.borderless

    def get_sellprice(self):
        match self.rank:
            case ('F'):
                price = 50
            case ('B'):
                price = 100
            case ('A'):
                price = 150
            case ('S'):
                price = 200
            case ('U'):
                price = 250

        return price * self.rarity

    def toString(self):
        return f'`{self.get_rarity_as_emoji()}` | **{self.theme}** {self.name} | {self.get_rank_as_emoji()} | `{self.unique_id}`'

IdolsList_One = [ #twice
                Idol('Nayeon', 'TWICE', 'twinyn101'),
                Idol('Jeongyeon', 'TWICE', 'twijyn101'),
                Idol('Momo', 'TWICE', 'twimmo101'),
                Idol('Sana', 'TWICE', 'twisna101'),
                Idol('Jihyo', 'TWICE', 'twijho101'),
                Idol('Mina', 'TWICE', 'twimna101'),
                Idol('Dahyun', 'TWICE', 'twidhn101'),
                Idol('Chaeyoung', 'TWICE', 'twicyg101'),
                Idol('Tzuyu', 'TWICE', 'twitzu101'),

                #aespa
                Idol('Karina', 'AESPA', 'aeskna101'),
                Idol('Winter', 'AESPA', 'aeswtr101'),
                Idol('Ningning', 'AESPA', 'aesnng101'),
                Idol('Giselle', 'AESPA', 'aesgse101'),

                #blackpink
                Idol('Jennie', 'BLACKPINK', 'bpkjne101'),
                Idol('Jisoo', 'BLACKPINK', 'bpkjso101'),
                Idol('Rose', 'BLACKPINK', 'bpkrse101'),
                Idol('Lisa', 'BLACKPINK', 'bpklsa101'),

                #bts
                Idol('J-Hope', 'BTS', 'btsjhe101'),
                Idol('Jin', 'BTS', 'btsjin101'),
                Idol('Jungkook', 'BTS', 'btsjkk101'),
                Idol('Jimin', 'BTS', 'btsjmn101'),
                Idol('RM', 'BTS', 'btsrm101'),
                Idol('Suga', 'BTS', 'btssga101'),
                Idol('V', 'BTS', 'btsv101'),

                #fromis_9
                Idol('Saerom', 'FROMIS_9', 'fm9srm101'),
                Idol('Chaeyoung', 'FROMIS_9', 'fm9cyg101'),
                Idol('Gyuri', 'FROMIS_9', 'fm9gri101'),
                Idol('Hayoung', 'FROMIS_9', 'fm9hyg101'),
                Idol('Jiheon', 'FROMIS_9', 'fm9jhn101'),
                Idol('Jisun', 'FROMIS_9', 'fm9jsn101'),
                Idol('Jiwon', 'FROMIS_9', 'fm9jwn101'),
                Idol('Nagyung', 'FROMIS_9', 'fm9ngg101'),
                Idol('Seoyeon', 'FROMIS_9', 'fm9syn101'),

                #golden child
                Idol('Bomin', 'GOLDEN CHILD', 'gcdbmn101'),
                Idol('Donghyun', 'GOLDEN CHILD', 'gcddhn101'),
                Idol('Daeyeol', 'GOLDEN CHILD', 'gcddyl101'),
                Idol('Jibeom', 'GOLDEN CHILD', 'gcdjbm101'),
                Idol('Joochan', 'GOLDEN CHILD', 'gcdjcn101'),
                Idol('Jaehyun', 'GOLDEN CHILD', 'gcdjhn101'),
                Idol('Jangjun', 'GOLDEN CHILD', 'gcdjjn101'),
                Idol('Seungmin', 'GOLDEN CHILD', 'gcdsmn101'),
                Idol('TAG', 'GOLDEN CHILD', 'gcdtag101'),
                Idol('Y', 'GOLDEN CHILD', 'gcdy101'),

                #kep1er
                Idol('Bahiyyih', 'KEP1ER', 'kp1bhh101'),
                Idol('Chaehyun', 'KEP1ER', 'kp1chn101'),
                Idol('Dayeon', 'KEP1ER', 'kp1dyn101'),
                Idol('Hikaru', 'KEP1ER', 'kp1hku101'),
                Idol('Mashiro', 'KEP1ER', 'kp1mso101'),
                Idol('Xiaoting', 'KEP1ER', 'kp1xtg101'),
                Idol('Youngeun', 'KEP1ER', 'kp1yen101'),
                Idol('Yujin', 'KEP1ER', 'kp1yjn101'),
                Idol('Yeseo', 'KEP1ER', 'kp1yso101'),

                #soloists
                Idol('Chungha', 'SOLO', 'solcha101'),
                Idol('Sunmi', 'SOLO', 'solsnmi101'),
                Idol('Somi', 'SOLO', 'solsomi101'),
                Idol('Taeyeon', 'SOLO', 'soltyn101')
            ]

IdolsList_Two = [ #twice
                Idol('Nayeon', 'TWICE', 'twinyn201', 2, 'The Story Begins'),
                Idol('Jeongyeon', 'TWICE', 'twijyn201', 2, 'The Story Begins'),
                Idol('Momo', 'TWICE', 'twimmo201', 2, 'The Story Begins'),
                Idol('Sana', 'TWICE', 'twisna201', 2, 'The Story Begins'),
                Idol('Jihyo', 'TWICE', 'twijho201', 2, 'The Story Begins'),
                Idol('Mina', 'TWICE', 'twimna201', 2, 'The Story Begins'),
                Idol('Dahyun', 'TWICE', 'twidhn201', 2, 'The Story Begins'),
                Idol('Chaeyoung', 'TWICE', 'twicyg201', 2, 'The Story Begins'),
                Idol('Tzuyu', 'TWICE', 'twitzu201', 2, 'The Story Begins'),

                Idol('Nayeon', 'TWICE', 'twinyn202', 2, 'Page Two'),
                Idol('Jeongyeon', 'TWICE', 'twijyn202', 2, 'Page Two'),
                Idol('Momo', 'TWICE', 'twimmo202', 2, 'Page Two'),
                Idol('Sana', 'TWICE', 'twisna202', 2, 'Page Two'),
                Idol('Jihyo', 'TWICE', 'twijho202', 2, 'Page Two'),
                Idol('Mina', 'TWICE', 'twimna202', 2, 'Page Two'),
                Idol('Dahyun', 'TWICE', 'twidhn202', 2, 'Page Two'),
                Idol('Chaeyoung', 'TWICE', 'twicyg202', 2, 'Page Two'),
                Idol('Tzuyu', 'TWICE', 'twitzu202', 2, 'Page Two'),

                Idol('Nayeon', 'TWICE', 'twinyn203', 2, 'Feel Special'),
                Idol('Jeongyeon', 'TWICE', 'twijyn203', 2, 'Feel Special'),
                Idol('Momo', 'TWICE', 'twimmo203', 2, 'Feel Special'),
                Idol('Sana', 'TWICE', 'twisna203', 2, 'Feel Special'),
                Idol('Jihyo', 'TWICE', 'twijho203', 2, 'Feel Special'),
                Idol('Mina', 'TWICE', 'twimna203', 2, 'Feel Special'),
                Idol('Dahyun', 'TWICE', 'twidhn203', 2, 'Feel Special'),
                Idol('Chaeyoung', 'TWICE', 'twicyg203', 2, 'Feel Special'),
                Idol('Tzuyu', 'TWICE', 'twitzu203', 2, 'Feel Special'),

                # aespa
                Idol('Giselle', 'AESPA', 'aesgse201', 2, 'Black Mamba'),
                Idol('Karina', 'AESPA', 'aeskna201', 2, 'Black Mamba'),
                Idol('Ningning', 'AESPA', 'aesnng201', 2, 'Black Mamba'),
                Idol('Winter', 'AESPA', 'aeswtr201', 2, 'Black Mamba'),

                Idol('Giselle', 'AESPA', 'aesgse202', 2, 'Forever'),
                Idol('Karina', 'AESPA', 'aeskna202', 2, 'Forever'),
                Idol('Ningning', 'AESPA', 'aesnng202', 2, 'Forever'),
                Idol('Winter', 'AESPA', 'aeswtr202', 2, 'Forever'),

                Idol('Giselle', 'AESPA', 'aesgse203', 2, 'NU EVO'),
                Idol('Karina', 'AESPA', 'aeskna203', 2, 'NU EVO'),
                Idol('Ningning', 'AESPA', 'aesnng203', 2, 'NU EVO'),
                Idol('Winter', 'AESPA', 'aeswtr203', 2, 'NU EVO'),

                Idol('Giselle', 'AESPA', 'aesgse204', 2, 'Algorithm'),
                Idol('Karina', 'AESPA', 'aeskna204', 2, 'Algorithm'),
                Idol('Ningning', 'AESPA', 'aesnng204', 2, 'Algorithm'),
                Idol('Winter', 'AESPA', 'aeswtr204', 2, 'Algorithm'),

                Idol('Giselle', 'AESPA', 'aesgse205', 2, 'Twilight Zone'),
                Idol('Karina', 'AESPA', 'aeskna205', 2, 'Twilight Zone'),
                Idol('Ningning', 'AESPA', 'aesnng205', 2, 'Twilight Zone'),
                Idol('Winter', 'AESPA', 'aeswtr205', 2, 'Twilight Zone')
            ]

IdolsList_Three = [ #twice
                    Idol('Nayeon', 'TWICE', 'twinyn301', 3, 'Do It Again'),

                    Idol('Nayeon', 'TWICE', 'twinyn302', 3, 'Cheer Up'),

                    #solo
                    Idol('Nayeon', 'SOLO', 'solnyn301', 3, 'POP!'),

                    #aespa
                    Idol('Giselle', 'AESPA', 'aesgse301', 3, 'Next Level'),
                    Idol('Karina', 'AESPA', 'aeskna301', 3, 'Next Level'),
                    Idol('Ningning', 'AESPA', 'aesnng301', 3, 'Next Level'),
                    Idol('Winter', 'AESPA', 'aeswtr301', 3, 'Next Level')
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

    set_stats(idol_rolled, idol_rolled.get_rarity(), idol_rolled.get_rank())

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

def set_stats(idol_rolled, rarity=1, rank='F'):
    match (rank):
        case ('F'):
            idol_rolled.sethp(randrange(750, 851))
            idol_rolled.setatk(randrange(50, 76))
            idol_rolled.setdefnd(randrange(1, 6))
        case ('B'):
            idol_rolled.sethp(randrange(851, 951))
            idol_rolled.setatk(randrange(76, 101))
            idol_rolled.setdefnd(randrange(6, 11))
        case ('A'):
            idol_rolled.sethp(randrange(951, 1051))
            idol_rolled.setatk(randrange(101, 126))
            idol_rolled.setdefnd(randrange(11, 16))
        case ('S'):
            idol_rolled.sethp(randrange(1051, 1151))
            idol_rolled.setatk(randrange(126, 151))
            idol_rolled.setdefnd(randrange(16, 21))
        case ('U'):
            idol_rolled.sethp(randrange(1151, 1251))
            idol_rolled.setatk(randrange(151, 176))
            idol_rolled.setdefnd(randrange(21, 26))

    idol_rolled.sethp(int(idol_rolled.gethp() * rarity))
    idol_rolled.setatk(int(float(idol_rolled.getatk() * (1 + ((rarity - 1) * 0.2)))))
    idol_rolled.setdefnd(int(float(idol_rolled.getdefnd() * (1 + ((rarity - 1) * 0.4)))))

    idol_rolled.setcritr(randrange(5, 76))
    idol_rolled.setcritdmg(randrange(50, 200))

def parseToString(idol_rolled):

    uniqueid = idol_rolled.get_uniqueid()
    name = idol_rolled.get_name()
    group = idol_rolled.get_group()
    id = idol_rolled.get_id()
    rarity = str(idol_rolled.get_rarity())
    theme = idol_rolled.get_theme()

    if (idol_rolled.get_shiny() == True):
        shiny = '1'
    else:
        shiny = '0'

    rank = str(idol_rolled.get_rank())
    hp = str(idol_rolled.gethp())
    atk = str(idol_rolled.getatk())
    defnd = str(idol_rolled.getdefnd())
    critr = str(idol_rolled.getcritr())
    critdmg = str(idol_rolled.getcritdmg())

    owner = str(idol_rolled.get_owner())

    if (idol_rolled.get_borderless() == True):
        borderless = '1'
    else:
        borderless = '0'

    cardinfo = [uniqueid, name, group, id, rarity, theme, rank, shiny, hp, atk, defnd, critr, critdmg, owner, borderless]

    compressed = '|'.join(cardinfo)

    return compressed

def parseToIdol(compressed):

    cardinfo = compressed.split('|')

    uniqueid = cardinfo[0]
    name = cardinfo[1]
    group = cardinfo[2]
    id = cardinfo[3]
    rarity = int(cardinfo[4])
    theme = cardinfo[5]
    rank = cardinfo[6]
    shiny = int(cardinfo[7])

    if (shiny == 0):
        shiny = False
    else:
        shiny = True

    hp = int(cardinfo[8])
    atk = int(cardinfo[9])
    defnd = int(cardinfo[10])
    critr = int(cardinfo[11])
    critdmg = int(cardinfo[12])
    owner = int(cardinfo[13])
    borderless = int(cardinfo[14])
    
    if (borderless == 0):
        borderless = False
    else:
        borderless = True

    return Idol(name, group, id, rarity, theme, rank, shiny, uniqueid, hp, atk, defnd, critr, critdmg, owner, borderless)

async def add_idol_to_database(rolled:Idol):
    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT uniqueid FROM cards_details WHERE uniqueid = ?", [rolled.get_uniqueid()])

    result = await cursor.fetchone()

    if (rolled.get_shiny == True):
        shiny = 1
    else:
        shiny = 0

    if (rolled.get_borderless == True):
        bless = 1
    else:
        bless = 0

    if (result is None):
        await cursor.execute("INSERT INTO cards_details(uniqueid, name, groupname, id, rarity, theme, rank, shiny, hp, atk, defnd, critr, critdmg, owner, borderless) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (rolled.get_uniqueid(), rolled.get_name(), rolled.get_group(), rolled.get_id(), rolled.get_rarity(), rolled.get_theme(), rolled.get_rank(), shiny, rolled.gethp(), rolled.getatk(), rolled.getdefnd(), rolled.getcritr(), rolled.getcritdmg(), rolled.get_owner(), bless))

    await db.commit()
    await cursor.close()
    await db.close()

async def get_idol_from_database(uniqueid:str):
    db = await aiosqlite.connect("main.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM cards_details WHERE uniqueid = ?", [uniqueid])

    cardinfo = await cursor.fetchone()

    if (cardinfo is None):
        return None

    uniqueid = cardinfo[0]
    name = cardinfo[1]
    group = cardinfo[2]
    id = cardinfo[3]
    rarity = int(cardinfo[4])
    theme = cardinfo[5]
    rank = cardinfo[6]
    shiny = int(cardinfo[7])

    if (shiny == 0):
        shiny = False
    else:
        shiny = True

    hp = int(cardinfo[8])
    atk = int(cardinfo[9])
    defnd = int(cardinfo[10])
    critr = int(cardinfo[11])
    critdmg = int(cardinfo[12])
    owner = int(cardinfo[13])
    borderless = int(cardinfo[14])
    
    if (borderless == 0):
        borderless = False
    else:
        borderless = True

    return Idol(name, group, id, rarity, theme, rank, shiny, uniqueid, hp, atk, defnd, critr, critdmg, owner, borderless)


