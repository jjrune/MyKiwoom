import os
import sys
import time
import sqlite3
import zipfile
import pythoncom
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QAxContainer import QAxWidget
from multiprocessing import Process, Queue, Lock
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from login.manuallogin import find_window, manual_login
from utility.static import strf_time, now, telegram_msg
from utility.setting import openapi_path, sn_brrq, db_day, db_stg
app = QtWidgets.QApplication(sys.argv)


class UpdaterMid:
    def __init__(self, gubun, queryQQ, lockk):
        self.gubun = gubun
        self.queryQ = queryQQ
        self.lock = lockk
        self.str_trname = None
        self.str_tday = strf_time('%Y%m%d')
        self.df_tr = None
        self.dict_tritems = None
        self.dict_bool = {
            '로그인': False,
            'TR수신': False
        }

        self.ocx = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')
        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.Start()

    def Start(self):
        self.CommConnect()
        self.Updater()

    def CommConnect(self):
        self.ocx.dynamicCall('CommConnect()')
        while not self.dict_bool['로그인']:
            pythoncom.PumpWaitingMessages()

    def Updater(self):
        con = sqlite3.connect(db_stg)
        df = pd.read_sql('SELECT * FROM mid', con)
        con.close()
        df = df.set_index('index')
        codes = list(df.index)
        codes = [code for i, code in enumerate(codes) if i % 4 == self.gubun]
        count = len(codes)
        for i, code in enumerate(codes):
            time.sleep(3.6)
            self.lock.acquire()
            df = self.Block_Request('opt10081', 종목코드=code, 기준일자=self.str_tday, 수정주가구분=1,
                                    output='주식일봉차트조회', next=0)
            self.lock.release()
            df = df.set_index('일자')
            df[['현재가', '저가']] = df[['현재가', '저가']].astype(int).abs()
            df = df[::-1]
            df['이평05'] = df['현재가'].rolling(window=5).mean().round(2)
            df['5일최저저가'] = df['저가'].rolling(window=5).min()
            df['240일최고종가'] = df['현재가'].rolling(window=240).max()
            premid = 1 if df['현재가'][-1] <= df['이평05'][-1] else 0
            prelow = 0
            for h, index in enumerate(df.index):
                if h <= 239:
                    continue
                if df['현재가'][index] < df['240일최고종가'][index] * 0.70:
                    prelow = 0
                elif df['현재가'][h - 1] <= df['이평05'][h - 1] and df['현재가'][index] > df['이평05'][index]:
                    prelow = df['5일최저저가'][index]
            ll04 = df['저가'][-4:].min()
            tc04 = df['현재가'][-4:].sum()
            self.queryQ.put([code, premid, prelow, ll04, tc04])
            print(f'[{now()}] {self.gubun} 데이터 업데이트 중 ... [{i + 1}/{count}]')
        if self.gubun == 3:
            self.queryQ.put('업데이트완료')
        sys.exit()

    def OnEventConnect(self, err_code):
        if err_code == 0:
            self.dict_bool['로그인'] = True

    def OnReceiveTrData(self, screen, rqname, trcode, record, nnext):
        if screen == '' and record == '':
            return
        items = None
        self.dict_bool['TR다음'] = True if nnext == '2' else False
        for output in self.dict_tritems['output']:
            record = list(output.keys())[0]
            items = list(output.values())[0]
            if record == self.str_trname:
                break
        rows = self.ocx.dynamicCall('GetRepeatCnt(QString, QString)', trcode, rqname)
        if rows == 0:
            rows = 1
        df2 = []
        for row in range(rows):
            row_data = []
            for item in items:
                data = self.ocx.dynamicCall('GetCommData(QString, QString, int, QString)', trcode, rqname, row, item)
                row_data.append(data.strip())
            df2.append(row_data)
        df = pd.DataFrame(data=df2, columns=items)
        self.df_tr = df
        self.dict_bool['TR수신'] = True

    def Block_Request(self, *args, **kwargs):
        trcode = args[0].lower()
        liness = self.ReadEnc(trcode)
        self.dict_tritems = self.ParseDat(trcode, liness)
        self.str_trname = kwargs['output']
        nnext = kwargs['next']
        for i in kwargs:
            if i.lower() != 'output' and i.lower() != 'next':
                self.ocx.dynamicCall('SetInputValue(QString, QString)', i, kwargs[i])
        self.dict_bool['TR수신'] = False
        self.ocx.dynamicCall('CommRqData(QString, QString, int, QString)', self.str_trname, trcode, nnext, sn_brrq)
        while not self.dict_bool['TR수신']:
            pythoncom.PumpWaitingMessages()
        return self.df_tr

    # noinspection PyMethodMayBeStatic
    def ReadEnc(self, trcode):
        enc = zipfile.ZipFile(f'{openapi_path}/data/{trcode}.enc')
        liness = enc.read(trcode.upper() + '.dat').decode('cp949')
        return liness

    # noinspection PyMethodMayBeStatic
    def ParseDat(self, trcode, liness):
        liness = liness.split('\n')
        start = [i for i, x in enumerate(liness) if x.startswith('@START')]
        end = [i for i, x in enumerate(liness) if x.startswith('@END')]
        block = zip(start, end)
        enc_data = {'trcode': trcode, 'input': [], 'output': []}
        for start, end in block:
            block_data = liness[start - 1:end + 1]
            block_info = block_data[0]
            block_type = 'input' if 'INPUT' in block_info else 'output'
            record_line = block_data[1]
            tokens = record_line.split('_')[1].strip()
            record = tokens.split('=')[0]
            fields = block_data[2:-1]
            field_name = []
            for line in fields:
                field = line.split('=')[0].strip()
                field_name.append(field)
            fields = {record: field_name}
            enc_data['input'].append(fields) if block_type == 'input' else enc_data['output'].append(fields)
        return enc_data


