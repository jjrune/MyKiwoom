import os
import sys
import sqlite3
import pandas as pd
from matplotlib import pyplot as plt
from multiprocessing import Process, Queue
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.setting import db_tick, db_backtest
from utility.static import now, timedelta_sec, strp_time, strf_time, timedelta_day


class BackTesterTickm:
    def __init__(self, q_, code_list_, df_mt_, num_):
        self.q = q_
        self.code_list = code_list_
        self.df_mt = df_mt_

        self.gap_ch = num_[0]
        self.gap_sm = num_[1]
        self.avgtime = num_[2]
        self.selltime = num_[3]
        self.chlow = num_[4]
        self.vplow = num_[5]
        self.dmlow = num_[6]
        self.phigh = num_[7]
        self.hlmplow = num_[8]

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

        self.gap_ch = num_[0]
        self.gap_sm = num_[1]
        self.avgtime = num_[2]
        self.selltime = num_[3]
        self.chlow = num_[4]
        self.vplow = num_[5]
        self.dmlow = num_[6]
        self.phigh = num_[7]
        self.hlmplow = num_[8]

        self.Start()

    def Start(self):
        columns = ['거래횟수', '익절', '손절', '승률', '수익률', '수익금']
        df_back = pd.DataFrame(columns=columns)
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

        if len(df_back) > 0:
            tc = sum(df_back['거래횟수'])
            if tc != 0:
                pc = sum(df_back['익절'])
                mc = sum(df_back['손절'])
                pper = round(pc / tc * 100, 2)
                tsp = round(sum(df_back['수익률']), 2)
                tsg = int(sum(df_back['수익금']))
                text = f" 거래횟수 {tc}회, 익절 {pc}회, 손절 {mc}회, 승률 {pper}%, 수익률 {tsp}%,"\
                       f" 수익금합계 {format(tsg, ',')}원 [{self.gap_ch}, {self.gap_sm}, {self.avgtime},"\
                       f" {self.selltime}, {self.chlow}, {self.vplow}, {self.dmlow}, {self.phigh}, {self.hlmplow}]"
                print(text)
                conn = sqlite3.connect(db_backtest)
                df_back.to_sql(f"{strf_time('%Y%m%d')}_tickm", conn, if_exists='replace', chunksize=1000)
                conn.close()

        if len(df_tsg) > 0:
            df_tsg['일자'] = df_tsg.index
            df_tsg.sort_values(by=['일자'], inplace=True)
            df_tsg['ttsg_cumsum'] = df_tsg['ttsg'].cumsum()
            df_tsg.plot(figsize=(12, 9), rot=45)
            plt.show()


if __name__ == "__main__":
    start = now()

    gap_ch = 10
    gap_sm = 0
    avgtime = 300
    selltime = 5
    chlow = 0
    vplow = 0
    dmlow = 0
    phigh = 25.
    hlmplow = 0.
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

    w = Process(target=Total, args=(q, last, num))
    w.start()
    procs = []
    workcount = int(last / 6) + 1
    for j in range(0, last, workcount):
        code_list = table_list[j:j + workcount]
        p = Process(target=BackTesterTickm, args=(q, code_list, df_mt, num))
        procs.append(p)
        p.start()
    for p in procs:
        p.join()
    w.join()

    end = now()
    print(f" 백테스팅 소요시간 {end - start}")
