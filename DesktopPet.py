import re

from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QAction, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtCore import Qt, QCoreApplication, QPoint, QObject, QThread, pyqtSignal, QTimer, QEvent
import random

import time

import pyautogui
import mouse


from Menu.MyMenu import MyMenu
from recordButton.recordButton import buttonWindow, recordThread
from textBox.DisplayWindow import DisplayWindow, ThreadForDwindow


class DesktopPet(QWidget):
    def __init__(self, cfg, util, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        self.config = util.readConfig()
        self.variable = self.config["VARIABLES"]
        # ****
        self.DWindow = DisplayWindow(self.variable)
        self.DWindowThread = ThreadForDwindow(cfg, self.config)
        self.DWindow.moveToThread(self.DWindowThread)
        self.DWindowThread.toMain.connect(lambda x: self.DWindow.addComment(x))
        self.DWindow.show()


        self.BWindow = buttonWindow()
        self.BWindow.thread_obj.recordDone2Main.connect(lambda x: self.recordDone(x))
        self.BWindow.show()

        self.cfg = cfg
        self.util = util
        self.setWindowFlags(
            self.windowFlags() | Qt.SubWindow | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()

        self.setGeometry(10, 10, self.cfg.windowsize[0], self.cfg.windowsize[1])
        self.movie = QMovie(self.cfg.playing)
        self.image = QLabel(self)
        self.image.setMovie(self.movie)
        self.movie.start()

        monitorwidth = self.cfg.monitorwidth
        ground = self.cfg.ground
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.move(monitorwidth * 0.6, ground)
        self.DWindow.move(monitorwidth * 0.6 + self.cfg.windowsize[0]//2, ground - self.cfg.windowsize[1]//2)
        self.BWindow.move(monitorwidth * 0.6 + self.cfg.windowsize[0]//2, ground - self.cfg.windowsize[1]//2-70)

        self.settings = self.config["SETTINGS"]

        self.stealingCursor = False  # if is stealing cursor

        self.cursorhistory = [(0, 0), 0]

        # action timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.petsAction)

        duration = util.find_duration(self.cfg.playing)
        self.timer.start(duration)

        self.yeettimer = QTimer()
        self.yeettimer.timeout.connect(self.Yeet)

        self.leaptimer = QTimer()
        self.leaptimer.timeout.connect(self.Leap)

        self.cursorcam = QTimer()
        self.cursorcam.timeout.connect(self.captureCursor)
        self.cursorcam.start(500)

        # self.installEventFilter(self)

    # def eventFilter(self, source, event):
    # return super(DesktopPet, self).eventFilter(source, event)

    def recordDone(self, str):
        if str == "Done":
            self.cfg.chatmode = "recordDone"
            self.DWindowThread.start()

    def showMenu(self, event):

        menu = MyMenu()
        menu.clear()

        if self.settings["walk"] == False:
            walk = menu.addAction("Free")
        else:
            walk = menu.addAction("Sit Still")

        cursorcatch = menu.addAction("Catch My Cursor")

        settingsMenu = menu.addMenu("Settings")



        if self.settings["gravity"] == True:
            gravity = settingsMenu.addAction("Disable Gravity")
        else:
            gravity = settingsMenu.addAction("Enable Gravity")

        if self.settings["cursorTheft"] == False:
            cursortheft = settingsMenu.addAction("Enable cursor stealing")
        else:
            cursortheft = settingsMenu.addAction("Disable cursor stealing")

        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event))

        if action == quit_action:
            # run offscreen
            self.settings["ongoingAction"] = True
            finished = False
            imageset = False
            monitorwidth = self.cfg.monitorwidth
            x = self.x()
            if x > monitorwidth // 2:  # right
                while x <= monitorwidth + 100:
                    self.cfg.cycle, self.cfg.frame = self.util.animate(self.cfg.cycle, self.cfg.walkright)
                    x += self.cfg.walkingstep
                    time.sleep(0.03)
                    if re.search(".gif$", self.cfg.frame) != None:
                        self.timer.setInterval(self.util.find_duration(self.cfg.playing))
                        self.movie = QMovie(self.cfg.frame)
                        self.image.setMovie(self.movie)
                        self.movie.start()
                    else:
                        self.timer.setInterval(50)
                        self.image.setPixmap(QPixmap(self.cfg.frame))
                    self.repaint()
                    self.move(x, self.y())
                    self.DWindow.move(x + self.cfg.windowsize[0] // 2,
                                      self.y() - self.cfg.windowsize[1] // 2)
                    self.BWindow.move(x + self.cfg.windowsize[0] // 2,
                                      self.y() - self.cfg.windowsize[1] // 2-70)
                finished = True

            else:
                while x >= -100:
                    self.cfg.cycle, self.cfg.frame = self.util.animate(self.cfg.cycle, self.cfg.walkleft)
                    x -= self.cfg.walkingstep
                    time.sleep(0.03)
                    if re.search(".gif$", self.cfg.frame) != None:
                        self.timer.setInterval(self.util.find_duration(self.cfg.playing))
                        self.movie = QMovie(self.cfg.frame)
                        self.image.setMovie(self.movie)
                        self.movie.start()
                    else:
                        self.timer.setInterval(50)
                        self.image.setPixmap(QPixmap(self.cfg.frame))
                    self.repaint()
                    self.move(x, self.y())
                    self.DWindow.move(x + self.cfg.windowsize[0] // 2,
                                      self.y() - self.cfg.windowsize[1] // 2)
                    self.BWindow.move(x + self.cfg.windowsize[0] // 2,
                                      self.y() - self.cfg.windowsize[1] // 2-70)
                finished = True

            # quit
            if finished:
                QCoreApplication.instance().quit()

        if action == cursorcatch:
            self.settings["ongoingAction"] = True
            self.leaptimer.start(1000)

        if action == gravity:
            self.settings["gravity"] = not self.settings["gravity"]
            self.util.writeConfig(self.config)
            if self.settings["gravity"] == True:
                self.settings["ongoingAction"] = True
                self.image.setPixmap(QPixmap(self.cfg.fall))
                self.repaint()
                startingpos = self.cfg.startingpos
                startingpos = (self.x(), self.y())

                self.Yeet()

        if action == walk:
            self.settings["walk"] = not self.settings["walk"]
            self.movie = QMovie(self.cfg.playing)
            self.image.setMovie(self.movie)
            self.movie.start()
            # self.image.setPixmap(QPixmap(self.cfg.idle))
            # self.loading_gif = QMovie(self.cfg.idle)
            # self.loading_label = QLabel(self)
            # self.loading_label.setMovie(self.loading_gif)
            # self.loading_gif.start()
            self.repaint()
            self.util.writeConfig(self.config)

        if action == cursortheft:
            self.settings["cursorTheft"] = not self.settings["cursorTheft"]
            self.util.writeConfig(self.config)

    def mousePressEvent(self, event):

        self.oldPos = event.globalPos()
        if event.buttons() == Qt.LeftButton:
            self.cfg.xvelocity = 0
            self.cfg.yvelocity = 0
            self.cfg.startingpos = (self.x(), self.y())

            self.settings["ongoingAction"] = True
            self.yeettimer.stop()
            self.DWindowThread.start()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

            self.cfg.angle = self.util.getAngle(delta.x(), delta.y())
            self.cfg.xvelocity = abs(delta.x())
            self.cfg.yvelocity = abs(delta.y())

            # t = 1
            self.cfg.startingpos = (self.x(), self.y())

            if delta.x() < -1:
                # self.image.setPixmap(QPixmap(self.cfg.dfleft))
                self.movie = QMovie(self.cfg.dfleft)
                self.image.setMovie(self.movie)
                self.movie.start()
            elif delta.x() < 0:
                # self.image.setPixmap(QPixmap(self.cfg.dleft))
                self.movie = QMovie(self.cfg.dleft)
                self.image.setMovie(self.movie)
                self.movie.start()
            elif delta.x() > 1:
                # self.image.setPixmap(QPixmap(self.cfg.dfright))
                self.movie = QMovie(self.cfg.dfright)
                self.image.setMovie(self.movie)
                self.movie.start()
            else:
                # self.image.setPixmap(QPixmap(self.cfg.dright))
                self.movie = QMovie(self.cfg.dright)
                self.image.setMovie(self.movie)
                self.movie.start()

    def mouseReleaseEvent(self, event):
        # self.settings["ongoingAction"] = False

        self.cfg.t = 1
        if self.settings["ongoingAction"] == True:
            if self.settings["gravity"]:
                self.image.setPixmap(QPixmap(self.cfg.fall))
                self.repaint()
                self.Yeet()
            else:
                self.settings["ongoingAction"] = False
                self.movie = QMovie(self.cfg.playing)
                self.image.setMovie(self.movie)
                self.movie.start()
                self.repaint()
                self.petsAction()

    def Yeet(self):

        if self.y() < self.cfg.ground and self.settings["ongoingAction"]:
            x, y = self.util.getDisplacement(self.x(), self.y())
            self.move(x, y)
            self.DWindow.move(self.x() + self.cfg.windowsize[0] // 2,
                              self.y() - self.cfg.windowsize[1] // 2)
            self.BWindow.move(self.x() + self.cfg.windowsize[0] // 2,
                              self.y() - self.cfg.windowsize[1] // 2-70)
            self.yeettimer.start(50 / self.cfg.t + 10)
        else:
            self.yeettimer.stop()
            self.image.setPixmap(QPixmap(self.cfg.fall))
            self.repaint()
            for i in range(5):
                x, y = self.util.getDisplacement(self.x(), self.y())
                if y != self.cfg.ground:
                    y = self.cfg.ground
                if x - self.x() > 0:
                    x += min((x - self.x()) * 0.05 * i, 10 - i)
                else:
                    x += max((x - self.x()) * 0.05 * i, i - 10)
                self.move(x, y)
                self.DWindow.move(self.x() + self.cfg.windowsize[0] // 2,
                                  self.y() - self.cfg.windowsize[1] // 2)
                self.BWindow.move(self.x() + self.cfg.windowsize[0] // 2,
                                  self.y() - self.cfg.windowsize[1] // 2-70)
                time.sleep(0.02 * 5 / self.cfg.t)
            if self.y() != self.cfg.ground:
                self.Yeet()

            self.settings["ongoingAction"] = False
            self.movie = QMovie(self.cfg.playing)
            self.image.setMovie(self.movie)
            self.movie.start()
            self.repaint()
            self.petsAction()

    def Leap(self):  # only works for gravity enabled

        if self.y() != self.cfg.ground or self.cfg.t == 1 or self.cfg.t == 2 or self.cfg.t == 3:
            if self.cfg.t == 1:  # play the first two frames
                self.cfg.startingpos = (self.x(), self.y())
                self.cfg.cursorpos = pyautogui.position()
                self.cfg.cursorpos = (self.cfg.cursorpos[0], self.cfg.monitorheight - self.cfg.cursorpos[1])
                self.image.setPixmap(QPixmap(self.cfg.jump[0]))
                self.repaint()
                self.cfg.t += 1
                self.leaptimer.setInterval(200)
            elif self.cfg.t == 2:
                self.image.setPixmap(QPixmap(self.cfg.jump[1]))
                self.repaint()
                self.cfg.t += 1
            else:
                self.image.setPixmap(QPixmap(self.cfg.jump[2]))
                self.repaint()
                x, y = self.util.getJumpHeight()
                self.move(x, y)
                self.DWindow.move(self.x() + self.cfg.windowsize[0] // 2,
                                  self.y() - self.cfg.windowsize[1] // 2)
                self.BWindow.move(self.x() + self.cfg.windowsize[0] // 2,
                                  self.y() - self.cfg.windowsize[1] // 2-70)
                currentcursorpos = pyautogui.position()
                if currentcursorpos[0] + 32 > x \
                        and currentcursorpos[0] < x + 440 \
                        and currentcursorpos[1] + 32 > y \
                        and currentcursorpos[1] < y + 440:
                    self.stealingCursor = True

                if self.stealingCursor == True and self.settings["cursorTheft"] == True:
                    mouse.move(x + self.cfg.windowsize[0] // 2, y + self.cfg.windowsize[1] // 2)
                    self.DWindow.move(self.x() + self.cfg.windowsize[0] ,
                                      self.y() - self.cfg.windowsize[1] )
                    self.BWindow.move(self.x() + self.cfg.windowsize[0] ,
                                      self.y() - self.cfg.windowsize[1] -70)
                self.leaptimer.setInterval(1)



        else:
            self.stealingCursor = False
            self.settings["ongoingAction"] = False
            self.cursorhistory[1] = 0
            self.cfg.t = 1
            self.movie = QMovie(self.cfg.playing)
            self.image.setMovie(self.movie)
            self.movie.start()
            self.repaint()
            self.leaptimer.stop()
            self.petsAction()

    def captureCursor(self):
        # print(self.settings)
        self.cfg.cursorpos = pyautogui.position()
        if self.cursorhistory[0] == self.cfg.cursorpos:
            self.cursorhistory[1] += 1  # add 1 second to timer
        else:
            self.cursorhistory[0] = self.cfg.cursorpos
            self.cursorhistory[1] = 0  # reset if cursor moves

    def getPetsAction(self):
        ifgif = False
        if not self.settings["walk"]:
            return 0
        choices = [i for i in range(4)]
        if self.x() > 1408:  # on the right
            choices.remove(2)
        elif self.x() < 440:  # on the left
            choices.remove(1)

        if self.y() < pyautogui.position()[1] or self.cursorhistory[1] < 60:  # if above cursor
            choices.remove(3)

        action = random.choice(choices)
        return action

    def petsAction(self):
        if not self.settings["ongoingAction"] and self.settings["walk"]:

            self.cfg.frame = self.cfg.playing
            # frame = idle
            x = self.x()
            if self.cfg.action == 0:
                self.cfg.animlength += 10

            elif self.cfg.action == 1:
                if x < 440:
                    self.cfg.animlength += 20
                else:
                    self.cfg.cycle, self.cfg.frame = self.util.animate(self.cfg.cycle, self.cfg.walkleft)
                    x -= self.cfg.walkingstep
                    self.cfg.animlength += 1

            elif self.cfg.action == 2:
                if x > 1408:
                    self.cfg.animlength += 20
                else:
                    self.cfg.cycle, self.cfg.frame = self.util.animate(self.cfg.cycle, self.cfg.walkright)
                    x += self.cfg.walkingstep
                    self.cfg.animlength += 1

            elif self.cfg.action == 3:
                self.settings["ongoingAction"] = True
                self.leaptimer.start(0.1)
                self.cfg.animlength += 20

            time.sleep(0.05)
            print(self.cfg.animlength)
            if self.cfg.animlength >= 20:
                self.cfg.animlength = 0
                self.cfg.action = self.getPetsAction()
            if re.search(".gif$", self.cfg.frame) != None:
                self.timer.setInterval(self.util.find_duration(self.cfg.playing))
                self.movie = QMovie(self.cfg.frame)
                self.image.setMovie(self.movie)
                self.movie.start()
            else:
                self.timer.setInterval(50)
                print(self.cfg.frame)
                self.image.setPixmap(QPixmap(self.cfg.frame))
            self.move(x, self.y())
            self.DWindow.move(self.x() + self.cfg.windowsize[0] // 2,
                              self.y() - self.cfg.windowsize[1] // 2)
            self.BWindow.move(self.x() + self.cfg.windowsize[0] // 2,
                              self.y() - self.cfg.windowsize[1] // 2-70)
