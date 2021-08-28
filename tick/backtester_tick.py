import os
import sys
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.setting import db_backtest, db_tick, db_stg, system_path
from utility.static import now, strf_time, telegram_msg, timedelta_sec, strp_time, timedelta_day


class BackTesterTick:
    def __init__(self, q_, code_list_, df_mt_, num_, high):
        self.q = q_
        self.code_list = code_list_
        self.df_mt = df_mt_
        self.high = high

        self.gap_ch = num_[0][0]
        self.gap_sm = num_[1][0]
        self.avgtime = num_[2][0]
        self.selltime = num_[3][0]
        self.chlow = num_[4][0]
        self.vplow = num_[5][0]
        self.dmlow = num_[6][0]
        self.phigh = num_[7][0]
        self.hlmplow = num_[8][0]

        self.batting = 5000000

        self.code = None
        self.df = None

        self.totalcount = 0
        self.totalcount_p = 0
        self.totalcount_m = 0
        self.totaleyun = 0
        self.totalper = 0.

        self.hold = False
        self.buycount = 0
        self.buyprice = 0
        self.sellprice = 0
        self.index = 0
        self.indexb = 0

        self.indexn = 0
        self.ccond = 0
        self.csell = 0

        self.Start()

    def Start(self):
        conn = sqlite3.connect(db_tick)
        tcount = len(self.code_list)
        int_daylimit = int(strf_time('%Y%m%d', timedelta_day(-30)))
        for k, code in enumerate(self.code_list):
            self.code = code
            self.df = pd.read_sql(f"SELECT * FROM '{code}'", conn)
            self.df = self.df.set_index('index')
            self.df['직전거래대금'] = self.df['거래대금'].shift(1)
            self.df['직전체결강도'] = self.df['체결강도'].shift(1)
            self.df['거래대금평균'] = self.df['직전거래대금'].rolling(window=self.avgtime).mean()
            self.df['체결강도평균'] = self.df['직전체결강도'].rolling(window=self.avgtime).mean()
            self.df['최고체결강도'] = self.df['직전체결강도'].rolling(window=self.avgtime).max()
            self.df = self.df.fillna(0)
            self.totalcount = 0
            self.totalcount_p = 0
            self.totalcount_m = 0
            self.totaleyun = 0
            self.totalper = 0.
            self.ccond = 0
            lasth = len(self.df) - 1
            for h, index in enumerate(self.df.index):
                if int(index[:8]) < int_daylimit:
                    continue
                self.index = index
                self.indexn = h
                if not self.hold and self.BuyTerm():
                    self.Buy()
                elif self.hold and self.SellTerm():
                    self.Sell()
                if self.hold and (h == lasth or index[:8] != self.df.index[h + 1][:8]):
                    self.Sell()
                if h != lasth and index[:8] != self.df.index[h + 1][:8]:
                    self.ccond = 0
            self.Report(k + 1, tcount)
        conn.close()

    def BuyTerm(self):
        if self.code not in self.df_mt['거래대금상위100'][self.index]:
            self.ccond = 0
        else:
            self.ccond += 1
        if self.ccond < self.avgtime:
            return False
        # 전략 비공개
        return True

    def Buy(self):
        if self.df['매도1호가'][self.index] * self.df['매도1잔량'][self.index] >= self.batting:
            s1hg = self.df['매도1호가'][self.index]
            self.buycount = int(self.batting / s1hg)
            self.buyprice = s1hg
        else:
            s1hg = self.df['매도1호가'][self.index]
            s1jr = self.df['매도1잔량'][self.index]
            s2hg = self.df['매도2호가'][self.index]
            ng = self.batting - s1hg * s1jr
            s2jc = int(ng / s2hg)
            self.buycount = s1jr + s2jc
            self.buyprice = round((s1hg * s1jr + s2hg * s2jc) / self.buycount, 2)
        self.hold = True
        self.indexb = self.indexn
        self.csell = 0

    def SellTerm(self):
        if self.df['등락율'][self.index] > 29:
            return True
        # 전략 비공개
        return False

    def Sell(self):
        if self.df['매수1잔량'][self.index] >= self.buycount:
            self.sellprice = self.df['매수1호가'][self.index]
        else:
            b1hg = self.df['매수1호가'][self.index]
            b1jr = self.df['매수1잔량'][self.index]
            b2hg = self.df['매수2호가'][self.index]
            nc = self.buycount - b1jr
            self.sellprice = round((b1hg * b1jr + b2hg * nc) / self.buycount, 2)
        self.hold = False
        self.indexb = 0
        self.CalculationEyun()

    def CalculationEyun(self):
        self.totalcount += 1
        bg = self.buycount * self.buyprice
        cg = self.buycount * self.sellprice
        eyun, per = self.GetEyunPer(bg, cg)
        self.totalper = round(self.totalper + per, 2)
        self.totaleyun = int(self.totaleyun + eyun)
        if per > 0:
            self.totalcount_p += 1
        else:
            self.totalcount_m += 1
        if self.high:
            self.q.put([self.index, eyun])

    # noinspection PyMethodMayBeStatic
    def GetEyunPer(self, bg, cg):
        gtexs = cg * 0.0023
        gsfee = cg * 0.00015
        gbfee = bg * 0.00015
        texs = gtexs - (gtexs % 1)
        sfee = gsfee - (gsfee % 10)
        bfee = gbfee - (gbfee % 10)
        pg = int(cg - texs - sfee - bfee)
        eyun = pg - bg
        per = round(eyun / bg * 100, 2)
        return eyun, per

    def Report(self, count, tcount):
        plus_per = 0.
        if self.totalcount > 0:
            plus_per = round((self.totalcount_p / self.totalcount) * 100, 2)
            self.q.put([self.code, self.totalcount, self.totalcount_p, self.totalcount_m,
                        plus_per, self.totalper, self.totaleyun])
        else:
            self.q.put([self.code, 0, 0, 0, 0., 0., 0])
        totalcount, totalcount_p, totalcount_m, plus_per, totalper, totaleyun = self.GetTotal(plus_per)
        print(f" 종목코드 {self.code} | 거래횟수 {totalcount}회 | 익절 {totalcount_p}회 |"
              f" 손절 {totalcount_m}회 | 승률 {plus_per}% | 수익률 {totalper}% |"
              f" 수익금 {totaleyun}원 [{count}/{tcount}]")

    def GetTotal(self, plus_per):
        totalcount = str(self.totalcount)
        totalcount = '  ' + totalcount if len(totalcount) == 1 else totalcount
        totalcount = ' ' + totalcount if len(totalcount) == 2 else totalcount
        totalcount_p = str(self.totalcount_p)
        totalcount_p = '  ' + totalcount_p if len(totalcount_p) == 1 else totalcount_p
        totalcount_p = ' ' + totalcount_p if len(totalcount_p) == 2 else totalcount_p
        totalcount_m = str(self.totalcount_m)
        totalcount_m = '  ' + totalcount_m if len(totalcount_m) == 1 else totalcount_m
        totalcount_m = ' ' + totalcount_m if len(totalcount_m) == 2 else totalcount_m
        plus_per = str(plus_per)
        plus_per = '  ' + plus_per if len(plus_per.split('.')[0]) == 1 else plus_per
        plus_per = ' ' + plus_per if len(plus_per.split('.')[0]) == 2 else plus_per
        plus_per = plus_per + '0' if len(plus_per.split('.')[1]) == 1 else plus_per
        totalper = str(self.totalper)
        totalper = '   ' + totalper if len(totalper.split('.')[0]) == 1 else totalper
        totalper = '  ' + totalper if len(totalper.split('.')[0]) == 2 else totalper
        totalper = ' ' + totalper if len(totalper.split('.')[0]) == 3 else totalper
        totalper = totalper + '0' if len(totalper.split('.')[1]) == 1 else totalper
        totaleyun = format(self.totaleyun, ',')
        if len(totaleyun.split(',')) == 1:
            totaleyun = '         ' + totaleyun if len(totaleyun.split(',')[0]) == 1 else totaleyun
            totaleyun = '        ' + totaleyun if len(totaleyun.split(',')[0]) == 2 else totaleyun
            totaleyun = '       ' + totaleyun if len(totaleyun.split(',')[0]) == 3 else totaleyun
            totaleyun = '      ' + totaleyun if len(totaleyun.split(',')[0]) == 4 else totaleyun
        elif len(totaleyun.split(',')) == 2:
            totaleyun = '     ' + totaleyun if len(totaleyun.split(',')[0]) == 1 else totaleyun
            totaleyun = '    ' + totaleyun if len(totaleyun.split(',')[0]) == 2 else totaleyun
            totaleyun = '   ' + totaleyun if len(totaleyun.split(',')[0]) == 3 else totaleyun
            totaleyun = '  ' + totaleyun if len(totaleyun.split(',')[0]) == 4 else totaleyun
        elif len(totaleyun.split(',')) == 3:
            totaleyun = ' ' + totaleyun if len(totaleyun.split(',')[0]) == 1 else totaleyun
        return totalcount, totalcount_p, totalcount_m, plus_per, totalper, totaleyun


