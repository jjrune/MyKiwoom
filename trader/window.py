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
        self.dict_ctpg[ui_num['??????P1']] = setPg('?????? ??????', self.chart_00_tabWidget, self.chart_00_tab)
        self.dict_ctpg[ui_num['??????P6']] = setPg('?????? ??????', self.chart_00_tabWidget, self.chart_05_tab)

        self.chart_01_tabWidget = QtWidgets.QTabWidget(self)
        self.chart_01_tab = QtWidgets.QWidget()
        self.chart_06_tab = QtWidgets.QWidget()
        self.dict_ctpg[ui_num['??????P2']] = setPg('?????? ??????', self.chart_01_tabWidget, self.chart_01_tab)
        self.dict_ctpg[ui_num['??????P7']] = setPg('?????? ??????', self.chart_01_tabWidget, self.chart_06_tab)

        self.chart_02_tabWidget = QtWidgets.QTabWidget(self)
        self.chart_02_tab = QtWidgets.QWidget()
        self.chart_07_tab = QtWidgets.QWidget()
        self.dict_ctpg[ui_num['??????P3']] = setPg('?????? ??????', self.chart_02_tabWidget, self.chart_02_tab)
        self.dict_ctpg[ui_num['??????P8']] = setPg('?????? ??????', self.chart_02_tabWidget, self.chart_07_tab)

        self.chart_03_tabWidget = QtWidgets.QTabWidget(self)
        self.chart_03_tab = QtWidgets.QWidget()
        self.chart_08_tab = QtWidgets.QWidget()
        self.dict_ctpg[ui_num['??????P4']] = setPg('?????? ??????', self.chart_03_tabWidget, self.chart_03_tab)
        self.dict_ctpg[ui_num['??????P9']] = setPg('?????? ??????', self.chart_03_tabWidget, self.chart_08_tab)

        self.chart_04_tabWidget = QtWidgets.QTabWidget(self)
        self.chart_04_tab = QtWidgets.QWidget()
        self.dict_ctpg[ui_num['??????P5']] = setPg('?????? ??????', self.chart_04_tabWidget, self.chart_04_tab)

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
        self.hoga_00_sell_pushButton_01 = setPushbutton('????????? ??????', self.hoga_00_tab, self.ButtonClicked_1,
                                                        '???????????????0')
        self.hoga_00_sell_pushButton_02 = setPushbutton('?????? ??????', self.hoga_00_tab, self.ButtonClicked_1,
                                                        '????????????0')
        self.hoga_00_buy_pushButton_01 = setPushbutton('?????? ??????', self.hoga_00_tab, self.ButtonClicked_2,
                                                       '????????????0')
        self.hoga_00_buy_pushButton_02 = setPushbutton('????????? ??????', self.hoga_00_tab, self.ButtonClicked_2,
                                                       '???????????????0')
        self.hoga_00_hj_tableWidget = setTablewidget(self.hoga_00_tab, columns_hj, len(columns_hj), 1)
        self.hoga_00_hs_tableWidget = setTablewidget(self.hoga_00_tab, columns_hs, len(columns_hs), 22,
                                                     clicked=self.CellClicked_1, color=True)
        self.hoga_00_hc_tableWidget = setTablewidget(self.hoga_00_tab, columns_hc, len(columns_hc), 22)
        self.hoga_00_hg_tableWidget = setTablewidget(self.hoga_00_tab, columns_hg, len(columns_hg), 22)
        self.hoga_00_hb_tableWidget = setTablewidget(self.hoga_00_tab, columns_hb, len(columns_hb), 22,
                                                     clicked=self.CellClicked_2, color=True)
        self.hoga_00_line = setLine(self.hoga_00_tab, 1)
        self.hoga_00_tabWidget.addTab(self.hoga_00_tab, '?????? ??????')

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
        self.hoga_01_sell_pushButton_01 = setPushbutton('????????? ??????', self.hoga_01_tab, self.ButtonClicked_1,
                                                        '???????????????1')
        self.hoga_01_sell_pushButton_02 = setPushbutton('?????? ??????', self.hoga_01_tab, self.ButtonClicked_1,
                                                        '????????????1')
        self.hoga_01_buy_pushButton_01 = setPushbutton('?????? ??????', self.hoga_01_tab, self.ButtonClicked_2,
                                                       '????????????1')
        self.hoga_01_buy_pushButton_02 = setPushbutton('????????? ??????', self.hoga_01_tab, self.ButtonClicked_2,
                                                       '???????????????1')
        self.hoga_01_hj_tableWidget = setTablewidget(self.hoga_01_tab, columns_hj, len(columns_hj), 1)
        self.hoga_01_hs_tableWidget = setTablewidget(self.hoga_01_tab, columns_hs, len(columns_hs), 22,
                                                     clicked=self.CellClicked_3, color=True)
        self.hoga_01_hc_tableWidget = setTablewidget(self.hoga_01_tab, columns_hc, len(columns_hc), 22)
        self.hoga_01_hg_tableWidget = setTablewidget(self.hoga_01_tab, columns_hg, len(columns_hg), 22)
        self.hoga_01_hb_tableWidget = setTablewidget(self.hoga_01_tab, columns_hb, len(columns_hb), 22,
                                                     clicked=self.CellClicked_4, color=True)
        self.hoga_01_line = setLine(self.hoga_01_tab, 1)
        self.hoga_01_tabWidget.addTab(self.hoga_01_tab, '?????? ??????')

        self.gg_tabWidget = QtWidgets.QTabWidget(self)
        self.gg_tab = QtWidgets.QWidget()
        self.gg_textEdit = setTextEdit(self.gg_tab, qfont14)
        self.gg_tabWidget.addTab(self.gg_tab, '?????? ??????')

        self.gs_tabWidget = QtWidgets.QTabWidget(self)
        self.gs_tab = QtWidgets.QWidget()
        self.gs_tableWidget = setTablewidget(self.gs_tab, columns_gc, len(columns_gc), 22, qfont=qfont13)
        self.gs_tabWidget.addTab(self.gs_tab, '?????? ??????')

        self.ns_tabWidget = QtWidgets.QTabWidget(self)
        self.ns_tab = QtWidgets.QWidget()
        self.ns_tableWidget = setTablewidget(self.ns_tab, columns_ns, len(columns_ns), 12, qfont=qfont13)
        self.ns_tabWidget.addTab(self.ns_tab, '?????? ??????')

        self.jj_tabWidget = QtWidgets.QTabWidget(self)
        self.jj_tab = QtWidgets.QWidget()
        self.jj_tableWidget = setTablewidget(self.jj_tab, columns_jj, len(columns_jj), 28)
        self.jj_tabWidget.addTab(self.jj_tab, '???????????? ????????????')

        self.jm_tabWidget = QtWidgets.QTabWidget(self)
        self.jm_tab = QtWidgets.QWidget()
        self.jm1_tableWidget = setTablewidget(self.jm_tab, columns_jm1, len(columns_jm1), 13, sectionsize=21)
        self.jm2_tableWidget = setTablewidget(self.jm_tab, columns_jm2, len(columns_jm2), 13, sectionsize=21)
        self.jm_tabWidget.addTab(self.jm_tab, '????????????')

        self.jb_tabWidget = QtWidgets.QTabWidget(self)
        self.jb_tab = QtWidgets.QWidget()
        self.jb_tableWidget = setTablewidget(self.jb_tab, columns_jb, len(columns_jb), 14, sectionsize=21)
        self.jb_tabWidget.addTab(self.jb_tab, '??????????????????')

        self.ch_tabWidget = QtWidgets.QTabWidget(self)
        self.ch_tab = QtWidgets.QWidget()
        self.ch_tableWidget = setTablewidget(self.ch_tab, columns_ch, len(columns_ch), 28)
        self.ch_tabWidget.addTab(self.ch_tab, '????????????')

        self.lgsj_tabWidget = QtWidgets.QTabWidget(self)
        self.lg_tab = QtWidgets.QWidget()
        self.sj_tab = QtWidgets.QWidget()

        self.lg_textEdit = setTextEdit(self.lg_tab)

        self.sj_groupBox_01 = QtWidgets.QGroupBox(self.sj_tab)
        self.sj_label_01 = QtWidgets.QLabel('??????????????? ??????', self.sj_groupBox_01)
        self.sj_label_02 = QtWidgets.QLabel('????????? ?????????', self.sj_groupBox_01)
        self.sj_lineEdit_01 = setLineedit(self.sj_groupBox_01)
        self.sj_lineEdit_02 = setLineedit(self.sj_groupBox_01)
        self.sj_pushButton_01 = setPushbutton('??????', self.sj_groupBox_01, self.ButtonClicked_3)
        self.sj_groupBox_02 = QtWidgets.QGroupBox(self.sj_tab)
        self.sj_pushButton_02 = setPushbutton('?????????????????? ????????????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_03 = setPushbutton('OPENAPI ?????????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_04 = setPushbutton('???????????? ??? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_05 = setPushbutton('????????? ????????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_06 = setPushbutton('??????????????? ?????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_07 = setPushbutton('???????????? ???????????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_08 = setPushbutton('???????????? ???????????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_09 = setPushbutton('VI???????????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_10 = setPushbutton('???????????????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_11 = setPushbutton('????????? ??????????????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_12 = setPushbutton('?????? ??????????????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_13 = setPushbutton('?????? ?????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_14 = setPushbutton('????????????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_15 = setPushbutton('????????? ????????? ?????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_16 = setPushbutton('???????????? ????????????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_17 = setPushbutton('?????????????????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_18 = setPushbutton('??????????????? ON/OFF', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_19 = setPushbutton('???????????? ON/OFF', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_20 = setPushbutton('???????????? ON/OFF', self.sj_groupBox_02, self.ButtonClicked_3)
        self.sj_pushButton_21 = setPushbutton('????????? ??????', self.sj_groupBox_02, self.ButtonClicked_3)

        self.lgsj_tabWidget.addTab(self.lg_tab, '??????')
        self.lgsj_tabWidget.addTab(self.sj_tab, '???????????????')

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
        self.sg_pushButton_01 = setPushbutton('????????????', self.sg_groupBox, self.ButtonClicked_3)
        self.sg_pushButton_02 = setPushbutton('????????????', self.sg_groupBox, self.ButtonClicked_3)
        self.sg_pushButton_03 = setPushbutton('???????????????', self.sg_groupBox, self.ButtonClicked_3)
        self.sgt_tableWidget = setTablewidget(self.sg_tab, columns_ln, len(columns_ln), 1)
        self.sgl_tableWidget = setTablewidget(self.sg_tab, columns_lt, len(columns_lt), 41)

        self.table_tabWidget.addTab(self.td_tab, '????????????')
        self.table_tabWidget.addTab(self.gjt_tab, '??????')
        self.table_tabWidget.addTab(self.gjs_tab, '??????')
        self.table_tabWidget.addTab(self.gjm_tab, '??????')
        self.table_tabWidget.addTab(self.gjl_tab, '??????')
        self.table_tabWidget.addTab(self.st_tab, '????????????')
        self.table_tabWidget.addTab(self.sg_tab, '????????????')

        self.info_label_01 = QtWidgets.QLabel(self)
        self.info_label_02 = QtWidgets.QLabel(self)
        self.info_label_03 = QtWidgets.QLabel(self)
        self.info_label_04 = QtWidgets.QLabel(self)
        self.info_label_05 = QtWidgets.QLabel(self)
        self.info_label_06 = QtWidgets.QLabel(self)

        self.etc_pushButton_00 = setPushbutton('???????????????', self, self.ButtonClicked_4, 0)
        self.etc_pushButton_01 = setPushbutton('??????????????????', self, self.ButtonClicked_4, 1)
        self.etc_pushButton_02 = setPushbutton('???????????????', self, self.ButtonClicked_4, 2)

        self.ct_label_01 = QtWidgets.QLabel('????????? ?????? ???????????? ??????', self)
        self.ct_label_02 = QtWidgets.QLabel('????????? ?????? ???????????? ??????', self)
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
            '????????????': 0,
            '???????????????': 0.,
            '?????????????????????????????????': 0.,
            '??????????????????': 0,
            '????????????????????????': 0,
            '??????????????????': 0.,
            '???????????????????????????': 0.,
            '??????????????????': 0,
            '??????????????????': 0.,
            '???????????????????????????': 0.
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

        self.dict_intu = {'?????????': 0, '?????????': 0., '?????????': 0.}
        self.dict_intt = {'?????????': 0, '?????????': 0., '?????????': 0.}
        self.dict_intl = {'?????????': 0, '?????????': 0., '?????????': 0.}
        self.dict_intm = {'?????????': 0, '?????????': 0., '?????????': 0.}
        self.dict_ints = {'?????????': 0, '?????????': 0., '?????????': 0.}

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
                windowQ.put([1, '????????? ?????? ?????? ?????? - ????????? ?????? ??????????????? ???????????????????????????.'])
                return
        if self.mode1 == 0:
            workerQ.put(f"?????????{ui_num['??????P1']} {code}")
        elif self.mode1 == 1:
            workerQ.put(f"?????????{ui_num['??????P0']} {code}")

    def ReturnPressed_2(self):
        codeorname = self.ct_lineEdit_02.text()
        try:
            code = self.dict_code[codeorname]
        except KeyError:
            if codeorname in self.dict_code.values():
                code = codeorname
            else:
                windowQ.put([1, '????????? ?????? ?????? ?????? - ????????? ?????? ??????????????? ???????????????????????????.'])
                return
        workerQ.put(f"?????????{ui_num['??????P3']} {code}")

    def UpdateTexedit(self, msg):
        if msg[0] == 0:
            self.gg_textEdit.clear()
            self.gg_textEdit.append(msg[1])
        elif msg[0] == 1:
            if '??????' in msg[1] or '??????' in msg[1] or '??????' in msg[1]:
                self.lg_textEdit.setTextColor(color_fg_bc)
            elif '??????' in msg[1] or '??????' in msg[1] or '??????' in msg[1]:
                self.lg_textEdit.setTextColor(color_fg_bt)
            else:
                self.lg_textEdit.setTextColor(color_fg_dk)
            self.lg_textEdit.append(f'[{now()}] {msg[1]}')
            self.log.info(f'[{now()}] {msg[1]}')
            if msg[1] == '????????? ?????? ?????? ?????? - ????????? ??????':
                sys.exit()
        elif msg[0] == 2:
            pushbutton = None
            if msg[1] == '?????????????????? ????????????':
                pushbutton = self.sj_pushButton_02
            elif msg[1] == 'OPENAPI ?????????':
                pushbutton = self.sj_pushButton_03
                self.ButtonClicked_4(0)
            elif msg[1] == '???????????? ??? ??????':
                pushbutton = self.sj_pushButton_04
            elif msg[1] == '????????? ????????? ??????':
                pushbutton = self.sj_pushButton_05
            elif msg[1] == '??????????????? ?????? ??????':
                pushbutton = self.sj_pushButton_06
            elif msg[1] == '???????????? ???????????? ??????':
                pushbutton = self.sj_pushButton_07
            elif msg[1] == '???????????? ???????????? ??????':
                pushbutton = self.sj_pushButton_08
            elif msg[1] == 'VI???????????? ??????':
                self.ButtonClicked_4(2)
                pushbutton = self.sj_pushButton_09
            elif msg[1] == '???????????????':
                pushbutton = self.sj_pushButton_10
            elif msg[1] == '????????? ??????????????? ??????':
                pushbutton = self.sj_pushButton_11
            elif msg[1] == '?????? ??????????????? ??????':
                pushbutton = self.sj_pushButton_12
            elif msg[1] == '?????? ?????? ??????':
                pushbutton = self.sj_pushButton_13
            elif msg[1] == '????????????':
                pushbutton = self.sj_pushButton_14
            elif msg[1] == '????????? ????????? ?????? ??????':
                pushbutton = self.sj_pushButton_15
            elif msg[1] == '???????????? ????????????':
                pushbutton = self.sj_pushButton_16
            elif msg[1] == '?????????????????? ??????':
                pushbutton = self.sj_pushButton_17
            elif msg[1] == '????????? ??????':
                pushbutton = self.sj_pushButton_21
            if pushbutton is not None:
                pushbutton.setStyleSheet(style_bc_dk)
                pushbutton.setFont(qfont12)

            pushbutton = None
            text = None
            if '???????????????' in msg[1]:
                pushbutton = self.sj_pushButton_18
                text = '??????????????? ON' if msg[1].split(' ')[-1] in ['ON', '1'] else '??????????????? OFF'
            elif '????????????' in msg[1]:
                pushbutton = self.sj_pushButton_19
                text = '???????????? ON' if msg[1].split(' ')[-1] in ['ON', '1'] else '???????????? OFF'
            elif '????????????' in msg[1]:
                pushbutton = self.sj_pushButton_20
                text = '???????????? ON' if msg[1].split(' ')[-1] in ['ON', '1'] else '???????????? OFF'

            if pushbutton is not None and text is not None:
                pushbutton.setText(text)
                if msg[1].split(' ')[-1] in ['ON', '1']:
                    pushbutton.setStyleSheet(style_bc_bt)
                else:
                    pushbutton.setStyleSheet(style_bc_dk)
                pushbutton.setFont(qfont12)

            if '?????????????????????' in msg[1]:
                text = msg[1].split(' ')[-1]
                self.sj_lineEdit_01.setText(text)
                self.sj_lineEdit_01.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            elif '??????????????????' in msg[1]:
                text = msg[1].split(' ')[-1]
                self.sj_lineEdit_02.setText(text)
                self.sj_lineEdit_02.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        elif msg[0] == 3:
            float_memory = float2str3p2(self.dict_intu['?????????'])
            float_cpuper = float2str2p2(self.dict_intu['?????????'])
            label01text = f"UI Process - Memory {float_memory}MB | Threads {self.dict_intu['?????????']}EA | "\
                          f'CPU {float_cpuper}%'

            float_memory = float2str3p2(msg[1])
            float_cpuper = float2str2p2(msg[3])
            label02text = f'Worker Process - Memory {float_memory}MB | Threads {msg[2]}EA | CPU {float_cpuper}%'

            float_memory = self.dict_intt['?????????'] + self.dict_intl['?????????']
            float_memory += self.dict_intm['?????????'] + self.dict_ints['?????????']
            float_thread = self.dict_intt['?????????'] + self.dict_intl['?????????']
            float_thread += self.dict_intm['?????????'] + self.dict_ints['?????????']
            float_cpuper = self.dict_intt['?????????'] + self.dict_intl['?????????']
            float_cpuper += self.dict_intm['?????????'] + self.dict_ints['?????????']
            float_memory = round(float_memory, 2)
            float_cpuper = round(float_cpuper, 2)

            total_memory = round(self.dict_intu['?????????'] + msg[1] + float_memory, 2)
            total_threads = self.dict_intu['?????????'] + msg[2] + float_thread
            total_cpuper = round(self.dict_intu['?????????'] + msg[3] + float_cpuper, 2)

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
            self.dict_intt['?????????'] = msg[1]
            self.dict_intt['?????????'] = msg[2]
            self.dict_intt['?????????'] = msg[3]
        elif msg[0] == 5:
            self.dict_intl['?????????'] = msg[1]
            self.dict_intl['?????????'] = msg[2]
            self.dict_intl['?????????'] = msg[3]
        elif msg[0] == 6:
            self.dict_intm['?????????'] = msg[1]
            self.dict_intm['?????????'] = msg[2]
            self.dict_intm['?????????'] = msg[3]
        elif msg[0] == 7:
            self.dict_ints['?????????'] = msg[1]
            self.dict_ints['?????????'] = msg[2]
            self.dict_ints['?????????'] = msg[3]
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
        if gubun in [ui_num['??????P1'], ui_num['??????P2']] and (self.mode0 != 0 or self.mode1 not in [0, 1]):
            return
        if gubun in [ui_num['??????P3'], ui_num['??????P4']] and (self.mode0 != 0 or self.mode1 != 0):
            return
        if gubun in [ui_num['??????P6'], ui_num['??????P7'], ui_num['??????P8'], ui_num['??????P9']] and \
                (self.mode0 != 1 or self.mode1 != 0):
            return
        if gubun == ui_num['??????P5'] and self.mode1 != 2:
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
                    label.setText(f"????????? {format(int(mousePoint.y()), ',')}\n????????? {per}%")
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
            cc = df['?????????'][-1]
            per = round((c / df['????????????'][0] - 1) * 100, 2)
            nlist = [ui_num['??????P2'], ui_num['??????P4'], ui_num['??????P5'], ui_num['??????P7'], ui_num['??????P9']]
            if gubun in nlist:
                ema05 = df['????????????05'][-1]
                ema10 = df['????????????10'][-1]
                ema20 = df['????????????20'][-1]
                textt = f"05?????? {format(ema05, ',')}\n10?????? {format(ema10, ',')}\n" \
                        f"20?????? {format(ema20, ',')}\n?????????  {format(cc, ',')}\n?????????  {per}%"
            else:
                ema05 = df['????????????05'][-1]
                ema20 = df['????????????20'][-1]
                ema60 = df['????????????60'][-1]
                textt = f"05?????? {format(ema05, ',')}\n20?????? {format(ema20, ',')}\n" \
                        f"60?????? {format(ema60, ',')}\n?????????  {format(cc, ',')}\n?????????  {per}%"
            return textt

        def getSubLegendText():
            money = int(df['?????????'][-1])
            per = round(df['?????????'][-1] / df['?????????'][-2] * 100, 2)
            textt = f"????????? {format(money, ',')}\n????????? {per}%"
            return textt

        x = len(df) - 1
        c = df['?????????'][-1]
        o = df['??????'][-1]
        prec = df['????????????'][0]
        v = df['?????????'][-1]
        vmax = df['?????????'].max()
        name = df['?????????'][0]

        if gubun in [ui_num['??????P1'], ui_num['??????P3']]:
            ymin = min(df['??????'].min(), df['????????????05'].min(), df['????????????20'].min(), df['????????????60'].min(),
                       df['????????????120'].min(), df['????????????240'].min(), df['????????????480'].min())
            ymax = max(df['??????'].max(), df['????????????05'].max(), df['????????????20'].max(), df['????????????60'].max(),
                       df['????????????120'].max(), df['????????????240'].max(), df['????????????480'].max())
        elif gubun in [ui_num['??????P2'], ui_num['??????P4'], ui_num['??????P5'], ui_num['??????P7'], ui_num['??????P9']]:
            ymin = min(df['??????'].min(), df['????????????05'].min(), df['????????????10'].min(), df['????????????20'].min(),
                       df['????????????40'].min(), df['????????????60'].min(), df['????????????120'].min())
            ymax = max(df['??????'].max(), df['????????????05'].max(), df['????????????10'].max(), df['????????????20'].max(),
                       df['????????????40'].max(), df['????????????60'].max(), df['????????????120'].max())
        else:
            ymin = min(df['??????'].min(), df['????????????05'].min(), df['????????????20'].min(), df['????????????60'].min())
            ymax = max(df['??????'].max(), df['????????????05'].max(), df['????????????20'].max(), df['????????????60'].max())

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
            if gubun == ui_num['??????P5'] and self.mode1 == 2:
                for i, index2 in enumerate(df.index):
                    if df['???????????????'][index2] != '':
                        for price in df['???????????????'][index2].split(';'):
                            arrow = pg.ArrowItem(angle=-180, tipAngle=30, baseAngle=20, headLen=20, tailLen=10,
                                                 tailWidth=2, pen=None, brush='r')
                            arrow.setPos(i, int(price))
                            self.dict_ctpg[gubun][0].addItem(arrow)
                            text = pg.TextItem(anchor=(1, 0.5), color=color_fg_bt, border=color_bg_bt, fill=color_bg_ld)
                            text.setFont(qfont12)
                            text.setPos(i - 1, int(price))
                            text.setText(price)
                            self.dict_ctpg[gubun][0].addItem(text)
                    if df['???????????????'][index2] != '':
                        for price in df['???????????????'][index2].split(';'):
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

        if gubun == ui_num['????????????']:
            df = data[1]
            self.dict_intg['??????????????????'] = df['??????????????????'][0]
            self.dict_intg['??????????????????'] = df['??????????????????'][0]
            self.dict_intg['????????????'] = df['????????????'][0]
            self.dict_intg['????????????'] = df['????????????'][0]
            self.dict_intg['??????????????????'] = df['??????????????????'][0]
            self.dict_intg['???????????????????????????'] = df['???????????????????????????'][0]
            self.dict_intg['????????????????????????'] = df['????????????????????????'][0]
            self.dict_intg['???????????????'] = df['???????????????'][0]
            self.dict_intg['?????????????????????????????????'] = df['?????????????????????????????????'][0]
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
            smavg = dict_df[code]['????????????'][self.dict_intg['????????????'] + 1]
            item = QtWidgets.QTableWidgetItem(changeFormat(smavg))
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.gjt_tableWidget.setItem(j, 7, item)
            chavg = dict_df[code]['????????????'][self.dict_intg['????????????'] + 1]
            item = QtWidgets.QTableWidgetItem(changeFormat(chavg))
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.gjt_tableWidget.setItem(j, 8, item)
            chhigh = dict_df[code]['??????????????????'][self.dict_intg['????????????'] + 1]
            item = QtWidgets.QTableWidgetItem(changeFormat(chhigh))
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.gjt_tableWidget.setItem(j, 9, item)
            for i, column in enumerate(columns_gs2):
                if column in ['????????????', '??????????????????']:
                    item = QtWidgets.QTableWidgetItem(changeFormat(dict_df[code][column][0]).split('.')[0])
                else:
                    item = QtWidgets.QTableWidgetItem(changeFormat(dict_df[code][column][0]))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                # ????????? ?????? ?????? ?????? ?????????

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
                if column == '?????????':
                    item = QtWidgets.QTableWidgetItem(self.dict_name[code])
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                else:
                    if column == '??????':
                        item = QtWidgets.QTableWidgetItem(changeFormat(df[column][code], True))
                    else:
                        item = QtWidgets.QTableWidgetItem(changeFormat(df[column][code]))
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                # ????????? ?????? ?????? ?????? ?????????

                gj_tableWidget.setItem(j, i, item)
        if len(df) < 46:
            gj_tableWidget.setRowCount(46)

    def UpdateTablewidget(self, data):
        gubun = data[0]
        df = data[1]

        if gubun == ui_num['????????????'] and (self.mode2 != 0 or self.mode1 != 1):
            return
        nlist = [ui_num['????????????0'], ui_num['????????????0'], ui_num['????????????0'], ui_num['??????0'], ui_num['????????????0']]
        if gubun in nlist and (self.mode2 != 0 or self.mode1 not in [0, 1]):
            return
        nlist = [ui_num['????????????1'], ui_num['????????????1'], ui_num['????????????1'], ui_num['??????1'], ui_num['????????????1']]
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
            nnlist = [ui_num['????????????0'], ui_num['??????0'], ui_num['????????????1'], ui_num['??????1']]
            if gubun in nnlist and format_data in ['0', '0.00']:
                format_data = ''
            return format_data

        tableWidget = None
        if gubun == ui_num['????????????']:
            tableWidget = self.tt_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.td_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.tj_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.jg_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.cj_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.gs_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.ns_tableWidget
        elif gubun == ui_num['?????????']:
            tableWidget = self.jj_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.jm1_tableWidget
            tableWidget.setHorizontalHeaderLabels(df.columns)
        elif gubun == ui_num['????????????']:
            tableWidget = self.jm2_tableWidget
            tableWidget.setHorizontalHeaderLabels(df.columns)
        elif gubun == ui_num['???????????????']:
            tableWidget = self.jb_tableWidget
            tableWidget.setHorizontalHeaderLabels(df.columns)
        elif gubun == ui_num['????????????']:
            tableWidget = self.ch_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.stn_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.stl_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.sgt_tableWidget
        elif gubun == ui_num['????????????']:
            tableWidget = self.sgl_tableWidget
        elif gubun == ui_num['????????????0']:
            tableWidget = self.hoga_00_hj_tableWidget
        elif gubun == ui_num['????????????0']:
            tableWidget = self.hoga_00_hs_tableWidget
        elif gubun == ui_num['????????????0']:
            tableWidget = self.hoga_00_hc_tableWidget
        elif gubun == ui_num['??????0']:
            tableWidget = self.hoga_00_hg_tableWidget
        elif gubun == ui_num['????????????0']:
            tableWidget = self.hoga_00_hb_tableWidget
        elif gubun == ui_num['????????????1']:
            tableWidget = self.hoga_01_hj_tableWidget
        elif gubun == ui_num['????????????1']:
            tableWidget = self.hoga_01_hs_tableWidget
        elif gubun == ui_num['????????????1']:
            tableWidget = self.hoga_01_hc_tableWidget
        elif gubun == ui_num['??????1']:
            tableWidget = self.hoga_01_hg_tableWidget
        elif gubun == ui_num['????????????1']:
            tableWidget = self.hoga_01_hb_tableWidget
        if tableWidget is None:
            return

        if len(df) == 0:
            tableWidget.clearContents()
            return

        tableWidget.setRowCount(len(df))
        for j, index in enumerate(df.index):
            for i, column in enumerate(df.columns):
                if column == '????????????':
                    cgtime = df[column][index]
                    if gubun == ui_num['????????????']:
                        cgtime = f'{cgtime[:2]}:{cgtime[2:4]}:{cgtime[4:6]}'
                    else:
                        cgtime = f'{cgtime[8:10]}:{cgtime[10:12]}:{cgtime[12:14]}'
                    item = QtWidgets.QTableWidgetItem(cgtime)
                elif column in ['????????????', '??????']:
                    day = df[column][index]
                    if '.' not in day:
                        day = day[:4] + '.' + day[4:6] + '.' + day[6:]
                    item = QtWidgets.QTableWidgetItem(day)
                elif column in ['?????????', '????????????', '???????????????', '??????', '?????????????????????', '?????????????????????',
                                '??????', '????????????', '?????????', '??????', '????????????']:
                    item = QtWidgets.QTableWidgetItem(str(df[column][index]))
                elif gubun in [ui_num['????????????'], ui_num['????????????'], ui_num['???????????????']]:
                    try:
                        item = QtWidgets.QTableWidgetItem(str(df[column][index]))
                    except KeyError:
                        continue
                elif column not in ['?????????', '?????????', '???????????????????????????', '????????????',
                                    '????????????5???', '????????????20???', '????????????60???', '??????????????????']:
                    item = QtWidgets.QTableWidgetItem(changeFormat(df[column][index]).split('.')[0])
                else:
                    item = QtWidgets.QTableWidgetItem(changeFormat(df[column][index]))

                if column in ['?????????', '???????????????', '??????', '??????', '??????']:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                elif column in ['????????????', '??????????????????', '???????????????', '???????????????', '????????????', '????????????', '????????????', '??????',
                                '??????', '?????????????????????', '?????????????????????', '????????????', '?????????', '????????????']:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                if column == '????????????':
                    if j == 0:
                        item.setIcon(self.icon_totalb)
                    elif j == 21:
                        item.setIcon(self.icon_totals)
                elif column == '????????????' and gubun in [ui_num['????????????0'], ui_num['????????????1']]:
                    if j == 0:
                        item.setIcon(self.icon_up)
                    elif j == 21:
                        item.setIcon(self.icon_down)
                elif gubun in [ui_num['??????0'], ui_num['??????1']]:
                    if column == '??????':
                        if j == 0:
                            item.setIcon(self.icon_perb)
                        elif j == 21:
                            item.setIcon(self.icon_pers)
                    elif column == '??????':
                        if j == 0:
                            item.setIcon(self.icon_totalb)
                        elif j == 21:
                            item.setIcon(self.icon_totals)
                    elif column == '??????':
                        if j == 0:
                            item.setIcon(self.icon_up)
                        elif j == 21:
                            item.setIcon(self.icon_down)
                        else:
                            if gubun == ui_num['??????0']:
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
                    elif column == '?????????':
                        if j == 0:
                            item.setIcon(self.icon_up)
                        elif j == 21:
                            item.setIcon(self.icon_down)
                        else:
                            if gubun == ui_num['??????0']:
                                hj_tableWidget = self.hoga_00_hj_tableWidget
                            else:
                                hj_tableWidget = self.hoga_01_hj_tableWidget
                            if hj_tableWidget.item(0, 0) is not None:
                                uvi = comma2int(hj_tableWidget.item(0, 13).text())
                                dvi = comma2int(hj_tableWidget.item(0, 14).text())
                                if df[column][index] != 0:
                                    if j < 11:
                                        if df['??????'][index] == uvi:
                                            item.setIcon(self.icon_vi)
                                    else:
                                        if df['??????'][index] == dvi:
                                            item.setIcon(self.icon_vi)

                if '?????????' in df.columns:
                    if df['?????????'][index] >= 0:
                        item.setForeground(color_fg_bt)
                    else:
                        item.setForeground(color_fg_dk)
                elif gubun == ui_num['????????????']:
                    if df['????????????'][index] == '??????':
                        item.setForeground(color_fg_bt)
                    elif df['????????????'][index] == '??????':
                        item.setForeground(color_fg_dk)
                    elif df['????????????'][index] in ['????????????', '????????????']:
                        item.setForeground(color_fg_bc)
                elif gubun in [ui_num['????????????'], ui_num['????????????']]:
                    cname = '??????' if gubun == ui_num['????????????'] else '??????'
                    if '????????????' in df[cname][index] or '????????????' in df[cname][index] or \
                            '????????????' in df[cname][index] or '????????????' in df[cname][index] or \
                            '????????????' in df[cname][index] or '????????????' in df[cname][index] or \
                            '???????????????' in df[cname][index] or '????????????' in df[cname][index] or \
                            '????????????' in df[cname][index] or '????????????' in df[cname][index] or \
                            '????????????' in df[cname][index]:
                        item.setForeground(color_fg_bt)
                    else:
                        item.setForeground(color_fg_dk)
                elif gubun == ui_num['?????????']:
                    if column in ['?????????', '???????????????', '??????????????????', '?????????']:
                        if df[column][index] >= 0:
                            item.setForeground(color_fg_bt)
                        else:
                            item.setForeground(color_fg_dk)
                elif gubun in [ui_num['????????????'],  ui_num['????????????'],  ui_num['???????????????']]:
                    if '-' not in df[column][index] and column != '??????':
                        item.setForeground(color_fg_bt)
                    else:
                        item.setForeground(color_fg_dk)
                elif gubun == ui_num['????????????']:
                    if column == '?????????':
                        if df[column][index] >= 0:
                            item.setForeground(color_fg_bt)
                        else:
                            item.setForeground(color_fg_dk)
                    elif '????????????' in column:
                        if df[column][index] >= 100:
                            item.setForeground(color_fg_bt)
                        else:
                            item.setForeground(color_fg_dk)
                elif gubun in [ui_num['????????????0'], ui_num['????????????1']]:
                    if column == '????????????':
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
                            if gubun == ui_num['????????????0']:
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
                    elif column == '????????????':
                        if df[column][index] >= 100:
                            item.setForeground(color_fg_bt)
                        else:
                            item.setForeground(color_fg_dk)
                elif gubun in [ui_num['??????0'], ui_num['??????1']]:
                    if '??????' in column:
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
                            if df[column][index] * df['??????'][10] > 90000000:
                                item.setBackground(color_bf_bt)
                        elif df[column][index] < 0:
                            item.setForeground(color_fg_dk)
                            if df[column][index] * df['??????'][11] < -90000000:
                                item.setBackground(color_bf_dk)
                    elif column == '??????':
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
                    elif column in ['??????', '?????????']:
                        if df['?????????'][index] > 0:
                            item.setForeground(color_fg_bt)
                        elif df['?????????'][index] < 0:
                            item.setForeground(color_fg_dk)
                        if column == '??????' and df[column][index] != 0:
                            if gubun == ui_num['??????0']:
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
                elif gubun in [ui_num['????????????0'], ui_num['????????????1'], ui_num['????????????0'], ui_num['????????????1']]:
                    item.setForeground(color_fg_bt)
                    item.setBackground(color_bg_bt)
                tableWidget.setItem(j, i, item)

        if len(df) < 13 and gubun in [ui_num['????????????'], ui_num['????????????'], ui_num['????????????']]:
            tableWidget.setRowCount(13)
        elif len(df) < 22 and gubun == ui_num['????????????']:
            tableWidget.setRowCount(22)
        elif len(df) < 12 and gubun == ui_num['????????????']:
            tableWidget.setRowCount(12)
        elif len(df) < 28 and gubun == ui_num['????????????']:
            tableWidget.setRowCount(28)
        elif len(df) < 31 and gubun == ui_num['????????????']:
            tableWidget.setRowCount(31)
        elif len(df) < 41 and gubun == ui_num['????????????']:
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
            windowQ.put([2, '????????? ?????? ?????? ?????? - ??????????????? ??????????????????.'])
            return
        oc = int(jc * (bper / 100))
        if oc == 0:
            oc = 1
        code = self.dict_code[self.hoga_00_hj_tableWidget.item(0, 0).text()]
        order = ['??????', '4989', '', 2, code, oc, hg, '00', '', hg, name]
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
            windowQ.put([2, '????????? ?????? ?????? ?????? - ??????????????? ??????????????????.'])
            return
        oc = int(og / hg)
        code = self.dict_code[name]
        order = ['??????', '4989', '', 1, code, oc, hg, '00', '', hg, name]
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
            windowQ.put([2, '????????? ?????? ?????? ?????? - ??????????????? ??????????????????.'])
            return
        oc = int(jc * (bper / 100))
        if oc == 0:
            oc = 1
        code = self.dict_code[name]
        order = ['??????', '4989', '', 2, code, oc, hg, '00', '', hg, name]
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
            windowQ.put([2, '????????? ?????? ?????? ?????? - ??????????????? ??????????????????.'])
            return
        oc = int(og / hg)
        code = self.dict_code[name]
        order = ['??????', '4989', '', 1, code, oc, hg, '00', '', hg, name]
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
                workerQ.put(f"?????????{ui_num['??????P1']} {code}")
            elif col == 1:
                workerQ.put(f"?????????{ui_num['??????P3']} {code}")
        elif self.mode1 == 1:
            workerQ.put(f"?????????{ui_num['??????P0']} {code}")
        elif self.mode1 == 2:
            if self.table_tabWidget.currentWidget() == self.st_tab:
                date = self.calendarWidget.selectedDate()
                tradeday = date.toString('yyyyMMdd')
            elif 0 < int(strf_time('%H%M%S')) < 90000:
                tradeday = strf_time('%Y%m%d', timedelta_day(-1))
            else:
                tradeday = strf_time('%Y%m%d')
            workerQ.put(f"?????????{ui_num['??????P5']} {tradeday} {code}")

    def CalendarClicked(self):
        date = self.calendarWidget.selectedDate()
        searchday = date.toString('yyyyMMdd')
        con = sqlite3.connect(db_stg)
        df = pd.read_sql(f"SELECT * FROM tradelist WHERE ???????????? LIKE '{searchday}%'", con)
        con.close()
        if len(df) > 0:
            df = df.set_index('index')
            df.sort_values(by=['????????????'], ascending=True, inplace=True)
            df = df[['????????????', '?????????', '????????????', '????????????', '????????????', '?????????', '?????????', '????????????']].copy()
            nbg, nsg = df['????????????'].sum(), df['????????????'].sum()
            sp = round((nsg / nbg - 1) * 100, 2)
            npg, nmg, nsig = df[df['?????????'] > 0]['?????????'].sum(), df[df['?????????'] < 0]['?????????'].sum(), df['?????????'].sum()
            df2 = pd.DataFrame(columns=columns_sn)
            df2.at[0] = searchday, nbg, nsg, npg, nmg, sp, nsig
        else:
            df = pd.DataFrame(columns=columns_st)
            df2 = pd.DataFrame(columns=columns_sn)
        windowQ.put([ui_num['????????????'], df2])
        windowQ.put([ui_num['????????????'], df])

    def ButtonClicked_1(self, gubun):
        if gubun in ['???????????????0', '????????????0']:
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
        if '???????????????' in gubun:
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
                windowQ.put([1, '????????? ?????? ?????? ?????? - ??????????????? ??????????????????.'])
                return
            c = comma2int(hg_tableWidget.item(11, 2).text())
            if hj_tableWidget.item(0, 11).text() == '':
                return
            jc = comma2int(hj_tableWidget.item(0, 11).text())
            oc = int(jc * (bper / 10))
            if oc == 0:
                oc = 1
            name = hj_tableWidget.item(0, 0).text()
            order = ['??????', '4989', '', 2, code, oc, 0, '03', '', c, name]
            workerQ.put(order)
        elif '????????????' in gubun:
            order = f'???????????? {code}'
            workerQ.put(order)

    def ButtonClicked_2(self, gubun):
        if gubun in ['???????????????0', '????????????0']:
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
        if '???????????????' in gubun:
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
                windowQ.put([1, '????????? ?????? ?????? ?????? - ??????????????? ??????????????????.'])
                return
            c = comma2int(hg_tableWidget.item(10, 2).text())
            oc = int(og / c)
            name = hj_tableWidget.item(0, 0).text()
            order = ['??????', '4989', '', 1, code, oc, 0, '03', '', c, name]
            workerQ.put(order)
        elif '????????????' in gubun:
            order = f'???????????? {code}'
            workerQ.put(order)

    def ButtonClicked_3(self, cmd):
        if cmd == '??????':
            text1 = self.sj_lineEdit_01.text()
            text2 = self.sj_lineEdit_02.text()
            if text1 == '' or text2 == '':
                windowQ.put([1, '????????? ?????? ?????? ?????? - ???????????? ????????? ??? ????????? ???????????? ??????????????????.'])
                return
            workerQ.put(f'{cmd} {text1} {text2}')
        elif '??????' in cmd:
            con = sqlite3.connect(db_stg)
            df = pd.read_sql('SELECT * FROM totaltradelist', con)
            con.close()
            df = df[::-1]
            if len(df) > 0:
                sd = strp_time('%Y%m%d', df['index'][df.index[0]])
                ld = strp_time('%Y%m%d', df['index'][df.index[-1]])
                pr = str((sd - ld).days + 1) + '???'
                nbg, nsg = df['???????????????'].sum(), df['???????????????'].sum()
                sp = round((nsg / nbg - 1) * 100, 2)
                npg, nmg = df['???????????????'].sum(), df['???????????????'].sum()
                nsig = df['???????????????'].sum()
                df2 = pd.DataFrame(columns=columns_ln)
                df2.at[0] = pr, nbg, nsg, npg, nmg, sp, nsig
                windowQ.put([ui_num['????????????'], df2])
            else:
                return
            if cmd == '????????????':
                df = df.rename(columns={'index': '??????'})
                windowQ.put([ui_num['????????????'], df])
            elif cmd == '????????????':
                df['??????'] = df['index'].apply(lambda x: x[:6])
                df2 = pd.DataFrame(columns=columns_lt)
                lastmonth = df['??????'][df.index[-1]]
                month = strf_time('%Y%m')
                while int(month) >= int(lastmonth):
                    df3 = df[df['??????'] == month]
                    if len(df3) > 0:
                        tbg, tsg = df3['???????????????'].sum(), df3['???????????????'].sum()
                        sp = round((tsg / tbg - 1) * 100, 2)
                        tpg, tmg = df3['???????????????'].sum(), df3['???????????????'].sum()
                        ttsg = df3['???????????????'].sum()
                        df2.at[month] = month, tbg, tsg, tpg, tmg, sp, ttsg
                    month = str(int(month) - 89) if int(month[4:]) == 1 else str(int(month) - 1)
                windowQ.put([ui_num['????????????'], df2])
            elif cmd == '???????????????':
                df['??????'] = df['index'].apply(lambda x: x[:4])
                df2 = pd.DataFrame(columns=columns_lt)
                lastyear = df['??????'][df.index[-1]]
                year = strf_time('%Y')
                while int(year) >= int(lastyear):
                    df3 = df[df['??????'] == year]
                    if len(df3) > 0:
                        tbg, tsg = df3['???????????????'].sum(), df3['???????????????'].sum()
                        sp = round((tsg / tbg - 1) * 100, 2)
                        tpg, tmg = df3['???????????????'].sum(), df3['???????????????'].sum()
                        ttsg = df3['???????????????'].sum()
                        df2.at[year] = year, tbg, tsg, tpg, tmg, sp, ttsg
                    year = str(int(year) - 1)
                windowQ.put([ui_num['????????????'], df2])
        else:
            workerQ.put(f'{cmd}')

    def ButtonClicked_4(self, gubun):
        if (gubun in [0, 1] and self.mode2 == 1) or (gubun == 0 and self.mode1 in [1, 2]):
            windowQ.put([1, '????????? ?????? ?????? ?????? - ?????? ??????????????? ???????????? ????????????.'])
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
        self.dict_intu['?????????'] = round(p.memory_info()[0] / 2 ** 20.86, 2)
        self.dict_intu['?????????'] = p.num_threads()
        self.dict_intu['?????????'] = round(p.cpu_percent(interval=2) / 2, 2)


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
        tlist = [ui_num['????????????'], ui_num['tick'], ui_num['tick'] + 100]
        clist = [ui_num['??????P1'], ui_num['??????P2'], ui_num['??????P3'], ui_num['??????P4'], ui_num['??????P5'],
                 ui_num['??????P6'], ui_num['??????P7'], ui_num['??????P8'], ui_num['??????P9']]
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
    ??????, ??????, ?????? ?????? ?????? ??? ?????????
    from strategy_long import StrategyLong
    from strategy_mid import StrategyMid
    from strategy_short import StrategyShort
    """

    Process(target=Sound, args=(qlist,), daemon=True).start()
    Process(target=Query, args=(qlist,), daemon=True).start()
    Process(target=TelegramMsg, args=(qlist,), daemon=True).start()
    Process(target=UpdaterHoga, args=(qlist, ui_num['??????P0']), daemon=True).start()
    Process(target=UpdaterHoga, args=(qlist, ui_num['??????P1']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['??????P1']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['??????P2']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['??????P3']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['??????P4']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['??????P5']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['??????P6']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['??????P7']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['??????P8']), daemon=True).start()
    Process(target=UpdaterChart, args=(qlist, ui_num['??????P9']), daemon=True).start()
    Process(target=StrategyTick, args=(qlist,), daemon=True).start()
    """
    ??????, ??????, ?????? ?????? ?????? ??? ?????????
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
