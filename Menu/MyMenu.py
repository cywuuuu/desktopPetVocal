import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import QAbstractAnimation, QEasingCurve, QEvent, QPropertyAnimation, QRect, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QGraphicsDropShadowEffect, QMenu

from Menu.window_effect import WindowEffect


class MyMenu(QMenu):
    """ 自定义菜单 """
    windowEffect = WindowEffect()

    def __init__(self, string='', parent=None):
        super().__init__(string, parent)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.hWnd = HWND(int(self.winId()))
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ 开启特效 """
        self.windowEffect.setAeroEffect(self.hWnd)
        self.windowEffect.addShadowEffect(True, self.hWnd)

    def setQss(self):
        """ 设置层叠样式 """
        with open(r'Menu/menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

