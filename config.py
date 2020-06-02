import json

from quotedb import QuoteDB

with open('creds.json', 'rt', encoding='utf-8') as f:
    creds = json.loads(''.join(f.readlines()))

token = creds['token']
proxy = creds['proxy_url']

rules_link = 'https://docs.google.com/document/d/1DRhi1jzjQFqg4WRxeSY38I2W-1PQccJptQ8bmg-kEN8/edit'
engine_link = 'https://lmgtfy.com/?q='

lat_rus_map = {ord(l): r for l, r in zip("f,dult`;pbqrkvyjghcnea[wxio]sm'.z&",
                                         "абвгдеёжзийклмнопрстуфхцчшщъыьэюя?")}

PY_CHAT_ID = creds['py_chat']
TEST_CHAT_ID = creds['test_chat']
SELF_USER = creds['self_user']

bot_admins = [SELF_USER]

qdb = QuoteDB()
