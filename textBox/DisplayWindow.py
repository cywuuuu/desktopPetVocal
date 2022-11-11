import threading
import time

from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QPlainTextEdit, QGridLayout, QSizePolicy

from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QAction, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QPixmap, QMovie, QColor, QFont, QTextCharFormat, QTextBlockFormat, QEnterEvent, \
    QTextCursor
from PyQt5.QtCore import Qt, QCoreApplication, QPoint, QObject, QThread, pyqtSignal, QTimer, QEvent
import random

from destopPetInteraction.pet_interaction import PetInteraction
from textBox.dwindow import Ui_DockWidget
from textBox.preparation import *

cat_words = ["戳我干什么",  "喵喵喵!放开人家", "痛痛痛！"]

class ThreadForDwindow(QThread):
    toMain = pyqtSignal(str)
    def __init__(self,cfg, settings):
        super().__init__()
        self.cfg = cfg
        self.var = settings["VARIABLES"]
        self.interaction = PetInteraction(cfg, self.var, settings)
    def run(self) -> None:
        if self.cfg.chatmode == "free":
            time.sleep(1)
            self.toMain.emit("{}: {}".format(self.var["cat"], random.choice(cat_words)))
        if self.cfg.chatmode == "recordDone":
            res, text = self.interaction.step()
            if (res is not None) and (text is not None):
                self.toMain.emit("{}: {}".format(self.var["master"], text))
                self.toMain.emit("{}: {}".format(self.var["cat"], res))
            self.cfg.chatmode = "free"



