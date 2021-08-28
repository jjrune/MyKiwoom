import os
import sys
import sqlite3
import requests
import pandas as pd
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.setting import *
from utility.static import now, timedelta_sec, strf_time, strp_time


class UpdaterChart:
    def __init__(self, qlist, gubun):
        self.gubun = gubun
        self.windowQ = qlist[0]
        self.workerQ = qlist[1]
        if self.gubun == ui_num['차트P1']:
            self.chartQ = qlist[11]
        elif self.gubun == ui_num['차트P2']:
            self.chartQ = qlist[12]
        elif self.gubun == ui_num['차트P3']:
            self.chartQ = qlist[13]
        elif self.gubun == ui_num['차트P4']:
            self.chartQ = qlist[14]
        elif self.gubun == ui_num['차트P5']:
            self.chartQ = qlist[15]
        elif self.gubun == ui_num['차트P6']:
            self.chartQ = qlist[16]
        elif self.gubun == ui_num['차트P7']:
            self.chartQ = qlist[17]
        elif self.gubun == ui_num['차트P8']:
            self.chartQ = qlist[18]
        elif self.gubun == ui_num['차트P9']:
            self.chartQ = qlist[19]
        self.df_ct = None
        self.df_ch = None
        self.bool_ctup = False
        self.str_ccode = str
        self.dict_name = {}
        self.time_ctup = now()
        self.Start()

    def Start(self):
        while True:
            chart = self.chartQ.get()
            if type(chart) == dict:
                self.dict_name = chart
            elif type(chart) == str:
                self.WebCrawling(chart.split(' ')[0], chart.split(' ')[1])
            elif type(chart) == list:
                if len(chart) == 4:
                    self.UpdateJongmokChart(chart[0], chart[1], chart[2], chart[3])
                elif len(chart) == 3:
                    if type(chart[2]) == pd.DataFrame:
                        self.UpdateTujajaChegeolH(chart[0], chart[1], chart[2])
                    elif type(chart[2]) == int:
                        self.UpdateRealChart(chart[0], chart[1], chart[2])
                elif len(chart) == 5:
                    self.UpdateRealChegeolH(chart[0], chart[1], chart[2], chart[3], chart[4])

            if now() > self.time_ctup:
                if self.bool_ctup:
                    self.windowQ.put([self.gubun, self.df_ct])
                    self.bool_ctup = False
                self.time_ctup = timedelta_sec(1)

    def WebCrawling(self, cmd, code):
        if cmd == '기업개요':
            url = f'https://finance.naver.com/item/coinfo.nhn?code={code}'
            source = requests.get(url).text
            html = BeautifulSoup(source, 'lxml')
            html.select('.summary_info')
            gugy_result = ''
            titles = html.select('.summary_info')
            for title in titles:
                title = title.get_text().replace('\n', '')
                if title != '':
                    gugy_result += title
            gugy_result = gugy_result.strip('기업개요').replace('.', '. ').split('출처')[0]
            self.windowQ.put([0, gugy_result])
        elif cmd == '기업공시':
            date_result = []
            jbjg_result = []
            gygs_result = []
            for i in [1, 2, 3]:
                url = f'https://finance.naver.com/item/news_notice.nhn?code={code}&page={i}'
                source = requests.get(url).text
                html = BeautifulSoup(source, 'lxml')
                dates = html.select('.date')
                if len(dates) != 0:
                    date_result += [date.get_text() for date in dates]
                    infos = html.select('.info')
                    jbjg_result += [info.get_text() for info in infos]
                    titles = html.select('.title')
                    for title in titles:
                        title = title.get_text().replace('\n', '').replace('\xa0', '')
                        if title != '':
                            gygs_result.append(title)
            df = pd.DataFrame({'일자': date_result, '정보제공': jbjg_result, '공시': gygs_result})
            self.windowQ.put([ui_num['기업공시'], df])
        elif cmd == '종목뉴스':
            date_result = []
            title_result = []
            ulsa_result = []
            for i in [1, 2]:
                url = f'https://finance.naver.com/item/news_news.nhn?code={code}&page={i}'
                source = requests.get(url).text
                html = BeautifulSoup(source, 'lxml')
                dates = html.select('.date')
                if len(dates) != 0:
                    date_result += [date.get_text() for date in dates]
                    infos = html.select('.info')
                    ulsa_result += [info.get_text() for info in infos]
                    titles = html.select('.title')
                    for title in titles:
                        title = title.get_text().replace('\n', '')
                        if title != '':
                            title_result.append(title)
            df = pd.DataFrame({'일자': date_result, '언론사': ulsa_result, '제목': title_result})
            self.windowQ.put([ui_num['기업뉴스'], df])
        elif cmd == '재무제표':
            url = f'https://finance.naver.com/item/main.nhn?code={code}'
            source = requests.get(url)
            soup = BeautifulSoup(source.content, 'html.parser')
            html = soup.select('div.section.cop_analysis div.sub_section')[0]
            text_list = [item.get_text().strip() for item in html.select('th')]
            num_list = [item.get_text().strip() for item in html.select('td')]
            num_list = num_list[:130]
            columns1 = ['구분'] + text_list[3:7]
            columns2 = text_list[7:13]
            data1 = []
            data2 = []
            data1.append(text_list[-16:-3])
            data1.append([num for j, num in enumerate(num_list) if j % 10 == 0])
            data1.append([num for j, num in enumerate(num_list) if j % 10 == 1])
            data1.append([num for j, num in enumerate(num_list) if j % 10 == 2])
            data1.append([num for j, num in enumerate(num_list) if j % 10 == 4])
            data2.append([num for j, num in enumerate(num_list) if j % 10 == 5])
            data2.append([num for j, num in enumerate(num_list) if j % 10 == 6])
            data2.append([num for j, num in enumerate(num_list) if j % 10 == 7])
            data2.append([num for j, num in enumerate(num_list) if j % 10 == 8])
            data2.append([num for j, num in enumerate(num_list) if j % 10 == 9])
            df1 = pd.DataFrame(data=dict(zip(columns1, data1)))
            df2 = pd.DataFrame(data=dict(zip(columns2, data2)))

            try:
                html = soup.select('div.section.trade_compare')[0]
            except IndexError:
                df3 = pd.DataFrame(columns=columns_jb)
            else:
                text_list = [item.get_text().strip() for item in html.select('th')]
                num_list = [item.get_text().strip() for item in html.select('td')]
                columns = text_list[1:6]
                ccount = 0
                for i, column in enumerate(columns):
                    try:
                        columns[i] = self.dict_name[column[-6:]]
                    except KeyError:
                        del columns[i]
                    else:
                        ccount += 1
                if ccount == 5:
                    columns = ['구분'] + columns
                else:
                    columns = ['구분'] + columns + ['']
                for i, num in enumerate(num_list):
                    num = num.strip('상향\n\t\t\t\t').strip('하향\n\t\t\t\t').strip('보합')
                    num_list[i] = num
                data3 = {}
                k = 0
                for i, column in enumerate(columns):
                    if column == '구분':
                        data3[column] = text_list[ccount + 1:]
                    elif column == '':
                        data3[column] = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']
                    else:
                        data3[column] = [num for j, num in enumerate(num_list) if j % ccount == k]
                        k += 1
                df3 = pd.DataFrame(data=data3)

            self.windowQ.put([ui_num['재무년도'], df1])
            self.windowQ.put([ui_num['재무분기'], df2])
            self.windowQ.put([ui_num['동업종비교'], df3])

    def UpdateJongmokChart(self, name, prec, df, tradeday):
        df = df[::-1]
        if self.gubun in [ui_num['차트P1'], ui_num['차트P2'], ui_num['차트P3'], ui_num['차트P4'], ui_num['차트P5']]:
            df[['현재가', '시가', '고가', '저가', '거래량']] = df[['현재가', '시가', '고가', '저가', '거래량']].astype(int).abs()
        elif self.gubun in [ui_num['차트P6'], ui_num['차트P7'], ui_num['차트P8'], ui_num['차트P9']]:
            df[['현재가', '시가', '고가', '저가', '거래량']] = df[['현재가', '시가', '고가', '저가', '거래량']].astype(int).abs()
            df['현재가'] = df['현재가'].apply(lambda x: round(x / 100, 2))
            df['시가'] = df['시가'].apply(lambda x: round(x / 100, 2))
            df['고가'] = df['고가'].apply(lambda x: round(x / 100, 2))
            df['저가'] = df['저가'].apply(lambda x: round(x / 100, 2))

        if self.gubun in [ui_num['차트P6'], ui_num['차트P8']]:
            ema_columns = ['지수이평05', '지수이평20', '지수이평60']
        elif self.gubun in [ui_num['차트P1'], ui_num['차트P3']]:
            ema_columns = ['지수이평05', '지수이평20', '지수이평60', '지수이평120', '지수이평240', '지수이평480']
        else:
            ema_columns = ['지수이평05', '지수이평10', '지수이평20', '지수이평40', '지수이평60', '지수이평120']

        for ema_column in ema_columns:
            df[ema_column] = df['현재가'].ewm(span=int(ema_column[4:]), adjust=False).mean().round(2)

        if self.gubun in [ui_num['차트P1'], ui_num['차트P3'], ui_num['차트P6'], ui_num['차트P8']]:
            df['일자'] = df['일자'].apply(lambda x: x[4:6] + '-' + x[6:])
            df = df.set_index('일자')
            if len(df) > 120:
                pema1 = df['지수이평05'][-121]
                pema2 = df['지수이평20'][-121]
                pema3 = df['지수이평60'][-121]
                df = df[-120:]
            else:
                pema1, pema2, pema3 = 0., 0., 0.
        else:
            if self.gubun == ui_num['차트P5']:
                pema1, pema2, pema3 = 0., 0., 0.
                df['day'] = df['체결시간'].apply(lambda x: int(x[:8]))
                df['time'] = df['체결시간'].apply(lambda x: int(x[8:]))
                cond = (df['day'] < int(tradeday)) & (df['time'] != '153300')
                df2 = df[cond]
                prec = df2['현재가'][df2.index[-1]]
                cond = (df['day'] == int(tradeday)) & (df['time'] != 153300)
                if len(df[cond]) > 0:
                    df = df[cond]
                else:
                    df = df[df['day'] == df['day'][df.index[-1]]]
            else:
                if len(df) > 130:
                    df = df[-130:]
                df['day'] = df['체결시간'].apply(lambda x: int(x[:8]))
                df['time'] = df['체결시간'].apply(lambda x: int(x[8:]))
                lastday = df['day'][df.index[-1]]
                df2 = df[df['day'] != lastday]
                preday = df2['day'][df2.index[-1]]
                pema1 = df2['지수이평05'][df2.index[-1]]
                pema2 = df2['지수이평10'][df2.index[-1]]
                pema3 = df2['지수이평20'][df2.index[-1]]
                lasttime = df['time'][df.index[-1]]
                cond = (df['day'] == lastday) | \
                       ((df['day'] == preday) & (df['time'] > lasttime) & (df['time'] != 153300))
                df = df[cond]

            df['체결시간'] = df['체결시간'].apply(lambda x: x[8:10] + ':' + x[10:12])
            df = df.set_index('체결시간')

        df['전일종가'] = prec
        df['종목명'] = name

        df['시종차'] = df['현재가'] - df['시가']
        if self.gubun in [ui_num['차트P2'], ui_num['차트P4'], ui_num['차트P7'], ui_num['차트P9'], ui_num['차트P5']]:
            df['직전지수이평05'] = df['지수이평05'].shift(1)
            df['직전지수이평10'] = df['지수이평10'].shift(1)
            df['직전지수이평20'] = df['지수이평20'].shift(1)
            df.at[df.index[0], ['직전지수이평05', '직전지수이평10', '직전지수이평20']] = pema1, pema2, pema3
            df['추세'] = (df['지수이평05'] > df['직전지수이평05']) & (df['지수이평10'] > df['직전지수이평10']) & \
                       (df['지수이평20'] > df['직전지수이평20'])
        else:
            df['직전지수이평05'] = df['지수이평05'].shift(1)
            df['직전지수이평20'] = df['지수이평20'].shift(1)
            df['직전지수이평60'] = df['지수이평60'].shift(1)
            df.at[df.index[0], ['직전지수이평05', '지수이평20', '지수이평60']] = pema1, pema2, pema3
            df['추세'] = (df['지수이평05'] > df['직전지수이평05']) & (df['지수이평20'] > df['직전지수이평20']) & \
                       (df['지수이평60'] > df['직전지수이평60'])

        if tradeday != '':
            df['매수체결가'] = ''
            df['매도체결가'] = ''
            name = df['종목명'][0]
            con = sqlite3.connect(db_stg)
            df2 = pd.read_sql(f"SELECT * FROM chegeollist WHERE 종목명 = '{name}' and 체결시간 LIKE '{tradeday}%'", con)
            con.close()
            df2 = df2.set_index('index')
            df2['체결시간'] = df2['체결시간'].apply(lambda x: self.GetStrTime3Minute(x[8:12]))
            try:
                df3 = df2[(df2['주문구분'] == '매수') & (df2['체결가'] != 0)]
                for i, index in enumerate(df3.index):
                    df_index = df3['체결시간'][index]
                    pre_bp = df['매수체결가'][df_index]
                    if pre_bp == '':
                        df.at[df_index, '매수체결가'] = str(df3['체결가'][i])
                    else:
                        df.at[df_index, '매수체결가'] = pre_bp + ';' + str(df3['체결가'][i])
                df3 = df2[(df2['주문구분'] == '매도') & (df2['체결가'] != 0)]
                for i, index in enumerate(df3.index):
                    df_index = df3['체결시간'][index]
                    pre_sp = df['매도체결가'][df_index]
                    if pre_sp == '':
                        df.at[df_index, '매도체결가'] = str(df3['체결가'][i])
                    else:
                        df.at[df_index, '매도체결가'] = pre_sp + ';' + str(df3['체결가'][i])
            except KeyError:
                self.windowQ.put([1, f'시스템 명령 오류 알림 - 차트에 체결시간의 캔들이 존재하지 않습니다.'])

        if tradeday != '':
            columns = ['현재가', '시가', '고가', '저가', '거래량'] + ema_columns + ['전일종가', '종목명', '시종차', '추세',
                                                                        '매수체결가', '매도체결가']
        else:
            columns = ['현재가', '시가', '고가', '저가', '거래량'] + ema_columns + ['전일종가', '종목명', '시종차', '추세']
        self.df_ct = df[columns].copy()
        self.windowQ.put([self.gubun, self.df_ct])

    def UpdateTujajaChegeolH(self, code, df1, df2):
        columns = ['일자', '현재가', '등락율', '누적거래대금', '개인투자자', '외국인투자자', '기관계']
        df1 = df1[columns].copy()
        columns = ['현재가', '누적거래대금', '개인투자자', '외국인투자자', '기관계']
        df1[columns] = df1[columns].astype(int)
        df1[['현재가']] = df1[['현재가']].abs()
        df1[['등락율']] = df1[['등락율']].astype(float).round(2)

        columns = ['체결시간', '현재가', '등락율', '체결강도', '체결강도5분', '체결강도20분', '체결강도60분']
        df2 = df2[columns].copy()
        df2[['현재가']] = df2[['현재가']].astype(int).abs()
        columns = ['등락율', '체결강도', '체결강도5분', '체결강도20분', '체결강도60분']
        df2[columns] = df2[columns].astype(float).round(2)
        self.df_ch = df2.set_index('체결시간')
        self.df_ch = self.df_ch[::-1]
        self.str_ccode = code

        self.windowQ.put([ui_num['투자자'], df1])
        self.windowQ.put([ui_num['체결강도'], df2])

    def UpdateRealChart(self, d, c, v):
        if self.df_ct is None:
            return
        if self.gubun in [ui_num['차트P1'], ui_num['차트P3'], ui_num['차트P6'], ui_num['차트P8']]:
            d = strf_time('%m-%d')
        else:
            d = self.GetStrTime3Minute(d)

        if d != self.df_ct.index[-1]:
            prec = self.df_ct['전일종가'][-1]
            name = self.df_ct['종목명'][-1]
            v = abs(v)
            if strp_time('%H:%M', self.df_ct.index[0]) <= strp_time('%H:%M', d):
                self.df_ct.drop(index=self.df_ct.index[0], inplace=True)
            ema05, ema10, ema20, ema40, ema60, ema120 = self.GetMinema(-1, c)
            chuse = ema05 > self.df_ct['지수이평05'][-1] and ema10 > self.df_ct['지수이평10'][-1] and \
                ema20 > self.df_ct['지수이평20'][-1]
            self.df_ct.at[d] = c, c, c, c, v, ema05, ema10, ema20, ema40, ema60, ema120, prec, name, 0, chuse
            self.bool_ctup = True
        else:
            v = self.df_ct['거래량'][-1] + abs(v)
            if c == self.df_ct['현재가'][-1]:
                self.df_ct.at[d, '거래량'] = v
            else:
                o = self.df_ct['시가'][-1]
                h = self.df_ct['고가'][-1]
                low = self.df_ct['저가'][-1]
                if c > h:
                    h = c
                if c < low:
                    low = c
                gap = c - o
                if self.gubun in [ui_num['차트P1'], ui_num['차트P3'], ui_num['차트P6'], ui_num['차트P8']]:
                    ema05, ema20, ema60, ema120, ema240, ema480 = self.GetDayema(-2, c)
                    chuse = ema05 > self.df_ct['지수이평05'][-2] and ema20 > self.df_ct['지수이평20'][-2] and \
                        ema60 > self.df_ct['지수이평60'][-2]
                    if self.gubun in [ui_num['차트P1'], ui_num['차트P3']]:
                        columns = ['현재가', '시가', '고가', '저가', '거래량', '지수이평05', '지수이평20', '지수이평60',
                                   '지수이평120', '지수이평240', '지수이평480', '시종차', '추세']
                        self.df_ct.at[d, columns] = \
                            c, o, h, low, v, ema05, ema20, ema60, ema120, ema240, ema480, gap, chuse
                    else:
                        columns = ['현재가', '시가', '고가', '저가', '거래량', '지수이평05', '지수이평20', '지수이평60',
                                   '시종차', '추세']
                        self.df_ct.at[d, columns] = c, o, h, low, v, ema05, ema20, ema60, gap, chuse
                    self.bool_ctup = True
                else:
                    ema05, ema10, ema20, ema40, ema60, ema120 = self.GetMinema(-2, c)
                    chuse = ema05 > self.df_ct['지수이평05'][-2] and ema10 > self.df_ct['지수이평10'][-2] and \
                        ema20 > self.df_ct['지수이평20'][-2]
                    columns = ['현재가', '시가', '고가', '저가', '거래량', '지수이평05', '지수이평10', '지수이평20',
                               '지수이평40', '지수이평60', '지수이평120', '시종차', '추세']
                    try:
                        self.df_ct.at[d, columns] = c, o, h, low, v, ema05, ema10, ema20, ema40, ema60, ema120, gap, chuse
                    except Exception as e:
                        self.windowQ.put([1, f'UpdateRealChart {e}'])
                    else:
                        self.bool_ctup = True

    def UpdateRealChegeolH(self, code, d, c, per, ch):
        if code == self.str_ccode:
            d = d[:4] + '00'
            if self.df_ch.index[-1] != d:
                ma05 = round((self.df_ch['체결강도'][-4:].sum() + ch) / 5, 2)
                ma20 = round((self.df_ch['체결강도'][-19:].sum() + ch) / 20, 2)
                ma60 = round((self.df_ch['체결강도'][-59:].sum() + ch) / 60, 2)
                self.df_ch.at[d] = c, per, ch, ma05, ma20, ma60
                df = self.df_ch.copy()
                df[['현재가']] = df[['현재가']].astype(int)
                df['체결시간'] = df.index
                columns = ['체결시간', '현재가', '등락율', '체결강도', '체결강도5분', '체결강도20분', '체결강도60분']
                df = df[columns].copy()
                df = df[::-1]
                self.windowQ.put([ui_num['체결강도'], df])

    def GetMinema(self, index, c):
        ema05 = round(self.df_ct['지수이평05'][index] * 4 / 6 + 2 / 6 * c, 2)
        ema10 = round(self.df_ct['지수이평10'][index] * 9 / 11 + 2 / 11 * c, 2)
        ema20 = round(self.df_ct['지수이평20'][index] * 19 / 21 + 2 / 21 * c, 2)
        ema40 = round(self.df_ct['지수이평40'][index] * 39 / 41 + 2 / 41 * c, 2)
        ema60 = round(self.df_ct['지수이평60'][index] * 59 / 61 + 2 / 61 * c, 2)
        ema120 = round(self.df_ct['지수이평120'][index] * 119 / 121 + 2 / 121 * c, 2)
        return ema05, ema10, ema20, ema40, ema60, ema120

    def GetDayema(self, index, c):
        ema05 = round(self.df_ct['지수이평05'][index] * 4 / 6 + 2 / 6 * c, 2)
        ema20 = round(self.df_ct['지수이평20'][index] * 19 / 21 + 2 / 21 * c, 2)
        ema60 = round(self.df_ct['지수이평60'][index] * 59 / 61 + 2 / 61 * c, 2)
        if self.gubun in [ui_num['차트P1'], ui_num['차트P3']]:
            ema120 = round(self.df_ct['지수이평120'][index] * 119 / 121 + 2 / 121 * c, 2)
            ema240 = round(self.df_ct['지수이평240'][index] * 239 / 241 + 2 / 241 * c, 2)
            ema480 = round(self.df_ct['지수이평480'][index] * 479 / 481 + 2 / 481 * c, 2)
        else:
            ema120 = 0
            ema240 = 0
            ema480 = 0
        return ema05, ema20, ema60, ema120, ema240, ema480

    # noinspection PyMethodMayBeStatic
    def GetStrTime3Minute(self, t):
        minute = str(int(t[2:4]) - int(t[2:4]) % 3)
        if len(minute) == 1:
            minute = '0' + minute
        if t[:2] == '15' and 18 <= int(minute) < 30:
            minute = '18'
        if t[:2] == '15' and 30 <= int(minute):
            minute = '30'
        t = t[:2] + ':' + minute
        return t
