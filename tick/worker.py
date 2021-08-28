import os
import sys
import time
import zipfile
import pythoncom
from PyQt5 import QtWidgets
from threading import Timer
from PyQt5.QAxContainer import QAxWidget
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.static import *
from utility.setting import *
app = QtWidgets.QApplication(sys.argv)


class Worker:
    def __init__(self, windowQ, workerQ, queryQ, tick1Q, tick2Q, tick3Q, tick4Q, tick5Q, tick6Q, tick7Q, tick8Q):
        self.windowQ = windowQ
        self.workerQ = workerQ
        self.queryQ = queryQ
        self.tick1Q = tick1Q
        self.tick2Q = tick2Q
        self.tick3Q = tick3Q
        self.tick4Q = tick4Q
        self.tick5Q = tick5Q
        self.tick6Q = tick6Q
        self.tick7Q = tick7Q
        self.tick8Q = tick8Q

        self.dict_code = {
            '틱0': [],
            '틱1': [],
            '틱2': [],
            '틱3': [],
            '틱4': [],
            '틱5': [],
            '틱6': [],
            '틱7': [],
            '틱8': []
        }
        self.dict_bool = {
            '로그인': False,
            '실시간데이터수신등록': False,
            'VI발동해제등록': False,
            '실시간조건검색시작': False,
            '실시간조건검색중단': False,
            '실시간데이터수신중단': False,
            '틱데이터저장': False,
            'DB저장': False,
            'TR수신': False,
            'TR다음': False,
            'CD수신': False,
            'CR수신': False
        }
        self.dict_intg = {
            '장운영상태': 1,
            '초당주식체결수신횟수': 0,
            '초당호가잔량수신횟수': 0
        }
        self.df_mt = pd.DataFrame(columns=['거래대금상위100'])
        self.df_tr = None
        self.dict_tritems = None
        self.dict_vipr = {}
        self.dict_tick = {}
        self.dict_cond = {}
        self.name_code = {}
        self.list_code = []
        self.list_trcd = []
        self.list_kosd = None
        self.time_info = now()
        self.str_trname = None
        self.str_tday = strf_time('%Y%m%d')
        self.str_jcct = self.str_tday + '090000'

        self.ocx = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')
        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.ocx.OnReceiveRealData.connect(self.OnReceiveRealData)
        self.ocx.OnReceiveTrCondition.connect(self.OnReceiveTrCondition)
        self.ocx.OnReceiveConditionVer.connect(self.OnReceiveConditionVer)
        self.ocx.OnReceiveRealCondition.connect(self.OnReceiveRealCondition)
        self.Start()

    def Start(self):
        self.CommConnect()
        self.EventLoop()

    def CommConnect(self):
        self.ocx.dynamicCall('CommConnect()')
        while not self.dict_bool['로그인']:
            pythoncom.PumpWaitingMessages()

        self.dict_bool['CD수신'] = False
        self.ocx.dynamicCall('GetConditionLoad()')
        while not self.dict_bool['CD수신']:
            pythoncom.PumpWaitingMessages()

        self.list_kosd = self.GetCodeListByMarket('10')
        list_code = self.GetCodeListByMarket('0') + self.list_kosd
        for code in list_code:
            name = self.GetMasterCodeName(code)
            self.name_code[name] = code

        data = self.ocx.dynamicCall('GetConditionNameList()')
        conditions = data.split(';')[:-1]
        for condition in conditions:
            cond_index, cond_name = condition.split('^')
            self.dict_cond[int(cond_index)] = cond_name

        self.windowQ.put('시스템 명령 실행 알림 - OpenAPI 로그인 완료')

    def EventLoop(self):
        while True:
            if not self.workerQ.empty():
                work = self.workerQ.get()
                if type(work) == list:
                    self.UpdateRealreg(work)
                elif type(work) == str:
                    self.RunWork(work)
            if self.dict_intg['장운영상태'] == 1:
                if not self.dict_bool['실시간데이터수신등록']:
                    self.OperationRealreg()
                if not self.dict_bool['VI발동해제등록']:
                    self.ViRealreg()
            if self.dict_intg['장운영상태'] == 3:
                if not self.dict_bool['실시간조건검색시작']:
                    self.ConditionSearchStart()
            if self.dict_intg['장운영상태'] == 8:
                if not self.dict_bool['실시간조건검색중단']:
                    self.ConditionSearchStop()
                if not self.dict_bool['실시간데이터수신중단']:
                    self.RemoveRealreg()
                if not self.dict_bool['DB저장']:
                    self.SaveDatabase()
                    self.SysExit(False)

            if now() > self.time_info:
                if len(self.df_mt) > 0:
                    self.UpdateMoneyTop()
                self.UpdateInfo()
                self.time_info = timedelta_sec(+1)
            time_loop = timedelta_sec(0.25)
            while now() < time_loop:
                pythoncom.PumpWaitingMessages()
                time.sleep(0.0001)

    def UpdateRealreg(self, rreg):
        sn = rreg[0]
        if len(rreg) == 2:
            self.ocx.dynamicCall('SetRealRemove(QString, QString)', rreg)
            self.windowQ.put(f'실시간 알림 중단 완료 - 모든 실시간 데이터 수신 중단')
        elif len(rreg) == 4:
            ret = self.ocx.dynamicCall('SetRealReg(QString, QString, QString, QString)', rreg)
            result = '완료' if ret == 0 else '실패'
            if sn == sn_oper:
                self.windowQ.put(f'실시간 알림 등록 {result} - 장운영시간 [{sn}]')
            else:
                self.windowQ.put(f"실시간 알림 등록 {result} - [{sn}] 종목갯수 {len(rreg[1].split(';'))}")

    def RunWork(self, work):
        if work == '틱데이터 저장 완료':
            self.dict_bool['틱데이터저장'] = True

    def OperationRealreg(self):
        self.workerQ.put([sn_oper, ' ', '215;20;214', 0])
        self.dict_code['틱0'] = self.SendCondition(sn_oper, self.dict_cond[1], 1, 0)
        self.dict_code['틱1'] = [code for i, code in enumerate(self.dict_code['틱0']) if i % 8 == 0]
        self.dict_code['틱2'] = [code for i, code in enumerate(self.dict_code['틱0']) if i % 8 == 1]
        self.dict_code['틱3'] = [code for i, code in enumerate(self.dict_code['틱0']) if i % 8 == 2]
        self.dict_code['틱4'] = [code for i, code in enumerate(self.dict_code['틱0']) if i % 8 == 3]
        self.dict_code['틱5'] = [code for i, code in enumerate(self.dict_code['틱0']) if i % 8 == 4]
        self.dict_code['틱6'] = [code for i, code in enumerate(self.dict_code['틱0']) if i % 8 == 5]
        self.dict_code['틱7'] = [code for i, code in enumerate(self.dict_code['틱0']) if i % 8 == 6]
        self.dict_code['틱8'] = [code for i, code in enumerate(self.dict_code['틱0']) if i % 8 == 7]
        k = 0
        for i in range(0, len(self.dict_code['틱0']), 100):
            self.workerQ.put([sn_jchj + k, ';'.join(self.dict_code['틱0'][i:i + 100]),
                              '10;12;14;30;228;41;61;71;81', 1])
            k += 1
        self.dict_bool['실시간데이터수신등록'] = True
        telegram_msg('틱데이터 수집시스템를 시작하였습니다.')

    def ViRealreg(self):
        self.Block_Request('opt10054', 시장구분='000', 장전구분='1', 종목코드='', 발동구분='1', 제외종목='111111011',
                           거래량구분='0', 거래대금구분='0', 발동방향='0', output='발동종목', next=0)
        self.windowQ.put('시스템 명령 실행 알림 - VI발동해제 등록 완료')
        self.dict_bool['VI발동해제등록'] = True

    def SendCondition(self, screen, cond_name, cond_index, search):
        self.dict_bool['CR수신'] = False
        self.ocx.dynamicCall('SendCondition(QString, QString, int, int)', screen, cond_name, cond_index, search)
        while not self.dict_bool['CR수신']:
            pythoncom.PumpWaitingMessages()
        return self.list_trcd

    def ConditionSearchStart(self):
        self.list_code = self.SendCondition(sn_cond, self.dict_cond[0], 0, 1)
        self.df_mt.at[self.str_tday + '090000'] = ';'.join(self.list_code)
        self.dict_bool['실시간조건검색시작'] = True

    def ConditionSearchStop(self):
        self.ocx.dynamicCall("SendConditionStop(QString, QString, int)", sn_cond, self.dict_cond[0], 0)
        self.dict_bool['실시간조건검색중단'] = True

    def RemoveRealreg(self):
        self.workerQ.put(['ALL', 'ALL'])
        self.windowQ.put('시스템 명령 실행 알림 - 실시간 데이터 중단 완료')
        self.dict_bool['실시간데이터수신중단'] = True

    def SaveDatabase(self):
        con = sqlite3.connect(db_tick)
        self.df_mt.to_sql('moneytop', con, if_exists='append', chunksize=1000)
        con.close()
        self.tick1Q.put('틱데이터저장')
        self.tick2Q.put('틱데이터저장')
        self.tick3Q.put('틱데이터저장')
        self.tick4Q.put('틱데이터저장')
        self.tick5Q.put('틱데이터저장')
        self.tick6Q.put('틱데이터저장')
        self.tick7Q.put('틱데이터저장')
        self.tick8Q.put('틱데이터저장')
        self.dict_bool['DB저장'] = True
        """
        전략 테스트 프로그램에서 거래한 종목만 저장
        con = sqlite3.connect(db_stg)
        df = pd.read_sql(f"SELECT * FROM tradelist WHERE 체결시간 LIKE '{self.str_tday}%'", con)
        con.close()
        df = df.set_index('index')
        codes = []
        for index in df.index:
            code = self.name_code[df['종목명'][index]]
            stg = df['전략구분'][index]
            if stg == '단타' and code not in codes:
                codes.append(code)
        self.tick1Q.put(['틱데이터저장', codes])
        self.tick2Q.put(['틱데이터저장', codes])
        self.tick3Q.put(['틱데이터저장', codes])
        self.tick4Q.put(['틱데이터저장', codes])
        self.tick5Q.put(['틱데이터저장', codes])
        self.tick6Q.put(['틱데이터저장', codes])
        self.tick7Q.put(['틱데이터저장', codes])
        self.tick8Q.put(['틱데이터저장', codes])
        self.dict_bool['DB저장'] = True
        """

    def OnEventConnect(self, err_code):
        if err_code == 0:
            self.dict_bool['로그인'] = True

    def OnReceiveConditionVer(self, ret, msg):
        if msg == '':
            return
        if ret == 1:
            self.dict_bool['CD수신'] = True

    def OnReceiveTrCondition(self, screen, code_list, cond_name, cond_index, nnext):
        if screen == "" and cond_name == "" and cond_index == "" and nnext == "":
            return
        codes = code_list.split(';')[:-1]
        self.list_trcd = codes
        self.dict_bool['CR수신'] = True

    def OnReceiveRealCondition(self, code, IorD, cname, cindex):
        if cname == "":
            return
        if IorD == "I" and cindex == "0" and code not in self.list_code:
            self.list_code.append(code)
        elif IorD == "D" and cindex == "0" and code in self.list_code:
            self.list_code.remove(code)

    def OnReceiveRealData(self, code, realtype, realdata):
        if realdata == '':
            return
        if realtype == '장시작시간':
            if self.dict_intg['장운영상태'] == 8:
                return
            try:
                self.dict_intg['장운영상태'] = int(self.GetCommRealData(code, 215))
                current = self.GetCommRealData(code, 20)
                remain = self.GetCommRealData(code, 214)
            except Exception as e:
                self.windowQ.put(f'OnReceiveRealData 장시작시간 {e}')
            else:
                self.OperationAlert(current, remain)
        elif realtype == 'VI발동/해제':
            if self.dict_bool['실시간데이터수신중단']:
                return
            try:
                code = self.GetCommRealData(code, 9001).strip('A').strip('Q')
                gubun = self.GetCommRealData(code, 9068)
                name = self.GetMasterCodeName(code)
            except Exception as e:
                self.windowQ.put(f'OnReceiveRealData VI발동/해제 {e}')
            else:
                if gubun == '1' and code in self.dict_code['틱0'] and \
                        (code not in self.dict_vipr.keys() or
                         (self.dict_vipr[code][0] and now() > self.dict_vipr[code][1])):
                    self.UpdateViPriceDown5(code, name)
        elif realtype == '주식체결':
            if self.dict_bool['실시간데이터수신중단']:
                return
            self.dict_intg['초당주식체결수신횟수'] += 1
            try:
                d = self.GetCommRealData(code, 20)
            except Exception as e:
                self.windowQ.put(f'OnReceiveRealData 주식체결 {e}')
            else:
                if d != self.str_jcct[8:]:
                    self.str_jcct = self.str_tday + d
                try:
                    c = abs(int(self.GetCommRealData(code, 10)))
                    o = abs(int(self.GetCommRealData(code, 16)))
                except Exception as e:
                    self.windowQ.put(f'OnReceiveRealData 주식체결 {e}')
                else:
                    if code not in self.dict_vipr.keys():
                        self.InsertViPriceDown5(code, o)
                    if code in self.dict_vipr.keys() and not self.dict_vipr[code][0] and now() > self.dict_vipr[code][1]:
                        self.UpdateViPriceDown5(code, c)
                    if code in self.dict_tick.keys() and d == self.dict_tick[code][0]:
                        return
                    try:
                        h = abs(int(self.GetCommRealData(code, 17)))
                        low = abs(int(self.GetCommRealData(code, 18)))
                        per = float(self.GetCommRealData(code, 12))
                        dm = int(self.GetCommRealData(code, 14))
                        ch = float(self.GetCommRealData(code, 228))
                        vp = abs(float(self.GetCommRealData(code, 30)))
                    except Exception as e:
                        self.windowQ.put(f'OnReceiveRealData 주식체결 {e}')
                    else:
                        self.UpdateTickData(code, c, o, h, low, per, dm, ch, vp, d)
        elif realtype == '주식호가잔량':
            if self.dict_bool['실시간데이터수신중단']:
                return
            self.dict_intg['초당호가잔량수신횟수'] += 1
            try:
                s1jr = int(self.GetCommRealData(code, 61))
                s2jr = int(self.GetCommRealData(code, 62))
                b1jr = int(self.GetCommRealData(code, 71))
                b2jr = int(self.GetCommRealData(code, 72))
                s1hg = abs(int(self.GetCommRealData(code, 41)))
                s2hg = abs(int(self.GetCommRealData(code, 42)))
                b1hg = abs(int(self.GetCommRealData(code, 51)))
                b2hg = abs(int(self.GetCommRealData(code, 52)))
            except Exception as e:
                self.windowQ.put(f'OnReceiveRealData 주식호가잔량 {e}')
            else:
                self.UpdateHoga(code, s1jr, s2jr, b1jr, b2jr, s1hg, s2hg, b1hg, b2hg)

    def OperationAlert(self, current, remain):
        self.windowQ.put(f"장운영 시간 수신 알림 - {self.dict_intg['장운영상태']} "
                         f'{current[:2]}:{current[2:4]}:{current[4:]} '
                         f'남은시간 {remain[:2]}:{remain[2:4]}:{remain[4:]}')

    def InsertViPriceDown5(self, code, o):
        vid5 = self.GetVIPriceDown5(code, o)
        self.dict_vipr[code] = [True, timedelta_sec(-180), vid5]

    def GetVIPriceDown5(self, code, std_price):
        vi = std_price * 1.1
        x = self.GetHogaunit(code, vi)
        if vi % x != 0:
            vi = vi + (x - vi % x)
        return int(vi - x * 5)

    def GetHogaunit(self, code, price):
        if price < 1000:
            x = 1
        elif 1000 <= price < 5000:
            x = 5
        elif 5000 <= price < 10000:
            x = 10
        elif 10000 <= price < 50000:
            x = 50
        elif code in self.list_kosd:
            x = 100
        elif 50000 <= price < 100000:
            x = 100
        elif 100000 <= price < 500000:
            x = 500
        else:
            x = 1000
        return x

    def UpdateViPriceDown5(self, code, key):
        if type(key) == str:
            if code in self.dict_vipr.keys():
                self.dict_vipr[code][0] = False
                self.dict_vipr[code][1] = timedelta_sec(5)
            else:
                self.dict_vipr[code] = [False, timedelta_sec(5), 0]
            self.windowQ.put(f'변동성 완화 장치 발동 - [{code}] {key}')
        elif type(key) == int:
            vid5 = self.GetVIPriceDown5(code, key)
            self.dict_vipr[code] = [True, timedelta_sec(5), vid5]

    def UpdateTickData(self, code, c, o, h, low, per, dm, ch, vp, d):
        vitime = strf_time('%Y%m%d%H%M%S', self.dict_vipr[code][1])
        vi = self.dict_vipr[code][2]
        try:
            s1jr, s2jr, b1jr, b2jr, s1hg, s2hg, b1hg, b2hg = self.dict_tick[code][1:]
            self.dict_tick[code][0] = d
        except KeyError:
            s1jr, s2jr, b1jr, b2jr, s1hg, s2hg, b1hg, b2hg = 0, 0, 0, 0, 0, 0, 0, 0
            self.dict_tick[code] = [d, 0, 0, 0, 0, 0, 0, 0, 0]
        data = [code, c, o, h, low, per, dm, ch, vp, vitime, vi,
                s1jr, s2jr, b1jr, b2jr, s1hg, s2hg, b1hg, b2hg, d, now()]
        if code in self.dict_code['틱1']:
            self.tick1Q.put(data)
        elif code in self.dict_code['틱2']:
            self.tick2Q.put(data)
        elif code in self.dict_code['틱3']:
            self.tick3Q.put(data)
        elif code in self.dict_code['틱4']:
            self.tick4Q.put(data)
        elif code in self.dict_code['틱5']:
            self.tick5Q.put(data)
        elif code in self.dict_code['틱6']:
            self.tick6Q.put(data)
        elif code in self.dict_code['틱7']:
            self.tick7Q.put(data)
        elif code in self.dict_code['틱8']:
            self.tick8Q.put(data)

    def UpdateHoga(self, code, s1jr, s2jr, b1jr, b2jr, s1hg, s2hg, b1hg, b2hg):
        try:
            d = self.dict_tick[code][0]
        except KeyError:
            d = '090000'
        self.dict_tick[code] = [d, s1jr, s2jr, b1jr, b2jr, s1hg, s2hg, b1hg, b2hg]

    def UpdateMoneyTop(self):
        if self.str_jcct == self.df_mt.index[-1]:
            return
        timetype = '%Y%m%d%H%M%S'
        curr_datetime = strp_time(timetype, self.str_jcct)
        last_datetime = strp_time(timetype, self.df_mt.index[-1])
        list_text = ';'.join(self.list_code)
        if (curr_datetime - last_datetime).total_seconds() > 1:
            pre_time = strf_time(timetype, timedelta_sec(-1, curr_datetime))
            self.df_mt.at[pre_time] = list_text
        self.df_mt.at[self.str_jcct] = list_text

    def UpdateInfo(self):
        self.windowQ.put(f"부가정보 {self.dict_intg['초당주식체결수신횟수']} {self.dict_intg['초당호가잔량수신횟수']}")
        self.dict_intg['초당주식체결수신횟수'] = 0
        self.dict_intg['초당호가잔량수신횟수'] = 0

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
        self.dict_bool['TR다음'] = False
        self.ocx.dynamicCall('CommRqData(QString, QString, int, QString)', self.str_trname, trcode, nnext, sn_brrq)
        sleeptime = timedelta_sec(0.25)
        while not self.dict_bool['TR수신'] or now() < sleeptime:
            pythoncom.PumpWaitingMessages()
        return self.df_tr

    def GetMasterCodeName(self, code):
        return self.ocx.dynamicCall('GetMasterCodeName(QString)', code)

    def GetCodeListByMarket(self, market):
        data = self.ocx.dynamicCall('GetCodeListByMarket(QString)', market)
        tokens = data.split(';')[:-1]
        return tokens

    def GetCommRealData(self, code, fid):
        return self.ocx.dynamicCall('GetCommRealData(QString, int)', code, fid)

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

    def SysExit(self, gubun):
        if not self.dict_bool['틱데이터저장']:
            Timer(1, self.SysExit, args=[gubun]).start()
            return
        telegram_msg('틱데이터를 저장하였습니다.')
        if gubun:
            os.system('shutdown /s /t 20')
        self.windowQ.put('시스템 명령 실행 알림 - 10초 후 시스템을 종료합니다.')
        i = 10
        while i > 0:
            self.windowQ.put(f'시스템 명령 실행 알림 - 시스템 종료 카운터 {i}')
            i -= 1
            time.sleep(1)
        self.windowQ.put('시스템 명령 실행 알림 - 시스템 종료')
