import sqlite3
import datetime
import telegram
import pandas as pd
from threading import Thread
from utility.setting import db_stg

bot = ''
user_id = 0
try:
    connn = sqlite3.connect(db_stg)
    df_tg = pd.read_sql('SELECT * FROM telegram', connn)
    connn.close()
except pd.io.sql.DatabaseError:
    pass
else:
    bot = df_tg['str_bot'][0]
    user_id = int(df_tg['int_id'][0])


def thread_decorator(func):
    def wrapper(*args):
        Thread(target=func, args=args, daemon=True).start()
    return wrapper


def telegram_msg(text):
    if bot == '':
        print('텔레그램 봇이 설정되지 않아 메세지를 보낼 수 없습니다.')
    else:
        try:
            telegram.Bot(bot).sendMessage(chat_id=user_id, text=text)
        except Exception as e:
            print(f'텔레그램 설정 오류 알림 - telegram_msg {e}')


def now():
    return datetime.datetime.now()


def timedelta_sec(second, std_time=None):
    if std_time is None:
        next_time = now() + datetime.timedelta(seconds=second)
    else:
        next_time = std_time + datetime.timedelta(seconds=second)
    return next_time


def timedelta_day(day, std_time=None):
    if std_time is None:
        next_time = now() + datetime.timedelta(days=day)
    else:
        next_time = std_time + datetime.timedelta(days=day)
    return next_time


def strp_time(timetype, str_time):
    return datetime.datetime.strptime(str_time, timetype)


def strf_time(timetype, std_time=None):
    if std_time is None:
        str_time = now().strftime(timetype)
    else:
        str_time = std_time.strftime(timetype)
    return str_time


def comma2int(t):
    if ' ' in t:
        t = t.split(' ')[1]
    if ',' in t:
        t = t.replace(',', '')
    return int(t)


def float2str3p2(t):
    t = str(t)
    if len(t.split('.')[0]) == 1:
        t = '  ' + t
    if len(t.split('.')[0]) == 2:
        t = ' ' + t
    if len(t.split('.')[1]) == 1:
        t += '0'
    return t


def float2str2p2(t):
    t = str(t)
    if len(t.split('.')[0]) == 1:
        t = ' ' + t
    if len(t.split('.')[1]) == 1:
        t += '0'
    return t
