import os
import sys
import pyqtgraph as pg
from PyQt5.QtGui import QPicture, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.setting import *


class ChuseItem(pg.GraphicsObject):
    def __init__(self, df, ymin, ymax):
        pg.GraphicsObject.__init__(self)
        self.picture = QPicture()
        self.Chuse(df, ymin, ymax)

    def Chuse(self, df, ymin, ymax):
        p = QPainter(self.picture)
        height = ymax - ymin
        for i in range(len(df)):
            if i < len(df) - 1:
                if df['추세'][i]:
                    p.setBrush(pg.mkBrush(color_chuse2))
                    p.setPen(pg.mkPen(color_chuse2))
                    p.drawRect(QRectF(i - 1, ymin, 1, height))
                else:
                    p.setBrush(pg.mkBrush(color_chuse1))
                    p.setPen(pg.mkPen(color_chuse1))
                    p.drawRect(QRectF(i - 1, ymin, 1, height))
        p.end()

    def paint(self, p, *args):
        if args is None:
            return
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class LastChuseItem(pg.GraphicsObject):
    def __init__(self, df, ymin, ymax):
        pg.GraphicsObject.__init__(self)
        self.picture = QPicture()
        self.LastChuse(df, ymin, ymax)

    def LastChuse(self, df, ymin, ymax):
        p = QPainter(self.picture)
        height = ymax - ymin
        if df['추세'][-1]:
            p.setBrush(pg.mkBrush(color_chuse2))
            p.setPen(pg.mkPen(color_chuse2))
            p.drawRect(QRectF(len(df) - 2, ymin, 1, height))
        else:
            p.setBrush(pg.mkBrush(color_chuse1))
            p.setPen(pg.mkPen(color_chuse1))
            p.drawRect(QRectF(len(df) - 2, ymin, 1, height))
        p.end()

    def paint(self, p, *args):
        if args is None:
            return
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class MoveavgItem(pg.GraphicsObject):
    def __init__(self, df, gubun):
        pg.GraphicsObject.__init__(self)
        self.picture = QPicture()
        self.Movwavg(df, gubun)

    def Movwavg(self, df, gubun):
        p = QPainter(self.picture)
        for i in range(len(df)):
            if i < len(df) - 2:
                if gubun in [ui_num['차트P2'], ui_num['차트P4'], ui_num['차트P5'], ui_num['차트P7'], ui_num['차트P9']]:
                    ema050 = df['지수이평05'][i]
                    ema051 = df['지수이평05'][i + 1]
                    ema100 = df['지수이평10'][i]
                    ema101 = df['지수이평10'][i + 1]
                    ema200 = df['지수이평20'][i]
                    ema201 = df['지수이평20'][i + 1]
                    ema400 = df['지수이평40'][i]
                    ema401 = df['지수이평40'][i + 1]
                    ema600 = df['지수이평60'][i]
                    ema601 = df['지수이평60'][i + 1]
                    ema120 = df['지수이평120'][i]
                    ema121 = df['지수이평120'][i + 1]
                    p.setPen(pg.mkPen(color_ema05))
                    p.drawLine(QPointF(i, ema050), QPointF(i + 1, ema051))
                    p.setPen(pg.mkPen(color_ema10))
                    p.drawLine(QPointF(i, ema100), QPointF(i + 1, ema101))
                    p.setPen(pg.mkPen(color_ema20))
                    p.drawLine(QPointF(i, ema200), QPointF(i + 1, ema201))
                    p.setPen(pg.mkPen(color_ema40))
                    p.drawLine(QPointF(i, ema400), QPointF(i + 1, ema401))
                    p.setPen(pg.mkPen(color_ema60))
                    p.drawLine(QPointF(i, ema600), QPointF(i + 1, ema601))
                    p.setPen(pg.mkPen(color_ema120))
                    p.drawLine(QPointF(i, ema120), QPointF(i + 1, ema121))
                else:
                    ema050 = df['지수이평05'][i]
                    ema051 = df['지수이평05'][i + 1]
                    ema200 = df['지수이평20'][i]
                    ema201 = df['지수이평20'][i + 1]
                    ema600 = df['지수이평60'][i]
                    ema601 = df['지수이평60'][i + 1]
                    p.setPen(pg.mkPen(color_ema05))
                    p.drawLine(QPointF(i, ema050), QPointF(i + 1, ema051))
                    p.setPen(pg.mkPen(color_ema20))
                    p.drawLine(QPointF(i, ema200), QPointF(i + 1, ema201))
                    p.setPen(pg.mkPen(color_ema60))
                    p.drawLine(QPointF(i, ema600), QPointF(i + 1, ema601))
                    if gubun in [ui_num['차트P1'], ui_num['차트P3']]:
                        ema120 = df['지수이평120'][i]
                        ema121 = df['지수이평120'][i + 1]
                        ema240 = df['지수이평240'][i]
                        ema241 = df['지수이평240'][i + 1]
                        ema480 = df['지수이평480'][i]
                        ema481 = df['지수이평480'][i + 1]
                        p.setPen(pg.mkPen(color_ema120))
                        p.drawLine(QPointF(i, ema120), QPointF(i + 1, ema121))
                        p.setPen(pg.mkPen(color_ema240))
                        p.drawLine(QPointF(i, ema240), QPointF(i + 1, ema241))
                        p.setPen(pg.mkPen(color_ema480))
                        p.drawLine(QPointF(i, ema480), QPointF(i + 1, ema481))
        p.end()

    def paint(self, p, *args):
        if args is None:
            return
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class LastMoveavgItem(pg.GraphicsObject):
    def __init__(self, df, gubun):
        pg.GraphicsObject.__init__(self)
        self.picture = QPicture()
        self.LastMovwavg(df, gubun)

    def LastMovwavg(self, df, gubun):
        p = QPainter(self.picture)
        if gubun in [ui_num['차트P2'], ui_num['차트P4'], ui_num['차트P5'], ui_num['차트P7'], ui_num['차트P9']]:
            ema050 = df['지수이평05'][-2]
            ema051 = df['지수이평05'][-1]
            ema100 = df['지수이평10'][-2]
            ema101 = df['지수이평10'][-1]
            ema200 = df['지수이평20'][-2]
            ema201 = df['지수이평20'][-1]
            ema400 = df['지수이평40'][-2]
            ema401 = df['지수이평40'][-1]
            ema600 = df['지수이평60'][-2]
            ema601 = df['지수이평60'][-1]
            ema120 = df['지수이평120'][-2]
            ema121 = df['지수이평120'][-1]
            p.setPen(pg.mkPen(color_ema05))
            p.drawLine(QPointF(len(df) - 2, ema050), QPointF(len(df) - 1, ema051))
            p.setPen(pg.mkPen(color_ema10))
            p.drawLine(QPointF(len(df) - 2, ema100), QPointF(len(df) - 1, ema101))
            p.setPen(pg.mkPen(color_ema20))
            p.drawLine(QPointF(len(df) - 2, ema200), QPointF(len(df) - 1, ema201))
            p.setPen(pg.mkPen(color_ema40))
            p.drawLine(QPointF(len(df) - 2, ema400), QPointF(len(df) - 1, ema401))
            p.setPen(pg.mkPen(color_ema60))
            p.drawLine(QPointF(len(df) - 2, ema600), QPointF(len(df) - 1, ema601))
            p.setPen(pg.mkPen(color_ema120))
            p.drawLine(QPointF(len(df) - 2, ema120), QPointF(len(df) - 1, ema121))
        else:
            ema050 = df['지수이평05'][-2]
            ema051 = df['지수이평05'][-1]
            ema200 = df['지수이평20'][-2]
            ema201 = df['지수이평20'][-1]
            ema600 = df['지수이평60'][-2]
            ema601 = df['지수이평60'][-1]
            p.setPen(pg.mkPen(color_ema05))
            p.drawLine(QPointF(len(df) - 2, ema050), QPointF(len(df) - 1, ema051))
            p.setPen(pg.mkPen(color_ema20))
            p.drawLine(QPointF(len(df) - 2, ema200), QPointF(len(df) - 1, ema201))
            p.setPen(pg.mkPen(color_ema60))
            p.drawLine(QPointF(len(df) - 2, ema600), QPointF(len(df) - 1, ema601))
            if gubun in [ui_num['차트P1'], ui_num['차트P3']]:
                ema120 = df['지수이평120'][-2]
                ema121 = df['지수이평120'][-1]
                ema240 = df['지수이평240'][-2]
                ema241 = df['지수이평240'][-1]
                ema480 = df['지수이평480'][-2]
                ema481 = df['지수이평480'][-1]
                p.setPen(pg.mkPen(color_ema120))
                p.drawLine(QPointF(len(df) - 2, ema120), QPointF(len(df) - 1, ema121))
                p.setPen(pg.mkPen(color_ema240))
                p.drawLine(QPointF(len(df) - 2, ema240), QPointF(len(df) - 1, ema241))
                p.setPen(pg.mkPen(color_ema480))
                p.drawLine(QPointF(len(df) - 2, ema480), QPointF(len(df) - 1, ema481))
        p.end()

    def paint(self, p, *args):
        if args is None:
            return
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class CandlestickItem(pg.GraphicsObject):
    def __init__(self, df):
        pg.GraphicsObject.__init__(self)
        self.picture = QPicture()
        self.CandleSticks(df)

    def CandleSticks(self, df):
        p = QPainter(self.picture)
        for i in range(len(df)):
            if i < len(df) - 2:
                c = df['현재가'][i]
                o = df['시가'][i]
                h = df['고가'][i]
                low = df['저가'][i]
                if c >= o:
                    p.setPen(pg.mkPen(color_pluss))
                    p.setBrush(pg.mkBrush(color_pluss))
                else:
                    p.setPen(pg.mkPen(color_minus))
                    p.setBrush(pg.mkBrush(color_minus))
                if h != low:
                    p.drawLine(QPointF(i, h), QPointF(i, low))
                    p.drawRect(QRectF(i - 0.25, o, 0.5, c - o))
                else:
                    p.drawLine(QPointF(i - 0.25, c), QPointF(i + 0.25, c))
        p.end()

    def paint(self, p, *args):
        if args is None:
            return
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class LastCandlestickItem(pg.GraphicsObject):
    def __init__(self, df):
        pg.GraphicsObject.__init__(self)
        self.picture = QPicture()
        self.LastCandleStick(df)

    def LastCandleStick(self, df):
        p = QPainter(self.picture)
        for i in range(len(df)):
            if i >= len(df) - 2:
                c = df['현재가'][i]
                o = df['시가'][i]
                h = df['고가'][i]
                low = df['저가'][i]
                if c >= o:
                    p.setPen(pg.mkPen(color_pluss))
                    p.setBrush(pg.mkBrush(color_pluss))
                else:
                    p.setPen(pg.mkPen(color_minus))
                    p.setBrush(pg.mkBrush(color_minus))
                if h != low:
                    p.drawLine(QPointF(i, h), QPointF(i, low))
                    p.drawRect(QRectF(i - 0.25, o, 0.5, c - o))
                else:
                    p.drawLine(QPointF(i - 0.25, c), QPointF(i + 0.25, c))
        p.end()

    def paint(self, p, *args):
        if args is None:
            return
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class VolumeBarsItem(pg.GraphicsObject):
    def __init__(self, df):
        pg.GraphicsObject.__init__(self)
        self.picture = QPicture()
        self.MoneyBars(df)

    def MoneyBars(self, df):
        p = QPainter(self.picture)
        for i in range(len(df)):
            if i < len(df) - 1:
                c = df['현재가'][i]
                o = df['시가'][i]
                v = df['거래량'][i]
                if c >= o:
                    p.setPen(pg.mkPen(color_pluss))
                    p.setBrush(pg.mkBrush(color_pluss))
                else:
                    p.setPen(pg.mkPen(color_minus))
                    p.setBrush(pg.mkBrush(color_minus))
                p.drawRect(QRectF(i - 0.25, 0, 0.25 * 2, v))
        p.end()

    def paint(self, p, *args):
        if args is None:
            return
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class LastVolumeBarItem(pg.GraphicsObject):
    def __init__(self, x, c, o, v):
        pg.GraphicsObject.__init__(self)
        self.picture = QPicture()
        self.LastMoneybar(x, c, o, v)

    def LastMoneybar(self, x, c, o, v):
        p = QPainter(self.picture)
        if c >= o:
            p.setPen(pg.mkPen(color_pluss))
            p.setBrush(pg.mkBrush(color_pluss))
        else:
            p.setPen(pg.mkPen(color_minus))
            p.setBrush(pg.mkBrush(color_minus))
        p.drawRect(QRectF(x - 0.25, 0, 0.25 * 2, v))
        p.end()

    def paint(self, p, *args):
        if args is None:
            return
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class CustomViewBox1(pg.ViewBox):
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)
        self.setMouseEnabled(x=False, y=False)

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.enableAutoRange()


class CustomViewBox2(pg.ViewBox):
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)
        self.setMouseEnabled(x=False, y=False)

    def mouseClickEvent(self, ev):
        pass

    def mouseDragEvent(self, ev, axis=None):
        pass
