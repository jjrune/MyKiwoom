import os
import sys
import warnings
import numpy as np
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.static import strf_time, timedelta_sec, now
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


class UpdaterTick:
    def __init__(self, tickQ, queryQ, workerQ, windowQ):
        self.tickQ = tickQ
        self.queryQ = queryQ
        self.workerQ = workerQ
        self.windowQ = windowQ

        self.dict_df = {}
        self.time_info = now()
        self.str_tday = strf_time('%Y%m%d')
        self.Start()

    def Start(self):
        while True:
            tick = self.tickQ.get()
            if type(tick) == list:
                self.UpdateTickData(tick[0], tick[1], tick[2], tick[3], tick[4], tick[5], tick[6], tick[7],
                                    tick[8], tick[9], tick[10], tick[11], tick[12], tick[13], tick[14],
                                    tick[15], tick[16], tick[17], tick[18], tick[19], tick[20])
            elif tick == '틱데이터저장':
                self.PutTickData()
            """
            전략 테스트 프로그램이 거래한 종목만 저장
            if len(tick) != 2:
                self.UpdateTickData(tick[0], tick[1], tick[2], tick[3], tick[4], tick[5], tick[6], tick[7],
                                    tick[8], tick[9], tick[10], tick[11], tick[12], tick[13], tick[14],
                                    tick[15], tick[16], tick[17], tick[18], tick[19], tick[20])
            else:
                self.PutTickData(tick[0], tick[1])
            """

    def UpdateTickData(self, code, c, o, h, low, per, dm, ch, vp, vitime, vid5,
                       s1jr, s2jr, b1jr, b2jr, s1hg, s2hg, b1hg, b2hg, d, receiv_time):
        try:
            hlm = int(round((h + low) / 2))
            hlmp = round((c / hlm - 1) * 100, 2)
        except ZeroDivisionError:
            return
        d = self.str_tday + d
        if code not in self.dict_df.keys():
            self.dict_df[code] = pd.DataFrame(
                [[c, o, per, hlmp, dm, dm, ch, vp, vitime, vid5, s1jr, s2jr, b1jr, b2jr, s1hg, s2hg, b1hg, b2hg]],
                columns=['현재가', '시가', '등락율', '고저평균대비등락율', '거래대금', '누적거래대금', '체결강도', '전일거래량대비',
                         'VI발동시간', '상승VID5가격', '매도1잔량', '매도2잔량', '매수1잔량', '매수2잔량', '매도1호가', '매도2호가',
                         '매수1호가', '매수2호가'],
                index=[d])
        else:
            sm = int(dm - self.dict_df[code]['누적거래대금'][-1])
            self.dict_df[code].at[d] = \
                c, o, per, hlmp, sm, dm, ch, vp, vitime, vid5, s1jr, s2jr, b1jr, b2jr, s1hg, s2hg, b1hg, b2hg
        if now() > self.time_info:
            self.UpdateInfo(receiv_time)
            self.time_info = timedelta_sec(60)

    def UpdateInfo(self, receiv_time):
        gap = (now() - receiv_time).total_seconds()
        self.windowQ.put(f'수신시간과 갱신시간의 차이는 [{gap}]초입니다.')

    def PutTickData(self):
        for code in list(self.dict_df.keys()):
            columns = ['현재가', '시가', '거래대금', '누적거래대금', '상승VID5가격',
                       '매도1잔량', '매도2잔량', '매수1잔량', '매수2잔량', '매도1호가', '매도2호가', '매수1호가', '매수2호가']
            self.dict_df[code][columns] = self.dict_df[code][columns].astype(int)
        self.queryQ.put(self.dict_df)

    """
    전략 테스트 프로그램이 거래한 종목만 저장
    def PutTickData(self, cmd, codes):
        if cmd != '틱데이터저장':
            return
        for code in list(self.dict_df.keys()):
            if code in codes:
                columns = ['현재가', '시가', '거래대금', '누적거래대금', '상승VID5가격',
                           '매도1잔량', '매도2잔량', '매수1잔량', '매수2잔량', '매도1호가', '매도2호가', '매수1호가', '매수2호가']
                self.dict_df[code][columns] = self.dict_df[code][columns].astype(int)
            else:
                del self.dict_df[code]
        self.queryQ.put(self.dict_df)
    """
