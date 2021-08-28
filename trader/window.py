import psutil
import logging
from chartItem import *
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QPalette
from multiprocessing import Process, Queue
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.static import *


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger('Window')
        self.log.setLevel(logging.INFO)
        filehandler = logging.FileHandler(filename=f"{system_path}/Log/S{strf_time('%Y%m%d')}.txt", encoding='utf-8')
        self.log.addHandler(filehandler)

        def setIcon(path):
            icon = QIcon()
            icon.addPixmap(QPixmap(path))
            return icon

        def setLine(tab, width):
            line = QtWidgets.QFrame(tab)
            line.setLineWidth(width)
            line.setStyleSheet(style_fc_dk)
            line.setFrameShape(QtWidgets.QFrame.HLine)
            return line

        def setLineedit(groupbox, returnPressed=None):
            lineedit = QtWidgets.QLineEdit(groupbox)
            if returnPressed is not None:
                lineedit.setAlignment(Qt.AlignCenter)
            else:
                lineedit.setAlignment(Qt.AlignRight)
            if returnPressed is not None:
                lineedit.setStyleSheet(style_bc_bt)
            else:
                lineedit.setStyleSheet(style_fc_bt)
            lineedit.setFont(qfont12)
            if returnPressed is not None:
                lineedit.returnPressed.connect(returnPressed)
            return lineedit

        def setPushbutton(name, groupbox, buttonclicked, cmd=None):
            pushbutton = QtWidgets.QPushButton(name, groupbox)
            pushbutton.setStyleSheet(style_bc_bt)
            pushbutton.setFont(qfont12)
            if cmd is not None:
                pushbutton.clicked.connect(lambda: buttonclicked(cmd))
            else:
                pushbutton.clicked.connect(lambda: buttonclicked(name))
            return pushbutton

        def setTextEdit(tab, qfont=None):
            textedit = QtWidgets.QTextEdit(tab)
            textedit.setReadOnly(True)
            textedit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            textedit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            textedit.setStyleSheet(style_bc_dk)
            if qfont is not None:
                textedit.setFont(qfont)
            else:
                textedit.setFont(qfont12)
            return textedit

        def setPg(tname, tabwidget, tab):
            ctpg = pg.GraphicsLayoutWidget()
            ctpg_01 = ctpg.addPlot(row=0, col=0, viewBox=CustomViewBox1())
            ctpg_02 = ctpg.addPlot(row=1, col=0, viewBox=CustomViewBox2())
            ctpg_01.showAxis('left', False)
            ctpg_01.showAxis('right', True)
            ctpg_01.getAxis('right').setStyle(tickTextWidth=45, autoExpandTextSpace=False)
            ctpg_01.getAxis('right').setTickFont(qfont12)
            ctpg_01.getAxis('bottom').setTickFont(qfont12)
            ctpg_02.showAxis('left', False)
            ctpg_02.showAxis('right', True)
            ctpg_02.getAxis('right').setStyle(tickTextWidth=45, autoExpandTextSpace=False)
            ctpg_02.getAxis('right').setTickFont(qfont12)
            ctpg_02.getAxis('bottom').setTickFont(qfont12)
            ctpg_02.setXLink(ctpg_01)
            qGraphicsGridLayout = ctpg.ci.layout
            qGraphicsGridLayout.setRowStretchFactor(0, 2)
            qGraphicsGridLayout.setRowStretchFactor(1, 1)
            ctpg_vboxLayout = QtWidgets.QVBoxLayout(tab)
            ctpg_vboxLayout.setContentsMargins(5, 5, 5, 5)
            ctpg_vboxLayout.addWidget(ctpg)
            tabwidget.addTab(tab, tname)
            return [ctpg_01, ctpg_02]

        def setTablewidget(tab, columns, colcount, rowcount, sectionsize=None, clicked=None, color=False, qfont=None):
            tableWidget = QtWidgets.QTableWidget(tab)
            if sectionsize is not None:
                tableWidget.verticalHeader().setDefaultSectionSize(sectionsize)
            else:
                tableWidget.verticalHeader().setDefaultSectionSize(23)
            tableWidget.verticalHeader().setVisible(False)
            tableWidget.setAlternatingRowColors(True)
            tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            tableWidget.setColumnCount(len(columns))
            tableWidget.setRowCount(rowcount)
            tableWidget.setHorizontalHeaderLabels(columns)
            if qfont is not None:
                tableWidget.setFont(qfont)
            if colcount == 1:
                tableWidget.setColumnWidth(0, 84)
            elif colcount == 2:
                tableWidget.setColumnWidth(0, 84)
                tableWidget.setColumnWidth(1, 84)
            elif colcount == 3:
                tableWidget.setColumnWidth(0, 126)
                tableWidget.setColumnWidth(1, 90)
                tableWidget.setColumnWidth(2, 450)
            elif colcount == 4:
                tableWidget.setColumnWidth(0, 84)
                tableWidget.setColumnWidth(1, 84)
                tableWidget.setColumnWidth(2, 84)
                tableWidget.setColumnWidth(3, 84)
            elif colcount == 5:
                tableWidget.setColumnWidth(0, 66)
                tableWidget.setColumnWidth(1, 60)
                tableWidget.setColumnWidth(2, 60)
                tableWidget.setColumnWidth(3, 60)
                tableWidget.setColumnWidth(4, 60)
            elif colcount == 6:
                if rowcount == 13:
                    tableWidget.setColumnWidth(0, 60)
                    tableWidget.setColumnWidth(1, 60)
                    tableWidget.setColumnWidth(2, 60)
                    tableWidget.setColumnWidth(3, 60)
                    tableWidget.setColumnWidth(4, 60)
                    tableWidget.setColumnWidth(5, 60)
                else:
                    tableWidget.setColumnWidth(0, 111)
                    tableWidget.setColumnWidth(1, 111)
                    tableWidget.setColumnWidth(2, 111)
                    tableWidget.setColumnWidth(3, 111)
                    tableWidget.setColumnWidth(4, 111)
                    tableWidget.setColumnWidth(5, 111)
            elif colcount == 10:
                tableWidget.setColumnWidth(0, 81)
                tableWidget.setColumnWidth(1, 65)
                tableWidget.setColumnWidth(2, 65)
                tableWidget.setColumnWidth(3, 65)
                tableWidget.setColumnWidth(4, 65)
                tableWidget.setColumnWidth(5, 65)
                tableWidget.setColumnWidth(6, 65)
                tableWidget.setColumnWidth(7, 65)
                tableWidget.setColumnWidth(8, 65)
                tableWidget.setColumnWidth(9, 65)
            else:
                if colcount >= 7:
                    tableWidget.setColumnWidth(0, 126)
                    tableWidget.setColumnWidth(1, 90)
                    tableWidget.setColumnWidth(2, 90)
                    tableWidget.setColumnWidth(3, 90)
                    tableWidget.setColumnWidth(4, 90)
                    tableWidget.setColumnWidth(5, 90)
                    tableWidget.setColumnWidth(6, 90)
                if colcount >= 8:
                    tableWidget.setColumnWidth(7, 90)
                if colcount >= 9:
                    tableWidget.setColumnWidth(8, 90)
                if colcount >= 11:
                    tableWidget.setColumnWidth(9, 90)
                    tableWidget.setColumnWidth(10, 90)
                if colcount >= 12:
                    tableWidget.setColumnWidth(11, 90)
                if colcount >= 13:
                    tableWidget.setColumnWidth(12, 90)
                if colcount >= 14:
                    tableWidget.setColumnWidth(13, 90)
                if colcount >= 15:
                    tableWidget.setColumnWidth(14, 90)
            if clicked is not None:
                tableWidget.cellClicked.connect(clicked)
            if color:
                for i in range(22):
                    tableitem = QtWidgets.QTableWidgetItem()
                    tableitem.setBackground(color_bg_bt)
                    tableWidget.setItem(i, 0, tableitem)
            return tableWidget

        self.setFont(qfont12)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.icon_open = setIcon(f'{system_path}/Icon/open.bmp')
        self.icon_high = setIcon(f'{system_path}/Icon/high.bmp')
        self.icon_low = setIcon(f'{system_path}/Icon/low.bmp')
        self.icon_up = setIcon(f'{system_path}/Icon/up.bmp')
        self.icon_down = setIcon(f'{system_path}/Icon/down.bmp')
        self.icon_vi = setIcon(f'{system_path}/Icon/vi.bmp')
        self.icon_totals = setIcon(f'{system_path}/Icon/totals.bmp')
        self.icon_totalb = setIcon(f'{system_path}/Icon/totalb.bmp')
        self.icon_pers = setIcon(f'{system_path}/Icon/pers.bmp')
        self.icon_perb = setIcon(f'{system_path}/Icon/perb.bmp')

        pg.setConfigOptions(background=color_bg_dk, foreground=color_fg_dk, leftButtonPan=False)
        self.dict_ctpg = {}

        self.chart_00_tabWidget = QtWidgets.QTabWidget(self)
        self.chart_00_tab = QtWidgets.QWidget()
        self.chart_05_tab = QtWidgets.QWidget()
        self.dict_ctpg[ui_num['차트P1']] = setPg('일봉 차트', self.chart_00_tabWidget, self.chart_00_tab)
        self.dict_ctpg[ui_num['차트P6']] = setPg('일봉 차트', self.chart_00_tabWidget, self.chart_05_tab)

        self.chart_01_tabWidget = QtWidgets.QTabWidget(self)
        self.chart_01_tab = QtWidgets.QWidget()
        self.chart_06_tab = QtWidgets.QWidget()
        self.dict_ctpg[ui_num['차트P2']] = setPg('분봉 차트', self.chart_01_tabWidget, self.chart_01_tab)
        self.dict_ctpg[ui_num['차트P7']] = setPg('분봉 차트', self.chart_01_tabWidget, self.chart_06_tab)

        self.chart_02_tabWidget = QtWidgets.QTabWidget(self)
        self.chart_02_tab = QtWidgets.QWidget()
        self.chart_07_tab = QtWidgets.QWidget()
        self.dict_ctpg[ui_num['차트P3']] = setPg('일봉 차트', self.chart_02_tabWidget, self.chart_02_tab)
        self.dict_ctpg[ui_num['차트P8']] = setPg('일봉 차트', self.chart_02_tabWidget, self.chart_07_tab)

        self.chart_03_tabWidget = QtWidgets.QTabWidget(self)
        self.chart_03_tab = QtWidgets.QWidget()
        self.chart_08_tab = QtWidgets.QWidget()
        self.dict_ctpg[ui_num['차트P4']] = setPg('분봉 차트', self.chart_03_tabWidget, self.chart_03_tab)
        self.dict_ctpg[ui_num['차트P9']] = setPg('분봉 차트', self.chart_03_tabWidget, self.chart_08_tab)

        self.chart_04_tabWidget = QtWidgets.QTabWidget(self)
        self.chart_04_tab = QtWidgets.QWidget()
        self.dict_ctpg[ui_num['차트P5']] = setPg('복기 차트', self.chart_04_tabWidget, self.chart_04_tab)

        self.hoga_00_tabWidget = QtWidgets.QTabWidget(self)
        self.hoga_00_tab = QtWidgets.QWidget()
        self.hoga_00_sellper_groupBox = QtWidgets.QGroupBox(' ', self.hoga_00_tab)
        self.hoga_00_sell_radioButton_01 = QtWidgets.QRadioButton('10%', self.hoga_00_sellper_groupBox)
        self.hoga_00_sell_radioButton_02 = QtWidgets.QRadioButton('25%', self.hoga_00_sellper_groupBox)
        self.hoga_00_sell_radioButton_03 = QtWidgets.QRadioButton('33%', self.hoga_00_sellper_groupBox)
        self.hoga_00_sell_radioButton_04 = QtWidgets.QRadioButton('50%', self.hoga_00_sellper_groupBox)
        self.hoga_00_sell_radioButton_05 = QtWidgets.QRadioButton('75%', self.hoga_00_sellper_groupBox)
        self.hoga_00_sell_radioButton_06 = QtWidgets.QRadioButton('100%', self.hoga_00_sellper_groupBox)
        self.hoga_00_buywon_groupBox = QtWidgets.QGroupBox(' ', self.hoga_00_tab)
        self.hoga_00_buy_radioButton_01 = QtWidgets.QRadioButton('100,000', self.hoga_00_buywon_groupBox)
        self.hoga_00_buy_radioButton_02 = QtWidgets.QRadioButton('500,000', self.hoga_00_buywon_groupBox)
        self.hoga_00_buy_radioButton_03 = QtWidgets.QRadioButton('1,000,000', self.hoga_00_buywon_groupBox)
        self.hoga_00_buy_radioButton_04 = QtWidgets.QRadioButton('5,000,000', self.hoga_00_buywon_groupBox)
        self.hoga_00_buy_radioButton_05 = QtWidgets.QRadioButton('10,000,000', self.hoga_00_buywon_groupBox)
        self.hoga_00_buy_radioButton_06 = QtWidgets.QRadioButton('50,000,000', self.hoga_00_buywon_groupBox)
        self.hoga_00_sell_pushButton_01 = setPushbutton('시장가 매도', self.hoga_00_tab, self.ButtonClicked_1,
                                                        '시장가매도0')
        self.hoga_00_sell_pushButton_02 = setPushbutton('매도 취소', self.hoga_00_tab, self.ButtonClicked_1,
                                                        '매도취소0')
        self.hoga_00_buy_pushButton_01 = setPushbutton('매수 취소', self.hoga_00_tab, self.ButtonClicked_2,
                                                       '매수취소0')
        self.hoga_00_buy_pushButton_02 = setPushbutton('시장가 매수', self.hoga_00_tab, self.ButtonClicked_2,
                                                       '시장가매수0')
        self.hoga_00_hj_tableWidget = setTablewidget(self.hoga_00_tab, columns_hj, len(columns_hj), 1)
        self.hoga_00_hs_tableWidget = setTablewidget(self.hoga_00_tab, columns_hs, len(columns_hs), 22,
                                                     clicked=self.CellClicked_1, color=True)
        self.hoga_00_hc_tableWidget = setTablewidget(self.hoga_00_tab, columns_hc, len(columns_hc), 22)
        self.hoga_00_hg_tableWidget = setTablewidget(self.hoga_00_tab, columns_hg, len(columns_hg), 22)
        self.hoga_00_hb_tableWidget = setTablewidget(self.hoga_00_tab, columns_hb, len(columns_hb), 22,
                                                     clicked=self.CellClicked_2, color=True)
        self.hoga_00_line = setLine(self.hoga_00_tab, 1)
        self.hoga_00_tabWidget.addTab(self.hoga_00_tab, '호가 주문')

        self.hoga_01_tabWidget = QtWidgets.QTabWidget(self)
        self.hoga_01_tab = QtWidgets.QWidget()
        self.hoga_01_sellper_groupBox = QtWidgets.QGroupBox(' ', self.hoga_01_tab)
        self.hoga_01_sell_radioButton_01 = QtWidgets.QRadioButton('10%', self.hoga_01_sellper_groupBox)
        self.hoga_01_sell_radioButton_02 = QtWidgets.QRadioButton('25%', self.hoga_01_sellper_groupBox)
        self.hoga_01_sell_radioButton_03 = QtWidgets.QRadioButton('33%', self.hoga_01_sellper_groupBox)
        self.hoga_01_sell_radioButton_04 = QtWidgets.QRadioButton('50%', self.hoga_01_sellper_groupBox)
        self.hoga_01_sell_radioButton_05 = QtWidgets.QRadioButton('75%', self.hoga_01_sellper_groupBox)
        self.hoga_01_sell_radioButton_06 = QtWidgets.QRadioButton('100%', self.hoga_01_sellper_groupBox)
        self.hoga_01_buywon_groupBox = QtWidgets.QGroupBox(' ', self.hoga_01_tab)
        self.hoga_01_buy_radioButton_01 = QtWidgets.QRadioButton('100,000', self.hoga_01_buywon_groupBox)
        self.hoga_01_buy_radioButton_02 = QtWidgets.QRadioButton('500,000', self.hoga_01_buywon_groupBox)
        self.hoga_01_buy_radioButton_03 = QtWidgets.QRadioButton('1,000,000', self.hoga_01_buywon_groupBox)
        self.hoga_01_buy_radioButton_04 = QtWidgets.QRadioButton('5,000,000', self.hoga_01_buywon_groupBox)
        self.hoga_01_buy_radioButton_05 = QtWidgets.QRadioButton('10,000,000', self.hoga_01_buywon_groupBox)
        self.hoga_01_buy_radioButton_06 = QtWidgets.QRadioButton('50,000,000', self.hoga_01_buywon_groupBox)
        self.hoga_01_sell_pushButton_01 = setPushbutton('시장가 매도', self.hoga_01_tab, self.ButtonClicked_1,
                                                        '시장가매도1')
        self.hoga_01_sell_pushButton_02 = setPushbutton('매도 취소', self.hoga_01_tab, self.ButtonClicked_1,
                                                        '매도취소1')
        self.hoga_01_buy_pushButton_01 = setPushbutton('매수 취소', self.hoga_01_tab, self.ButtonClicked_2,
                                                       '매수취소1')
        self.hoga_01_buy_pushButton_02 = setPushbutton('시장가 매수', self.hoga_01_tab, self.ButtonClicked_2,
                                                       '시장가매수1')
        self.hoga_01_hj_tableWidget = setTablewidget(self.hoga_01_tab, columns_hj, len(columns_hj), 1)
        self.hoga_01_hs_tableWidget = setTablewidget(self.hoga_01_tab, columns_hs, len(columns_hs), 22,
                                                     clicked=self.CellClicked_3, color=True)
        self.hoga_01_hc_tableWidget = setTablewidget(self.hoga_01_tab, columns_hc, len(columns_hc), 22)
        self.hoga_01_hg_tableWidget = setTablewidget(self.hoga_01_tab, columns_hg, len(columns_hg), 22)
        self.hoga_01_hb_tableWidget = setTablewidget(self.hoga_01_tab, columns_hb, len(columns_hb), 22,
                                                     clicked=self.CellClicked_4, color=True)
        self.hoga_01_line = setLine(self.hoga_01_tab, 1)
        self.hoga_01_tabWidget.addTab(self.hoga_01_tab, '호가 주문')

        self.gg_tabWidget = QtWidgets.QTabWidget(self)
        self.gg_tab = QtWidgets.QWidget()
        self.gg_textEdit = setTextEdit(self.gg_tab, qfont14)
        self.gg_tabWidget.addTab(self.gg_tab, '기업 개요')

        self.gs_tabWidget = QtWidgets.QTabWidget(self)
        self.gs_tab = QtWidgets.QWidget()
        self.gs_tableWidget = setTablewidget(self.gs_tab, columns_gc, len(columns_gc), 22, qfont=qfont13)
        self.gs_tabWidget.addTab(self.gs_tab, '기업 공시')

        self.ns_tabWidget = QtWidgets.QTabWidget(self)
        self.ns_tab = QtWidgets.QWidget()
        self.ns_tableWidget = setTablewidget(self.ns_tab, columns_ns, len(columns_ns), 12, qfont=qfont13)
        self.ns_tabWidget.addTab(self.ns_tab, '종목 뉴스')

        self.jj_tabWidget = QtWidgets.QTabWidget(self)
        self.jj_tab = QtWidgets.QWidget()
        self.jj_tableWidget = setTablewidget(self.jj_tab, columns_jj, len(columns_jj), 28)
        self.jj_tabWidget.addTab(self.jj_tab, '투자자별 매매동향')

        self.jm_tabWidget = QtWidgets.QTabWidget(self)
        self.jm_tab = QtWidgets.QWidget()
        self.jm1_tableWidget = setTablewidget(self.jm_tab, columns_jm1, len(columns_jm1), 13, sectionsize=21)
        self.jm2_tableWidget = setTablewidget(self.jm_tab, columns_jm2, len(columns_jm2), 13, sectionsize=21)
        self.jm_tabWidget.addTab(self.jm_tab, '재무제표')

        self.jb_tabWidget = QtWidgets.QTabWidget(self)
        self.jb_tab = QtWidgets.QWidget()
        self.jb_tableWidget = setTablewidget(self.jb_tab, columns_jb, len(columns_jb), 14, sectionsize=21)
        self.jb_tabWidget.addTab(self.jb_tab, '동일업종비교')

        self.ch_tabWidget = QtWidgets.QTabWidget(self)
        self.ch_tab = QtWidgets.QWidget()
        self.ch_tableWidget = setTablewidget(self.ch_tab, columns_ch, len(columns_ch), 28)
        self.ch_tabWidget.addTab(self.ch_tab, '체결강도')

        self.lgsj_tabWidget = QtWidgets.QTabWidget(self)
        self.lg_tab = QtWidgets.QWidget()
        self.sj_tab = QtWidgets.QWidget()

        self.lg_textEdit = setTextEdit(self.lg_tab)

        self.sj_groupBox_01 = QtWidgets.QGroupBox(self.sj_tab)
        self.sj_label_01 = QtWidgets.QLabel('텔레그램봇 넘버', self.sj_groupBox_01)
        self.sj_label_02 = QtWidgets.QLabel('사용자 아이디', self.sj_groupBox_01)
        self.sj_lineEdit_01 = setLineedit(self.sj_groupBox_01)
        self.sj_lineEdit_02 = setLineedit(self.sj_groupBox_01)
        self.sj_pushButton_01 = setPushbutton('설정', self.sj_groupBox_01, self.ButtonClicked_3)
        self.sj_groupBox_02 = QtWidgets.QGroupBox(self.sj_tab)
        self.sj_pushButton_02 = setPushbutton('데이터베이스 불러오기', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_03 = setPushbutton('OPENAPI 로그인', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_04 = setPushbutton('계좌평가 및 잔고', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_05 = setPushbutton('코스피 코스닥 차트', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_06 = setPushbutton('장운영시간 알림 등록', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_07 = setPushbutton('업종지수 주식체결 등록', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_08 = setPushbutton('단중장기 주식체결 등록', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_09 = setPushbutton('VI발동해제 등록', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_10 = setPushbutton('장운영상태', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_11 = setPushbutton('실시간 조건검색식 등록', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_12 = setPushbutton('단타 목표수익률 달성', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_13 = setPushbutton('단타 전략 중단', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_14 = setPushbutton('잔고청산', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_15 = setPushbutton('실시간 데이터 수신 중단', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_16 = setPushbutton('단중장기 매수주문', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_17 = setPushbutton('일별거래목록 저장', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_18 = setPushbutton('테스트모드 ON/OFF', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_19 = setPushbutton('모의투자 ON/OFF', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_20 = setPushbutton('알림소리 ON/OFF', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_21 = setPushbutton('시스템 종료', self.sj_groupBox_02, self.ButtonClicked_3)

        self.lgsj_tabWidget.addTab(self.lg_tab, '로그')
        self.lgsj_tabWidget.addTab(self.sj_tab, '시스템설정')

        self.table_tabWidget = QtWidgets.QTabWidget(self)
        self.td_tab = QtWidgets.QWidget()
        self.gjt_tab = QtWidgets.QWidget()
        self.gjs_tab = QtWidgets.QWidget()
        self.gjm_tab = QtWidgets.QWidget()
        self.gjl_tab = QtWidgets.QWidget()
        self.st_tab = QtWidgets.QWidget()
        self.sg_tab = QtWidgets.QWidget()

        self.tt_tableWidget = setTablewidget(self.td_tab, columns_tt, len(columns_tt), 1)
        self.td_tableWidget = setTablewidget(self.td_tab, columns_td, len(columns_td), 13, clicked=self.CellClicked_5)
        self.tj_tableWidget = setTablewidget(self.td_tab, columns_tj, len(columns_tj), 1)
        self.jg_tableWidget = setTablewidget(self.td_tab, columns_jg, len(columns_jg), 13, clicked=self.CellClicked_6)
        self.cj_tableWidget = setTablewidget(self.td_tab, columns_cj, len(columns_cj), 12, clicked=self.CellClicked_7)
        self.gjt_tableWidget = setTablewidget(self.gjt_tab, columns_gjt, len(columns_gjt), 46, clicked=self.CellClicked_8)
        self.gjs_tableWidget = setTablewidget(self.gjs_tab, columns_gjs, len(columns_gjs), 46, clicked=self.CellClicked_9)
        self.gjm_tableWidget = setTablewidget(self.gjm_tab, columns_gjm, len(columns_gjm), 46, clicked=self.CellClicked_10)
        self.gjl_tableWidget = setTablewidget(self.gjl_tab, columns_gjl, len(columns_gjl), 46, clicked=self.CellClicked_11)

        self.st_groupBox = QtWidgets.QGroupBox(self.st_tab)
        self.calendarWidget = QtWidgets.QCalendarWidget(self.st_groupBox)
        todayDate = QtCore.QDate.currentDate()
        self.calendarWidget.setCurrentPage(todayDate.year(), todayDate.month())
        self.calendarWidget.clicked.connect(self.CalendarClicked)
        self.stn_tableWidget = setTablewidget(self.st_tab, columns_sn, len(columns_sn), 1)
        self.stl_tableWidget = setTablewidget(self.st_tab, columns_st, len(columns_st), 31, clicked=self.CellClicked_12)

        self.sg_groupBox = QtWidgets.QGroupBox(self.sg_tab)
        self.sg_pushButton_01 = setPushbutton('일별집계', self.sg_groupBox, self.ButtonClicked_3)
        self.sg_pushButton_02 = setPushbutton('월별집계', self.sg_groupBox, self.ButtonClicked_3)
        self.sg_pushButton_03 = setPushbutton('연도별집계', self.sg_groupBox, self.ButtonClicked_3)
        self.sgt_tableWidget = setTablewidget(self.sg_tab, columns_ln, len(columns_ln), 1)
        self.sgl_tableWidget = setTablewidget(self.sg_tab, columns_lt, len(columns_lt), 41)

        self.table_tabWidget.addTab(self.td_tab, '계좌평가')
        self.table_tabWidget.addTab(self.gjt_tab, '단타')
        self.table_tabWidget.addTab(self.gjs_tab, '단기')
        self.table_tabWidget.addTab(self.gjm_tab, '중기')
        self.table_tabWidget.addTab(self.gjl_tab, '장기')
        self.table_tabWidget.addTab(self.st_tab, '거래목록')
        self.table_tabWidget.addTab(self.sg_tab, '수익현황')

        self.info_label_01 = QtWidgets.QLabel(self)
        self.info_label_02 = QtWidgets.QLabel(self)
        self.info_label_03 = QtWidgets.QLabel(self)
        self.info_label_04 = QtWidgets.QLabel(self)
        self.info_label_05 = QtWidgets.QLabel(self)
        self.info_label_06 = QtWidgets.QLabel(self)

        self.etc_pushButton_00 = setPushbutton('차트탭변경', self, self.ButtonClicked_4, 0)
        self.etc_pushButton_01 = setPushbutton('차트유형변경', self, self.ButtonClicked_4, 1)
        self.etc_pushButton_02 = setPushbutton('창크기변경', self, self.ButtonClicked_4, 2)

        self.ct_label_01 = QtWidgets.QLabel('종목명 또는 종목코드 조회', self)
        self.ct_label_02 = QtWidgets.QLabel('종목명 또는 종목코드 조회', self)
        self.ct_lineEdit_01 = setLineedit(self, self.ReturnPressed_1)
        self.ct_lineEdit_02 = setLineedit(self, self.ReturnPressed_2)

        self.setGeometry(0, 0, 3440, 1400)
        self.chart_00_tabWidget.setGeometry(5, 5, 1025, 692)
        self.chart_01_tabWidget.setGeometry(1035, 5, 1026, 692)
        self.chart_02_tabWidget.setGeometry(5, 702, 1025, 692)
        self.chart_03_tabWidget.setGeometry(1035, 702, 1026, 692)
        self.chart_04_tabWidget.setGeometry(3500, 5, 2743, 1390)
        self.hoga_00_tabWidget.setGeometry(2066, 5, 682, 692)
        self.hoga_01_tabWidget.setGeometry(2066, 702, 682, 692)
        self.lgsj_tabWidget.setGeometry(2753, 5, 682, 282)
        self.table_tabWidget.setGeometry(2753, 292, 682, 1103)
        self.info_label_01.setGeometry(155, 1, 400, 30)
        self.info_label_02.setGeometry(600, 1, 400, 30)
        self.info_label_03.setGeometry(1185, 1, 400, 30)
        self.info_label_04.setGeometry(2145, 1, 600, 30)
        self.info_label_05.setGeometry(2145, 699, 600, 30)
        self.info_label_06.setGeometry(2888, 1, 400, 30)
        self.etc_pushButton_00.setGeometry(3185, 291, 80, 20)
        self.etc_pushButton_01.setGeometry(3270, 291, 80, 20)
        self.etc_pushButton_02.setGeometry(3355, 291, 80, 20)
        self.ct_label_01.setGeometry(3500, 5, 140, 20)
        self.ct_label_02.setGeometry(3500, 702, 140, 20)
        self.ct_lineEdit_01.setGeometry(3500, 5, 100, 20)
        self.ct_lineEdit_02.setGeometry(3500, 702, 100, 20)

        self.hoga_00_sellper_groupBox.setGeometry(5, -10, 331, 65)
        self.hoga_00_sell_radioButton_01.setGeometry(10, 22, 100, 20)
        self.hoga_00_sell_radioButton_02.setGeometry(110, 22, 100, 20)
        self.hoga_00_sell_radioButton_03.setGeometry(220, 22, 100, 20)
        self.hoga_00_sell_radioButton_04.setGeometry(10, 42, 100, 20)
        self.hoga_00_sell_radioButton_05.setGeometry(110, 42, 100, 20)
        self.hoga_00_sell_radioButton_06.setGeometry(220, 42, 100, 20)
        self.hoga_00_buywon_groupBox.setGeometry(341, -10, 331, 65)
        self.hoga_00_buy_radioButton_01.setGeometry(10, 22, 100, 20)
        self.hoga_00_buy_radioButton_02.setGeometry(110, 22, 100, 20)
        self.hoga_00_buy_radioButton_03.setGeometry(220, 22, 100, 20)
        self.hoga_00_buy_radioButton_04.setGeometry(10, 42, 100, 20)
        self.hoga_00_buy_radioButton_05.setGeometry(110, 42, 100, 20)
        self.hoga_00_buy_radioButton_06.setGeometry(220, 42, 100, 20)
        self.hoga_00_sell_pushButton_01.setGeometry(5, 60, 163, 20)
        self.hoga_00_sell_pushButton_02.setGeometry(173, 60, 163, 20)
        self.hoga_00_buy_pushButton_01.setGeometry(341, 60, 163, 20)
        self.hoga_00_buy_pushButton_02.setGeometry(509, 60, 163, 20)
        self.hoga_00_hj_tableWidget.setGeometry(5, 85, 668, 42)
        self.hoga_00_hs_tableWidget.setGeometry(5, 132, 84, 525)
        self.hoga_00_hc_tableWidget.setGeometry(88, 132, 168, 525)
        self.hoga_00_hg_tableWidget.setGeometry(255, 132, 336, 525)
        self.hoga_00_hb_tableWidget.setGeometry(590, 132, 84, 525)
        self.hoga_00_line.setGeometry(6, 402, 667, 1)

        self.hoga_01_sellper_groupBox.setGeometry(5, -10, 331, 65)
        self.hoga_01_sell_radioButton_01.setGeometry(10, 22, 100, 20)
        self.hoga_01_sell_radioButton_02.setGeometry(110, 22, 100, 20)
        self.hoga_01_sell_radioButton_03.setGeometry(220, 22, 100, 20)
        self.hoga_01_sell_radioButton_04.setGeometry(10, 42, 100, 20)
        self.hoga_01_sell_radioButton_05.setGeometry(110, 42, 100, 20)
        self.hoga_01_sell_radioButton_06.setGeometry(220, 42, 100, 20)
        self.hoga_01_buywon_groupBox.setGeometry(341, -10, 331, 65)
        self.hoga_01_buy_radioButton_01.setGeometry(10, 22, 100, 20)
        self.hoga_01_buy_radioButton_02.setGeometry(110, 22, 100, 20)
        self.hoga_01_buy_radioButton_03.setGeometry(220, 22, 100, 20)
        self.hoga_01_buy_radioButton_04.setGeometry(10, 42, 100, 20)
        self.hoga_01_buy_radioButton_05.setGeometry(110, 42, 100, 20)
        self.hoga_01_buy_radioButton_06.setGeometry(220, 42, 100, 20)
        self.hoga_01_sell_pushButton_01.setGeometry(5, 60, 163, 20)
        self.hoga_01_sell_pushButton_02.setGeometry(173, 60, 163, 20)
        self.hoga_01_buy_pushButton_01.setGeometry(341, 60, 163, 20)
        self.hoga_01_buy_pushButton_02.setGeometry(509, 60, 163, 20)
        self.hoga_01_hj_tableWidget.setGeometry(5, 85, 668, 42)
        self.hoga_01_hs_tableWidget.setGeometry(5, 132, 84, 525)
        self.hoga_01_hc_tableWidget.setGeometry(88, 132, 168, 525)
        self.hoga_01_hg_tableWidget.setGeometry(255, 132, 336, 525)
        self.hoga_01_hb_tableWidget.setGeometry(590, 132, 84, 525)
        self.hoga_01_line.setGeometry(6, 402, 667, 1)

        self.gg_tabWidget.setGeometry(3500, 702, 682, 120)
        self.gs_tabWidget.setGeometry(3500, 807, 682, 567)
        self.ns_tabWidget.setGeometry(3500, 702, 682, 330)
        self.jj_tabWidget.setGeometry(3500, 1039, 682, 360)
        self.jm_tabWidget.setGeometry(3500, 702, 682, 330)
        self.jb_tabWidget.setGeometry(3500, 1039, 682, 360)
        self.ch_tabWidget.setGeometry(3500, 702, 682, 682)

        self.gg_textEdit.setGeometry(5, 5, 668, 80)
        self.gs_tableWidget.setGeometry(5, 5, 668, 527)
        self.ns_tableWidget.setGeometry(5, 5, 668, 293)
        self.jj_tableWidget.setGeometry(5, 5, 668, 315)
        self.jm1_tableWidget.setGeometry(5, 5, 310, 293)
        self.jm2_tableWidget.setGeometry(310, 5, 363, 293)
        self.jb_tableWidget.setGeometry(5, 5, 668, 315)
        self.ch_tableWidget.setGeometry(5, 5, 668, 653)

        self.lg_textEdit.setGeometry(5, 5, 668, 242)

        self.sj_groupBox_01.setGeometry(5, 3, 668, 65)
        self.sj_label_01.setGeometry(10, 13, 180, 20)
        self.sj_label_02.setGeometry(10, 38, 180, 20)
        self.sj_lineEdit_01.setGeometry(95, 12, 486, 20)
        self.sj_lineEdit_02.setGeometry(95, 37, 486, 20)
        self.sj_pushButton_01.setGeometry(586, 12, 75, 45)

        self.sj_groupBox_02.setGeometry(5, 70, 668, 177)
        self.sj_pushButton_02.setGeometry(5, 10, 161, 28)
        self.sj_pushButton_03.setGeometry(171, 10, 161, 28)
        self.sj_pushButton_04.setGeometry(337, 10, 161, 28)
        self.sj_pushButton_05.setGeometry(503, 10, 160, 28)
        self.sj_pushButton_06.setGeometry(5, 43, 161, 28)
        self.sj_pushButton_07.setGeometry(171, 43, 161, 28)
        self.sj_pushButton_08.setGeometry(337, 43, 161, 28)
        self.sj_pushButton_09.setGeometry(503, 43, 161, 28)
        self.sj_pushButton_10.setGeometry(5, 77, 160, 28)
        self.sj_pushButton_11.setGeometry(171, 77, 161, 28)
        self.sj_pushButton_12.setGeometry(337, 77, 161, 28)
        self.sj_pushButton_13.setGeometry(503, 77, 161, 28)
        self.sj_pushButton_14.setGeometry(5, 110, 161, 28)
        self.sj_pushButton_15.setGeometry(171, 110, 161, 28)
        self.sj_pushButton_16.setGeometry(337, 110, 161, 28)
        self.sj_pushButton_17.setGeometry(503, 110, 161, 28)
        self.sj_pushButton_18.setGeometry(5, 143, 161, 28)
        self.sj_pushButton_19.setGeometry(171, 143, 161, 28)
        self.sj_pushButton_20.setGeometry(337, 143, 161, 28)
        self.sj_pushButton_21.setGeometry(503, 143, 161, 28)

        self.tt_tableWidget.setGeometry(5, 5, 668, 42)
        self.td_tableWidget.setGeometry(5, 52, 668, 320)
        self.tj_tableWidget.setGeometry(5, 377, 668, 42)
        self.jg_tableWidget.setGeometry(5, 424, 668, 320)
        self.cj_tableWidget.setGeometry(5, 749, 668, 320)
        self.gjt_tableWidget.setGeometry(5, 5, 668, 1063)
        self.gjs_tableWidget.setGeometry(5, 5, 668, 1063)
        self.gjm_tableWidget.setGeometry(5, 5, 668, 1063)
        self.gjl_tableWidget.setGeometry(5, 5, 668, 1063)

        self.st_groupBox.setGeometry(5, 3, 668, 278)
        self.calendarWidget.setGeometry(5, 11, 658, 258)
        self.stn_tableWidget.setGeometry(5, 287, 668, 42)
        self.stl_tableWidget.setGeometry(5, 334, 668, 735)

        self.sg_groupBox.setGeometry(5, 3, 668, 48)
        self.sg_pushButton_01.setGeometry(5, 11, 216, 30)
        self.sg_pushButton_02.setGeometry(226, 12, 216, 30)
        self.sg_pushButton_03.setGeometry(447, 12, 216, 30)
        self.sgt_tableWidget.setGeometry(5, 57, 668, 42)
        self.sgl_tableWidget.setGeometry(5, 104, 668, 965)

        self.dict_intg = {
            '평균시간': 0,
            '등락율상한': 0.,
            '고저평균대비등락율하한': 0.,
            '거래대금하한': 0,
            '누적거래대금하한': 0,
            '체결강도하한': 0.,
            '전일거래량대비하한': 0.,
            '거래대금차이': 0,
            '체결강도차이': 0.,
            '전일거래량대비차이': 0.
        }

        self.dict_code = {}
        self.dict_name = {}
        self.dict_mcpg_lastindex = {}
        self.dict_mcpg_lastchuse = {}
        self.dict_mcpg_lastmoveavg = {}
        self.dict_mcpg_lastcandlestick = {}
        self.dict_mcpg_lastmoneybar = {}
        self.dict_mcpg_infiniteline = {}
        self.dict_mcpg_legend1 = {}
        self.dict_mcpg_legend2 = {}
        self.dict_mcpg_name = {}
        self.dict_mcpg_close = {}

        self.mode0 = 0
        self.mode1 = 0
        self.mode2 = 0

        self.dict_intu = {'스레드': 0, '시피유': 0., '메모리': 0.}
        self.dict_intt = {'스레드': 0, '시피유': 0., '메모리': 0.}
        self.dict_intl = {'스레드': 0, '시피유': 0., '메모리': 0.}
        self.dict_intm = {'스레드': 0, '시피유': 0., '메모리': 0.}
        self.dict_ints = {'스레드': 0, '시피유': 0., '메모리': 0.}

        self.writer = Writer(windowQ)
        self.writer.data0.connect(self.UpdateTexedit)
        self.writer.data1.connect(self.UpdateChart)
        self.writer.data2.connect(self.UpdateTick)
        self.writer.data3.connect(self.UpdateLongMidShort)
        self.writer.data4.connect(self.UpdateTablewidget)
        self.writer.start()

    def ReturnPressed_1(self):
        codeorname = self.ct_lineEdit_01.text()
        try:
            code = self.dict_code[codeorname]
        except KeyError:
            if codeorname in self.dict_code.values():
                code = codeorname
            else:
                windowQ.put([1, '시스템 명령 오류 알림 - 종목명 또는 종목코드를 잘못입력하였습니다.'])
                return
        if self.mode1 == 0:
            workerQ.put(f"현재가{ui_num['차트P1']} {code}")
        elif self.mode1 == 1:
            workerQ.put(f"현재가{ui_num['차트P0']} {code}")

    def ReturnPressed_2(self):
        codeorname = self.ct_lineEdit_02.text()
        try:
            code = self.dict_code[codeorname]
        except KeyError:
            if codeorname in self.dict_code.values():
                code = codeorname
            else:
                windowQ.put([1, '시스템 명령 오류 알림 - 종목명 또는 종목코드를 잘못입력하였습니다.'])
                return
        workerQ.put(f"현재가{ui_num['차트P3']} {code}")

    def UpdateTexedit(self, msg):
        if msg[0] == 0:
            self.gg_textEdit.clear()
            self.gg_textEdit.append(msg[1])
        elif msg[0] == 1:
            if '니다' in msg[1] or '시오' in msg[1] or '실패' in msg[1]:
                self.lg_textEdit.setTextColor(color_fg_bc)
            elif '주문' in msg[1] or '매수' in msg[1] or '매도' in msg[1]:
                self.lg_textEdit.setTextColor(color_fg_bt)
            else:
                self.lg_textEdit.setTextColor(color_fg_dk)
            self.lg_textEdit.append(f'[{now()}] {msg[1]}')
            self.log.info(f'[{now()}] {msg[1]}')
            if msg[1] == '시스템 명령 실행 알림 - 시스템 종료':
                sys.exit()
        elif msg[0] == 2:
            pushbutton = None
            if msg[1] == '데이터베이스 불러오기':
                pushbutton = self.sj_pushButton_02
            elif msg[1] == 'OPENAPI 로그인':
                pushbutton = self.sj_pushButton_03
                self.ButtonClicked_4(0)
            elif msg[1] == '계좌평가 및 잔고':
                pushbutton = self.sj_pushButton_04
            elif msg[1] == '코스피 코스닥 차트':
                pushbutton = self.sj_pushButton_05
            elif msg[1] == '장운영시간 알림 등록':
                pushbutton = self.sj_pushButton_06
            elif msg[1] == '업종지수 주식체결 등록':
                pushbutton = self.sj_pushButton_07
            elif msg[1] == '단중장기 주식체결 등록':
                pushbutton = self.sj_pushButton_08
            elif msg[1] == 'VI발동해제 등록':
                self.ButtonClicked_4(2)
                pushbutton = self.sj_pushButton_09
            elif msg[1] == '장운영상태':
                pushbutton = self.sj_pushButton_10
            elif msg[1] == '실시간 조건검색식 등록':
                pushbutton = self.sj_pushButton_11
            elif msg[1] == '단타 목표수익률 달성':
                pushbutton = self.sj_pushButton_12
            elif msg[1] == '단타 전략 중단':
                pushbutton = self.sj_pushButton_13
            elif msg[1] == '잔고청산':
                pushbutton = self.sj_pushButton_14
            elif msg[1] == '실시간 데이터 수신 중단':
                pushbutton = self.sj_pushButton_15
            elif msg[1] == '단중장기 매수주문':
                pushbutton = self.sj_pushButton_16
            elif msg[1] == '일별거래목록 저장':
                pushbutton = self.sj_pushButton_17
            elif msg[1] == '시스템 종료':
                pushbutton = self.sj_pushButton_21
            if pushbutton is not None:
                pushbutton.setStyleSheet(style_bc_dk)
                pushbutton.setFont(qfont12)

            pushbutton = None
            text = None
            if '테스트모드' in msg[1]:
                pushbutton = self.sj_pushButton_18
                text = '테스트모드 ON' if msg[1].split(' ')[-1] in ['ON', '1'] else '테스트모드 OFF'
            elif '모의투자' in msg[1]:
                pushbutton = self.sj_pushButton_19
                text = '모의투자 ON' if msg[1].split(' ')[-1] in ['ON', '1'] else '모의투자 OFF'
            elif '알림소리' in msg[1]:
                pushbutton = self.sj_pushButton_20
                text = '알림소리 ON' if msg[1].split(' ')[-1] in ['ON', '1'] else '알림소리 OFF'

            if pushbutton is not None and text is not None:
                pushbutton.setText(text)
                if msg[1].split(' ')[-1] in ['ON', '1']:
                    pushbutton.setStyleSheet(style_bc_bt)
                else:
                    pushbutton.setStyleSheet(style_bc_dk)
                pushbutton.setFont(qfont12)

            if '텔레그램봇넘버' in msg[1]:
                text = msg[1].split(' ')[-1]
                self.sj_lineEdit_01.setText(text)
                self.sj_lineEdit_01.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            elif '사용자아이디' in msg[1]:
                text = msg[1].split(' ')[-1]
                self.sj_lineEdit_02.setText(text)
                self.sj_lineEdit_02.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        elif msg[0] == 3:
            float_memory = float2str3p2(self.dict_intu['메모리'])
            float_cpuper = float2str2p2(self.dict_intu['시피유'])
            label01text = f"UI Process - Memory {float_memory}MB | Threads {self.dict_intu['스레드']}EA | "\
                          f'CPU {float_cpuper}%'

            float_memory = float2str3p2(msg[1])
            float_cpuper = float2str2p2(msg[3])
            label02text = f'Worker Process - Memory {float_memory}MB | Threads {msg[2]}EA | CPU {float_cpuper}%'

            float_memory = self.dict_intt['메모리'] + self.dict_intl['메모리']
            float_memory += self.dict_intm['메모리'] + self.dict_ints['메모리']
            float_thread = self.dict_intt['스레드'] + self.dict_intl['스레드']
            float_thread += self.dict_intm['스레드'] + self.dict_ints['스레드']
            float_cpuper = self.dict_intt['시피유'] + self.dict_intl['시피유']
            float_cpuper += self.dict_intm['시피유'] + self.dict_ints['시피유']
            float_memory = round(float_memory, 2)
            float_cpuper = round(float_cpuper, 2)

            total_memory = round(self.dict_intu['메모리'] + msg[1] + float_memory, 2)
            total_threads = self.dict_intu['스레드'] + msg[2] + float_thread
            total_cpuper = round(self.dict_intu['시피유'] + msg[3] + float_cpuper, 2)

            float_memory = float2str3p2(float_memory)
            float_cpuper = float2str2p2(float_cpuper)
            label03text = f"Strategy Process - Memory {float_memory}MB | Threads {float_thread}EA | "\
                          f"CPU {float_cpuper}%"

            chartq_size = chart1Q.qsize() + chart2Q.qsize() + chart3Q.qsize() + chart4Q.qsize() + chart5Q.qsize()
            chartq_size += chart6Q.qsize() + chart7Q.qsize() + chart8Q.qsize() + chart9Q.qsize()
            hogaq_size = hoga1Q.qsize() + hoga2Q.qsize()
            stgq_size = stgtQ.qsize() + stglQ.qsize() + stgmQ.qsize() + stgsQ.qsize()
            label04text = f'Queue - windowQ {windowQ.qsize()} | workerQ {workerQ.qsize()} | stgQ {stgq_size} | '\
                          f'chartQ {chartq_size} | hogaQ {hogaq_size} | queryQ {queryQ.qsize()} | '\
                          f'soundQ {soundQ.qsize()} | teleQ {teleQ.qsize()}'

            label05text = f'Data Received - TR {msg[4]} | CJ {msg[5]} | '\
                          f"JC {format(msg[6], ',')} | HJ {format(msg[7], ',')} | "\
                          f'RTJC {msg[8]} TICKps | RTHJ {msg[9]} TICKps'

            label06text = f'Total Process - Memory {total_memory}MB | Threads {total_threads}EA | CPU {total_cpuper}%'
            if self.mode2 == 0:
                self.info_label_01.setText(label01text)
                self.info_label_02.setText(label02text)
                self.info_label_03.setText(label03text)
                self.info_label_04.setText(label04text)
                self.info_label_05.setText(label05text)
            self.info_label_06.setText(label06text)
            self.UpdateSysinfo()
        elif msg[0] == 4:
            self.dict_intt['메모리'] = msg[1]
            self.dict_intt['스레드'] = msg[2]
            self.dict_intt['시피유'] = msg[3]
        elif msg[0] == 5:
            self.dict_intl['메모리'] = msg[1]
            self.dict_intl['스레드'] = msg[2]
            self.dict_intl['시피유'] = msg[3]
        elif msg[0] == 6:
            self.dict_intm['메모리'] = msg[1]
            self.dict_intm['스레드'] = msg[2]
            self.dict_intm['시피유'] = msg[3]
        elif msg[0] == 7:
            self.dict_ints['메모리'] = msg[1]
            self.dict_ints['스레드'] = msg[2]
            self.dict_ints['시피유'] = msg[3]
        elif msg[0] == 8:
            self.dict_code = msg[1]
        elif msg[0] == 9:
            self.dict_name = msg[1]
            completer = QtWidgets.QCompleter(list(self.dict_code.keys()) + list(self.dict_name.keys()))
            self.ct_lineEdit_01.setCompleter(completer)
            self.ct_lineEdit_02.setCompleter(completer)

    def UpdateChart(self, data):
        gubun = data[0]
        df = data[1]

        if self.mode2 != 0:
            return
        if gubun in [ui_num['차트P1'], ui_num['차트P2']] and (self.mode0 != 0 or self.mode1 not in [0, 1]):
            return
        if gubun in [ui_num['차트P3'], ui_num['차트P4']] and (self.mode0 != 0 or self.mode1 != 0):
            return
        if gubun in [ui_num['차트P6'], ui_num['차트P7'], ui_num['차트P8'], ui_num['차트P9']] and \
                (self.mode0 != 1 or self.mode1 != 0):
            return
        if gubun == ui_num['차트P5'] and self.mode1 != 2:
            return

        def crosshair(yminn, pc, main_pg=None, sub_pg=None):
            if main_pg is not None:
                vLine1 = pg.InfiniteLine()
                vLine1.setPen(pg.mkPen(color_fg_bk, width=1))
                hLine = pg.InfiniteLine(angle=0)
                hLine.setPen(pg.mkPen(color_fg_bk, width=1))
                main_pg.addItem(vLine1, ignoreBounds=True)
                main_pg.addItem(hLine, ignoreBounds=True)
                main_vb = main_pg.getViewBox()
                label = pg.TextItem(anchor=(0, 1), color=color_fg_bt, border=color_bg_bt, fill=color_bg_ld)
                label.setFont(qfont12)
                label.setPos(-0.25, yminn)
                main_pg.addItem(label)
            if sub_pg is not None:
                vLine2 = pg.InfiniteLine()
                vLine2.setPen(pg.mkPen(color_fg_bk, width=1))
                sub_pg.addItem(vLine2, ignoreBounds=True)
                sub_vb = sub_pg.getViewBox()

            def mouseMoved(evt):
                pos = evt[0]
                if main_pg is not None and main_pg.sceneBoundingRect().contains(pos):
                    mousePoint = main_vb.mapSceneToView(pos)
                    per = round((mousePoint.y() / pc - 1) * 100, 2)
                    label.setText(f"십자선 {format(int(mousePoint.y()), ',')}\n등락율 {per}%")
                    vLine1.setPos(mousePoint.x())
                    hLine.setPos(mousePoint.y())
                    if sub_pg is not None:
                        vLine2.setPos(mousePoint.x())
                if sub_pg is not None and sub_pg.sceneBoundingRect().contains(pos):
                    mousePoint = sub_vb.mapSceneToView(pos)
                    vLine1.setPos(mousePoint.x())
                    vLine2.setPos(mousePoint.x())
            if main_pg is not None:
                main_pg.proxy = pg.SignalProxy(main_pg.scene().sigMouseMoved, rateLimit=20, slot=mouseMoved)
            if sub_pg is not None:
                sub_pg.proxy = pg.SignalProxy(main_pg.scene().sigMouseMoved, rateLimit=20, slot=mouseMoved)

        def getMainLegendText():
            cc = df['현재가'][-1]
            per = round((c / df['전일종가'][0] - 1) * 100, 2)
            nlist = [ui_num['차트P2'], ui_num['차트P4'], ui_num['차트P5'], ui_num['차트P7'], ui_num['차트P9']]
            if gubun in nlist:
                ema05 = df['지수이평05'][-1]
                ema10 = df['지수이평10'][-1]
                ema20 = df['지수이평20'][-1]
                textt = f"05이평 {format(ema05, ',')}\n10이평 {format(ema10, ',')}\n" \
                        f"20이평 {format(ema20, ',')}\n현재가  {format(cc, ',')}\n등락율  {per}%"
            else:
                ema05 = df['지수이평05'][-1]
                ema20 = df['지수이평20'][-1]
                ema60 = df['지수이평60'][-1]
                textt = f"05이평 {format(ema05, ',')}\n20이평 {format(ema20, ',')}\n" \
                        f"60이평 {format(ema60, ',')}\n현재가  {format(cc, ',')}\n등락율  {per}%"
            return textt

        def getSubLegendText():
            money = int(df['거래량'][-1])
            per = round(df['거래량'][-1] / df['거래량'][-2] * 100, 2)
            textt = f"거래량 {format(money, ',')}\n증감비 {per}%"
            return textt

        x = len(df) - 1
        c = df['현재가'][-1]
        o = df['시가'][-1]
        prec = df['전일종가'][0]
        v = df['거래량'][-1]
        vmax = df['거래량'].max()
        name = df['종목명'][0]

        if gubun in [ui_num['차트P1'], ui_num['차트P3']]:
            ymin = min(df['저가'].min(), df['지수이평05'].min(), df['지수이평20'].min(), df['지수이평60'].min(),
                       df['지수이평120'].min(), df['지수이평240'].min(), df['지수이평480'].min())
            ymax = max(df['고가'].max(), df['지수이평05'].max(), df['지수이평20'].max(), df['지수이평60'].max(),
                       df['지수이평120'].max(), df['지수이평240'].max(), df['지수이평480'].max())
        elif gubun in [ui_num['차트P2'], ui_num['차트P4'], ui_num['차트P5'], ui_num['차트P7'], ui_num['차트P9']]:
            ymin = min(df['저가'].min(), df['지수이평05'].min(), df['지수이평10'].min(), df['지수이평20'].min(),
                       df['지수이평40'].min(), df['지수이평60'].min(), df['지수이평120'].min())
            ymax = max(df['고가'].max(), df['지수이평05'].max(), df['지수이평10'].max(), df['지수이평20'].max(),
                       df['지수이평40'].max(), df['지수이평60'].max(), df['지수이평120'].max())
        else:
            ymin = min(df['저가'].min(), df['지수이평05'].min(), df['지수이평20'].min(), df['지수이평60'].min())
            ymax = max(df['고가'].max(), df['지수이평05'].max(), df['지수이평20'].max(), df['지수이평60'].max())

        if gubun not in self.dict_mcpg_lastindex.keys() or self.dict_mcpg_lastindex[gubun] != df.index[-1] or \
                gubun not in self.dict_mcpg_name.keys() or self.dict_mcpg_name[gubun] != name:
            self.dict_ctpg[gubun][0].clear()
            self.dict_ctpg[gubun][1].clear()
            self.dict_mcpg_lastindex[gubun] = df.index[-1]
            self.dict_ctpg[gubun][0].addItem(ChuseItem(df, ymin, ymax))
            self.dict_ctpg[gubun][0].addItem(MoveavgItem(df, gubun))
            self.dict_ctpg[gubun][0].addItem(CandlestickItem(df))
            self.dict_mcpg_lastchuse[gubun] = LastChuseItem(df, ymin, ymax)
            self.dict_mcpg_lastmoveavg[gubun] = LastMoveavgItem(df, gubun)
            self.dict_mcpg_lastcandlestick[gubun] = LastCandlestickItem(df)
            self.dict_ctpg[gubun][0].addItem(self.dict_mcpg_lastchuse[gubun])
            self.dict_ctpg[gubun][0].addItem(self.dict_mcpg_lastmoveavg[gubun])
            self.dict_ctpg[gubun][0].addItem(self.dict_mcpg_lastcandlestick[gubun])
            if gubun == ui_num['차트P5'] and self.mode1 == 2:
                for i, index2 in enumerate(df.index):
                    if df['매수체결가'][index2] != '':
                        for price in df['매수체결가'][index2].split(';'):
                            arrow = pg.ArrowItem(angle=-180, tipAngle=30, baseAngle=20, headLen=20, tailLen=10,
                                                 tailWidth=2, pen=None, brush='r')
                            arrow.setPos(i, int(price))
                            self.dict_ctpg[gubun][0].addItem(arrow)
                            text = pg.TextItem(anchor=(1, 0.5), color=color_fg_bt, border=color_bg_bt, fill=color_bg_ld)
                            text.setFont(qfont12)
                            text.setPos(i - 1, int(price))
                            text.setText(price)
                            self.dict_ctpg[gubun][0].addItem(text)
                    if df['매도체결가'][index2] != '':
                        for price in df['매도체결가'][index2].split(';'):
                            arrow = pg.ArrowItem(angle=-180, tipAngle=30, baseAngle=20, headLen=20, tailLen=10,
                                                 tailWidth=2, pen=None, brush='b')
                            arrow.setPos(i, int(price))
                            self.dict_ctpg[gubun][0].addItem(arrow)
                            text = pg.TextItem(anchor=(1, 0.5), color=color_fg_bt, border=color_bg_bt, fill=color_bg_ld)
                            text.setFont(qfont12)
                            text.setPos(i - 1, int(price))
                            text.setText(price)
                            self.dict_ctpg[gubun][0].addItem(text)
            self.dict_mcpg_infiniteline[gubun] = pg.InfiniteLine(angle=0)
            self.dict_mcpg_infiniteline[gubun].setPen(pg.mkPen(color_cifl))
            self.dict_mcpg_infiniteline[gubun].setPos(c)
            self.dict_ctpg[gubun][0].addItem(self.dict_mcpg_infiniteline[gubun])
            xticks = [list(zip(range(len(df.index))[::12], df.index[::12]))]
            self.dict_ctpg[gubun][0].getAxis('bottom').setTicks(xticks)
            self.dict_ctpg[gubun][1].addItem(VolumeBarsItem(df))
            self.dict_mcpg_lastmoneybar[gubun] = LastVolumeBarItem(x, c, o, v)
            self.dict_ctpg[gubun][1].addItem(self.dict_mcpg_lastmoneybar[gubun])
            self.dict_ctpg[gubun][1].getAxis('bottom').setLabel(text=name)
            self.dict_ctpg[gubun][1].getAxis('bottom').setTicks(xticks)
            crosshair(ymin, prec, main_pg=self.dict_ctpg[gubun][0], sub_pg=self.dict_ctpg[gubun][1])
            self.dict_mcpg_legend1[gubun] = pg.TextItem(color=color_fg_bt, border=color_bg_bt, fill=color_bg_ld)
            self.dict_mcpg_legend1[gubun].setFont(qfont12)
            self.dict_mcpg_legend1[gubun].setPos(-0.25, ymax)
            self.dict_mcpg_legend1[gubun].setText(getMainLegendText())
            self.dict_ctpg[gubun][0].addItem(self.dict_mcpg_legend1[gubun])
            self.dict_mcpg_legend2[gubun] = pg.TextItem(color=color_fg_bt, border=color_bg_bt, fill=color_bg_ld)
            self.dict_mcpg_legend2[gubun].setFont(qfont12)
            self.dict_mcpg_legend2[gubun].setPos(-0.25, vmax)
            self.dict_mcpg_legend2[gubun].setText(getSubLegendText())
            self.dict_ctpg[gubun][1].addItem(self.dict_mcpg_legend2[gubun])
            if gubun not in self.dict_mcpg_name.keys() or self.dict_mcpg_name[gubun] != name:
                self.dict_ctpg[gubun][0].enableAutoRange(enable=True)
                self.dict_ctpg[gubun][1].enableAutoRange(enable=True)
                self.dict_mcpg_name[gubun] = name
        else:
            if gubun not in self.dict_mcpg_close.keys() or self.dict_mcpg_close[gubun] != c:
                self.dict_ctpg[gubun][0].removeItem(self.dict_mcpg_lastchuse[gubun])
                self.dict_ctpg[gubun][0].removeItem(self.dict_mcpg_lastmoveavg[gubun])
                self.dict_ctpg[gubun][0].removeItem(self.dict_mcpg_lastcandlestick[gubun])
                self.dict_mcpg_lastchuse[gubun] = LastChuseItem(df, ymin, ymax)
                self.dict_mcpg_lastmoveavg[gubun] = LastMoveavgItem(df, gubun)
                self.dict_mcpg_lastcandlestick[gubun] = LastCandlestickItem(df)
                self.dict_ctpg[gubun][0].addItem(self.dict_mcpg_lastchuse[gubun])
                self.dict_ctpg[gubun][0].addItem(self.dict_mcpg_lastmoveavg[gubun])
                self.dict_ctpg[gubun][0].addItem(self.dict_mcpg_lastcandlestick[gubun])
                self.dict_mcpg_infiniteline[gubun].setPos(c)
                self.dict_mcpg_legend1[gubun].setText(getMainLegendText())
                self.dict_mcpg_close[gubun] = c
            self.dict_ctpg[gubun][1].removeItem(self.dict_mcpg_lastmoneybar[gubun])
            self.dict_mcpg_lastmoneybar[gubun] = LastVolumeBarItem(x, c, o, v)
            self.dict_ctpg[gubun][1].addItem(self.dict_mcpg_lastmoneybar[gubun])
            self.dict_mcpg_legend2[gubun].setText(getSubLegendText())

    def UpdateTick(self, data):
        gubun = data[0]
        dict_df = data[1]

        if gubun == ui_num['단타설정']:
            df = data[1]
            self.dict_intg['체결강도차이'] = df['체결강도차이'][0]
            self.dict_intg['거래대금차이'] = df['거래대금차이'][0]
            self.dict_intg['평균시간'] = df['평균시간'][0]
            self.dict_intg['청산시간'] = df['청산시간'][0]
            self.dict_intg['체결강도하한'] = df['체결강도하한'][0]
            self.dict_intg['전일거래량대비하한'] = df['전일거래량대비하한'][0]
            self.dict_intg['누적거래대금하한'] = df['누적거래대금하한'][0]
            self.dict_intg['등락율상한'] = df['등락율상한'][0]
            self.dict_intg['고저평균대비등락율하한'] = df['고저평균대비등락율하한'][0]
            return

        if gubun == ui_num['tick'] and self.table_tabWidget.currentWidget() != self.gjt_tab:
            return

        if len(dict_df) == 0:
            self.gjt_tableWidget.clearContents()
            return

        def changeFormat(text):
            text = str(text)
            try:
                format_data = format(int(text), ',')
            except ValueError:
                format_data = format(float(text), ',')
                if len(format_data.split('.')) >= 2:
                    if len(format_data.split('.')[1]) == 1:
                        format_data += '0'
            return format_data

        self.gjt_tableWidget.setRowCount(len(dict_df))
        for j, code in enumerate(list(dict_df.keys())):
            item = QtWidgets.QTableWidgetItem(self.dict_name[code])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.gjt_tableWidget.setItem(j, 0, item)
            smavg = dict_df[code]['거래대금'][self.dict_intg['평균시간'] + 1]
            item = QtWidgets.QTableWidgetItem(changeFormat(smavg))
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.gjt_tableWidget.setItem(j, 7, item)
            chavg = dict_df[code]['체결강도'][self.dict_intg['평균시간'] + 1]
            item = QtWidgets.QTableWidgetItem(changeFormat(chavg))
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.gjt_tableWidget.setItem(j, 8, item)
            chhigh = dict_df[code]['최고체결강도'][self.dict_intg['평균시간'] + 1]
            item = QtWidgets.QTableWidgetItem(changeFormat(chhigh))
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.gjt_tableWidget.setItem(j, 9, item)
            for i, column in enumerate(columns_gs2):
                if column in ['거래대금', '누적거래대금']:
                    item = QtWidgets.QTableWidgetItem(changeFormat(dict_df[code][column][0]).split('.')[0])
                else:
                    item = QtWidgets.QTableWidgetItem(changeFormat(dict_df[code][column][0]))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                # 전략별 글자 색상 변공 비공개

                self.gjt_tableWidget.setItem(j, i + 1, item)
        if len(dict_df) < 46:
            self.gjt_tableWidget.setRowCount(46)

    def UpdateLongMidShort(self, data):
        gubun = data[0]
        df = data[1]

        gj_tableWidget = None
        columns = None
        if gubun in [ui_num['short'], ui_num['short'] + 100]:
            if gubun == ui_num['short'] and self.table_tabWidget.currentWidget() != self.gjs_tab:
                return
            columns = columns_gjs
            gj_tableWidget = self.gjs_tableWidget
        elif gubun in [ui_num['mid'], ui_num['mid'] + 100]:
            if gubun == ui_num['mid'] and self.table_tabWidget.currentWidget() != self.gjm_tab:
                return
            columns = columns_gjm
            gj_tableWidget = self.gjm_tableWidget
        elif gubun in [ui_num['long'], ui_num['long'] + 100]:
            if gubun == ui_num['long'] and self.table_tabWidget.currentWidget() != self.gjl_tab:
                return
            columns = columns_gjl
            gj_tableWidget = self.gjl_tableWidget

        if gj_tableWidget is None or columns is None:
            return

        if len(df) == 0:
            gj_tableWidget.clearContents()
            return

        def changeFormat(text, bijung=False):
            text = str(text)
            try:
                format_data = format(int(text), ',')
            except ValueError:
                format_data = format(float(text), ',')
                if len(format_data.split('.')) >= 2:
                    if bijung:
                        if len(format_data.split('.')[1]) == 3:
                            format_data += '0'
                        elif len(format_data.split('.')[1]) == 2:
                            format_data += '00'
                        elif len(format_data.split('.')[1]) == 1:
                            format_data += '000'
                    else:
                        if len(format_data.split('.')[1]) == 1:
                            format_data += '0'
            return format_data

        gj_tableWidget.setRowCount(len(df))
        for j, code in enumerate(df.index):
            for i, column in enumerate(columns):
                if column == '종목명':
                    item = QtWidgets.QTableWidgetItem(self.dict_name[code])
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                else:
                    if column == '비중':
                        item = QtWidgets.QTableWidgetItem(changeFormat(df[column][code], True))
                    else:
                        item = QtWidgets.QTableWidgetItem(changeFormat(df[column][code]))
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                # 전략별 글자 색상 변공 비공개

                gj_tableWidget.setItem(j, i, item)
        if len(df) < 46:
            gj_tableWidget.setRowCount(46)

    def UpdateTablewidget(self, data):
        gubun = data[0]
        df = data[1]

        if gubun == ui_num['체결강도'] and (self.mode2 != 0 or self.mode1 != 1):
            return
        nlist = [ui_num['호가잔고0'], ui_num['매도주문0'], ui_num['체결수량0'], ui_num['호가0'], ui_num['매수주문0']]
        if gubun in nlist and (self.mode2 != 0 or self.mode1 not in [0, 1]):
            return
        nlist = [ui_num['호가잔고1'], ui_num['매도주문1'], ui_num['체결수량1'], ui_num['호가1'], ui_num['매수주문1']]
        if gubun in nlist and (self.mode2 != 0 or self.mode1 != 0):
            return

        def changeFormat(text):
            text = str(text)
            try:
                format_data = format(int(text), ',')
            except ValueError:
                format_data = format(float(text), ',')
                if len(format_data.split('.')) >= 2:
                    if len(format_data.split('.')[1]) == 1:
                        format_data += '0'
            nnlist = [ui_num['체결수량0'], ui_num['호가0'], ui_num['체결수량1'], ui_num['호가1']]
            if gubun in nnlist and format_data in ['0', '0.00']:
                format_data = ''
            return format_data

        tableWidget = None
        if gubun == ui_num['거래합계']:
            tableWidget = self.tt_tableWidget
        elif gubun == ui_num['거래목록']:
            tableWidget = self.td_tableWidget
        elif gubun == ui_num['잔고평가']:
            tableWidget = self.tj_tableWidget
        elif gubun == ui_num['잔고목록']:
            tableWidget = self.jg_tableWidget
        elif gubun == ui_num['체결목록']:
            tableWidget = self.cj_tableWidget
        elif gubun == ui_num['기업공시']:
            tableWidget = self.gs_tableWidget
        elif gubun == ui_num['기업뉴스']:
            tableWidget = self.ns_tableWidget
        elif gubun == ui_num['투자자']:
            tableWidget = self.jj_tableWidget
        elif gubun == ui_num['재무년도']:
            tableWidget = self.jm1_tableWidget
            tableWidget.setHorizontalHeaderLabels(df.columns)
        elif gubun == ui_num['재무분기']:
            tableWidget = self.jm2_tableWidget
            tableWidget.setHorizontalHeaderLabels(df.columns)
        elif gubun == ui_num['동업종비교']:
            tableWidget = self.jb_tableWidget
            tableWidget.setHorizontalHeaderLabels(df.columns)
        elif gubun == ui_num['체결강도']:
            tableWidget = self.ch_tableWidget
        elif gubun == ui_num['당일합계']:
            tableWidget = self.stn_tableWidget
        elif gubun == ui_num['당일상세']:
            tableWidget = self.stl_tableWidget
        elif gubun == ui_num['누적합계']:
            tableWidget = self.sgt_tableWidget
        elif gubun == ui_num['누적상세']:
            tableWidget = self.sgl_tableWidget
        elif gubun == ui_num['호가잔고0']:
            tableWidget = self.hoga_00_hj_tableWidget
        elif gubun == ui_num['매도주문0']:
            tableWidget = self.hoga_00_hs_tableWidget
        elif gubun == ui_num['체결수량0']:
            tableWidget = self.hoga_00_hc_tableWidget
        elif gubun == ui_num['호가0']:
            tableWidget = self.hoga_00_hg_tableWidget
        elif gubun == ui_num['매수주문0']:
            tableWidget = self.hoga_00_hb_tableWidget
        elif gubun == ui_num['호가잔고1']:
            tableWidget = self.hoga_01_hj_tableWidget
        elif gubun == ui_num['매도주문1']:
            tableWidget = self.hoga_01_hs_tableWidget
        elif gubun == ui_num['체결수량1']:
            tableWidget = self.hoga_01_hc_tableWidget
        elif gubun == ui_num['호가1']:
            tableWidget = self.hoga_01_hg_tableWidget
        elif gubun == ui_num['매수주문1']:
            tableWidget = self.hoga_01_hb_tableWidget
        if tableWidget is None:
            return

        if len(df) == 0:
            tableWidget.clearContents()
            return

        tableWidget.setRowCount(len(df))
        for j, index in enumerate(df.index):
            for i, column in enumerate(df.columns):
                if column == '체결시간':
                    cgtime = df[column][index]
                    if gubun == ui_num['체결강도']:
                        cgtime = f'{cgtime[:2]}:{cgtime[2:4]}:{cgtime[4:6]}'
                    else:
                        cgtime = f'{cgtime[8:10]}:{cgtime[10:12]}:{cgtime[12:14]}'
                    item = QtWidgets.QTableWidgetItem(cgtime)
                elif column in ['거래일자', '일자']:
                    day = df[column][index]
                    if '.' not in day:
                        day = day[:4] + '.' + day[4:6] + '.' + day[6:]
                    item = QtWidgets.QTableWidgetItem(day)
                elif column in ['종목명', '주문구분', '호가종목명', '기간', '매도미체결수량', '매수미체결수량',
                                '공시', '정보제공', '언론사', '제목', '전략구분']:
                    item = QtWidgets.QTableWidgetItem(str(df[column][index]))
                elif gubun in [ui_num['재무년도'], ui_num['재무분기'], ui_num['동업종비교']]:
                    try:
                        item = QtWidgets.QTableWidgetItem(str(df[column][index]))
                    except KeyError:
                        continue
                elif column not in ['수익률', '등락율', '고저평균대비등락율', '체결강도',
                                    '체결강도5분', '체결강도20분', '체결강도60분', '최고체결강도']:
                    item = QtWidgets.QTableWidgetItem(changeFormat(df[column][index]).split('.')[0])
                else:
                    item = QtWidgets.QTableWidgetItem(changeFormat(df[column][index]))

                if column in ['종목명', '호가종목명', '공시', '제목', '구분']:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                elif column in ['거래횟수', '추정예탁자산', '추정예수금', '보유종목수', '주문구분', '체결시간', '거래일자', '기간',
                                '일자', '매도미체결수량', '매도미체결수량', '정보제공', '언론사', '전략구분']:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                if column == '체결수량':
                    if j == 0:
                        item.setIcon(self.icon_totalb)
                    elif j == 21:
                        item.setIcon(self.icon_totals)
                elif column == '체결강도' and gubun in [ui_num['체결수량0'], ui_num['체결수량1']]:
                    if j == 0:
                        item.setIcon(self.icon_up)
                    elif j == 21:
                        item.setIcon(self.icon_down)
                elif gubun in [ui_num['호가0'], ui_num['호가1']]:
                    if column == '증감':
                        if j == 0:
                            item.setIcon(self.icon_perb)
                        elif j == 21:
                            item.setIcon(self.icon_pers)
                    elif column == '잔량':
                        if j == 0:
                            item.setIcon(self.icon_totalb)
                        elif j == 21:
                            item.setIcon(self.icon_totals)
                    elif column == '호가':
                        if j == 0:
                            item.setIcon(self.icon_up)
                        elif j == 21:
                            item.setIcon(self.icon_down)
                        else:
                            if gubun == ui_num['호가0']:
                                hj_tableWidget = self.hoga_00_hj_tableWidget
                            else:
                                hj_tableWidget = self.hoga_01_hj_tableWidget
                            if hj_tableWidget.item(0, 0) is not None:
                                o = comma2int(hj_tableWidget.item(0, 7).text())
                                h = comma2int(hj_tableWidget.item(0, 8).text())
                                low = comma2int(hj_tableWidget.item(0, 9).text())
                                if o != 0:
                                    if df[column][index] == o:
                                        item.setIcon(self.icon_open)
                                    elif df[column][index] == h:
                                        item.setIcon(self.icon_high)
                                    elif df[column][index] == low:
                                        item.setIcon(self.icon_low)
                    elif column == '등락율':
                        if j == 0:
                            item.setIcon(self.icon_up)
                        elif j == 21:
                            item.setIcon(self.icon_down)
                        else:
                            if gubun == ui_num['호가0']:
                                hj_tableWidget = self.hoga_00_hj_tableWidget
                            else:
                                hj_tableWidget = self.hoga_01_hj_tableWidget
                            if hj_tableWidget.item(0, 0) is not None:
                                uvi = comma2int(hj_tableWidget.item(0, 13).text())
                                dvi = comma2int(hj_tableWidget.item(0, 14).text())
                                if df[column][index] != 0:
                                    if j < 11:
                                        if df['호가'][index] == uvi:
                                            item.setIcon(self.icon_vi)
                                    else:
                                        if df['호가'][index] == dvi:
                                            item.setIcon(self.icon_vi)

                if '수익률' in df.columns:
                    if df['수익률'][index] >= 0:
                        item.setForeground(color_fg_bt)
                    else:
                        item.setForeground(color_fg_dk)
                elif gubun == ui_num['체결목록']:
                    if df['주문구분'][index] == '매수':
                        item.setForeground(color_fg_bt)
                    elif df['주문구분'][index] == '매도':
                        item.setForeground(color_fg_dk)
                    elif df['주문구분'][index] in ['매도취소', '매수취소']:
                        item.setForeground(color_fg_bc)
                elif gubun in [ui_num['기업공시'], ui_num['기업뉴스']]:
                    cname = '공시' if gubun == ui_num['기업공시'] else '제목'
                    if '단기과열' in df[cname][index] or '투자주의' in df[cname][index] or \
                            '투자경고' in df[cname][index] or '투자위험' in df[cname][index] or \
                            '거래정지' in df[cname][index] or '환기종목' in df[cname][index] or \
                            '불성실공시' in df[cname][index] or '관리종목' in df[cname][index] or \
                            '정리매매' in df[cname][index] or '유상증자' in df[cname][index] or \
                            '무상증자' in df[cname][index]:
                        item.setForeground(color_fg_bt)
                    else:
                        item.setForeground(color_fg_dk)
                elif gubun == ui_num['투자자']:
                    if column in ['등락율', '개인투자자', '외국인투자자', '기관계']:
                        if df[column][index] >= 0:
                            item.setForeground(color_fg_bt)
                        else:
                            item.setForeground(color_fg_dk)
                elif gubun in [ui_num['재무년도'],  ui_num['재무분기'],  ui_num['동업종비교']]:
                    if '-' not in df[column][index] and column != '구분':
                        item.setForeground(color_fg_bt)
                    else:
                        item.setForeground(color_fg_dk)
                elif gubun == ui_num['체결강도']:
                    if column == '등락율':
                        if df[column][index] >= 0:
                            item.setForeground(color_fg_bt)
                        else:
                            item.setForeground(color_fg_dk)
                    elif '체결강도' in column:
                        if df[column][index] >= 100:
                            item.setForeground(color_fg_bt)
                        else:
                            item.setForeground(color_fg_dk)
                elif gubun in [ui_num['체결수량0'], ui_num['체결수량1']]:
                    if column == '체결수량':
                        if j == 0:
                            if df[column][index] > df[column][21]:
                                item.setForeground(color_fg_bt)
                            else:
                                item.setForeground(color_fg_dk)
                        elif j == 21:
                            if df[column][index] > df[column][0]:
                                item.setForeground(color_fg_bt)
                            else:
                                item.setForeground(color_fg_dk)
                        else:
                            if gubun == ui_num['체결수량0']:
                                hg_tableWidget = self.hoga_00_hg_tableWidget
                            else:
                                hg_tableWidget = self.hoga_01_hg_tableWidget
                            if hg_tableWidget.item(0, 0) is not None and hg_tableWidget.item(10, 2).text() != '':
                                c = comma2int(hg_tableWidget.item(10, 2).text())
                                if df[column][index] > 0:
                                    item.setForeground(color_fg_bt)
                                    if df[column][index] * c > 90000000:
                                        item.setBackground(color_bf_bt)
                                elif df[column][index] < 0:
                                    item.setForeground(color_fg_dk)
                                    if df[column][index] * c < -90000000:
                                        item.setBackground(color_bf_dk)
                    elif column == '체결강도':
                        if df[column][index] >= 100:
                            item.setForeground(color_fg_bt)
                        else:
                            item.setForeground(color_fg_dk)
                elif gubun in [ui_num['호가0'], ui_num['호가1']]:
                    if '증감' in column:
                        if j == 0:
                            if df[column][index] > 100:
                                item.setForeground(color_fg_bt)
                            else:
                                item.setForeground(color_fg_dk)
                        elif j == 21:
                            if df[column][index] > 100:
                                item.setForeground(color_fg_bt)
                            else:
                                item.setForeground(color_fg_dk)
                        elif df[column][index] > 0:
                            item.setForeground(color_fg_bt)
                            if df[column][index] * df['호가'][10] > 90000000:
                                item.setBackground(color_bf_bt)
                        elif df[column][index] < 0:
                            item.setForeground(color_fg_dk)
                            if df[column][index] * df['호가'][11] < -90000000:
                                item.setBackground(color_bf_dk)
                    elif column == '잔량':
                        if j == 0:
                            if df[column][index] > df[column][21]:
                                item.setForeground(color_fg_bt)
                            else:
                                item.setForeground(color_fg_dk)
                        elif j == 21:
                            if df[column][index] > df[column][0]:
                                item.setForeground(color_fg_bt)
                            else:
                                item.setForeground(color_fg_dk)
                        elif j < 11:
                            item.setForeground(color_fg_bt)
                        else:
                            item.setForeground(color_fg_dk)
                    elif column in ['호가', '등락율']:
                        if df['등락율'][index] > 0:
                            item.setForeground(color_fg_bt)
                        elif df['등락율'][index] < 0:
                            item.setForeground(color_fg_dk)
                        if column == '호가' and df[column][index] != 0:
                            if gubun == ui_num['호가0']:
                                hj_tableWidget = self.hoga_00_hj_tableWidget
                            else:
                                hj_tableWidget = self.hoga_01_hj_tableWidget
                            if hj_tableWidget.item(0, 0) is not None:
                                c = comma2int(hj_tableWidget.item(0, 2).text())
                                if j not in [0, 21] and df[column][index] == c:
                                    item.setBackground(color_bf_bt)
                                if hj_tableWidget.item(0, 1).text() != '0':
                                    gap = df[column][19] - df[column][20]
                                    bp = comma2int(hj_tableWidget.item(0, 1).text())
                                    if df[column][index] <= bp < df[column][index] + gap:
                                        item.setBackground(color_bf_dk)
                elif gubun in [ui_num['매도주문0'], ui_num['매도주문1'], ui_num['매수주문0'], ui_num['매수주문1']]:
                    item.setForeground(color_fg_bt)
                    item.setBackground(color_bg_bt)
                tableWidget.setItem(j, i, item)

        if len(df) < 13 and gubun in [ui_num['거래목록'], ui_num['잔고목록'], ui_num['체결목록']]:
            tableWidget.setRowCount(13)
        elif len(df) < 22 and gubun == ui_num['기업공시']:
            tableWidget.setRowCount(22)
        elif len(df) < 12 and gubun == ui_num['기업뉴스']:
            tableWidget.setRowCount(12)
        elif len(df) < 28 and gubun == ui_num['체결강도']:
            tableWidget.setRowCount(28)
        elif len(df) < 31 and gubun == ui_num['당일상세']:
            tableWidget.setRowCount(31)
        elif len(df) < 41 and gubun == ui_num['누적상세']:
            tableWidget.setRowCount(41)

    @QtCore.pyqtSlot(int)
    def CellClicked_1(self, row):
        item = self.hoga_00_hj_tableWidget.item(0, 0)
        if item is None:
            return
        name = item.text()
        if self.hoga_00_hj_tableWidget.item(0, 11).text() == '':
            return
        jc = comma2int(self.hoga_00_hj_tableWidget.item(0, 11).text())
        if self.hoga_00_hg_tableWidget.item(row, 2).text() == '':
            return
        hg = comma2int(self.hoga_00_hg_tableWidget.item(row, 2).text())
        bper = 0
        if self.hoga_00_sell_radioButton_01.isChecked():
            bper = 10
        elif self.hoga_00_sell_radioButton_02.isChecked():
            bper = 25
        elif self.hoga_00_sell_radioButton_03.isChecked():
            bper = 33
        elif self.hoga_00_sell_radioButton_04.isChecked():
            bper = 50
        elif self.hoga_00_sell_radioButton_05.isChecked():
            bper = 75
        elif self.hoga_00_sell_radioButton_06.isChecked():
            bper = 100
        if bper == 0:
            windowQ.put([2, '시스템 명령 오류 알림 - 매도비율을 선택하십시오.'])
            return
        oc = int(jc * (bper / 100))
        if oc == 0:
            oc = 1
        code = self.dict_code[self.hoga_00_hj_tableWidget.item(0, 0).text()]
        order = ['매도', '4989', '', 2, code, oc, hg, '00', '', hg, name]
        workerQ.put(order)

    @QtCore.pyqtSlot(int)
    def CellClicked_2(self, row):
        item = self.hoga_00_hj_tableWidget.item(0, 0)
        if item is None:
            return
        name = item.text()
        if self.hoga_00_hg_tableWidget.item(row, 2).text() == '':
            return
        hg = comma2int(self.hoga_00_hg_tableWidget.item(row, 2).text())
        og = 0
        if self.hoga_00_buy_radioButton_01.isChecked():
            og = 100000
        elif self.hoga_00_buy_radioButton_02.isChecked():
            og = 500000
        elif self.hoga_00_buy_radioButton_03.isChecked():
            og = 1000000
        elif self.hoga_00_buy_radioButton_04.isChecked():
            og = 5000000
        elif self.hoga_00_buy_radioButton_05.isChecked():
            og = 10000000
        elif self.hoga_00_buy_radioButton_06.isChecked():
            og = 50000000
        if og == 0:
            windowQ.put([2, '시스템 명령 오류 알림 - 매수금액을 선택하십시오.'])
            return
        oc = int(og / hg)
        code = self.dict_code[name]
        order = ['매수', '4989', '', 1, code, oc, hg, '00', '', hg, name]
        workerQ.put(order)

    @QtCore.pyqtSlot(int)
    def CellClicked_3(self, row):
        item = self.hoga_01_hj_tableWidget.item(0, 0)
        if item is None:
            return
        name = item.text()
        if self.hoga_01_hj_tableWidget.item(0, 11).text() == '':
            return
        jc = comma2int(self.hoga_01_hj_tableWidget.item(0, 11).text())
        if self.hoga_01_hg_tableWidget.item(row, 2).text() == '':
            return
        hg = comma2int(self.hoga_01_hg_tableWidget.item(row, 2).text())
        bper = 0
        if self.hoga_01_sell_radioButton_01.isChecked():
            bper = 10
        elif self.hoga_01_sell_radioButton_02.isChecked():
            bper = 25
        elif self.hoga_01_sell_radioButton_03.isChecked():
            bper = 33
        elif self.hoga_01_sell_radioButton_04.isChecked():
            bper = 50
        elif self.hoga_01_sell_radioButton_05.isChecked():
            bper = 75
        elif self.hoga_01_sell_radioButton_06.isChecked():
            bper = 100
        if bper == 0:
            windowQ.put([2, '시스템 명령 오류 알림 - 매도비율을 선택하십시오.'])
            return
        oc = int(jc * (bper / 100))
        if oc == 0:
            oc = 1
        code = self.dict_code[name]
        order = ['매도', '4989', '', 2, code, oc, hg, '00', '', hg, name]
        workerQ.put(order)

    @QtCore.pyqtSlot(int)
    def CellClicked_4(self, row):
        item = self.hoga_01_hj_tableWidget.item(0, 0)
        if item is None:
            return
        name = item.text()
        if self.hoga_01_hg_tableWidget.item(row, 2).text() == '':
            return
        hg = comma2int(self.hoga_01_hg_tableWidget.item(row, 2).text())
        og = 0
        if self.hoga_01_buy_radioButton_01.isChecked():
            og = 100000
        elif self.hoga_01_buy_radioButton_02.isChecked():
            og = 500000
        elif self.hoga_01_buy_radioButton_03.isChecked():
            og = 1000000
        elif self.hoga_01_buy_radioButton_04.isChecked():
            og = 5000000
        elif self.hoga_01_buy_radioButton_05.isChecked():
            og = 10000000
        elif self.hoga_01_buy_radioButton_06.isChecked():
            og = 50000000
        if og == 0:
            windowQ.put([2, '시스템 명령 오류 알림 - 매수금액을 선택하십시오.'])
            return
        oc = int(og / hg)
        code = self.dict_code[name]
        order = ['매수', '4989', '', 1, code, oc, hg, '00', '', hg, name]
        workerQ.put(order)

    @QtCore.pyqtSlot(int, int)
    def CellClicked_5(self, row, col):
        if col > 1:
            return
        item = self.td_tableWidget.item(row, 0)
        if item is None:
            return
        code = self.dict_code[item.text()]
        self.PutWorkerQ(code, col)

    @QtCore.pyqtSlot(int, int)
    def CellClicked_6(self, row, col):
        if col > 1:
            return
        item = self.jg_tableWidget.item(row, 0)
        if item is None:
            return
        code = self.dict_code[item.text()]
        self.PutWorkerQ(code, col)

    @QtCore.pyqtSlot(int, int)
    def CellClicked_7(self, row, col):
        if col > 1:
            return
        item = self.cj_tableWidget.item(row, 0)
        if item is None:
            return
        code = self.dict_code[item.text()]
        self.PutWorkerQ(code, col)

    @QtCore.pyqtSlot(int, int)
    def CellClicked_8(self, row, col):
        if col > 1:
            return
        item = self.gjt_tableWidget.item(row, 0)
        if item is None:
            return
        code = self.dict_code[item.text()]
        self.PutWorkerQ(code, col)

    @QtCore.pyqtSlot(int, int)
    def CellClicked_9(self, row, col):
        if col > 1:
            return
        item = self.gjs_tableWidget.item(row, 0)
        if item is None:
            return
        code = self.dict_code[item.text()]
        self.PutWorkerQ(code, col)

    @QtCore.pyqtSlot(int, int)
    def CellClicked_10(self, row, col):
        if col > 1:
            return
        item = self.gjm_tableWidget.item(row, 0)
        if item is None:
            return
        code = self.dict_code[item.text()]
        self.PutWorkerQ(code, col)

    @QtCore.pyqtSlot(int, int)
    def CellClicked_11(self, row, col):
        if col > 1:
            return
        item = self.gjl_tableWidget.item(row, 0)
        if item is None:
            return
        code = self.dict_code[item.text()]
        self.PutWorkerQ(code, col)

    @QtCore.pyqtSlot(int, int)
    def CellClicked_12(self, row, col):
        if col > 1:
            return
        item = self.stl_tableWidget.item(row, 1)
        if item is None:
            return
        code = self.dict_code[item.text()]
        self.PutWorkerQ(code, col)

    def PutWorkerQ(self, code, col):
        if self.mode2 != 0:
            return
        if self.mode1 == 0:
            if self.mode0 == 1:
                self.ButtonClicked_4(0)
            if col == 0:
                workerQ.put(f"현재가{ui_num['차트P1']} {code}")
            elif col == 1:
                workerQ.put(f"현재가{ui_num['차트P3']} {code}")
        elif self.mode1 == 1:
            workerQ.put(f"현재가{ui_num['차트P0']} {code}")
        elif self.mode1 == 2:
            if self.table_tabWidget.currentWidget() == self.st_tab:
                date = self.calendarWidget.selectedDate()
                tradeday = date.toString('yyyyMMdd')
            elif 0 < int(strf_time('%H%M%S')) < 90000:
                tradeday = strf_time('%Y%m%d', timedelta_day(-1))
            else:
                tradeday = strf_time('%Y%m%d')
            workerQ.put(f"현재가{ui_num['차트P5']} {tradeday} {code}")

    def CalendarClicked(self):
        date = self.calendarWidget.selectedDate()
        searchday = date.toString('yyyyMMdd')
        con = sqlite3.connect(db_stg)
        df = pd.read_sql(f"SELECT * FROM tradelist WHERE 체결시간 LIKE '{searchday}%'", con)
        con.close()
        if len(df) > 0:
            df = df.set_index('index')
            df.sort_values(by=['체결시간'], ascending=True, inplace=True)
            df = df[['체결시간', '종목명', '매수금액', '매도금액', '주문수량', '수익률', '수익금', '전략구분']].copy()
            nbg, nsg = df['매수금액'].sum(), df['매도금액'].sum()
            sp = round((nsg / nbg - 1) * 100, 2)
            npg, nmg, nsig = df[df['수익금'] > 0]['수익금'].sum(), df[df['수익금'] < 0]['수익금'].sum(), df['수익금'].sum()
            df2 = pd.DataFrame(columns=columns_sn)
            df2.at[0] = searchday, nbg, nsg, npg, nmg, sp, nsig
        else:
            df = pd.DataFrame(columns=columns_st)
            df2 = pd.DataFrame(columns=columns_sn)
        windowQ.put([ui_num['당일합계'], df2])
        windowQ.put([ui_num['당일상세'], df])

    def ButtonClicked_1(self, gubun):
        if gubun in ['시장가매도0', '매도취소0']:
            hj_tableWidget = self.hoga_00_hj_tableWidget
            hg_tableWidget = self.hoga_00_hg_tableWidget
            sell_radioButton_01 = self.hoga_00_sell_radioButton_01
            sell_radioButton_02 = self.hoga_00_sell_radioButton_02
            sell_radioButton_03 = self.hoga_00_sell_radioButton_03
            sell_radioButton_04 = self.hoga_00_sell_radioButton_04
            sell_radioButton_05 = self.hoga_00_sell_radioButton_05
            sell_radioButton_06 = self.hoga_00_sell_radioButton_06
        else:
            hj_tableWidget = self.hoga_01_hj_tableWidget
            hg_tableWidget = self.hoga_01_hg_tableWidget
            sell_radioButton_01 = self.hoga_01_sell_radioButton_01
            sell_radioButton_02 = self.hoga_01_sell_radioButton_02
            sell_radioButton_03 = self.hoga_01_sell_radioButton_03
            sell_radioButton_04 = self.hoga_01_sell_radioButton_04
            sell_radioButton_05 = self.hoga_01_sell_radioButton_05
            sell_radioButton_06 = self.hoga_01_sell_radioButton_06
        item = hj_tableWidget.item(0, 0)
        if item is None:
            return
        code = self.dict_code[item.text()]
        if '시장가매도' in gubun:
            bper = 0
            if sell_radioButton_01.isChecked():
                bper = 1
            elif sell_radioButton_02.isChecked():
                bper = 2
            elif sell_radioButton_03.isChecked():
                bper = 3
            elif sell_radioButton_04.isChecked():
                bper = 5
            elif sell_radioButton_05.isChecked():
                bper = 7.5
            elif sell_radioButton_06.isChecked():
                bper = 10
            if bper == 0:
                windowQ.put([1, '시스템 명령 오류 알림 - 매도비율을 선택하십시오.'])
                return
            c = comma2int(hg_tableWidget.item(11, 2).text())
            if hj_tableWidget.item(0, 11).text() == '':
                return
            jc = comma2int(hj_tableWidget.item(0, 11).text())
            oc = int(jc * (bper / 10))
            if oc == 0:
                oc = 1
            name = hj_tableWidget.item(0, 0).text()
            order = ['매도', '4989', '', 2, code, oc, 0, '03', '', c, name]
            workerQ.put(order)
        elif '매도취소' in gubun:
            order = f'매도취소 {code}'
            workerQ.put(order)

    def ButtonClicked_2(self, gubun):
        if gubun in ['시장가매수0', '매수취소0']:
            hj_tableWidget = self.hoga_00_hj_tableWidget
            hg_tableWidget = self.hoga_00_hg_tableWidget
            buy_radioButton_01 = self.hoga_00_buy_radioButton_01
            buy_radioButton_02 = self.hoga_00_buy_radioButton_02
            buy_radioButton_03 = self.hoga_00_buy_radioButton_03
            buy_radioButton_04 = self.hoga_00_buy_radioButton_04
            buy_radioButton_05 = self.hoga_00_buy_radioButton_05
            buy_radioButton_06 = self.hoga_00_buy_radioButton_06
        else:
            hj_tableWidget = self.hoga_01_hj_tableWidget
            hg_tableWidget = self.hoga_01_hg_tableWidget
            buy_radioButton_01 = self.hoga_01_buy_radioButton_01
            buy_radioButton_02 = self.hoga_01_buy_radioButton_02
            buy_radioButton_03 = self.hoga_01_buy_radioButton_03
            buy_radioButton_04 = self.hoga_01_buy_radioButton_04
            buy_radioButton_05 = self.hoga_01_buy_radioButton_05
            buy_radioButton_06 = self.hoga_01_buy_radioButton_06
        item = hj_tableWidget.item(0, 0)
        if item is None:
            return
        code = self.dict_code[item.text()]
        if '시장가매수' in gubun:
            og = 0
            if buy_radioButton_01.isChecked():
                og = 100000
            elif buy_radioButton_02.isChecked():
                og = 500000
            elif buy_radioButton_03.isChecked():
                og = 1000000
            elif buy_radioButton_04.isChecked():
                og = 5000000
            elif buy_radioButton_05.isChecked():
                og = 10000000
            elif buy_radioButton_06.isChecked():
                og = 50000000
            if og == 0:
                windowQ.put([1, '시스템 명령 오류 알림 - 매수금액을 선택하십시오.'])
                return
            c = comma2int(hg_tableWidget.item(10, 2).text())
            oc = int(og / c)
            name = hj_tableWidget.item(0, 0).text()
            order = ['매수', '4989', '', 1, code, oc, 0, '03', '', c, name]
            workerQ.put(order)
        elif '매수취소' in gubun:
            order = f'매수취소 {code}'
            workerQ.put(order)

    def ButtonClicked_3(self, cmd):
        if cmd == '설정':
            text1 = self.sj_lineEdit_01.text()
            text2 = self.sj_lineEdit_02.text()
            if text1 == '' or text2 == '':
                windowQ.put([1, '시스템 명령 오류 알림 - 텔레그램 봇넘버 및 사용자 아이디를 입력하십시오.'])
                return
            workerQ.put(f'{cmd} {text1} {text2}')
        elif '집계' in cmd:
            con = sqlite3.connect(db_stg)
            df = pd.read_sql('SELECT * FROM totaltradelist', con)
            con.close()
            df = df[::-1]
            if len(df) > 0:
                sd = strp_time('%Y%m%d', df['index'][df.index[0]])
                ld = strp_time('%Y%m%d', df['index'][df.index[-1]])
                pr = str((sd - ld).days + 1) + '일'
                nbg, nsg = df['총매수금액'].sum(), df['총매도금액'].sum()
                sp = round((nsg / nbg - 1) * 100, 2)
                npg, nmg = df['총수익금액'].sum(), df['총손실금액'].sum()
                nsig = df['수익금합계'].sum()
                df2 = pd.DataFrame(columns=columns_ln)
                df2.at[0] = pr, nbg, nsg, npg, nmg, sp, nsig
                windowQ.put([ui_num['누적합계'], df2])
            else:
                return
            if cmd == '일별집계':
                df = df.rename(columns={'index': '일자'})
                windowQ.put([ui_num['누적상세'], df])
            elif cmd == '월별집계':
                df['일자'] = df['index'].apply(lambda x: x[:6])
                df2 = pd.DataFrame(columns=columns_lt)
                lastmonth = df['일자'][df.index[-1]]
                month = strf_time('%Y%m')
                while int(month) >= int(lastmonth):
                    df3 = df[df['일자'] == month]
                    if len(df3) > 0:
                        tbg, tsg = df3['총매수금액'].sum(), df3['총매도금액'].sum()
                        sp = round((tsg / tbg - 1) * 100, 2)
                        tpg, tmg = df3['총수익금액'].sum(), df3['총손실금액'].sum()
                        ttsg = df3['수익금합계'].sum()
                        df2.at[month] = month, tbg, tsg, tpg, tmg, sp, ttsg
                    month = str(int(month) - 89) if int(month[4:]) == 1 else str(int(month) - 1)
                windowQ.put([ui_num['누적상세'], df2])
            elif cmd == '연도별집계':
                df['일자'] = df['index'].apply(lambda x: x[:4])
                df2 = pd.DataFrame(columns=columns_lt)
                lastyear = df['일자'][df.index[-1]]
                year = strf_time('%Y')
                while int(year) >= int(lastyear):
                    df3 = df[df['일자'] == year]
                    if len(df3) > 0:
                        tbg, tsg = df3['총매수금액'].sum(), df3['총매도금액'].sum()
                        sp = round((tsg / tbg - 1) * 100, 2)
                        tpg, tmg = df3['총수익금액'].sum(), df3['총손실금액'].sum()
                        ttsg = df3['수익금합계'].sum()
                        df2.at[year] = year, tbg, tsg, tpg, tmg, sp, ttsg
                    year = str(int(year) - 1)
                windowQ.put([ui_num['누적상세'], df2])
        else:
            workerQ.put(f'{cmd}')

    def ButtonClicked_4(self, gubun):
        if (gubun in [0, 1] and self.mode2 == 1) or (gubun == 0 and self.mode1 in [1, 2]):
            windowQ.put([1, '시스템 명령 오류 알림 - 현재 모드에서는 작동하지 않습니다.'])
            return
        if gubun == 0 and self.mode0 == 0 and self.mode1 == 0 and self.mode2 == 0:
            self.chart_00_tabWidget.setCurrentWidget(self.chart_05_tab)
            self.chart_01_tabWidget.setCurrentWidget(self.chart_06_tab)
            self.chart_02_tabWidget.setCurrentWidget(self.chart_07_tab)
            self.chart_03_tabWidget.setCurrentWidget(self.chart_08_tab)
            self.etc_pushButton_00.setStyleSheet(style_bc_dk)
            self.etc_pushButton_00.setFont(qfont12)
            self.ct_label_01.setGeometry(3500, 5, 140, 20)
            self.ct_lineEdit_01.setGeometry(3500, 5, 100, 20)
            self.ct_label_02.setGeometry(3500, 702, 140, 20)
            self.ct_lineEdit_02.setGeometry(3500, 702, 100, 20)
            self.mode0 = 1
        elif gubun == 0 and self.mode0 == 1 and self.mode1 == 0 and self.mode2 == 0:
            self.chart_00_tabWidget.setCurrentWidget(self.chart_00_tab)
            self.chart_01_tabWidget.setCurrentWidget(self.chart_01_tab)
            self.chart_02_tabWidget.setCurrentWidget(self.chart_02_tab)
            self.chart_03_tabWidget.setCurrentWidget(self.chart_03_tab)
            self.etc_pushButton_00.setStyleSheet(style_bc_bt)
            self.etc_pushButton_00.setFont(qfont12)
            self.ct_label_01.setGeometry(1820, 5, 140, 20)
            self.ct_lineEdit_01.setGeometry(1960, 5, 100, 20)
            self.ct_label_02.setGeometry(1820, 702, 140, 20)
            self.ct_lineEdit_02.setGeometry(1960, 702, 100, 20)
            self.mode0 = 0
        elif gubun == 1 and self.mode1 == 0 and self.mode2 == 0:
            self.chart_00_tabWidget.setGeometry(5, 5, 1025, 692)
            self.chart_01_tabWidget.setGeometry(1035, 5, 1026, 692)
            self.chart_02_tabWidget.setGeometry(3500, 702, 1025, 692)
            self.chart_03_tabWidget.setGeometry(3500, 702, 1026, 692)
            self.chart_04_tabWidget.setGeometry(3500, 5, 2743, 1390)
            self.hoga_00_tabWidget.setGeometry(2066, 5, 682, 692)
            self.hoga_01_tabWidget.setGeometry(3500, 702, 682, 692)
            self.gg_tabWidget.setGeometry(5, 702, 682, 120)
            self.gs_tabWidget.setGeometry(5, 827, 682, 567)
            self.ns_tabWidget.setGeometry(692, 702, 682, 332)
            self.jj_tabWidget.setGeometry(692, 1039, 682, 355)
            self.jm_tabWidget.setGeometry(1379, 702, 682, 332)
            self.jb_tabWidget.setGeometry(1379, 1039, 682, 355)
            self.ch_tabWidget.setGeometry(2066, 702, 682, 692)
            self.etc_pushButton_01.setStyleSheet(style_bc_dk)
            self.etc_pushButton_01.setFont(qfont12)
            self.chart_00_tabWidget.setCurrentWidget(self.chart_00_tab)
            self.chart_01_tabWidget.setCurrentWidget(self.chart_01_tab)
            self.chart_02_tabWidget.setCurrentWidget(self.chart_02_tab)
            self.chart_03_tabWidget.setCurrentWidget(self.chart_03_tab)
            self.etc_pushButton_00.setStyleSheet(style_bc_bt)
            self.etc_pushButton_00.setFont(qfont12)
            self.mode0 = 0
            self.ct_label_01.setGeometry(1820, 5, 140, 20)
            self.ct_lineEdit_01.setGeometry(1960, 5, 100, 20)
            self.ct_label_02.setGeometry(3500, 702, 65, 20)
            self.ct_lineEdit_02.setGeometry(3500, 702, 100, 20)
            self.mode1 = 1
        elif gubun == 1 and self.mode1 == 1 and self.mode2 == 0:
            self.chart_00_tabWidget.setGeometry(3500, 5, 1025, 692)
            self.chart_01_tabWidget.setGeometry(3500, 5, 1026, 692)
            self.chart_04_tabWidget.setGeometry(5, 5, 2743, 1390)
            self.hoga_00_tabWidget.setGeometry(3500, 5, 682, 692)
            self.gg_tabWidget.setGeometry(3500, 702, 682, 120)
            self.gs_tabWidget.setGeometry(3500, 827, 682, 567)
            self.ns_tabWidget.setGeometry(3500, 702, 682, 332)
            self.jj_tabWidget.setGeometry(3500, 1039, 682, 355)
            self.jm_tabWidget.setGeometry(3500, 702, 682, 332)
            self.jb_tabWidget.setGeometry(3500, 1039, 682, 355)
            self.ch_tabWidget.setGeometry(3500, 702, 682, 692)
            self.ct_label_01.setGeometry(3500, 5, 140, 20)
            self.ct_lineEdit_01.setGeometry(3500, 5, 100, 20)
            self.info_label_05.setGeometry(1630, 1, 600, 30)
            self.mode1 = 2
        elif gubun == 1 and self.mode1 == 2 and self.mode2 == 0:
            self.chart_00_tabWidget.setGeometry(5, 5, 1025, 692)
            self.chart_01_tabWidget.setGeometry(1035, 5, 1026, 692)
            self.chart_02_tabWidget.setGeometry(5, 702, 1025, 692)
            self.chart_03_tabWidget.setGeometry(1035, 702, 1026, 692)
            self.chart_04_tabWidget.setGeometry(3500, 5, 2743, 1390)
            self.chart_00_tabWidget.setCurrentWidget(self.chart_00_tab)
            self.chart_01_tabWidget.setCurrentWidget(self.chart_01_tab)
            self.chart_02_tabWidget.setCurrentWidget(self.chart_02_tab)
            self.chart_03_tabWidget.setCurrentWidget(self.chart_03_tab)
            self.etc_pushButton_00.setStyleSheet(style_bc_bt)
            self.etc_pushButton_00.setFont(qfont12)
            self.mode0 = 0
            self.hoga_00_tabWidget.setGeometry(2066, 5, 682, 692)
            self.hoga_01_tabWidget.setGeometry(2066, 702, 682, 692)
            self.etc_pushButton_01.setStyleSheet(style_bc_bt)
            self.etc_pushButton_01.setFont(qfont12)
            self.ct_label_01.setGeometry(1820, 5, 140, 20)
            self.ct_lineEdit_01.setGeometry(1960, 5, 100, 20)
            self.ct_label_02.setGeometry(1820, 702, 140, 20)
            self.ct_lineEdit_02.setGeometry(1960, 702, 100, 20)
            self.info_label_05.setGeometry(2145, 699, 600, 30)
            self.mode1 = 0
        elif gubun == 2 and self.mode2 == 0:
            self.setGeometry(2748, 0, 692, 1400)
            self.chart_00_tabWidget.setGeometry(3500, 5, 1025, 692)
            self.chart_01_tabWidget.setGeometry(3500, 702, 1026, 692)
            self.chart_02_tabWidget.setGeometry(3500, 5, 1025, 692)
            self.chart_03_tabWidget.setGeometry(3500, 702, 1026, 692)
            self.chart_04_tabWidget.setGeometry(3500, 5, 2743, 1390)
            self.hoga_00_tabWidget.setGeometry(3500, 5, 682, 692)
            self.hoga_01_tabWidget.setGeometry(3500, 702, 682, 692)
            self.lgsj_tabWidget.setGeometry(5, 5, 682, 282)
            self.table_tabWidget.setGeometry(5, 292, 682, 1103)
            self.info_label_01.setGeometry(3500, 1, 400, 30)
            self.info_label_02.setGeometry(3500, 1, 400, 30)
            self.info_label_03.setGeometry(3500, 1, 400, 30)
            self.info_label_04.setGeometry(3500, 1, 600, 30)
            self.info_label_05.setGeometry(3500, 699, 600, 30)
            self.info_label_06.setGeometry(140, 1, 400, 30)
            self.etc_pushButton_00.setGeometry(437, 291, 80, 20)
            self.etc_pushButton_01.setGeometry(522, 291, 80, 20)
            self.etc_pushButton_02.setGeometry(607, 291, 80, 20)
            self.etc_pushButton_02.setStyleSheet(style_bc_dk)
            self.etc_pushButton_02.setFont(qfont12)
            self.ct_label_01.setGeometry(3500, 5, 140, 20)
            self.ct_lineEdit_01.setGeometry(3500, 5, 100, 20)
            self.ct_label_02.setGeometry(3500, 702, 140, 20)
            self.ct_lineEdit_02.setGeometry(3500, 702, 100, 20)
            self.mode2 = 1
        elif gubun == 2 and self.mode2 == 1:
            self.setGeometry(0, 0, 3440, 1400)
            if self.mode1 == 0:
                self.chart_00_tabWidget.setGeometry(5, 5, 1025, 692)
                self.chart_01_tabWidget.setGeometry(1035, 5, 1026, 692)
                self.chart_02_tabWidget.setGeometry(5, 702, 1025, 692)
                self.chart_03_tabWidget.setGeometry(1035, 702, 1026, 692)
                self.hoga_00_tabWidget.setGeometry(2066, 5, 682, 692)
                self.hoga_01_tabWidget.setGeometry(2066, 702, 682, 692)
                self.info_label_05.setGeometry(2145, 699, 600, 30)
            elif self.mode1 == 1:
                self.chart_00_tabWidget.setGeometry(5, 5, 1025, 692)
                self.chart_01_tabWidget.setGeometry(1035, 5, 1026, 692)
                self.chart_00_tabWidget.setCurrentWidget(self.chart_00_tab)
                self.chart_01_tabWidget.setCurrentWidget(self.chart_01_tab)
                self.hoga_00_tabWidget.setGeometry(2066, 5, 682, 692)
                self.info_label_05.setGeometry(2145, 699, 600, 30)
            else:
                self.chart_04_tabWidget.setGeometry(5, 5, 2743, 1390)
                self.info_label_05.setGeometry(1630, 1, 600, 30)
            self.lgsj_tabWidget.setGeometry(2753, 5, 682, 282)
            self.table_tabWidget.setGeometry(2753, 292, 682, 1103)
            self.info_label_01.setGeometry(155, 1, 400, 30)
            self.info_label_02.setGeometry(600, 1, 400, 30)
            self.info_label_03.setGeometry(1185, 1, 400, 30)
            self.info_label_04.setGeometry(2145, 1, 600, 30)
            self.info_label_06.setGeometry(2888, 1, 400, 30)
            self.etc_pushButton_00.setGeometry(3185, 291, 80, 20)
            self.etc_pushButton_01.setGeometry(3270, 291, 80, 20)
            self.etc_pushButton_02.setGeometry(3355, 291, 80, 20)
            self.etc_pushButton_02.setStyleSheet(style_bc_bt)
            self.etc_pushButton_02.setFont(qfont12)
            if self.mode0 == 0 and self.mode1 == 0:
                self.ct_label_01.setGeometry(1820, 5, 140, 20)
                self.ct_lineEdit_01.setGeometry(1960, 5, 100, 20)
                self.ct_label_02.setGeometry(1820, 702, 140, 20)
                self.ct_lineEdit_02.setGeometry(1960, 702, 100, 20)
            elif self.mode1 == 1:
                self.ct_label_01.setGeometry(1820, 5, 120, 20)
                self.ct_lineEdit_01.setGeometry(1960, 5, 100, 20)
            self.mode2 = 0

    @thread_decorator
    def UpdateSysinfo(self):
        p = psutil.Process(os.getpid())
        self.dict_intu['메모리'] = round(p.memory_info()[0] / 2 ** 20.86, 2)
        self.dict_intu['스레드'] = p.num_threads()
        self.dict_intu['시피유'] = round(p.cpu_percent(interval=2) / 2, 2)


class Writer(QtCore.QThread):
    data0 = QtCore.pyqtSignal(list)
    data1 = QtCore.pyqtSignal(list)
    data2 = QtCore.pyqtSignal(list)
    data3 = QtCore.pyqtSignal(list)
    data4 = QtCore.pyqtSignal(list)

    def __init__(self, windowQQ):
        super().__init__()
        self.windowQ = windowQQ

    def run(self):
        tlist = [ui_num['단타설정'], ui_num['tick'], ui_num['tick'] + 100]
        clist = [ui_num['차트P1'], ui_num['차트P2'], ui_num['차트P3'], ui_num['차트P4'], ui_num['차트P5'],
                 ui_num['차트P6'], ui_num['차트P7'], ui_num['차트P8'], ui_num['차트P9']]
        dlist = [ui_num['long'], ui_num['mid'], ui_num['short'],
                 ui_num['long'] + 100, ui_num['mid'] + 100, ui_num['short'] + 100]
        while True:
            data = self.windowQ.get()
            if data[0] not in tlist and type(data[1]) != pd.DataFrame:
                self.data0.emit(data)
            elif data[0] in clist:
                self.data1.emit(data)
            elif data[0] in tlist:
                self.data2.emit(data)
            elif data[0] in dlist:
                self.data3.emit(data)
            else:
                self.data4.emit(data)


if __name__ == '__main__':
    windowQ, workerQ, stgtQ, stglQ, stgmQ, stgsQ, soundQ, queryQ, teleQ, hoga1Q, hoga2Q, chart1Q, chart2Q, chart3Q,\
        chart4Q, chart5Q, chart6Q, chart7Q, chart8Q, chart9Q = Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), \
        Queue(), Queue(), Queue(),  Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), \
        Queue(), Queue()

    qlist = [windowQ, workerQ, stgtQ, stglQ, stgmQ, stgsQ, soundQ, queryQ, teleQ, hoga1Q, hoga2Q,
             chart1Q, chart2Q, chart3Q, chart4Q, chart5Q, chart6Q, chart7Q, chart8Q, chart9Q]

    from query import Query
    from sound import Sound
    from worker import Worker
    from telegrammsg import TelegramMsg
    from updater_hoga import UpdaterHoga
    from updater_chart import UpdaterChart
    from strategy_tick import StrategyTick
    """
    단기, 중기, 장기 전략 완성 후 활성화
    from strategy_long import StrategyLong
    from strategy_mid import StrategyMid
    from strategy_short import StrategyShort
    """

    Process(target=Sound, args=(qlist,), daemon=True).start()
    Process(target=Query, args=(qlist,), daemon=True).start()
    Process(target=TelegramMsg, args=(qlist,), daemon=True).start()
    Process(target=UpdaterHoga, args=(qlist, ui_num['호가P0']), daemon=True).start()
    Process(target=UpdaterHoga, args=(qlist, ui_num['호가P1']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['차트P1']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['차트P2']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['차트P3']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['차트P4']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['차트P5']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['차트P6']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['차트P7']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['차트P8']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['차트P9']), daemon=True).start()
    Process(target=StrategyTick, args=(qlist,), daemon=True).start()
    """
    단기, 중기, 장기 전략 완성 후 활성화
    Process(target=StrategyShort, args=(qlist,), daemon=True).start()
    Process(target=StrategyMid, args=(qlist,), daemon=True).start()
    Process(target=StrategyLong, args=(qlist,), daemon=True).start()
    """
    Process(target=Worker, args=(qlist,), daemon=True).start()

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, color_bg_bc)
    palette.setColor(QPalette.Background, color_bg_bc)
    palette.setColor(QPalette.WindowText, color_fg_bc)
    palette.setColor(QPalette.Base, color_bg_bc)
    palette.setColor(QPalette.AlternateBase, color_bg_dk)
    palette.setColor(QPalette.Text, color_fg_bc)
    palette.setColor(QPalette.Button, color_bg_bc)
    palette.setColor(QPalette.ButtonText, color_fg_bc)
    palette.setColor(QPalette.Link, color_fg_bk)
    palette.setColor(QPalette.Highlight, color_fg_bk)
    palette.setColor(QPalette.HighlightedText, color_bg_bk)
    app.setPalette(palette)
    window = Window()
    window.show()
    app.exec_()
