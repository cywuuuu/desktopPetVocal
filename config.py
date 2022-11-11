import PyQt5
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QAction, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QCoreApplication, QPoint, QObject, QThread, pyqtSignal,QTimer, QEvent
import random
import sys
import time
from math import cos, sin, atan2
import os
import pyautogui
from win32api import GetMonitorInfo, MonitorFromPoint

from PIL import Image


# To iterate through the entire gif
from destopPetInteraction.pet_interaction import PetInteraction


def readGifs(imgpath):
    im = Image.open(imgpath)
    try:
        while 1:
            im.seek(im.tell() + 1)
            print(im.getdata())
            # do something to im
    except EOFError:
        pass  # end of sequence

class config():

    def __init__(self, imdir):
        self.windowsize = (440, 440)
        self.impath = os.getcwd() + imdir
        self.playing = self.idle = os.path.join(imdir, "playing.gif")
        self.like = os.path.join(imdir, "playing2.gif")
        self.dleft = os.path.join(imdir, "dragleft.gif")#imdir + '\\dragleft.gif'
        self.dright = os.path.join(imdir, 'dragright.gif')
        self.dfleft = os.path.join(imdir, 'dragfarleft.gif')
        self.dfright = os.path.join(imdir, 'dragfarright.gif')
        # readGifs("animations/randyrunning.gif")
        self.walkleft = [os.path.join(imdir, "walkingleft", '{}'.format(i))  for i in os.listdir(os.path.join(imdir, "walkingleft"))]
        self.walkright = [os.path.join(imdir, "walkingright", '{}'.format(i)) for i in
                         os.listdir(os.path.join(imdir, "walkingright"))]
        self.fall = os.path.join(imdir, 'fall.png')
        self.jump = [imdir + '\\{}.png'.format(i) for i in 'jump1 jump2 jump3'.split()]
        self.icon = imdir + "\\icon.ico"
        self.frame = self.idle
        self.monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
        self.monitor_area = self.monitor_info.get("Monitor")
        self.work_area = self.monitor_info.get("Work")
        # projectile motion
        self.startingpos = (0, 0)
        self.cursorpos = (0, 0)
        self.xvelocity = 0
        self.yvelocity = 0
        self.angle = 0
        self.t = 1
        self.acceleration = 0
        self.cycle = 0  # frame 0
        self.action = 0
        self.animlength = 0
        # sizing
        self.monitorwidth, self.monitorheight = pyautogui.size()
        self.taskbarheight = self.monitor_area[3] - self.work_area[3]
        self.ground = self.monitorheight - self.windowsize[1] #380-120=260  440-128=320
        self.walkingstep = 15
        self.chatmode = "free"

        print(self.taskbarheight)
    def setFrame(self, newFrame):
        self.frame = newFrame

    def setSize(self, x, y):
        self.windowsize = (x, y)