class Query:
    def __init__(self, queryQQ):
        self.queryQ = queryQQ
        self.con = sqlite3.connect(db_day)
        self.Start()

    def __del__(self):
        self.con.close()

    def Start(self):
        df_mid = pd.DataFrame(columns=['premid', 'prelow', 'll04', 'tc04'])
        while True:
            data = self.queryQ.get()
            if data != '업데이트완료':
                df_mid.at[data[0]] = data[1], data[2], data[3], data[4]
            else:
                break

        df_mid[['premid', 'prelow', 'll04', 'tc04']] = df_mid[['premid', 'prelow', 'll04', 'tc04']].astype(int)
        con = sqlite3.connect(db_stg)
        df = pd.read_sql('SELECT * FROM mid', con)
        df = df.set_index('index')
        df['premid'] = df_mid['premid']
        df['prelow'] = df_mid['prelow']
        df['ll04'] = df_mid['ll04']
        df['tc04'] = df_mid['tc04']
        df.to_sql('mid', con, if_exists='replace', chunksize=1000)
        con.close()
        telegram_msg('mid DB를 업데이트하였습니다.')
        sys.exit()


if __name__ == '__main__':
    queryQ = Queue()
    lock = Lock()

    login_info = f'{openapi_path}/system/Autologin.dat'
    if os.path.isfile(login_info):
        os.remove(f'{openapi_path}/system/Autologin.dat')

    Process(target=Query, args=(queryQ,)).start()

    Process(target=UpdaterMid, args=(0, queryQ, lock)).start()
    while find_window('Open API login') == 0:
        time.sleep(1)
    time.sleep(5)
    manual_login(1)
    while find_window('Open API login') != 0:
        time.sleep(1)

    Process(target=UpdaterMid, args=(1, queryQ, lock)).start()
    while find_window('Open API login') == 0:
        time.sleep(1)
    time.sleep(5)
    manual_login(2)
    while find_window('Open API login') != 0:
        time.sleep(1)

    Process(target=UpdaterMid, args=(2, queryQ, lock)).start()
    while find_window('Open API login') == 0:
        time.sleep(1)
    time.sleep(5)
    manual_login(3)
    while find_window('Open API login') != 0:
        time.sleep(1)

    Process(target=UpdaterMid, args=(3, queryQ, lock)).start()
    while find_window('Open API login') == 0:
        time.sleep(1)
    time.sleep(5)
    manual_login(4)
    while find_window('Open API login') != 0:
        time.sleep(1)