class DisplayWindow(QDockWidget, Ui_DockWidget):
    def __init__(self , var, parent=None):
        super(DisplayWindow, self).__init__(parent)
        self.setupUi(self)
        self.var = var
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.Tool)  # 置顶、无边框、隐藏任务栏
        self.setAttribute(Qt.WA_TranslucentBackground)    # 窗体背景透明
        self.setMouseTracking(True)  # 设置widget鼠标跟踪
        # print(self.width(), self.height())
        # 显示样式
        self.Userfont = QColor(initusercolor)
        self.Comfont = QColor(initcomcolor)
        self.masterColor = QColor(mastercolor)
        # 初始化
        self.Ui_init()
        # 设置鼠标跟踪判断扳机默认值
        self._initDrag()

    def Ui_init(self):

        # 底层label，设置背景图片
        self.backLabel = QLabel()
        self.backLabel.setObjectName("backLabel")
        pix = QPixmap(initbackground)
        self.backLabel.setPixmap(pix)
        self.backLabel.setScaledContents(True)
        self.gridLayout.addWidget(self.backLabel, 0, 26, 11, 11)

        # 中间层
        self.comWidget = QWidget()
        self.gridLayout.addWidget(self.comWidget, 0, 26, 11, 11)
        self.comVerticalLayout = QVBoxLayout(self.comWidget)
        self.comVerticalLayout.setObjectName("comVerticalLayout")

        self.textEdit = QPlainTextEdit(self.comWidget)
        self.textEdit.setReadOnly(True)
        self.textEdit.setUndoRedoEnabled(False)
        self.textEdit.setMaximumBlockCount(initlinenum)
        font = QFont(initfont)
        font.setWordSpacing(20)
        self.textEdit.setFont(font)
        self.textEdit.setStyleSheet(
            f"font-size:{initsize}px;border: none; background-color: transparent; font-weight: bold;")
        self.comVerticalLayout.addWidget(self.textEdit)
        self.FontFormat = QTextCharFormat()
        self.BlockFormat = QTextBlockFormat()
        self.tc = self.textEdit.textCursor()

        self.BlockFormat.setLineHeight(initlineheight, QTextBlockFormat.FixedHeight)
        self.BlockFormat.setAlignment(Qt.AlignRight)
        self.tc.setBlockFormat(self.BlockFormat)
        self.textEdit.setTextCursor(self.tc)

        self.topWidget = QWidget()
        self.bottomLabel = QLabel(self.topWidget)
        self.rightLabel = QLabel(self.topWidget)
        self.cornerLabel = QLabel(self.topWidget)
        self.bottomLabel.setObjectName("bottomLabel")
        self.rightLabel.setObjectName("rightLabel")
        self.cornerLabel.setObjectName("cornerLabel")
        self.gridLayout.addWidget(self.topWidget, 0, 26, 11, 11)
        self.topLayout = QGridLayout(self.topWidget)
        self.topLayout.setObjectName("topLayout")
        self.bottomLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.rightLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.cornerLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.bottomLabel.setMaximumSize(999999999,20)
        self.rightLabel.setMaximumSize(20,999999999)
        self.cornerLabel.setMaximumSize(20,20)
        self.topLayout.addWidget(self.bottomLabel,1,0,Qt.AlignBottom)
        self.topLayout.addWidget(self.rightLabel,0,1,Qt.AlignRight)
        self.topLayout.addWidget(self.cornerLabel,1,1,Qt.AlignBottom|Qt.AlignRight)



    def addComment(self, msg):
        owner = "".join(msg.split(': ')[0])
        if owner == self.var["cat"]:
            self.FontFormat.setForeground(self.Userfont)
        else:
            self.FontFormat.setForeground(self.masterColor)
        self.textEdit.mergeCurrentCharFormat(self.FontFormat)
        self.textEdit.appendPlainText("".join(msg.split(': ')[0]) + ": ")
        self.FontFormat.setForeground(self.Comfont)
        self.textEdit.mergeCurrentCharFormat(self.FontFormat)
        self.tc.movePosition(QTextCursor.End)
        self.textEdit.insertPlainText("".join(msg.split(': ')[1]))
        QApplication.processEvents()

    def modifySize(self,type,value):
        def aa():
            try:
                if type == 'charactersSize':
                    self.textEdit.setStyleSheet(
                        f"font-size:{value}px;font-weight:bold;border: none; background-color: transparent;")

                elif type == 'lineNum':
                    self.textEdit.setMaximumBlockCount(value)

                elif type == 'lineHeight':
                    self.BlockFormat.setLineHeight(value, QTextBlockFormat.FixedHeight)
                    self.tc.setBlockFormat(self.BlockFormat)
                    self.textEdit.setTextCursor(self.tc)

            except Exception as e:
                pass
        threading.Thread(target=aa).start()

    def modifyOther(self,type,value):
        def aa():
            try:
                if type == 'userColor':
                    self.Userfont = QColor(value)
                elif type == 'comColor':
                    self.Comfont = QColor(value)
                elif type == 'background':
                    pix = QPixmap(value)
                    self.backLabel.setPixmap(pix)
            except Exception as e:
                pass

        threading.Thread(target=aa).start()

    def modifyFont(self,font):
        def aa():
            try:
                self.textEdit.setFont(font)
            except Exception as e:
                pass
        threading.Thread(target=aa).start()

    def clearWindow(self):
        self.textEdit.clear()

    def _initDrag(self):
        self.moveDrag = False
        self.cornerDrag = False
        self.bottomDrag = False
        self.rightDrag = False
        self.cornerLabel.setCursor(Qt.SizeFDiagCursor)
        self.bottomLabel.setCursor(Qt.SizeVerCursor)
        self.rightLabel.setCursor(Qt.SizeHorCursor)

    def eventFilter(self, obj, event):
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(DisplayWindow, self).eventFilter(obj, event)
        # return QWidget.eventFilter(self, obj, event)  # 用这个也行，但要注意修改窗口类型

    def resizeEvent(self, QResizeEvent):
        ran = 30
        self.rightRect = [QPoint(x, y) for x in range(self.width() - ran, self.width())
                          for y in range(1, self.height()-ran)]
        self.bottomRect = [QPoint(x, y) for x in range(1, self.width() - ran)
                           for y in range(self.height() - ran, self.height())]
        self.cornerRect = [QPoint(x, y) for x in range(self.width() - ran, self.width())
                           for y in range(self.height() - ran, self.height() )]

    def mousePressEvent(self, event):
        if (event.button() == Qt.LeftButton) and (event.pos() in self.cornerRect):
            self.cornerDrag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self.rightRect):
            self.rightDrag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self.bottomRect):
            self.bottomDrag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self.height()-30):
            self.moveDrag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.rightDrag:
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        elif Qt.LeftButton and self.bottomDrag:
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self.cornerDrag:
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self.moveDrag:
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.moveDrag = False
        self.cornerDrag = False
        self.bottomDrag = False
        self.rightDrag = False