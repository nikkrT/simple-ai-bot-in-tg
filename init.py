from telebot import *
from openai import OpenAI
import configparser

def init():
    config = configparser.ConfigParser()
    config.read('config.ini')
    BOT_TOKEN = config['bot']['token']
    OPENAI_TOKEN = config['openai']['token']
    bot = telebot.TeleBot(BOT_TOKEN)
    limit = int(config['bot']['limit'])
    client = OpenAI(api_key=OPENAI_TOKEN)
    users = {int(i) for i in config['tg_ids']['users'].split(',') }
    risky = {int(i) for i in config['tg_ids']['risky'].split(',') }
    model=config['openai']['model']

    return BOT_TOKEN, OPENAI_TOKEN, bot,client, users, risky,limit,model