
import sys
import threading
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sounddevice as sd
import soundfile as sf
import queue

from PyQt5 import QtCore, QtGui, QtWidgets


class RecordButton(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(100, 100)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(0, 0, 70, 70))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(r"recordButton/undone.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "发音检测"))


# qt线程 录音
class recordThread(QThread):
    # 定义信号
    _signal = pyqtSignal(str)
    recordDone2Main = pyqtSignal(str)
    def __init__(self, parent=None):
        super(recordThread, self).__init__(parent)
        self.isStart = False

    # 播放
    def play(self):
        event = threading.Event()
        data, fs = sf.read("output.wav", always_2d=True)
        current_frame = 0

        def callback(outdata, frames, time, status):
            global current_frame
            if status:
                print(status)
            chunksize = min(len(data) - current_frame, frames)
            outdata[:chunksize] = data[current_frame:current_frame + chunksize]
            if chunksize < frames:
                outdata[chunksize:] = 0
                raise sd.CallbackStop()
            current_frame += chunksize

        stream = sd.OutputStream(
            samplerate=fs, device=None, channels=data.shape[1],
            callback=callback, finished_callback=event.set)
        with stream:
            event.wait()  # Wait until playback is finished

    def stop(self):
        print("停止录音")
        self.isStart = False

    def run(self):
        # 开始录音
        self.isStart = True
        q = queue.Queue()

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        # soundfile expects an int, sounddevice provides a float:
        samplerate = 16000
        channels = 1
        # Make sure the file is opened before recording anything:
        with sf.SoundFile("output.wav", mode='w', samplerate=samplerate, channels=channels) as file:
            with sd.InputStream(samplerate=samplerate, device=None, channels=channels, callback=callback):
                self._signal.emit("开始录音")
                while self.isStart:
                    file.write(q.get())
        self.recordDone2Main.emit("Done")
        # 停止录音
        self._signal.emit("录音线程结束")


class buttonWindow(QWidget, RecordButton):
    def __init__(self):
        super(buttonWindow, self).__init__()
        self.setupUi(self)
        self.flag = 0
        self.setWindowFlags(
            self.windowFlags() | Qt.SubWindow | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()

        # 创建线程对象
        self.thread_obj = recordThread()
        # 将信号与槽连接
        self.thread_obj._signal.connect(self.set_btn)

    def set_btn(self, a):
        print(a)
        self.label.setEnabled(True)

    def mouseReleaseEvent(self, event):
        x = event.x()
        y = event.y()
        label = self.childAt(x, y)
        # 判断鼠标松开的对象是否为label
        if isinstance(label, QLabel):
            # 获取label的名字
            name = label.objectName()
            if name == "label":
                # 设置不可点击
                self.label.setEnabled(False)
                # 判断是否为第一次按下
                if self.flag == 0:
                    # 更换图片

                    self.movie = QMovie("recordButton/tranparant.gif")
                    # self.image = QLabel(self)
                    self.label.setMovie(self.movie)
                    self.movie.start()
                    # 开启线程
                    self.thread_obj.start()
                    # 设置标志位为1
                    self.flag = 1
                else:
                    # 更换图片
                    label.setPixmap(QPixmap("recordButton/done.png"))
                    self.thread_obj.stop()
                    self.flag = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 初始化窗口
    m = buttonWindow()
    m.show()
    sys.exit(app.exec_())


