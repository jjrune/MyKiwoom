import os
import sys
import time
import psutil
import zipfile
import pythoncom
from PyQt5 import QtWidgets
from threading import Timer, Lock
from PyQt5.QAxContainer import QAxWidget
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.static import *
from utility.setting import *
app = QtWidgets.QApplication(sys.argv)


class Worker:
    def __init__(self, qlist):
        self.windowQ = qlist[0]
        self.workerQ = qlist[1]
        self.stgtQ = qlist[2]
        self.stglQ = qlist[3]
        self.stgmQ = qlist[4]
        self.stgsQ = qlist[5]
        self.soundQ = qlist[6]
        self.queryQ = qlist[7]
        self.teleQ = qlist[8]
        self.hoga1Q = qlist[9]
        self.hoga2Q = qlist[10]
        self.chart1Q = qlist[11]
        self.chart2Q = qlist[12]
        self.chart3Q = qlist[13]
        self.chart4Q = qlist[14]
        self.chart5Q = qlist[15]
        self.chart6Q = qlist[16]
        self.chart7Q = qlist[17]
        self.chart8Q = qlist[18]
        self.chart9Q = qlist[19]
        self.lock = Lock()

        self.dict_name = {}     # key: 종목코드, value: 종목명
        self.dict_sghg = {}     # key: 종목코드, value: [상한가, 하한가]
        self.dict_vipr = {}     # key: 종목코드, value: [갱신여부, 진입시간 + 5초, UVI, DVI]
        self.dict_cond = {}     # key: 조건검색식번호, value: 조건검색식명
        self.dict_hoga = {}     # key: 호가창번호, value: [종목코드, 갱신여부, 호가잔고(DataFrame)]
        self.dict_chat = {}     # key: UI번호, value: 종목코드

        self.dict_df = {
            '실현손익': pd.DataFrame(columns=columns_tt),
            '거래목록': pd.DataFrame(columns=columns_td),
            '잔고평가': pd.DataFrame(columns=columns_tj),
            '잔고목록': pd.DataFrame(columns=columns_jg),
            '체결목록': pd.DataFrame(columns=columns_cj),
            'TRDF': None
        }
        self.dict_intg = {
            '장운영상태': 1,
            '예수금': 0,
            '단타예수금': 0,
            '단기예수금': 0,
            '중기예수금': 0,
            '장기예수금': 0,
            '단타추정예수금': 0,
            '단기추정예수금': 0,
            '중기추정예수금': 0,
            '장기추정예수금': 0,
            '단타투자금액': 0,
            '장기투자금액': 0,
            '중기투자금액': 0,
            '단기투자금액': 0,
            '단타최고수익금': 0,

            'TR수신횟수': 0,
            '주식체결수신횟수': 0,
            '체결잔고수신횟수': 0,
            '호가잔량수신횟수': 0,
            '초당주식체결수신횟수': 0,
            '초당호가잔량수신횟수': 0,
            'TR제한수신횟수': 0,

            '평균시간': 0,
            '등락율상한': 0.,
            '고저평균대비등락율하한': 0.,
            '누적거래대금하한': 0,
            '체결강도하한': 0.,
            '거래대금하한': 0,
            '전일거래량대비하한': 0.,
            '체결강도차이': 0.,
            '거래대금차이': 0,
            '전일거래량대비차이': 0.,
            '청산시간': 0,

            '스레드': 0,
            '시피유': 0.,
            '메모리': 0.
        }
        self.dict_strg = {
            '당일날짜': strf_time('%Y%m%d'),
            '계좌번호': None,
            'TR종목명': None,
            'TR명': None
        }
        self.dict_bool = {
            'DB로딩': False,
            '계좌잔고': False,
            '업종차트': False,
            '장운영시간': False,
            '업종지수등록': False,
            '단중장기주식체결등록': False,
            'VI발동해제등록': False,
            '실시간조건검색시작': False,
            '실시간조건검색중단': False,
            '실시간데이터수신중단': False,
            '잔고청산': False,
            '단중장기매수주문': False,
            '단타목표수익률달성': False,
            '단타전략중단': False,
            'DB저장': False,

            '테스트': False,
            '모의투자': False,
            '알림소리': False,

            '로그인': False,
            'TR수신': False,
            'TR다음': False,
            'CD수신': False,
            'CR수신': False
        }
        remaintime = (strp_time('%Y%m%d%H%M%S', self.dict_strg['당일날짜'] + '090100') - now()).total_seconds()
        exittime = timedelta_sec(remaintime) if remaintime > 0 else timedelta_sec(600)
        self.dict_time = {
            '휴무종료': exittime,
            '거래정보': now(),
            '부가정보': now(),
            '호가잔고': now(),
            'TR시작': now(),
            'TR재개': now()
        }
        self.dict_buy = {}
        self.dict_sell = {}
        self.dict_item = None
        self.list_trcd = None
        self.list_kosd = None
        self.list_gsjm = []
        self.list_long = []
        self.list_mid = []
        self.list_short = []

        self.ocx = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')
        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.ocx.OnReceiveRealData.connect(self.OnReceiveRealData)
        self.ocx.OnReceiveChejanData.connect(self.OnReceiveChejanData)
        self.ocx.OnReceiveTrCondition.connect(self.OnReceiveTrCondition)
        self.ocx.OnReceiveConditionVer.connect(self.OnReceiveConditionVer)
        self.ocx.OnReceiveRealCondition.connect(self.OnReceiveRealCondition)
        self.Start()

    def Start(self):
        self.CreateDatabase()
        self.LoadDatabase()
        self.CommConnect()
        self.EventLoop()

    def CreateDatabase(self):
        con = sqlite3.connect(db_stg)
        df = pd.read_sql("SELECT name FROM sqlite_master WHERE TYPE = 'table'", con)
        table_list = df['name'].values
        con.close()

        if 'chegeollist' not in table_list:
            self.queryQ.put("CREATE TABLE chegeollist ('index' TEXT, '종목명' TEXT, '주문구분' TEXT,"
                            "'주문수량' INTEGER, '미체결수량' INTEGER, '주문가격' INTEGER, '체결가' INTEGER,"
                            "'체결시간' TEXT)")
            self.queryQ.put("CREATE INDEX 'ix_chegeollist_index' ON 'chegeollist' ('index')")
            self.windowQ.put([1, '시스템 명령 실행 알림 - 데이터베이스 chegeollist 테이블 생성 완료'])

        if 'jangolist' not in table_list:
            self.queryQ.put("CREATE TABLE 'jangolist' ('index' TEXT, '종목명' TEXT, '매입가' INTEGER,"
                            "'현재가' INTEGER, '수익률' REAL, '평가손익' INTEGER, '매입금액' INTEGER, '평가금액' INTEGER,"
                            "'시가' INTEGER, '고가' INTEGER, '저가' INTEGER, '전일종가' INTEGER, '보유수량' INTEGER,"
                            "'전략구분' TEXT)")
            self.queryQ.put("CREATE INDEX 'ix_jangolist_index' ON 'jangolist' ('index')")
            self.windowQ.put([1, '시스템 명령 실행 알림 - 데이터베이스 jangolist 테이블 생성 완료'])

        if 'tradelist' not in table_list:
            self.queryQ.put("CREATE TABLE tradelist ('index' TEXT, '종목명' TEXT, '매수금액' INTEGER,"
                            "'매도금액' INTEGER, '주문수량' INTEGER, '수익률' REAL, '수익금' INTEGER, '체결시간' TEXT,"
                            "'전략구분' TEXT)")
            self.queryQ.put("CREATE INDEX 'ix_tradelist_index' ON 'tradelist' ('index')")
            self.windowQ.put([1, '시스템 명령 실행 알림 - 데이터베이스 tradelist 테이블 생성 완료'])

        if 'totaltradelist' not in table_list:
            self.queryQ.put("CREATE TABLE 'totaltradelist' ('index' TEXT, '총매수금액' INTEGER, '총매도금액' INTEGER,"
                            "'총수익금액' INTEGER, '총손실금액' INTEGER, '수익률' REAL, '수익금합계' INTEGER)")
            self.queryQ.put("CREATE INDEX 'ix_totaltradelist_index' ON 'totaltradelist' ('index')")
            self.windowQ.put([1, '시스템 명령 실행 알림 - 데이터베이스 totaltradelist 테이블 생성 완료'])

        if 'setting' not in table_list:
            df = pd.DataFrame(
                [[0, 1, 1, 3.7, 89, 60, 1, 0, 3, 3000, 23., 0.8]],
                columns=['테스트', '모의투자', '알림소리', '체결강도차이', '거래대금차이', '평균시간', '청산시간',
                         '체결강도하한', '전일거래량대비하한', '누적거래대금하한', '등락율상한', '고저평균대비등락율하한'],
                index=[0])
            self.queryQ.put([df, 'setting', 'replace'])
            self.windowQ.put([1, '시스템 명령 실행 알림 - 데이터베이스 setting 테이블 생성 완료'])

        time.sleep(2)

    def LoadDatabase(self):
        self.windowQ.put([2, '데이터베이스 불러오기'])
        con = sqlite3.connect(db_stg)
        df = pd.read_sql('SELECT * FROM setting', con)
        df = df.set_index('index')
        self.dict_bool['테스트'] = df['테스트'][0]
        self.dict_bool['모의투자'] = df['모의투자'][0]
        self.dict_bool['알림소리'] = df['알림소리'][0]
        self.dict_intg['체결강도차이'] = df['체결강도차이'][0]
        self.dict_intg['거래대금차이'] = df['거래대금차이'][0]
        self.dict_intg['평균시간'] = df['평균시간'][0]
        self.dict_intg['청산시간'] = df['청산시간'][0]
        self.dict_intg['체결강도하한'] = df['체결강도하한'][0]
        self.dict_intg['전일거래량대비하한'] = df['전일거래량대비하한'][0]
        self.dict_intg['누적거래대금하한'] = df['누적거래대금하한'][0]
        self.dict_intg['등락율상한'] = df['등락율상한'][0]
        self.dict_intg['고저평균대비등락율하한'] = df['고저평균대비등락율하한'][0]
        self.windowQ.put([ui_num['단타설정'], df])
        self.windowQ.put([2, f"테스트모드 {self.dict_bool['테스트']}"])
        self.windowQ.put([2, f"모의투자 {self.dict_bool['모의투자']}"])
        self.windowQ.put([2, f"알림소리 {self.dict_bool['알림소리']}"])

        """
        단기, 중기, 장기 전략 완성 후 활성화
        df = pd.read_sql('SELECT * FROM long', con)
        self.list_long = list(df['index'])

        df = pd.read_sql('SELECT * FROM mid', con)
        self.list_mid = list(df['index'])

        df = pd.read_sql('SELECT * FROM short', con)
        self.list_short = list(df['index'])
        """

        df = pd.read_sql(f"SELECT * FROM chegeollist WHERE 체결시간 LIKE '{self.dict_strg['당일날짜']}%'", con)
        self.dict_df['체결목록'] = df.set_index('index').sort_values(by=['체결시간'], ascending=False)

        df = pd.read_sql(f'SELECT * FROM jangolist', con)
        self.dict_df['잔고목록'] = df.set_index('index').sort_values(by=['매입금액'], ascending=False)

        df = pd.read_sql(f"SELECT * FROM tradelist WHERE 체결시간 LIKE '{self.dict_strg['당일날짜']}%'", con)
        self.dict_df['거래목록'] = df.set_index('index').sort_values(by=['체결시간'], ascending=False)
        con.close()

        if len(self.dict_df['체결목록']) > 0:
            self.windowQ.put([ui_num['체결목록'], self.dict_df['체결목록']])
        if len(self.dict_df['거래목록']) > 0:
            self.windowQ.put([ui_num['거래목록'], self.dict_df['거래목록']])
            self.UpdateTotaltradelist()

        self.windowQ.put([1, '시스템 명령 실행 알림 - 데이터베이스 정보 불러오기 완료'])
        self.dict_bool['DB로딩'] = True

    def CommConnect(self):
        self.windowQ.put([2, 'OPENAPI 로그인'])
        self.ocx.dynamicCall('CommConnect()')
        while not self.dict_bool['로그인']:
            pythoncom.PumpWaitingMessages()

        self.dict_strg['계좌번호'] = self.ocx.dynamicCall('GetLoginInfo(QString)', 'ACCNO').split(';')[0]

        self.list_kosd = self.GetCodeListByMarket('10')
        list_code = self.GetCodeListByMarket('0') + self.list_kosd
        dict_code = {}
        for code in list_code:
            name = self.GetMasterCodeName(code)
            self.dict_name[code] = name
            dict_code[name] = code
        self.chart9Q.put(self.dict_name)
        self.windowQ.put([8, dict_code])
        self.windowQ.put([9, self.dict_name])

        self.dict_bool['CD수신'] = False
        self.ocx.dynamicCall('GetConditionLoad()')
        while not self.dict_bool['CD수신']:
            pythoncom.PumpWaitingMessages()

        data = self.ocx.dynamicCall('GetConditionNameList()')
        conditions = data.split(';')[:-1]
        for condition in conditions:
            cond_index, cond_name = condition.split('^')
            self.dict_cond[int(cond_index)] = cond_name

        self.windowQ.put([1, '시스템 명령 실행 알림 - OpenAPI 로그인 완료'])
        if self.dict_bool['알림소리']:
            self.soundQ.put('키움증권 오픈에이피아이에 로그인하였습니다.')

    def EventLoop(self):
        while True:
            if not self.workerQ.empty():
                work = self.workerQ.get()
                if type(work) == list:
                    if len(work) in [10, 11]:
                        self.SendOrder(work)
                    elif len(work) == 5:
                        self.BuySell(work[0], work[1], work[2], work[3], work[4])
                        continue
                    elif len(work) in [2, 4]:
                        self.UpdateRealreg(work)
                elif type(work) == str:
                    self.RunWork(work)

            if self.dict_intg['장운영상태'] == 1:
                if not self.dict_bool['테스트']:
                    if not self.dict_bool['계좌잔고']:
                        self.GetAccountjanGo()
                    if not self.dict_bool['업종차트']:
                        self.GetKospiKosdaqChart()
                    if not self.dict_bool['장운영시간']:
                        self.OperationRealreg()
                    if not self.dict_bool['업종지수등록']:
                        self.UpjongjisuRealreg()
                    """
                    단기, 중기, 장기 전략 완성 후 활성화
                    if not self.dict_bool['단중장기주식체결등록']:
                        self.LMSRealreg()
                    """
                    if not self.dict_bool['VI발동해제등록']:
                        self.ViRealreg()
                if now() > self.dict_time['휴무종료']:
                    self.SysExit(True)
            if self.dict_intg['장운영상태'] == 3:
                if not self.dict_bool['실시간조건검색시작']:
                    self.ConditionSearchStart()
                if self.dict_bool['단타목표수익률달성'] and not self.dict_bool['단타전략중단']:
                    self.StopTickStrategy()
            if self.dict_intg['장운영상태'] == 2:
                if not self.dict_bool['실시간조건검색중단']:
                    self.ConditionSearchStop()
                if not self.dict_bool['실시간데이터수신중단']:
                    self.RemoveRealreg()
                if int(strf_time('%H%M%S')) > 152500 and not self.dict_bool['잔고청산']:
                    self.JangoChungsan()
                if int(strf_time('%H%M%S')) > 152500 and not self.dict_bool['단중장기매수주문']:
                    self.PutLongMidShortBuy()
            if self.dict_intg['장운영상태'] == 8:
                if not self.dict_bool['DB저장']:
                    self.SaveDatabase()
                    self.SysExit(False)

            if now() > self.dict_time['호가잔고']:
                self.PutHogaJanngo()
                self.dict_time['호가잔고'] = timedelta_sec(0.25)
            if now() > self.dict_time['거래정보']:
                self.UpdateTotaljango()
                self.dict_time['거래정보'] = timedelta_sec(1)
            if now() > self.dict_time['부가정보']:
                self.UpdateInfo()
                self.dict_time['부가정보'] = timedelta_sec(2)
            time_loop = timedelta_sec(0.25)
            while now() < time_loop:
                pythoncom.PumpWaitingMessages()
                time.sleep(0.0001)

    def SendOrder(self, order):
        name = order[-1]
        del order[-1]
        if order[2] == '':
            code = order[4]
            order[2] = self.dict_strg['계좌번호']
            if order[0] == '매수':
                self.dict_buy[code] = '단타'
            else:
                self.dict_sell[code] = '단타'
            if self.dict_bool['모의투자']:
                c = order[-1]
                oc = order[5]
                self.UpdateChejanData(code, name, '체결', order[0], c, c, oc, 0,
                                      strf_time('%Y%m%d%H%M%S%f'), strf_time('%Y%m%d%H%M%S%f'))
                return
            del order[-1]
        ret = self.ocx.dynamicCall(
            'SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)', order)
        if ret != 0:
            self.windowQ.put([1, f'시스템 명령 오류 알림 - {name} {order[5]}주 {order[0]} 주문 실패'])

    def BuySell(self, gubun, code, name, c, oc):
        stg = gubun[:2]
        og = gubun[2:]

        if og == '매수' and code in self.dict_buy.keys():
            return
        elif og == '매도' and code in self.dict_sell.keys():
            return

        if og == '매수':
            if self.dict_intg[f'{stg}추정예수금'] < oc * c:
                cond = (self.dict_df['체결목록']['주문구분'] == '시드부족') & (self.dict_df['체결목록'].index == code)
                df = self.dict_df['체결목록'][cond]
                if len(df) == 0 or \
                        (len(df) > 0 and now() > timedelta_sec(180, strp_time('%Y%m%d%H%M%S%f', df['체결시간'][0]))):
                    self.dict_buy[code] = stg
                    self.UpdateChejanData(code, name, '체결', '시드부족', c, c, oc, 0,
                                          strf_time('%Y%m%d%H%M%S%f'), strf_time('%Y%m%d%H%M%S%f'))
                return
            else:
                self.dict_intg[f'{stg}추정예수금'] -= oc * c

        if self.dict_bool['모의투자']:
            if og == '매수':
                self.dict_buy[code] = stg
            else:
                self.dict_sell[code] = stg
            self.UpdateChejanData(code, name, '체결', og, c, c, oc, 0,
                                  strf_time('%Y%m%d%H%M%S%f'), strf_time('%Y%m%d%H%M%S%f'))
        else:
            self.Order(code, name, og, oc, stg)

    def Order(self, code, name, og, oc, stg):
        if og == '매수':
            self.dict_buy[code] = stg
            on = 1
        else:
            self.dict_sell[code] = stg
            on = 2
        self.workerQ.put([og, '4989', self.dict_strg['계좌번호'], on, code, oc, 0, '03', '', name])

    def UpdateRealreg(self, rreg):
        name = ''
        if rreg[1] == '001':
            name = '코스피종합'
        elif rreg[1] == '101':
            name = '코스닥종합'
        elif ';' in rreg[1]:
            count = len(rreg[1].split(';'))
            name = f'종목갯수 {count}'
        elif rreg[1] != '' and rreg[1] != ' ' and rreg[1] != 'ALL':
            name = self.dict_name[rreg[1]]

        sn = rreg[0]
        if len(rreg) == 2:
            self.ocx.dynamicCall('SetRealRemove(QString, QString)', rreg)
            if sn == 'ALL' and rreg[1] == 'ALL':
                self.windowQ.put([1, f'실시간 알림 중단 완료 - 모든 실시간 데이터 수신 중단'])
            else:
                self.windowQ.put([1, f'실시간 알림 중단 완료 - [{sn}] {name}'])
        elif len(rreg) == 4:
            ret = self.ocx.dynamicCall('SetRealReg(QString, QString, QString, QString)', rreg)
            result = '완료' if ret == 0 else '실패'
            if sn == sn_oper:
                if rreg[1] == ' ':
                    self.windowQ.put([1, f'실시간 알림 등록 {result} - 장운영시간 [{sn}]'])
                else:
                    self.windowQ.put([1, f'실시간 알림 등록 {result} - 업종지수 [{sn}] {name}'])
            else:
                self.windowQ.put([1, f'실시간 알림 등록 {result} - [{sn}] {name}'])

    def RunWork(self, work):
        if '현재가' in work:
            gubun = int(work.split(' ')[0][3:5])
            code = work.split(' ')[-1]
            name = self.dict_name[code]
            if gubun == ui_num['차트P0']:
                gubun = ui_num['차트P1']
                if ui_num['차트P1'] in self.dict_chat.keys() and code == self.dict_chat[ui_num['차트P1']]:
                    return
                if not self.TrtimeCondition:
                    self.windowQ.put([1, f'시스템 명령 오류 알림 - 해당 명령은 {self.RemainedTrtime}초 후에 실행됩니다.'])
                    Timer(self.RemainedTrtime, self.workerQ.put, args=[work]).start()
                    return
                self.chart6Q.put('기업개요 ' + code)
                self.chart7Q.put('기업공시 ' + code)
                self.chart8Q.put('종목뉴스 ' + code)
                self.chart9Q.put('재무제표 ' + code)
                self.hoga1Q.put('초기화')
                self.workerQ.put([sn_cthg, code, '10;12;14;30;228;41;61;71;81', 1])
                if 0 in self.dict_hoga.keys():
                    self.workerQ.put([sn_cthg, self.dict_hoga[0][0]])
                self.dict_hoga[0] = [code, True, pd.DataFrame(columns=columns_hj)]
                self.GetChart(gubun, code, name)
                self.GetTujajaChegeolH(code)
            elif gubun == ui_num['차트P1']:
                if (ui_num['차트P1'] in self.dict_chat.keys() and code == self.dict_chat[ui_num['차트P1']]) or \
                        (ui_num['차트P3'] in self.dict_chat.keys() and code == self.dict_chat[ui_num['차트P3']]):
                    return
                if not self.TrtimeCondition:
                    self.windowQ.put([1, f'시스템 명령 오류 알림 - 해당 명령은 {self.RemainedTrtime}초 후에 실행됩니다.'])
                    Timer(self.RemainedTrtime, self.workerQ.put, args=[work]).start()
                    return
                self.hoga1Q.put('초기화')
                self.workerQ.put([sn_cthg, code, '10;12;14;30;228;41;61;71;81', 1])
                if 0 in self.dict_hoga.keys():
                    self.workerQ.put([sn_cthg, self.dict_hoga[0][0]])
                self.dict_hoga[0] = [code, True, pd.DataFrame(columns=columns_hj)]
                self.GetChart(gubun, code, name)
            elif gubun == ui_num['차트P3']:
                if (ui_num['차트P1'] in self.dict_chat.keys() and code == self.dict_chat[ui_num['차트P1']]) or \
                        (ui_num['차트P3'] in self.dict_chat.keys() and code == self.dict_chat[ui_num['차트P3']]):
                    return
                if not self.TrtimeCondition:
                    self.windowQ.put([1, f'시스템 명령 오류 알림 - 해당 명령은 {self.RemainedTrtime}초 후에 실행됩니다.'])
                    Timer(self.RemainedTrtime, self.workerQ.put, args=[work]).start()
                    return
                self.hoga2Q.put('초기화')
                self.workerQ.put([sn_cthg, code, '10;12;14;30;228;41;61;71;81', 1])
                if 1 in self.dict_hoga.keys():
                    self.workerQ.put([sn_cthg, self.dict_hoga[1][0]])
                self.dict_hoga[1] = [code, True, pd.DataFrame(columns=columns_hj)]
                self.GetChart(gubun, code, name)
            elif gubun == ui_num['차트P5']:
                tradeday = work.split(' ')[-2]
                if ui_num['차트P5'] in self.dict_chat.keys() and code == self.dict_chat[ui_num['차트P5']]:
                    return
                if int(tradeday) < int(strf_time('%Y%m%d', timedelta_day(-5))):
                    self.windowQ.put([1, f'시스템 명령 오류 알림 - 5일 이전의 체결정보는 조회할 수 없습니다.'])
                    return
                if not self.TrtimeCondition:
                    self.windowQ.put([1, f'시스템 명령 오류 알림 - 해당 명령은 {self.RemainedTrtime}초 후에 실행됩니다.'])
                    Timer(self.RemainedTrtime, self.workerQ.put, args=[work]).start()
                    return
                self.GetChart(gubun, code, name, tradeday)
        elif '매수취소' in work:
            code = work.split(' ')[1]
            name = self.dict_name[code]
            term = (self.dict_df['체결목록']['종목명'] == name) & (self.dict_df['체결목록']['미체결수량'] > 0) & \
                   (self.dict_df['체결목록']['주문구분'] == '매수')
            df = self.dict_df['체결목록'][term]
            if len(df) == 1:
                on = df.index[0]
                omc = df['미체결수량'][on]
                order = ['매수취소', '4989', self.dict_strg['계좌번호'], 3, code, omc, 0, '00', on, name]
                self.workerQ.put(order)
        elif '매도취소' in work:
            code = work.split(' ')[1]
            name = self.dict_name[code]
            term = (self.dict_df['체결목록']['종목명'] == name) & (self.dict_df['체결목록']['미체결수량'] > 0) & \
                   (self.dict_df['체결목록']['주문구분'] == '매도')
            df = self.dict_df['체결목록'][term]
            if len(df) == 1:
                on = df.index[0]
                omc = df['미체결수량'][on]
                order = ['매도취소', '4989', self.dict_strg['계좌번호'], 4, code, omc, 0, '00', on, name]
                self.workerQ.put(order)
        elif work == '데이터베이스 불러오기':
            if not self.dict_bool['DB로딩']:
                self.LoadDatabase()
        elif work == 'OPENAPI 로그인':
            if self.ocx.dynamicCall('GetConnectState()') == 0:
                self.CommConnect()
        elif work == '계좌평가 및 잔고':
            if not self.dict_bool['계좌잔고']:
                self.GetAccountjanGo()
        elif work == '코스피 코스닥 차트':
            if not self.dict_bool['업종차트']:
                self.GetKospiKosdaqChart()
        elif work == '장운영시간 알림 등록':
            if not self.dict_bool['장운영시간']:
                self.OperationRealreg()
        elif work == '업종지수 주식체결 등록':
            if not self.dict_bool['업종지수등록']:
                self.UpjongjisuRealreg()
        elif work == '단중장기 주식체결 등록':
            if not self.dict_bool['단중장기주식체결등록']:
                self.LMSRealreg()
        elif work == 'VI발동해제 등록':
            if not self.dict_bool['VI발동해제등록']:
                self.ViRealreg()
        elif work == '장운영상태':
            if self.dict_intg['장운영상태'] != 3:
                self.windowQ.put([2, '장운영상태'])
                self.dict_intg['장운영상태'] = 3
        elif work == '실시간 조건검색식 등록':
            if not self.dict_bool['실시간조건검색시작']:
                self.ConditionSearchStart()
        elif work == '단타 목표수익률 달성':
            if not self.dict_bool['단타목표수익률달성']:
                self.windowQ.put([2, '단타 목표수익률 달성'])
                self.dict_bool['단타목표수익률달성'] = True
        elif work in ['단타 전략 중단', '/잔고청산주문']:
            if not self.dict_bool['단타전략중단']:
                self.StopTickStrategy()
        elif work == '잔고청산':
            if not self.dict_bool['잔고청산']:
                self.JangoChungsan()
        elif work == '실시간 데이터 수신 중단':
            if not self.dict_bool['실시간조건검색중단']:
                self.ConditionSearchStop()
            if not self.dict_bool['실시간데이터수신중단']:
                self.RemoveRealreg()
        elif work == '단중장기 매수주문':
            if not self.dict_bool['단중장기매수주문']:
                self.PutLongMidShortBuy()
        elif work == '일별거래목록 저장':
            if not self.dict_bool['DB저장']:
                self.SaveDatabase()
        elif work == '시스템 종료':
            if not self.dict_bool['DB저장']:
                self.SaveDatabase()
            self.SysExit(False)
        elif work == '/당일체결목록':
            if len(self.dict_df['체결목록']) > 0:
                self.teleQ.put(self.dict_df['체결목록'])
            else:
                self.teleQ.put('현재는 거래목록이 없습니다.')
        elif work == '/당일거래목록':
            if len(self.dict_df['거래목록']) > 0:
                self.teleQ.put(self.dict_df['거래목록'])
            else:
                self.teleQ.put('현재는 거래목록이 없습니다.')
        elif work == '/계좌잔고평가':
            if len(self.dict_df['잔고목록']) > 0:
                self.teleQ.put(self.dict_df['잔고목록'])
            else:
                self.teleQ.put('현재는 잔고목록이 없습니다.')
        elif '설정' in work:
            bot_number = work.split(' ')[1]
            chat_id = int(work.split(' ')[2])
            self.queryQ.put(f"UPDATE telegram SET str_bot = '{bot_number}'")
            self.queryQ.put(f"UPDATE telegram SET int_id = '{chat_id}'")
            if self.dict_bool['알림소리']:
                self.soundQ.put('텔레그램 봇넘버 및 아이디가 변경되었습니다.')
            else:
                self.windowQ.put([1, '시스템 명령 실행 알림 - 텔레그램 봇넘버 및 아이디 설정 완료'])
        elif work == '테스트모드 ON/OFF':
            if self.dict_bool['테스트']:
                self.dict_bool['테스트'] = False
                self.queryQ.put('UPDATE setting SET 테스트 = 0')
                self.windowQ.put([2, '테스트모드 OFF'])
                if self.dict_bool['알림소리']:
                    self.soundQ.put('테스트모드 설정이 OFF로 변경되었습니다.')
            else:
                self.dict_bool['테스트'] = True
                self.queryQ.put('UPDATE setting SET 테스트 = 1')
                self.windowQ.put([2, '테스트모드 ON'])
                if self.dict_bool['알림소리']:
                    self.soundQ.put('테스트모드 설정이 ON으로 변경되었습니다.')
        elif work == '모의투자 ON/OFF':
            if self.dict_bool['모의투자']:
                self.dict_bool['모의투자'] = False
                self.queryQ.put('UPDATE setting SET 모의투자 = 0')
                self.windowQ.put([2, '모의투자 OFF'])
                if self.dict_bool['알림소리']:
                    self.soundQ.put('모의투자 설정이 OFF로 변경되었습니다.')
            else:
                self.dict_bool['모의투자'] = True
                self.queryQ.put('UPDATE setting SET 모의투자 = 1')
                self.windowQ.put([2, '모의투자 ON'])
                if self.dict_bool['알림소리']:
                    self.soundQ.put('모의투자 설정이 ON으로 변경되었습니다.')
        elif work == '알림소리 ON/OFF':
            if self.dict_bool['알림소리']:
                self.dict_bool['알림소리'] = False
                self.queryQ.put('UPDATE setting SET 알림소리 = 0')
                self.windowQ.put([2, '알림소리 OFF'])
                if self.dict_bool['알림소리']:
                    self.soundQ.put('알림소리 설정이 OFF로 변경되었습니다.')
            else:
                self.dict_bool['알림소리'] = True
                self.queryQ.put('UPDATE setting SET 알림소리 = 1')
                self.windowQ.put([2, '알림소리 ON'])
                if self.dict_bool['알림소리']:
                    self.soundQ.put('알림소리 설정이 ON으로 변경되었습니다.')

    def GetChart(self, gubun, code, name, tradeday=None):
        prec = self.GetMasterLastPrice(code)
        if gubun in [ui_num['차트P1'], ui_num['차트P3']]:
            df = self.Block_Request('opt10081', 종목코드=code, 기준일자=self.dict_strg['당일날짜'], 수정주가구분=1,
                                    output='주식일봉차트조회', next=0)
            df2 = self.Block_Request('opt10080', 종목코드=code, 틱범위=3, 수정주가구분=1, output='주식분봉차트조회', next=0)
            if gubun == ui_num['차트P1']:
                self.chart1Q.put([name, prec, df, ''])
                self.chart2Q.put([name, prec, df2, ''])
            elif gubun == ui_num['차트P3']:
                self.chart3Q.put([name, prec, df, ''])
                self.chart4Q.put([name, prec, df2, ''])
        elif gubun == ui_num['차트P5'] and tradeday is not None:
            df2 = self.Block_Request('opt10080', 종목코드=code, 틱범위=3, 수정주가구분=1, output='주식분봉차트조회', next=0)
            self.chart5Q.put([name, prec, df2, tradeday])
        self.dict_chat[gubun] = code

    def GetTujajaChegeolH(self, code):
        df1 = self.Block_Request('opt10059', 일자=self.dict_strg['당일날짜'], 종목코드=code, 금액수량구분=1, 매매구분=0,
                                 단위구분=1, output='종목별투자자', next=0)
        df2 = self.Block_Request('opt10046', 종목코드=code, 틱구분=1, 체결강도구분=1, output='체결강도추이', next=0)
        self.chart1Q.put([code, df1, df2])

    def GetAccountjanGo(self):
        self.windowQ.put([2, '계좌평가 및 잔고'])
        jggm = 0
        pggm = 0
        sigm = 0
        if len(self.dict_df['잔고목록']) > 0:
            jggm = self.dict_df['잔고목록']['매입금액'].sum()
            pggm = self.dict_df['잔고목록']['평가금액'].sum()
        if len(self.dict_df['거래목록']) > 0:
            sigm = self.dict_df['거래목록']['수익금'].sum()

        while True:
            df = self.Block_Request('opw00004', 계좌번호=self.dict_strg['계좌번호'], 비밀번호='', 상장폐지조회구분=0,
                                    비밀번호입력매체구분='00', output='계좌평가현황', next=0)
            if df['D+2추정예수금'][0] != '':
                if self.dict_bool['모의투자']:
                    self.dict_intg['예수금'] = 100000000 - jggm + sigm
                else:
                    self.dict_intg['예수금'] = int(df['D+2추정예수금'][0])
                break
            else:
                self.windowQ.put([1, '시스템 명령 오류 알림 - 오류가 발생하여 계좌평가현황을 재조회합니다.'])
                time.sleep(3.35)

        while True:
            df = self.Block_Request('opw00018', 계좌번호=self.dict_strg['계좌번호'], 비밀번호='', 비밀번호입력매체구분='00',
                                    조회구분=2, output='계좌평가결과', next=0)
            if df['추정예탁자산'][0] != '':
                if self.dict_bool['모의투자']:
                    chujeongjasan = self.dict_intg['예수금'] + pggm
                else:
                    chujeongjasan = int(df['추정예탁자산'][0])
                self.dict_intg['단타투자금액'] = int(chujeongjasan * 0.249)
                self.dict_intg['단기투자금액'] = int(chujeongjasan * 0.249)
                self.dict_intg['중기투자금액'] = int(chujeongjasan * 0.249)
                self.dict_intg['장기투자금액'] = int(chujeongjasan * 0.249)
                tick_pggm = self.dict_df['잔고목록'][self.dict_df['잔고목록']['전략구분'] == '단타']['평가금액'].sum()
                short_pggm = self.dict_df['잔고목록'][self.dict_df['잔고목록']['전략구분'] == '단기']['평가금액'].sum()
                mid_pggm = self.dict_df['잔고목록'][self.dict_df['잔고목록']['전략구분'] == '중기']['평가금액'].sum()
                long_pggm = self.dict_df['잔고목록'][self.dict_df['잔고목록']['전략구분'] == '장기']['평가금액'].sum()
                self.dict_intg['단타예수금'] = self.dict_intg['단타투자금액'] - tick_pggm
                self.dict_intg['단기예수금'] = self.dict_intg['단기투자금액'] - short_pggm
                self.dict_intg['장기예수금'] = self.dict_intg['중기투자금액'] - mid_pggm
                self.dict_intg['중기예수금'] = self.dict_intg['장기투자금액'] - long_pggm
                self.dict_intg['단타추정예수금'] = self.dict_intg['단타예수금']
                self.dict_intg['단기추정예수금'] = self.dict_intg['단기예수금']
                self.dict_intg['중기추정예수금'] = self.dict_intg['장기예수금']
                self.dict_intg['장기추정예수금'] = self.dict_intg['중기예수금']
                if self.dict_bool['모의투자']:
                    self.dict_df['잔고평가'].at[self.dict_strg['당일날짜']] = \
                        chujeongjasan, self.dict_intg['예수금'], 0, 0, 0, 0, 0
                else:
                    tsp = float(int(df['총수익률(%)'][0]) / 100)
                    tsg = int(df['총평가손익금액'][0])
                    tbg = int(df['총매입금액'][0])
                    tpg = int(df['총평가금액'][0])
                    self.dict_df['잔고평가'].at[self.dict_strg['당일날짜']] = \
                        chujeongjasan, self.dict_intg['예수금'], 0, tsp, tsg, tbg, tpg
                self.windowQ.put([ui_num['잔고평가'], self.dict_df['잔고평가']])
                break
            else:
                self.windowQ.put([1, '시스템 명령 오류 알림 - 오류가 발생하여 계좌평가결과를 재조회합니다.'])
                time.sleep(3.35)

        if len(self.dict_df['잔고목록']) > 0:
            count = len(self.dict_df['잔고목록'])
            k = 0
            for i in range(0, count, 100):
                self.workerQ.put([sn_jgjc + k, ';'.join(self.dict_df['잔고목록'].index[i:i + 100]), '10;12;14;30;228', 1])
                k += 1

        self.dict_bool['계좌잔고'] = True

    def GetKospiKosdaqChart(self):
        self.windowQ.put([2, '코스피 코스닥 차트'])
        while True:
            df = self.Block_Request('opt20006', 업종코드='001', 기준일자=self.dict_strg['당일날짜'],
                                    output='업종일봉조회', next=0)
            if df['현재가'][0] != '':
                break
            else:
                self.windowQ.put([1, '시스템 명령 오류 알림 - 오류가 발생하여 코스피 일봉차트를 재조회합니다.'])
                time.sleep(3.35)

        while True:
            df2 = self.Block_Request('opt20005', 업종코드='001', 틱범위='3', output='업종분봉조회', next=0)
            if df2['현재가'][0] != '':
                break
            else:
                self.windowQ.put([1, '시스템 명령 오류 알림 - 오류가 발생하여 코스피 분봉차트를 재조회합니다.'])
                time.sleep(3.35)

        prec = abs(round(float(df['현재가'][1]) / 100, 2))
        self.chart6Q.put(['코스피종합', prec, df, ''])
        self.chart7Q.put(['코스피종합', prec, df2, ''])

        while True:
            df = self.Block_Request('opt20006', 업종코드='101', 기준일자=self.dict_strg['당일날짜'],
                                    output='업종일봉조회', next=0)
            if df['현재가'][0] != '':
                break
            else:
                self.windowQ.put([1, '시스템 명령 오류 알림 - 오류가 발생하여 코스닥 일봉차트를 재조회합니다.'])
                time.sleep(3.35)

        while True:
            df2 = self.Block_Request('opt20005', 업종코드='101', 틱범위='3', output='업종분봉조회', next=0)
            if df2['현재가'][0] != '':
                break
            else:
                self.windowQ.put([1, '시스템 명령 오류 알림 - 오류가 발생하여 코스닥 분봉차트를 재조회합니다.'])
                time.sleep(3.35)

        prec = abs(round(float(df['현재가'][1]) / 100, 2))
        self.chart8Q.put(['코스닥종합', prec, df, ''])
        self.chart9Q.put(['코스닥종합', prec, df2, ''])
        self.dict_bool['업종차트'] = True
        time.sleep(1)

    def OperationRealreg(self):
        self.windowQ.put([2, '장운영시간 알림 등록'])
        self.workerQ.put([sn_oper, ' ', '215;20;214', 0])
        self.dict_bool['장운영시간'] = True

    def UpjongjisuRealreg(self):
        self.windowQ.put([2, '업종지수 주식체결 등록'])
        self.workerQ.put([sn_oper, '001', '10;15;20', 1])
        self.workerQ.put([sn_oper, '101', '10;15;20', 1])
        self.dict_bool['업종지수등록'] = True

    def LMSRealreg(self):
        self.windowQ.put([2, '단중장기 주식체결 등록'])
        self.stgsQ.put('데이터베이스로딩')
        self.stgmQ.put('데이터베이스로딩')
        self.stglQ.put('데이터베이스로딩')

        count = len(self.list_short)
        k = 0
        for i in range(0, count, 100):
            self.workerQ.put([sn_short + k, ';'.join(self.list_short[i:i+100]), '10;12;14;30;228', 1])
            k += 1

        count = len(self.list_mid)
        k = 0
        for i in range(0, count, 100):
            self.workerQ.put([sn_mid + k, ';'.join(self.list_mid[i:i+100]), '10;12;14;30;228', 1])
            k += 1

        count = len(self.list_long)
        k = 0
        for i in range(0, count, 100):
            self.workerQ.put([sn_long + k, ';'.join(self.list_long[i:i+100]), '10;12;14;30;228', 1])
            k += 1

        self.dict_bool['단중장기주식체결등록'] = True

    def ViRealreg(self):
        self.windowQ.put([2, 'VI발동해제 등록'])
        self.Block_Request('opt10054', 시장구분='000', 장전구분='1', 종목코드='', 발동구분='1', 제외종목='111111011',
                           거래량구분='0', 거래대금구분='0', 발동방향='0', output='발동종목', next=0)
        if self.dict_bool['알림소리']:
            self.soundQ.put('자동매매 시스템을 시작하였습니다.')
        else:
            self.windowQ.put([1, '시스템 명령 실행 알림 - 시스템 시작 완료'])
        self.teleQ.put('자동매매 시스템을 시작하였습니다.')
        self.dict_bool['VI발동해제등록'] = True

    def ConditionSearchStart(self):
        self.windowQ.put([2, '실시간 조건검색식 등록'])
        codes = self.SendCondition(sn_cond, self.dict_cond[0], 0, 1)
        last = len(codes) - 1
        for i, code in enumerate(codes):
            self.list_gsjm.append(code)
            if i != last:
                self.stgtQ.put(['조건진입', code])
            else:
                self.stgtQ.put(['조건진입마지막', code])
        self.workerQ.put([sn_jscg, ';'.join(codes), '10;12;14;30;228', 1])
        if self.dict_bool['알림소리']:
            self.soundQ.put('실시간 조건검색식을 등록하였습니다.')
        self.windowQ.put([1, f'시스템 명령 실행 알림 - 실시간 조건검색식 등록 완료'])
        self.dict_bool['실시간조건검색시작'] = True

    def StopTickStrategy(self):
        self.windowQ.put([2, '단타 전략 중단'])
        if not self.dict_bool['실시간조건검색중단']:
            self.ConditionSearchStop()
        if not self.dict_bool['잔고청산']:
            self.JangoChungsan()
        self.workerQ.put([sn_jscg, 'ALL'])
        self.workerQ.put([sn_brrd, 'ALL'])
        self.dict_bool['단타전략중단'] = True

    def ConditionSearchStop(self):
        self.ocx.dynamicCall("SendConditionStop(QString, QString, int)", sn_cond, self.dict_cond[0], 0)
        self.windowQ.put([1, f'시스템 명령 실행 알림 - 실시간조건검색식 중단 완료'])
        self.dict_bool['실시간조건검색중단'] = True

    def RemoveRealreg(self):
        self.windowQ.put([2, '실시간 데이터 수신 중단'])
        self.workerQ.put(['ALL', 'ALL'])
        if self.dict_bool['알림소리']:
            self.soundQ.put('실시간 데이터의 수신을 중단하였습니다.')
        self.windowQ.put([1, f'시스템 명령 실행 알림 - 실시간 데이터 중단 완료'])
        self.dict_bool['실시간데이터수신중단'] = True

    def JangoChungsan(self):
        self.windowQ.put([2, '잔고청산'])
        if len(self.dict_df['잔고목록']) > 0:
            for code in self.dict_df['잔고목록'].index:
                if self.dict_df['잔고목록']['전략구분'][code] == '단타':
                    c = self.dict_df['잔고목록']['현재가'][code]
                    oc = self.dict_df['잔고목록']['보유수량'][code]
                    name = self.dict_name[code]
                    if self.dict_bool['모의투자']:
                        self.dict_sell[code] = '단타'
                        self.UpdateChejanData(code, name, '체결', '매도', c, c, oc, 0,
                                              strf_time('%Y%m%d%H%M%S%f'), strf_time('%Y%m%d%H%M%S%f'))
                    else:
                        self.Order(code, name, '매도', oc, '단타')
        if self.dict_bool['알림소리']:
            self.soundQ.put('잔고청산 주문을 전송하였습니다.')
        self.windowQ.put([1, '시스템 명령 실행 알림 - 잔고청산 주문 완료'])
        self.dict_bool['잔고청산'] = True

    def PutLongMidShortBuy(self):
        self.windowQ.put([2, '단중장기 매수주문'])
        self.stglQ.put([self.dict_name, list(self.dict_df['잔고목록'].index), self.dict_intg['장기투자금액']])
        self.stgmQ.put([self.dict_name, list(self.dict_df['잔고목록'].index), self.dict_intg['중기투자금액']])
        self.stgsQ.put([self.dict_name, list(self.dict_df['잔고목록'].index), self.dict_intg['단기투자금액']])
        if self.dict_bool['알림소리']:
            self.soundQ.put('단중장기 매수전략을 확인 중입니다.')
        self.windowQ.put([1, '시스템 명령 실행 알림 - 단중장기 매수전략 확인 중 ...'])
        self.dict_bool['단중장기매수주문'] = True

    def SaveDatabase(self):
        self.windowQ.put([2, '일별거래목록 저장'])
        self.queryQ.put([self.dict_df['잔고목록'], 'jangolist', 'replace'])
        if len(self.dict_df['거래목록']) > 0:
            df = self.dict_df['실현손익'][['총매수금액', '총매도금액', '총수익금액', '총손실금액', '수익률', '수익금합계']].copy()
            self.queryQ.put([df, 'totaltradelist', 'append'])
        if self.dict_bool['알림소리']:
            self.soundQ.put('일별거래목록을 저장하였습니다.')
        self.windowQ.put([1, '시스템 명령 실행 알림 - 일별거래목록 저장 완료'])
        self.dict_bool['DB저장'] = True

    @thread_decorator
    def PutHogaJanngo(self):
        if 0 in self.dict_hoga.keys() and self.dict_hoga[0][1]:
            self.windowQ.put([ui_num['호가잔고0'], self.dict_hoga[0][2]])
            self.dict_hoga[0][1] = False
        if 1 in self.dict_hoga.keys() and self.dict_hoga[1][1]:
            self.windowQ.put([ui_num['호가잔고1'], self.dict_hoga[1][2]])
            self.dict_hoga[1][1] = False

    @thread_decorator
    def UpdateTotaljango(self):
        if len(self.dict_df['잔고목록']) > 0:
            tsg = self.dict_df['잔고목록']['평가손익'].sum()
            tbg = self.dict_df['잔고목록']['매입금액'].sum()
            tpg = self.dict_df['잔고목록']['평가금액'].sum()
            bct = len(self.dict_df['잔고목록'])
            tsp = round(tsg / tbg * 100, 2)
            ttg = self.dict_intg['예수금'] + tpg
            self.dict_df['잔고평가'].at[self.dict_strg['당일날짜']] = \
                ttg, self.dict_intg['예수금'], bct, tsp, tsg, tbg, tpg
        else:
            self.dict_df['잔고평가'].at[self.dict_strg['당일날짜']] = \
                self.dict_intg['예수금'], self.dict_intg['예수금'], 0, 0.0, 0, 0, 0
        self.windowQ.put([ui_num['잔고목록'], self.dict_df['잔고목록']])
        self.windowQ.put([ui_num['잔고평가'], self.dict_df['잔고평가']])

        if not self.dict_bool['단타목표수익률달성']:
            psg = self.dict_df['거래목록'][self.dict_df['거래목록']['전략구분'] == '단타']['수익금'].sum()
            tsg = self.dict_df['잔고목록'][self.dict_df['잔고목록']['전략구분'] == '단타']['평가손익'].sum()
            tick_tsg = psg + tsg
            if self.dict_intg['단타투자금액'] * 0.02 < tick_tsg:
                if self.dict_intg['단타최고수익금'] == 0:
                    self.dict_intg['단타최고수익금'] = tick_tsg
                elif self.dict_intg['단타최고수익금'] < tick_tsg:
                    self.dict_intg['단타최고수익금'] = tick_tsg
                elif self.dict_intg['단타최고수익금'] * 0.80 > tick_tsg:
                    self.windowQ.put([2, '단타 목표수익률 달성'])
                    self.dict_bool['단타목표수익률달성'] = True
                    self.teleQ.put('단타 목표수익률 달성')

    @thread_decorator
    def UpdateInfo(self):
        info = [3, self.dict_intg['메모리'], self.dict_intg['스레드'], self.dict_intg['시피유'],
                self.dict_intg['TR수신횟수'], self.dict_intg['체결잔고수신횟수'], self.dict_intg['주식체결수신횟수'],
                self.dict_intg['호가잔량수신횟수'], self.dict_intg['초당주식체결수신횟수'], self.dict_intg['초당호가잔량수신횟수']]
        self.windowQ.put(info)
        self.dict_intg['초당주식체결수신횟수'] = 0
        self.dict_intg['초당호가잔량수신횟수'] = 0
        self.UpdateSysinfo()

    def UpdateSysinfo(self):
        p = psutil.Process(os.getpid())
        self.dict_intg['메모리'] = round(p.memory_info()[0] / 2 ** 20.86, 2)
        self.dict_intg['스레드'] = p.num_threads()
        self.dict_intg['시피유'] = round(p.cpu_percent(interval=2) / 2, 2)

    def OnEventConnect(self, err_code):
        if err_code == 0:
            self.dict_bool['로그인'] = True

    def OnReceiveTrData(self, screen, rqname, trcode, record, nnext):
        if screen == '' and record == '':
            return
        if 'ORD' in trcode:
            return

        items = None
        self.dict_bool['TR다음'] = True if nnext == '2' else False
        for output in self.dict_item['output']:
            record = list(output.keys())[0]
            items = list(output.values())[0]
            if record == self.dict_strg['TR명']:
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
        self.dict_df['TRDF'] = df
        self.dict_bool['TR수신'] = True
        self.windowQ.put([1, f"조회 데이터 수신 완료 - {rqname} [{trcode}] {self.dict_strg['TR종목명']}"])

    def OnReceiveRealCondition(self, code, IorD, cname, cindex):
        if cname == '' and cindex == '':
            return
        if self.dict_bool['단타목표수익률달성']:
            return

        if IorD == 'I':
            self.stgtQ.put(['조건진입', code])
            if code not in self.list_gsjm:
                self.list_gsjm.append(code)
            self.workerQ.put([sn_jscg, code, '10;12;14;30;228', 1])
        elif IorD == 'D':
            if code not in self.dict_df['잔고목록'].index and code not in self.dict_buy.keys():
                self.stgtQ.put(['조건이탈', code])
                if code in self.list_gsjm:
                    self.list_gsjm.remove(code)
                self.workerQ.put([sn_jscg, code])

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
                self.windowQ.put([1, f'OnReceiveRealData 장시작시간 {e}'])
            else:
                self.OperationAlert(current, remain)
        elif realtype == '업종지수':
            if self.dict_bool['실시간데이터수신중단']:
                return
            self.dict_intg['주식체결수신횟수'] += 1
            self.dict_intg['초당주식체결수신횟수'] += 1
            try:
                c = abs(float(self.GetCommRealData(code, 10)))
                v = int(self.GetCommRealData(code, 15))
                d = self.GetCommRealData(code, 20)
            except Exception as e:
                self.windowQ.put([1, f'OnReceiveRealData 업종지수 {e}'])
            else:
                self.UpdateUpjongjisu(code, d, c, v)
        elif realtype == 'VI발동/해제':
            if self.dict_bool['실시간데이터수신중단']:
                return
            if self.dict_bool['단타목표수익률달성']:
                return

            try:
                code = self.GetCommRealData(code, 9001).strip('A').strip('Q')
                gubun = self.GetCommRealData(code, 9068)
                name = self.dict_name[code]
            except Exception as e:
                self.windowQ.put([1, f'OnReceiveRealData VI발동/해제 {e}'])
            else:
                if gubun == '1' and (code not in self.dict_vipr.keys() or
                                     (self.dict_vipr[code][0] and now() > self.dict_vipr[code][1])):
                    self.UpdateViPrice(code, name)
        elif realtype == '주식체결':
            if self.dict_bool['실시간데이터수신중단']:
                return
            self.dict_intg['주식체결수신횟수'] += 1
            self.dict_intg['초당주식체결수신횟수'] += 1
            try:
                c = abs(int(self.GetCommRealData(code, 10)))
                o = abs(int(self.GetCommRealData(code, 16)))
                h = abs(int(self.GetCommRealData(code, 17)))
                low = abs(int(self.GetCommRealData(code, 18)))
                per = float(self.GetCommRealData(code, 12))
                v = int(self.GetCommRealData(code, 15))
                ch = float(self.GetCommRealData(code, 228))
                dm = int(self.GetCommRealData(code, 14))
                vp = abs(float(self.GetCommRealData(code, 30)))
                d = self.GetCommRealData(code, 20)
                name = self.dict_name[code]
                prec = self.GetMasterLastPrice(code)
            except Exception as e:
                self.windowQ.put([1, f'OnReceiveRealData 주식체결 {e}'])
            else:
                if not self.dict_bool['단타목표수익률달성']:
                    if code not in self.dict_vipr.keys():
                        self.InsertViPrice(code, o)
                    if code in self.dict_vipr.keys() and not self.dict_vipr[code][0] and \
                            now() > self.dict_vipr[code][1]:
                        self.UpdateViPrice(code, c)
                    if code in self.list_gsjm:
                        injango = True if code in self.dict_df['잔고목록'].index else False
                        vitimedown = True if now() < self.dict_vipr[code][2] else False
                        vid5priceup = True if c >= self.dict_vipr[code][5] else False
                        self.stgtQ.put([code, name, c, o, h, low, per, ch, dm, vp, d,
                                        injango, vitimedown, vid5priceup, self.dict_intg['단타투자금액']])
                """
                단기, 중기, 장기 전략 완성 후 활성화
                if int(d) > 150000:
                    if code in self.list_long:
                        self.stglQ.put([code, c, d])
                    if code in self.list_mid:
                        self.stgmQ.put([code, c, low, d])
                    if code in self.list_short:
                        self.stgsQ.put([code, c, o, per, d])
                """
                if code in self.dict_df['잔고목록'].index:
                    self.UpdateJango(code, name, c, o, h, low, per, ch)
                self.UpdateChartHoga(code, name, c, o, h, low, per, ch, v, d, prec)
        elif realtype == '주식호가잔량':
            if self.dict_bool['실시간데이터수신중단']:
                return
            self.dict_intg['호가잔량수신횟수'] += 1
            self.dict_intg['초당호가잔량수신횟수'] += 1
            if (0 in self.dict_hoga.keys() and code == self.dict_hoga[0][0]) or \
                    (1 in self.dict_hoga.keys() and code == self.dict_hoga[1][0]):
                try:
                    if code not in self.dict_sghg.keys():
                        Sanghanga, Hahanga = self.GetSangHahanga(code)
                        self.dict_sghg[code] = [Sanghanga, Hahanga]
                    else:
                        Sanghanga = self.dict_sghg[code][0]
                        Hahanga = self.dict_sghg[code][1]
                    prec = self.GetMasterLastPrice(code)
                    vp = [int(float(self.GetCommRealData(code, 139))),
                          int(self.GetCommRealData(code, 90)), int(self.GetCommRealData(code, 89)),
                          int(self.GetCommRealData(code, 88)), int(self.GetCommRealData(code, 87)),
                          int(self.GetCommRealData(code, 86)), int(self.GetCommRealData(code, 85)),
                          int(self.GetCommRealData(code, 84)), int(self.GetCommRealData(code, 83)),
                          int(self.GetCommRealData(code, 82)), int(self.GetCommRealData(code, 81)),
                          int(self.GetCommRealData(code, 91)), int(self.GetCommRealData(code, 92)),
                          int(self.GetCommRealData(code, 93)), int(self.GetCommRealData(code, 94)),
                          int(self.GetCommRealData(code, 95)), int(self.GetCommRealData(code, 96)),
                          int(self.GetCommRealData(code, 97)), int(self.GetCommRealData(code, 98)),
                          int(self.GetCommRealData(code, 99)), int(self.GetCommRealData(code, 100)),
                          int(float(self.GetCommRealData(code, 129)))]
                    jc = [int(self.GetCommRealData(code, 121)),
                          int(self.GetCommRealData(code, 70)), int(self.GetCommRealData(code, 69)),
                          int(self.GetCommRealData(code, 68)), int(self.GetCommRealData(code, 67)),
                          int(self.GetCommRealData(code, 66)), int(self.GetCommRealData(code, 65)),
                          int(self.GetCommRealData(code, 64)), int(self.GetCommRealData(code, 63)),
                          int(self.GetCommRealData(code, 62)), int(self.GetCommRealData(code, 61)),
                          int(self.GetCommRealData(code, 71)), int(self.GetCommRealData(code, 72)),
                          int(self.GetCommRealData(code, 73)), int(self.GetCommRealData(code, 74)),
                          int(self.GetCommRealData(code, 75)), int(self.GetCommRealData(code, 76)),
                          int(self.GetCommRealData(code, 77)), int(self.GetCommRealData(code, 78)),
                          int(self.GetCommRealData(code, 79)), int(self.GetCommRealData(code, 80)),
                          int(self.GetCommRealData(code, 125))]
                    hg = [Sanghanga,
                          abs(int(self.GetCommRealData(code, 50))), abs(int(self.GetCommRealData(code, 49))),
                          abs(int(self.GetCommRealData(code, 48))), abs(int(self.GetCommRealData(code, 47))),
                          abs(int(self.GetCommRealData(code, 46))), abs(int(self.GetCommRealData(code, 45))),
                          abs(int(self.GetCommRealData(code, 44))), abs(int(self.GetCommRealData(code, 43))),
                          abs(int(self.GetCommRealData(code, 42))), abs(int(self.GetCommRealData(code, 41))),
                          abs(int(self.GetCommRealData(code, 51))), abs(int(self.GetCommRealData(code, 52))),
                          abs(int(self.GetCommRealData(code, 53))), abs(int(self.GetCommRealData(code, 54))),
                          abs(int(self.GetCommRealData(code, 55))), abs(int(self.GetCommRealData(code, 56))),
                          abs(int(self.GetCommRealData(code, 57))), abs(int(self.GetCommRealData(code, 58))),
                          abs(int(self.GetCommRealData(code, 59))), abs(int(self.GetCommRealData(code, 60))),
                          Hahanga]
                    per = [round((hg[0] / prec - 1) * 100, 2), round((hg[1] / prec - 1) * 100, 2),
                           round((hg[2] / prec - 1) * 100, 2), round((hg[3] / prec - 1) * 100, 2),
                           round((hg[4] / prec - 1) * 100, 2), round((hg[5] / prec - 1) * 100, 2),
                           round((hg[6] / prec - 1) * 100, 2), round((hg[7] / prec - 1) * 100, 2),
                           round((hg[8] / prec - 1) * 100, 2), round((hg[9] / prec - 1) * 100, 2),
                           round((hg[10] / prec - 1) * 100, 2), round((hg[11] / prec - 1) * 100, 2),
                           round((hg[12] / prec - 1) * 100, 2), round((hg[13] / prec - 1) * 100, 2),
                           round((hg[14] / prec - 1) * 100, 2), round((hg[15] / prec - 1) * 100, 2),
                           round((hg[16] / prec - 1) * 100, 2), round((hg[17] / prec - 1) * 100, 2),
                           round((hg[18] / prec - 1) * 100, 2), round((hg[19] / prec - 1) * 100, 2),
                           round((hg[20] / prec - 1) * 100, 2), round((hg[21] / prec - 1) * 100, 2)]
                except Exception as e:
                    self.windowQ.put([1, f'OnReceiveRealData 주식호가잔량 {e}'])
                else:
                    self.UpdateHogajanryang(code, vp, jc, hg, per)

    @thread_decorator
    def OperationAlert(self, current, remain):
        if self.dict_intg['장운영상태'] == 3:
            self.windowQ.put([2, '장운영상태'])
        if self.dict_bool['알림소리']:
            if current == '084000':
                self.soundQ.put('장시작 20분 전입니다.')
            elif current == '085000':
                self.soundQ.put('장시작 10분 전입니다.')
            elif current == '085500':
                self.soundQ.put('장시작 5분 전입니다.')
            elif current == '085900':
                self.soundQ.put('장시작 1분 전입니다.')
            elif current == '085930':
                self.soundQ.put('장시작 30초 전입니다.')
            elif current == '085940':
                self.soundQ.put('장시작 20초 전입니다.')
            elif current == '085950':
                self.soundQ.put('장시작 10초 전입니다.')
            elif current == '090000':
                self.soundQ.put(f"{self.dict_strg['당일날짜'][:4]}년 {self.dict_strg['당일날짜'][4:6]}월 "
                                f"{self.dict_strg['당일날짜'][6:]}일 장이 시작되었습니다.")
            elif current == '152000':
                self.soundQ.put('장마감 10분 전입니다.')
            elif current == '152500':
                self.soundQ.put('장마감 5분 전입니다.')
            elif current == '152900':
                self.soundQ.put('장마감 1분 전입니다.')
            elif current == '152930':
                self.soundQ.put('장마감 30초 전입니다.')
            elif current == '152940':
                self.soundQ.put('장마감 20초 전입니다.')
            elif current == '152950':
                self.soundQ.put('장마감 10초 전입니다.')
            elif current == '153000':
                self.soundQ.put(f"{self.dict_strg['당일날짜'][:4]}년 {self.dict_strg['당일날짜'][4:6]}월 "
                                f"{self.dict_strg['당일날짜'][6:]}일 장이 종료되었습니다.")
        else:
            self.windowQ.put([1, f"장운영 시간 수신 알림 - {self.dict_intg['장운영상태']} "
                                 f'{current[:2]}:{current[2:4]}:{current[4:]} '
                                 f'남은시간 {remain[:2]}:{remain[2:4]}:{remain[4:]}'])

    @thread_decorator
    def UpdateUpjongjisu(self, code, d, c, v):
        if code == '001':
            self.chart6Q.put([d, c, v])
            self.chart7Q.put([d, c, v])
        elif code == '101':
            self.chart8Q.put([d, c, v])
            self.chart9Q.put([d, c, v])

    def InsertViPrice(self, code, o):
        uvi, dvi, uvid5 = self.GetVIPrice(code, o)
        self.dict_vipr[code] = [True, timedelta_sec(-180), timedelta_sec(-180), uvi, dvi, uvid5]

    def GetVIPrice(self, code, std_price):
        uvi = std_price * 1.1
        x = self.GetHogaunit(code, uvi)
        if uvi % x != 0:
            uvi = uvi + (x - uvi % x)
        uvid5 = uvi - x * 5

        dvi = std_price * 0.9
        x = self.GetHogaunit(code, dvi)
        if dvi % x != 0:
            dvi = dvi - dvi % x

        return int(uvi), int(dvi), int(uvid5)

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

    def UpdateViPrice(self, code, key):
        if type(key) == str:
            try:
                self.dict_vipr[code][:3] = False, timedelta_sec(5), timedelta_sec(180)
            except KeyError:
                self.dict_vipr[code] = [False, timedelta_sec(5), timedelta_sec(180), 0, 0, 0]
            self.windowQ.put([1, f'변동성 완화 장치 발동 - [{code}] {key}'])
            self.workerQ.put([sn_vijc, code, '10;12;14;30;228', 1])
        elif type(key) == int:
            uvi, dvi, uvid5 = self.GetVIPrice(code, key)
            self.dict_vipr[code] = [True, now(), timedelta_sec(180), uvi, dvi, uvid5]
            self.workerQ.put([sn_vijc, code])

    def UpdateJango(self, code, name, c, o, h, low, per, ch):
        try:
            pc = self.dict_df['잔고목록']['현재가'][code]
        except IndexError:
            return

        if pc != c:
            self.lock.acquire()
            bg = self.dict_df['잔고목록']['매입금액'][code]
            jc = self.dict_df['잔고목록']['보유수량'][code]
            pg, sg, sp = self.GetPgSgSp(bg, jc * c)
            columns = ['현재가', '수익률', '평가손익', '평가금액', '시가', '고가', '저가']
            self.dict_df['잔고목록'].at[code, columns] = c, sp, sg, pg, o, h, low
            self.lock.release()

            if self.dict_df['잔고목록']['전략구분'][code] == '단타':
                self.stgtQ.put([code, name, per, sp, jc, ch, c])
            elif self.dict_df['잔고목록']['전략구분'][code] == '장기':
                self.stglQ.put([code, name, jc, sp, c])
            elif self.dict_df['잔고목록']['전략구분'][code] == '중기':
                self.stgmQ.put([code, name, jc, sp, c])
            elif self.dict_df['잔고목록']['전략구분'][code] == '단기':
                self.stgsQ.put([code, name, jc, sp, c])

    # noinspection PyMethodMayBeStatic
    def GetPgSgSp(self, bg, cg):
        gtexs = cg * 0.0023
        gsfee = cg * 0.00015
        gbfee = bg * 0.00015
        texs = gtexs - (gtexs % 1)
        sfee = gsfee - (gsfee % 10)
        bfee = gbfee - (gbfee % 10)
        pg = int(cg - texs - sfee - bfee)
        sg = pg - bg
        sp = round(sg / bg * 100, 2)
        return pg, sg, sp

    @thread_decorator
    def UpdateChartHoga(self, code, name, c, o, h, low, per, ch, v, d, prec):
        if ui_num['차트P1'] in self.dict_chat.keys() and code == self.dict_chat[ui_num['차트P1']]:
            self.chart1Q.put([code, d, c, per, ch])
            self.chart1Q.put([d, c, v])
            self.chart2Q.put([d, c, v])
        elif ui_num['차트P3'] in self.dict_chat.keys() and code == self.dict_chat[ui_num['차트P3']]:
            self.chart3Q.put([d, c, v])
            self.chart4Q.put([d, c, v])

        if 0 in self.dict_hoga.keys() and code == self.dict_hoga[0][0]:
            self.hoga1Q.put([v, ch])
            self.UpdateHogajango(0, code, name, c, o, h, low, prec)
        elif 1 in self.dict_hoga.keys() and code == self.dict_hoga[1][0]:
            self.hoga2Q.put([v, ch])
            self.UpdateHogajango(1, code, name, c, o, h, low, prec)

    def UpdateHogajango(self, gubun, code, name, c, o, h, low, prec):
        try:
            uvi, dvi = self.dict_vipr[code][3:5]
        except KeyError:
            uvi, dvi = 0, 0

        if code in self.dict_df['잔고목록'].index:
            df = self.dict_df['잔고목록'][self.dict_df['잔고목록'].index == code].copy()
            df['UVI'] = uvi
            df['DVI'] = dvi
            self.dict_hoga[gubun] = [code, True, df.rename(columns={'종목명': '호가종목명'})]
        else:
            df = pd.DataFrame([[name, 0, c, 0., 0, 0, 0, o, h, low, prec, 0, 0., uvi, dvi]],
                              columns=columns_hj, index=[code])
            self.dict_hoga[gubun] = [code, True, df]

    def GetSangHahanga(self, code):
        predayclose = self.GetMasterLastPrice(code)

        uplimitprice = predayclose * 1.30
        x = self.GetHogaunit(code, uplimitprice)
        if uplimitprice % x != 0:
            uplimitprice -= uplimitprice % x

        downlimitprice = predayclose * 0.70
        x = self.GetHogaunit(code, downlimitprice)
        if downlimitprice % x != 0:
            downlimitprice += x - downlimitprice % x

        return int(uplimitprice), int(downlimitprice)

    @thread_decorator
    def UpdateHogajanryang(self, code, vp, jc, hg, per):
        per = [0 if p == -100 else p for p in per]
        og = ''
        op = ''
        omc = ''
        name = self.dict_name[code]
        cond = (self.dict_df['체결목록']['종목명'] == name) & (self.dict_df['체결목록']['미체결수량'] > 0)
        df = self.dict_df['체결목록'][cond]
        if len(df) > 0:
            og = df['주문구분'][0]
            op = df['주문가격'][0]
            omc = df['미체결수량'][0]
        if 0 in self.dict_hoga.keys() and code == self.dict_hoga[0][0]:
            self.hoga1Q.put([vp, jc, hg, per, og, op, omc])
        elif 1 in self.dict_hoga.keys() and code == self.dict_hoga[1][0]:
            self.hoga2Q.put([vp, jc, hg, per, og, op, omc])

    def OnReceiveChejanData(self, gubun, itemcnt, fidlist):
        if gubun != '0' and itemcnt != '' and fidlist != '':
            return
        if self.dict_bool['모의투자']:
            return
        on = self.GetChejanData(9203)
        if on == '':
            return

        self.dict_intg['체결잔고수신횟수'] += 1
        try:
            code = self.GetChejanData(9001).strip('A')
            name = self.dict_name[code]
            ot = self.GetChejanData(913)
            og = self.GetChejanData(905)[1:]
            op = int(self.GetChejanData(901))
            oc = int(self.GetChejanData(900))
            omc = int(self.GetChejanData(902))
            d = self.dict_strg['당일날짜'] + self.GetChejanData(908)
        except Exception as e:
            self.windowQ.put([1, f'OnReceiveChejanData {e}'])
        else:
            try:
                cp = int(self.GetChejanData(910))
            except ValueError:
                cp = 0
            self.UpdateChejanData(code, name, ot, og, op, cp, oc, omc, on, d)

    @thread_decorator
    def UpdateChejanData(self, code, name, ot, og, op, cp, oc, omc, on, d):
        self.lock.acquire()
        if ot == '체결' and omc == 0 and cp != 0:
            if og == '매수':
                self.dict_intg['예수금'] -= oc * cp
                stg = self.dict_buy[code]
                self.dict_intg[f'{stg}예수금'] -= oc * cp
                self.dict_intg[f'{stg}추정예수금'] = self.dict_intg[f'{stg}예수금']
                self.UpdateChegeoljango(code, name, og, oc, cp, stg)
                self.windowQ.put([1, f'매매 시스템 체결 알림 - {name} {oc}주 {og}'])
            elif og == '매도':
                bp = self.dict_df['잔고목록']['매입가'][code]
                bg = bp * oc
                pg, sg, sp = self.GetPgSgSp(bg, oc * cp)
                stg = self.dict_sell[code]
                self.dict_intg['예수금'] += pg
                self.dict_intg[f'{stg}예수금'] += pg
                self.dict_intg[f'{stg}추정예수금'] = self.dict_intg[f'{stg}예수금']
                self.UpdateChegeoljango(code, name, og, oc, cp, stg)
                self.UpdateTradelist(name, oc, sp, sg, bg, pg, on, stg)
                self.windowQ.put([1, f"매매 시스템 체결 알림 - {name} {oc}주 {og}, 수익률 {sp}% 수익금{format(sg, ',')}원"])
        self.UpdateChegeollist(name, og, oc, omc, op, cp, d, on)
        self.lock.release()

    def UpdateChegeoljango(self, code, name, og, oc, cp, stg):
        columns = ['매입가', '현재가', '수익률', '평가손익', '매입금액', '평가금액', '보유수량']
        if og == '매수':
            if code not in self.dict_df['잔고목록'].index:
                bg = oc * cp
                pg, sg, sp = self.GetPgSgSp(bg, oc * cp)
                prec = self.GetMasterLastPrice(code)
                self.dict_df['잔고목록'].at[code] = name, cp, cp, sp, sg, bg, pg, 0, 0, 0, prec, oc, stg
            else:
                jc = self.dict_df['잔고목록']['보유수량'][code]
                bg = self.dict_df['잔고목록']['매입금액'][code]
                jc = jc + oc
                bg = bg + oc * cp
                bp = int(bg / jc)
                pg, sg, sp = self.GetPgSgSp(bg, jc * cp)
                self.dict_df['잔고목록'].at[code, columns] = bp, cp, sp, sg, bg, pg, jc
        elif og == '매도':
            jc = self.dict_df['잔고목록']['보유수량'][code]
            if jc - oc == 0:
                self.dict_df['잔고목록'].drop(index=code, inplace=True)
            else:
                bp = self.dict_df['잔고목록']['매입가'][code]
                jc = jc - oc
                bg = jc * bp
                pg, sg, sp = self.GetPgSgSp(bg, jc * cp)
                self.dict_df['잔고목록'].at[code, columns] = bp, cp, sp, sg, bg, pg, jc

        if og == '매수':
            if stg == '단타':
                self.stgtQ.put(['매수완료', code])
            elif stg == '단기':
                self.stgsQ.put(['매수완료', code])
            elif stg == '중기':
                self.stgmQ.put(['매수완료', code])
            elif stg == '장기':
                self.stglQ.put(['매수완료', code])
            del self.dict_buy[code]
        elif og == '매도':
            if stg == '단타':
                self.stgtQ.put(['매도완료', code])
            elif stg == '단기':
                self.stgsQ.put(['매도완료', code])
            elif stg == '중기':
                self.stgmQ.put(['매도완료', code])
            elif stg == '장기':
                self.stglQ.put(['매도완료', code])
            del self.dict_sell[code]

        columns = ['매입가', '현재가', '평가손익', '매입금액']
        self.dict_df['잔고목록'][columns] = self.dict_df['잔고목록'][columns].astype(int)
        self.dict_df['잔고목록'].sort_values(by=['매입금액'], inplace=True)

        if self.dict_bool['알림소리']:
            self.soundQ.put(f'{name} {int(oc)}주를 {og}하였습니다')

    def UpdateTradelist(self, name, oc, sp, sg, bg, pg, on, stg):
        d = strf_time('%Y%m%d%H%M%S')
        if self.dict_bool['모의투자'] and len(self.dict_df['거래목록']) > 0:
            if on in self.dict_df['거래목록'].index:
                while on in self.dict_df['거래목록'].index:
                    on = str(int(on) + 1)
            if d in self.dict_df['거래목록']['체결시간'].values:
                while d in self.dict_df['거래목록']['체결시간'].values:
                    d = str(int(d) + 1)

        self.dict_df['거래목록'].at[on] = name, bg, pg, oc, sp, sg, d, stg
        self.dict_df['거래목록'].sort_values(by=['체결시간'], ascending=False, inplace=True)
        self.windowQ.put([ui_num['거래목록'], self.dict_df['거래목록']])

        df = pd.DataFrame([[name, bg, pg, oc, sp, sg, d, stg]], columns=columns_td, index=[on])
        self.queryQ.put([df, 'tradelist', 'append'])
        self.UpdateTotaltradelist()

    def UpdateTotaltradelist(self):
        tsg = self.dict_df['거래목록']['매도금액'].sum()
        tbg = self.dict_df['거래목록']['매수금액'].sum()
        tsig = self.dict_df['거래목록'][self.dict_df['거래목록']['수익금'] > 0]['수익금'].sum()
        tssg = self.dict_df['거래목록'][self.dict_df['거래목록']['수익금'] < 0]['수익금'].sum()
        sg = self.dict_df['거래목록']['수익금'].sum()
        sp = round(sg / tbg * 100, 2)
        tdct = len(self.dict_df['거래목록'])
        self.dict_df['실현손익'] = pd.DataFrame([[tdct, tbg, tsg, tsig, tssg, sp, sg]],
                                            columns=columns_tt, index=[self.dict_strg['당일날짜']])
        self.windowQ.put([ui_num['거래합계'], self.dict_df['실현손익']])

        if self.dict_intg['장운영상태'] in [2, 3, 4]:
            self.teleQ.put(
                f"거래횟수 {len(self.dict_df['거래목록'])}회 / 총매수금액 {format(int(tbg), ',')}원 / "
                f"총매도금액 {format(int(tsg), ',')}원 / 총수익금액 {format(int(tsig), ',')}원 / "
                f"총손실금액 {format(int(tssg), ',')}원 / 수익률 {sp}% / 수익금합계 {format(int(sg), ',')}원")

    def UpdateChegeollist(self, name, og, oc, omc, op, cp, d, on):
        if self.dict_bool['모의투자'] and len(self.dict_df['체결목록']) > 0:
            if on in self.dict_df['체결목록'].index:
                while on in self.dict_df['체결목록'].index:
                    on = str(int(on) + 1)
            if d in self.dict_df['체결목록']['체결시간'].values:
                while d in self.dict_df['체결목록']['체결시간'].values:
                    d = str(int(d) + 1)

        if on in self.dict_df['체결목록'].index:
            self.dict_df['체결목록'].at[on, ['미체결수량', '체결가', '체결시간']] = omc, cp, d
        else:
            self.dict_df['체결목록'].at[on] = name, og, oc, omc, op, cp, d
        self.dict_df['체결목록'].sort_values(by=['체결시간'], ascending=False, inplace=True)
        self.windowQ.put([ui_num['체결목록'], self.dict_df['체결목록']])

        if omc == 0:
            df = pd.DataFrame([[name, og, oc, omc, op, cp, d]], columns=columns_cj, index=[on])
            self.queryQ.put([df, 'chegeollist', 'append'])

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

    def Block_Request(self, *args, **kwargs):
        if self.dict_intg['TR제한수신횟수'] == 0:
            self.dict_time['TR시작'] = now()
        if '종목코드' in kwargs.keys() and kwargs['종목코드'] != '':
            self.dict_strg['TR종목명'] = self.dict_name[kwargs['종목코드']]
        else:
            self.dict_strg['TR종목명'] = ''
        trcode = args[0].lower()
        liness = self.ReadEnc(trcode)
        self.dict_item = self.ParseDat(trcode, liness)
        self.dict_strg['TR명'] = kwargs['output']
        nnext = kwargs['next']
        for i in kwargs:
            if i.lower() != 'output' and i.lower() != 'next':
                self.ocx.dynamicCall('SetInputValue(QString, QString)', i, kwargs[i])
        self.dict_bool['TR수신'] = False
        self.dict_bool['TR다음'] = False
        if trcode == 'optkwfid':
            code_list = args[1]
            code_count = args[2]
            self.ocx.dynamicCall('CommKwRqData(QString, bool, int, int, QString, QString)',
                                 code_list, 0, code_count, '0', self.dict_strg['TR명'], sn_brrq)
        elif trcode == 'opt10054':
            self.ocx.dynamicCall('CommRqData(QString, QString, int, QString)',
                                 self.dict_strg['TR명'], trcode, nnext, sn_brrd)
        else:
            self.ocx.dynamicCall('CommRqData(QString, QString, int, QString)',
                                 self.dict_strg['TR명'], trcode, nnext, sn_brrq)
        sleeptime = timedelta_sec(0.25)
        while not self.dict_bool['TR수신'] or now() < sleeptime:
            pythoncom.PumpWaitingMessages()
        if trcode != 'opt10054':
            self.DisconnectRealData(sn_brrq)
        self.dict_intg['TR수신횟수'] += 1
        self.dict_intg['TR제한수신횟수'] += 1
        self.UpdateTrtime()
        return self.dict_df['TRDF']

    @thread_decorator
    def UpdateTrtime(self):
        if self.dict_intg['TR제한수신횟수'] > 95:
            self.dict_time['TR재개'] = timedelta_sec(self.dict_intg['TR제한수신횟수'] * 3.35, self.dict_time['TR시작'])
            remaintime = (self.dict_time['TR재개'] - now()).total_seconds()
            if remaintime > 0:
                self.windowQ.put([1, f'시스템 명령 실행 알림 - TR 조회 재요청까지 남은 시간은 {round(remaintime, 2)}초입니다.'])
            self.dict_intg['TR제한수신횟수'] = 0

    @property
    def TrtimeCondition(self):
        return now() > self.dict_time['TR재개']

    @property
    def RemainedTrtime(self):
        return round((self.dict_time['TR재개'] - now()).total_seconds(), 2)

    def SendCondition(self, screen, cond_name, cond_index, search):
        self.dict_bool['CR수신'] = False
        self.ocx.dynamicCall('SendCondition(QString, QString, int, int)', screen, cond_name, cond_index, search)
        while not self.dict_bool['CR수신']:
            pythoncom.PumpWaitingMessages()
        return self.list_trcd

    def DisconnectRealData(self, screen):
        self.ocx.dynamicCall('DisconnectRealData(QString)', screen)

    def GetMasterCodeName(self, code):
        return self.ocx.dynamicCall('GetMasterCodeName(QString)', code)

    def GetCodeListByMarket(self, market):
        data = self.ocx.dynamicCall('GetCodeListByMarket(QString)', market)
        tokens = data.split(';')[:-1]
        return tokens

    def GetMasterLastPrice(self, code):
        return int(self.ocx.dynamicCall('GetMasterLastPrice(QString)', code))

    def GetCommRealData(self, code, fid):
        return self.ocx.dynamicCall('GetCommRealData(QString, int)', code, fid)

    def GetChejanData(self, fid):
        return self.ocx.dynamicCall('GetChejanData(int)', fid)

    # noinspection PyMethodMayBeStatic
    def ReadEnc(self, trcode):
        enc = zipfile.ZipFile(f'{openapi_path}/data/{trcode}.enc')
        lines = enc.read(trcode.upper() + '.dat').decode('cp949')
        return lines

    # noinspection PyMethodMayBeStatic
    def ParseDat(self, trcode, lines):
        lines = lines.split('\n')
        start = [i for i, x in enumerate(lines) if x.startswith('@START')]
        end = [i for i, x in enumerate(lines) if x.startswith('@END')]
        block = zip(start, end)
        enc_data = {'trcode': trcode, 'input': [], 'output': []}
        for start, end in block:
            block_data = lines[start - 1:end + 1]
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
        self.windowQ.put([2, '시스템 종료'])
        if gubun:
            os.system('shutdown /s /t 60')
        self.teleQ.put('10초 후 시스템을 종료합니다.')
        if self.dict_bool['알림소리']:
            self.soundQ.put('십초 후 시스템을 종료합니다.')
        else:
            self.windowQ.put([1, '시스템 명령 실행 알림 - 10초 후 시스템을 종료합니다.'])
        i = 10
        while i > 0:
            self.windowQ.put([1, f'시스템 명령 실행 알림 - 시스템 종료 카운터 {i}'])
            i -= 1
            time.sleep(1)
        self.windowQ.put([1, '시스템 명령 실행 알림 - 시스템 종료'])
