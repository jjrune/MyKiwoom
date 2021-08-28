import os
import sys
import psutil
import sqlite3
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.setting import db_stg, ui_num
from utility.static import now, timedelta_sec, thread_decorator


class StrategyLong:
    def __init__(self, qlist):
        self.windowQ = qlist[0]
        self.workerQ = qlist[1]
        self.stglQ = qlist[3]

        self.list_buy = []
        self.list_sell = []
        self.df = None
        self.dict_intg = {
            '스레드': 0,
            '시피유': 0.,
            '메모리': 0.
        }
        self.dict_time = {
            '관심종목': now(),
            '부가정보': now()
        }

        self.Start()

    def Start(self):
        while True:
            data = self.stglQ.get()
            if data == '데이터베이스로딩':
                self.DatabaseLoad()
            elif len(data) == 2:
                self.UpdateList(data[0], data[1])
            elif len(data) == 3:
                if type(data[0]) == str:
                    self.UpdateStrategy(data[0], data[1], data[2])
                elif type(data[0]) == dict:
                    self.BuyStrategy(data[0], data[1], data[2])
            elif len(data) == 5:
                self.SellStrategy(data[0], data[1], data[2], data[3], data[4])

            if now() > self.dict_time['관심종목']:
                self.df.sort_values(by=['prelong', '비중'], ascending=False, inplace=True)
                self.windowQ.put([ui_num['long'], self.df])
                self.dict_time['관심종목'] = timedelta_sec(1)
            if now() > self.dict_time['부가정보']:
                self.UpdateInfo()
                self.dict_time['부가정보'] = timedelta_sec(2)

    def DatabaseLoad(self):
        con = sqlite3.connect(db_stg)
        df = pd.read_sql('SELECT * FROM long', con)
        con.close()
        self.df = df.set_index('index')
        self.df['현재가'] = 0
        self.df['이평2005'] = 0.
        self.df['이평20'] = 0.
        self.df['체결시간'] = '150000'
        self.df.sort_values(by=['prelong', '비중'], ascending=False, inplace=True)
        self.windowQ.put([ui_num['long'] + 100, self.df])

    def UpdateList(self, gubun, code):
        if gubun == '매수완료':
            if code in self.list_buy:
                self.list_buy.remove(code)
        elif gubun == '매도완료':
            if code in self.list_sell:
                self.list_sell.remove(code)

    def UpdateStrategy(self, code, c, d):
        if d != self.df['체결시간'][code]:
            ma20 = round((self.df['tc19'][code] + c) / 20, 2)
            ma2005 = round(ma20 * 1.05, 2)
            self.df.at[code, ['현재가', '이평2005', '이평20', '체결시간']] = c, ma2005, ma20, d

    def BuyStrategy(self, dict_name, jangolist, batting):
        for code in self.df.index:
            if code not in jangolist:
                continue

            # 전략 비공개

            bj = self.df['비중'][code]
            c = self.df['현재가'][code]
            oc = int(batting * bj * 3.33 / c)
            name = dict_name[code]
            if oc > 0:
                self.list_buy.append(code)
                self.workerQ.put(['장기매수', code, name, c, oc])

    def SellStrategy(self, code, name, jc, sp, c):
        if code in self.list_sell:
            return

        # 전략 비공개

        self.list_sell.append(code)
        self.workerQ.put(['장기매도', code, name, c, jc])

    @thread_decorator
    def UpdateInfo(self):
        info = [5, self.dict_intg['메모리'], self.dict_intg['스레드'], self.dict_intg['시피유']]
        self.windowQ.put(info)
        self.UpdateSysinfo()

    def UpdateSysinfo(self):
        p = psutil.Process(os.getpid())
        self.dict_intg['메모리'] = round(p.memory_info()[0] / 2 ** 20.86, 2)
        self.dict_intg['스레드'] = p.num_threads()
        self.dict_intg['시피유'] = round(p.cpu_percent(interval=2) / 2, 2)
