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
handled_chats = [PY_CHAT_ID, TEST_CHAT_ID]
chat_admins = [810095709]

chat_alias = {
    'py': PY_CHAT_ID
}

qdb = QuoteDB()
bot_auth = BotAuth()
