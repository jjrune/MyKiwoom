import os
import sys
import time
import sqlite3
import telegram
import pandas as pd
from telegram.ext import Updater, MessageHandler, Filters
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.setting import db_stg


class TelegramMsg:
    def __init__(self, qlist):
        self.windowQ = qlist[0]
        self.workerQ = qlist[1]
        self.queryQ = qlist[7]
        self.teleQ = qlist[8]
        self.updater = None

        con = sqlite3.connect(db_stg)
        df = pd.read_sql("SELECT name FROM sqlite_master WHERE TYPE = 'table'", con)
        if 'telegram' not in df['name'].values:
            df2 = pd.DataFrame({'str_bot': [''], 'int_id': [0]}, index=[0])
            self.queryQ.put([df2, 'telegram', 'replace'])
        time.sleep(2)
        df = pd.read_sql('SELECT * FROM telegram', con)
        self.str_botn = df['str_bot'][0]
        self.int_usid = int(df['int_id'][0])
        if self.str_botn != '':
            self.bot = telegram.Bot(self.str_botn)
            self.windowQ.put([2, f'텔레그램봇넘버 {self.str_botn}'])
            self.windowQ.put([2, f'사용자아이디 {self.int_usid}'])
            self.SetCustomButton()
        else:
            self.str_botn = None
            self.int_usid = None
            self.bot = None
        con.close()
        self.Start()

    def Start(self):
        while True:
            msg = self.teleQ.get()
            if type(msg) == str:
                self.SendMsg(msg)
            elif type(msg) == pd.DataFrame:
                self.UpdateDataframe(msg)

    def __del__(self):
        if self.updater is not None:
            self.updater.stop()

    def SetCustomButton(self):
        custum_button = [['/당일체결목록', '/당일거래목록', '/계좌잔고평가', '/잔고청산주문']]
        reply_markup = telegram.ReplyKeyboardMarkup(custum_button)
        self.bot.send_message(chat_id=self.int_usid, text='사용자버튼 설정을 완료하였습니다.', reply_markup=reply_markup)
        self.updater = Updater(self.str_botn)
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.ButtonClicked))
        self.updater.start_polling(drop_pending_updates=True)

    def ButtonClicked(self, update, context):
        if context == '':
            return
        self.workerQ.put(update.message.text)

    def SendMsg(self, msg):
        if self.bot is not None:
            try:
                self.bot.sendMessage(chat_id=self.int_usid, text=msg)
            except Exception as e:
                self.windowQ.put([1, f'시스템 명령 오류 알림 - SendMsg {e}'])
        else:
            self.windowQ.put([1, '시스템 명령 오류 알림 - 텔레그램 봇이 설정되지 않아 메세지를 보낼 수 없습니다.'])

    def UpdateDataframe(self, df):
        if df.columns[1] == '매수금액':
            df = df[::-1]
            text = ''
            for index in df.index:
                ct = df['체결시간'][index][8:10] + ':' + df['체결시간'][index][10:12]
                per = str(df['수익률'][index]) + '%'
                if len(per.split('.')[0]) == 1:
                    per = '  ' + per
                sg = format(int(df['수익금'][index]), ',') + '원'
                if len(sg.split(',')[0]) == 2:
                    sg = '    ' + sg
                elif len(sg.split(',')[0]) == 3:
                    sg = '  ' + sg
                name = df['종목명'][index]
                text += f'{ct} {per} {sg} {name}\n'
            self.SendMsg(text)
        elif df.columns[1] == '매입가':
            text = ''
            for index in df.index:
                per = str(df['수익률'][index]) + '%'
                if len(per.split('.')[0]) == 1:
                    per = ' ' + per
                sg = format(int(df['평가손익'][index]), ',') + '원'
                if len(sg.split(',')[0]) == 2:
                    sg = '    ' + sg
                elif len(sg.split(',')[0]) == 3:
                    sg = '  ' + sg
                name = df['종목명'][index]
                text += f'{per} {sg} {name}\n'
            tbg = format(int(df['매입금액'].sum()), ',') + '원'
            tpg = format(int(df['평가금액'].sum()), ',') + '원'
            tsg = format(int(df['평가손익'].sum()), ',') + '원'
            tsp = str(round(df['평가손익'].sum() / df['매입금액'].sum() * 100, 2)) + '%'
            text += f'{tbg} {tpg} {tsp} {tsg}\n'
            self.SendMsg(text)
        elif df.columns[1] == '주문구분':
            df = df[::-1]
            text = ''
            for index in df.index:
                ct = df['체결시간'][index][8:10] + ':' + df['체결시간'][index][10:12]
                bs = df['주문구분'][index]
                bp = int(df['체결가'][index])
                name = df['종목명'][index]
                text += f'{ct} {bs} {bp} {name}\n'
            self.SendMsg(text)
