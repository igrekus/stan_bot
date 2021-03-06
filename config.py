import json

from botauth import BotAuth
from quotedb import QuoteDB

with open('creds.json', 'rt', encoding='utf-8') as f:
    creds = json.loads(''.join(f.readlines()))

token = creds['token']
proxy = creds['proxy_url']

rules_link = 'https://docs.google.com/document/d/1DRhi1jzjQFqg4WRxeSY38I2W-1PQccJptQ8bmg-kEN8/edit'
engine_link = 'https://lmgtfy.com/?q='
google_link = 'https://www.google.com/search?q='

lat_rus_map = {ord(l): r for l, r in zip("f,dult`;pbqrkvyjghcnea[wxio]sm'.z&?/",
                                         "абвгдеёжзийклмнопрстуфхцчшщъыьэюя?,.")}

PY_CHAT_ID = creds['py_chat']
TEST_CHAT_ID = -1001204542632
SELF_USER = creds['self_user']

# TODO move auth stuff to the db
bot_admins = [SELF_USER]
handled_chats = [PY_CHAT_ID, TEST_CHAT_ID, -1001473452731]
chat_admins = [810095709]

# TODO refactor: move to database
banned_users = {1031419184, 817523974, 1078771932, 988327820, 875981908, 1319784856, 1175535795, 1353007865, 500423762}
allowed_to_add = {
    292830777: {
        'username': 'baa lique',
        'times': 3
    },
    301703093: {
        'username': 'Denis',
        'times': 1
    },
    562159867: {
        'username': 'Andy',
        'times': 1
    },
}

chat_alias = {
    'py': PY_CHAT_ID
}

qdb = QuoteDB()
bot_auth = BotAuth()
