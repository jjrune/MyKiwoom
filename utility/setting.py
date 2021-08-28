from PyQt5.QtGui import QFont, QColor

openapi_path = 'D:/OpenAPI'
system_path = 'D:/PythonProjects/MyKiwoom'
db_path = 'D:/PythonProjects/MyKiwoom/db'
db_stg = f'{db_path}/stg.db'
db_day = f'{db_path}/day.db'
db_tick = f'{db_path}/tick.db'
db_backtest = f'{db_path}/backtest.db'
db_backfind = f'{db_path}/backfind.db'

qfont12 = QFont()
qfont12.setFamily('나눔고딕')
qfont12.setPixelSize(12)
qfont13 = QFont()
qfont13.setFamily('나눔고딕')
qfont13.setPixelSize(13)
qfont14 = QFont()
qfont14.setFamily('나눔고딕')
qfont14.setPixelSize(14)

sn_brrq = 1000
sn_brrd = 1001
sn_cond = 1002
sn_oper = 1003
sn_jscg = 1004
sn_vijc = 1005
sn_cthg = 1006
sn_jgjc = 2000
sn_short = 2100
sn_mid = 2200
sn_long = 2300
sn_jchj = 3000

color_fg_bt = QColor(230, 230, 235)
color_fg_bc = QColor(190, 190, 195)
color_fg_dk = QColor(150, 150, 155)
color_fg_bk = QColor(110, 110, 115)

color_bg_bt = QColor(50, 50, 55)
color_bg_bc = QColor(40, 40, 45)
color_bg_dk = QColor(30, 30, 35)
color_bg_bk = QColor(20, 20, 25)
color_bg_ld = (50, 50, 55, 150)

color_bf_bt = QColor(110, 110, 115)
color_bf_dk = QColor(70, 70, 75)

color_cifl = QColor(230, 230, 255)
color_pluss = QColor(230, 230, 235)
color_minus = QColor(120, 120, 125)

color_chuse1 = QColor(35, 35, 40)
color_chuse2 = QColor(30, 30, 35)
color_ema05 = QColor(230, 230, 235)
color_ema10 = QColor(200, 200, 205)
color_ema20 = QColor(170, 170, 175)
color_ema40 = QColor(140, 140, 145)
color_ema60 = QColor(110, 110, 115)
color_ema120 = QColor(80, 80, 85)
color_ema240 = QColor(70, 70, 75)
color_ema480 = QColor(60, 60, 65)

style_fc_bt = 'color: rgb(230, 230, 235);'
style_fc_dk = 'color: rgb(150, 150, 155);'
style_bc_bt = 'background-color: rgb(50, 50, 55);'
style_bc_dk = 'background-color: rgb(30, 30, 35);'

ui_num = {'거래합계': 1, '거래목록': 2, '잔고평가': 3, '잔고목록': 4, '체결목록': 5, '기업공시': 6,
          '기업뉴스': 7, '투자자': 8, '재무년도': 9, '재무분기': 10, '동업종비교': 11, '체결강도': 12,
          '당일합계': 13, '당일상세': 14, '누적합계': 15, '누적상세': 16, '단타설정': 17,
          'tick': 18, 'long': 19, 'mid': 20, 'short': 21,
          '호가P0': 30, '호가잔고0': 31, '매도주문0': 32, '체결수량0': 33, '호가0': 34, '매수주문0': 35,
          '호가P1': 40, '호가잔고1': 41, '매도주문1': 42, '체결수량1': 43, '호가1': 44, '매수주문1': 45,
          '차트P0': 50, '차트P1': 51, '차트P2': 52, '차트P3': 53, '차트P4': 54, '차트P5': 55,
          '차트P6': 56, '차트P7': 57, '차트P8': 58, '차트P9': 59}

columns_tt = ['거래횟수', '총매수금액', '총매도금액', '총수익금액', '총손실금액', '수익률', '수익금합계']
columns_td = ['종목명', '매수금액', '매도금액', '주문수량', '수익률', '수익금', '체결시간', '전략구분']
columns_tj = ['추정예탁자산', '추정예수금', '보유종목수', '수익률', '총평가손익', '총매입금액', '총평가금액']
columns_jg = ['종목명', '매입가', '현재가', '수익률', '평가손익', '매입금액', '평가금액',
              '시가', '고가', '저가', '전일종가', '보유수량', '전략구분']
columns_cj = ['종목명', '주문구분', '주문수량', '미체결수량', '주문가격', '체결가', '체결시간']
columns_gs1 = ['등락율', '고저평균대비등락율', '거래대금', '누적거래대금', '체결강도', '최고체결강도', '전일거래량대비']
columns_gs2 = ['등락율', '고저평균대비등락율', '거래대금', '누적거래대금', '체결강도', '전일거래량대비']
columns_gjt = ['종목명', 'PER', 'HLMPER', 'SMONEY', 'DMONEY', 'CH', 'VP', 'SMAVG', 'CHAVG', 'CHHIGH']
columns_gjs = ['종목명', '현재가', '시가', '등락율', 'preshort', '승률', '비중']
columns_gjm = ['종목명', '현재가', '이평05', '5일최저저가', 'prelow', 'premid', '비중']
columns_gjl = ['종목명', '현재가', '이평2005', '이평20', 'prelong', '승률', '비중']

columns_ln = ['기간', '누적매수금액', '누적매도금액', '누적수익금액', '누적손실금액', '수익률', '누적수익금']
columns_lt = ['일자', '총매수금액', '총매도금액', '총수익금액', '총손실금액', '수익률', '수익금합계']
columns_sn = ['거래일자', '누적매수금액', '누적매도금액', '누적수익금액', '누적손실금액', '수익률', '누적수익금']
columns_st = ['체결시간', '종목명', '매수금액', '매도금액', '주문수량', '수익률', '수익금', '전략구분']

columns_hs = ['매도주문']
columns_hc = ['체결수량', '체결강도']
columns_hg = ['증감', '잔량', '호가', '등락율']
columns_hb = ['매수주문']
columns_hj = ['호가종목명', '매입가', '현재가', '수익률', '평가손익', '매입금액', '평가금액',
              '시가', '고가', '저가', '전일종가', '보유수량', '전략구분', 'UVI', 'DVI']

columns_ns = ['일자', '언론사', '제목']
columns_gc = ['일자', '정보제공', '공시']
columns_jj = ['일자', '현재가', '등락율', '거래대금', '개인', '외국인', '기관']
columns_jm1 = ['', '', '', '', '']
columns_jm2 = ['', '', '', '', '', '']
columns_jb = ['', '', '', '', '', '']
columns_ch = ['체결시간', '현재가', '등락율', '체결강도', '체결강도5분', '체결강도20분', '체결강도60분']
