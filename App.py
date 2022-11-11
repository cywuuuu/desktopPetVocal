import PyQt5
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QAction, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QCoreApplication, QPoint, QObject, QThread, pyqtSignal, QTimer, QEvent
import random
import sys
import time
from math import cos, sin, atan2
import os
import pyautogui
import mouse
import configparser

from DesktopPet import DesktopPet
from textBox.DisplayWindow import DisplayWindow
from util import Util


class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def readQssFile(qssFileName):
        with open(qssFileName, 'r', encoding='UTF-8') as file:
            return file.read()


class MainApp(QApplication):
    def __init__(self, args, config):
        super(MainApp, self).__init__(args)
        # trayicon
        self.trayicon = QSystemTrayIcon(QIcon(config.icon))
        self.trayicon.show()
        self.menu = QMenu()
        self.trayicon.setContextMenu(self.menu)
        reset_action = self.menu.addAction("Reset Position",
                                           lambda: self.widget.move(config.monitorwidth * 0.6, config.ground))
        quit_action = self.menu.addAction("Force Quit", lambda: QCoreApplication.instance().quit())

        # mainWindow
        util = Util(config)
        self.widget = DesktopPet(config, util)
        # styleFile = "pets.qss"
        # styleSheet = QSSLoader.readQssFile(styleFile)
        # self.widget.setStyleSheet(styleSheet)
        self.widget.show()
        # self.dwindow = DisplayWindow()
        # self.dwindow.show()