class Total:
    def __init__(self, q_, last_, num_):
        super().__init__()
        self.q = q_
        self.last = last_

        self.gap_ch = num_[0][0]
        self.gap_sm = num_[1][0]
        self.avgtime = num_[2][0]
        self.selltime = num_[3][0]
        self.chlow = num_[4][0]
        self.vplow = num_[5][0]
        self.dmlow = num_[6][0]
        self.phigh = num_[7][0]
        self.hlmplow = num_[8][0]

        self.Start()

    def Start(self):
        columns1 = ['거래횟수', '익절', '손절', '승률', '수익률', '수익금']
        columns2 = ['거래횟수', '익절', '손절', '승률', '수익률합계', '수익금합계',
                    '체결강도차이', '거래대금차이', '평균시간', '청산시간', '체결강도하한',
                    '전일거래량대비하한', '누적거래대금하한', '등락율상한', '고저평균대비등락율하한']
        df_back = pd.DataFrame(columns=columns1)
        df_tsg = pd.DataFrame(columns=['ttsg'])
        k = 0
        while True:
            data = self.q.get()
            if len(data) == 2:
                if data[0] in df_tsg.index:
                    df_tsg.at[data[0]] = df_tsg['ttsg'][data[0]] + data[1]
                else:
                    df_tsg.at[data[0]] = data[1]
            else:
                df_back.at[data[0]] = data[1], data[2], data[3], data[4], data[5], data[6]
                k += 1
            if k == self.last:
                break

        tsg = 0
        if len(df_back) > 0:
            tc = sum(df_back['거래횟수'])
            if tc != 0:
                pc = sum(df_back['익절'])
                mc = sum(df_back['손절'])
                pper = round(pc / tc * 100, 2)
                tsp = round(sum(df_back['수익률']), 2)
                tsg = int(sum(df_back['수익금']))
                text = f" 수익금합계 {format(tsg, ',')}원 [{self.gap_ch}, {self.gap_sm}, {self.avgtime}, " \
                       f"{self.selltime}, {self.chlow}, {self.vplow}, {self.dmlow}, {self.phigh}, {self.hlmplow}]"
                print(text)
                df_back = pd.DataFrame(
                    [[tc, pc, mc, pper, tsp, tsg, self.gap_ch, self.gap_sm, self.avgtime, self.selltime,
                      self.chlow, self.vplow, self.dmlow, self.phigh, self.hlmplow]],
                    columns=columns2, index=[strf_time('%H%M%S')]
                )
                conn = sqlite3.connect(db_backtest)
                df_back.to_sql(f"{strf_time('%Y%m%d')}_tick", conn, if_exists='append', chunksize=1000)
                conn.close()

        if len(df_tsg) > 0:
            df_tsg['체결시간'] = df_tsg.index
            df_tsg.sort_values(by=['체결시간'], inplace=True)
            df_tsg['ttsg_cumsum'] = df_tsg['ttsg'].cumsum()
            title = f'[{self.gap_ch} {self.gap_sm} {self.avgtime} {self.selltime} {self.chlow} ' \
                    f'{self.vplow} {self.dmlow} {self.phigh} {self.hlmplow}]'
            df_tsg.plot(title=title, figsize=(12, 9), rot=45)
            plt.savefig(f"{system_path}/tick/graph/{strf_time('%Y%m%d')}.png")

            conn = sqlite3.connect(db_stg)
            cur = conn.cursor()
            query = f"UPDATE setting SET 체결강도차이 = {self.gap_ch}, 거래대금차이 = {self.gap_sm}, "\
                    f"평균시간 = {self.avgtime}, 청산시간 = {self.selltime}, 체결강도하한 = {self.chlow}, "\
                    f"전일거래량대비하한 = {self.vplow}, 누적거래대금하한 = {self.dmlow}, 등락율상한 = {self.phigh}, "\
                    f"고저평균대비등락율하한 = {self.hlmplow}"
            cur.execute(query)
            conn.commit()
            conn.close()
        else:
            self.q.put(tsg)


