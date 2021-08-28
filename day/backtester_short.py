import os
import sys
import sqlite3
import pandas as pd
from multiprocessing import Process, Queue
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.static import now
from utility.setting import db_day, db_stg


class BackTesterShort:
    def __init__(self, q_, code_list_):
        self.q = q_
        self.code_list = code_list_

        self.batting = 1000000
        self.code = None
        self.df = None

        self.totalcount = 0
        self.totalcount_p = 0
        self.totalcount_m = 0
        self.totalholdday = 0
        self.totaleyun = 0
        self.totalper = 0.

        self.hold = False
        self.buycount = 0
        self.buyprice = 0
        self.sellprice = 0
        self.index = 0
        self.indexb = 0
        self.indexn = 0

        self.Start()

    def Start(self):
        conn = sqlite3.connect(db_day)
        tcount = len(self.code_list)
        for k, code in enumerate(self.code_list):
            self.code = code
            self.df = pd.read_sql(f"SELECT * FROM '{code}'", conn)
            self.df = self.df.set_index('일자')
            self.totalcount = 0
            self.totalholdday = 0
            self.totalcount_p = 0
            self.totalcount_m = 0
            self.totaleyun = 0
            self.totalper = 0.
            lasth = len(self.df) - 1
            for h, index in enumerate(self.df.index):
                if h < 2:
                    continue
                self.index = index
                self.indexn = h
                if not self.hold and self.BuyTerm():
                    self.Buy()
                elif self.hold and self.SellTerm():
                    self.Sell()
                if self.hold and h == lasth:
                    self.Sell()
            self.Report(k + 1, tcount)
        conn.close()

    def BuyTerm(self):
        # 전략 비공개
        return False

    def Buy(self):
        self.buycount = int(self.batting / self.df['현재가'][self.index])
        if self.buycount == 0:
            return
        self.buyprice = self.df['현재가'][self.index]
        self.indexb = self.indexn
        self.hold = True

    def SellTerm(self):
        # 전략 비공개
        return False

    def Sell(self):
        self.hold = False
        self.CalculationEyun()

    def CalculationEyun(self):
        self.totalcount += 1
        bg = self.buycount * self.buyprice
        cg = self.buycount * self.sellprice
        eyun, per = self.GetEyunPer(bg, cg)
        holdday = self.indexn - self.indexb
        self.totalper = round(self.totalper + per, 2)
        self.totaleyun = int(self.totaleyun + eyun)
        self.totalholdday += holdday
        if per > 0:
            self.totalcount_p += 1
        else:
            self.totalcount_m += 1

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
        if self.totalcount > 0:
            plus_per = round((self.totalcount_p / self.totalcount) * 100, 2)
            avgholdday = int(self.totalholdday / self.totalcount)
            self.q.put([self.code, self.totalcount, avgholdday, self.totalcount_p, self.totalcount_m,
                        plus_per, self.totalper, self.totaleyun])
            totalcount, avgholdday, totalcount_p, totalcount_m, plus_per, totalper, totaleyun = \
                self.GetTotal(plus_per, avgholdday)
            print(f" 종목코드 {self.code} | 평균보유기간 {avgholdday}일 | 거래횟수 {totalcount}회 | "
                  f" 익절 {totalcount_p}회 | 손절 {totalcount_m}회 | 승률 {plus_per}% |"
                  f" 수익률 {totalper}% | 수익금 {totaleyun}원 [{count}/{tcount}]")
        else:
            self.q.put([self.code, 0, 0, 0, 0, 0., 0., 0])

    def GetTotal(self, plus_per, avgholdday):
        totalcount = str(self.totalcount)
        totalcount = '  ' + totalcount if len(totalcount) == 1 else totalcount
        totalcount = ' ' + totalcount if len(totalcount) == 2 else totalcount
        avgholdday = str(avgholdday)
        avgholdday = '   ' + avgholdday if len(avgholdday) == 1 else avgholdday
        avgholdday = '  ' + avgholdday if len(avgholdday) == 2 else avgholdday
        avgholdday = ' ' + avgholdday if len(avgholdday) == 3 else avgholdday
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
        return totalcount, avgholdday, totalcount_p, totalcount_m, plus_per, totalper, totaleyun


class Total:
    def __init__(self, q_, last_):
        super().__init__()
        self.q = q_
        self.last = last_
        self.Start()

    def Start(self):
        columns = ['거래횟수', '평균보유기간', '익절', '손절', '승률', '수익률', '수익금']
        df_back = pd.DataFrame(columns=columns)
        k = 0
        while True:
            data = self.q.get()
            df_back.at[data[0]] = data[1], data[2], data[3], data[4], data[5], data[6], data[7]
            k += 1
            if k == self.last:
                break

        if len(df_back) > 0:
            tc = df_back['거래횟수'].sum()
            if tc != 0:
                avghold = int(df_back['평균보유기간'].sum() / len(df_back))
                pc = df_back['익절'].sum()
                mc = df_back['손절'].sum()
                pper = round(pc / tc * 100, 2)
                avgsp = round(df_back['수익률'].mean(), 2)
                avgtc = round(df_back['거래횟수'].mean(), 2)
                avgsg = round(df_back['수익금'].mean(), 2)
                tsg = int(df_back['수익금'].sum())
                text = f" 거래횟수 {tc}회, 평균보유기간 {avghold}일, 익절 {pc}회, 손절 {mc}회, 승률 {pper}%,"\
                       f" 평균수익률 {avgsp}%, 수익금합계 {format(tsg, ',')}원"
                print(text)
                df_back = df_back[(df_back['거래횟수'] > avgtc) & (df_back['승률'] > pper) & (df_back['수익금'] > avgsg) &
                                  (df_back['수익률'] > avgsp) & (df_back['평균보유기간'] < avghold)]
                conn = sqlite3.connect(db_stg)
                df_long = pd.read_sql('SELECT * FROM long', conn)
                df_long = df_long.set_index('index')
                longandmidcodes = list(df_long.index)
                df_mid = pd.read_sql('SELECT * FROM mid', conn)
                df_mid = df_mid.set_index('index')
                longandmidcodes += list(df_mid.index)
                for code in df_back.index:
                    if code in longandmidcodes:
                        df_back.drop(index=code, inplace=True)
                ttsg = df_back['수익금'].sum()
                df_back['비중'] = df_back['수익금'].apply(lambda x: round(x / ttsg, 4))
                df_back.to_sql('short', conn, if_exists='replace', chunksize=1000)
                conn.close()


if __name__ == "__main__":
    start = now()

    con = sqlite3.connect(db_day)
    df = pd.read_sql("SELECT name FROM sqlite_master WHERE TYPE = 'table'", con)
    con.close()
    table_list = list(df['name'].values)
    last = len(table_list)

    q = Queue()

    w = Process(target=Total, args=(q, last))
    w.start()
    procs = []
    workcount = int(last / 6) + 1
    for j in range(0, last, workcount):
        code_list = table_list[j:j + workcount]
        p = Process(target=BackTesterShort, args=(q, code_list))
        procs.append(p)
        p.start()
    for p in procs:
        p.join()
    w.join()

    end = now()
    print(f" 백테스팅 소요시간 {end - start}")