if __name__ == "__main__":
    start = now()

    gap_ch = [2, 10, 1, 0.1]
    gap_sm = [50, 150, 10, 1]
    avgtime = [30, 300, 30, 10]
    selltime = [1, 5, 1, 1]
    chlow = [50, 150, 10, 1]
    vplow = [0, 100, 10, 1]
    dmlow = [0, 10000, 1000, 100]
    phigh = [25., 15., -1, -1]
    hlmplow = [0., 5., 1, 0.1]
    num = [gap_ch, gap_sm, avgtime, selltime, chlow, vplow, dmlow, phigh, hlmplow]

    con = sqlite3.connect(db_tick)
    df = pd.read_sql("SELECT name FROM sqlite_master WHERE TYPE = 'table'", con)
    df_mt = pd.read_sql('SELECT * FROM moneytop', con)
    con.close()
    df_mt = df_mt.set_index('index')
    table_list = list(df['name'].values)
    table_list.remove('moneytop')
    last = len(table_list)

    q = Queue()
    ttsg = -100000000
    high_var = num[0][0]
    ogin_var = num[0][0]

    i = 0
    while True:
        w = Process(target=Total, args=(q, last, num))
        w.start()
        procs = []
        workcount = int(last / 6) + 1
        for j in range(0, last, workcount):
            code_list = table_list[j:j + workcount]
            p = Process(target=BackTesterTick, args=(q, code_list, df_mt, num, False))
            procs.append(p)
            p.start()
        for p in procs:
            p.join()
        w.join()
        sg = q.get()
        if sg > ttsg:
            ttsg = sg
            high_var = num[i][0]
        if num[i][0] == num[i][1]:
            if num[i][2] != num[i][3]:
                num[i][0] = high_var
                if num[i][0] != ogin_var:
                    num[i][0] -= num[i][2]
                    num[i][1] = round(num[i][0] + num[i][2] * 2 - num[i][3], 1)
                else:
                    num[i][1] = round(num[i][0] + num[i][2] - num[i][3], 1)
                num[i][2] = num[i][3]
            else:
                num[i][0] = high_var
                if i < len(num) - 1:
                    i += 1
                    high_var = num[i][0]
                    ogin_var = num[i][0]
                else:
                    break
        num[i][0] = round(num[i][0] + num[i][2], 1)

    w = Process(target=Total, args=(q, last, num))
    w.start()
    procs = []
    workcount = int(last / 6) + 1
    for j in range(0, last, workcount):
        db_list = table_list[j:j + workcount]
        p = Process(target=BackTesterTick, args=(q, db_list, df_mt, num, True))
        procs.append(p)
        p.start()
    for p in procs:
        p.join()
    w.join()

    end = now()
    print(f" 백테스팅 소요시간 {end - start}")
    telegram_msg('백테스트을 완료하였습니다.')
