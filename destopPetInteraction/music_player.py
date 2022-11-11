import sys,json,os,psutil,tinytag,numpy # time,
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QStringListModel,QSize,QTimer,QThread,pyqtSignal
from PyQt5.QtGui import QIcon,QPainter,QColor,QFont,QPixmap,QCursor
#from PyQt5.QtMultimedia import *
import pathlib as pa
from PyQt5 import sip
from pygame import mixer
#from all import All
#小心命名问题，如果文件名，脚本中的类名，函数名与python内置的函数名一致会使pyinstaller打包失败
class All():
    def __init__(self,all):
        self.like=all['like']  #list
        self.playlist=all['playlist'] #{}
        self.musiclist=all['musiclist']
        self.playingmusic=all['playingmusic']
        self.playingtime=all['playingtime']
        self.musicsec=all['musicsec']
        self.playmode=all['playmode']
        self.playhistory=all['playhistory']
        self.allmusic=all['allmusic']
        self.volume=all['volume']
#all={'like':[],'allmusic':[],'playlist':{},'musiclist':[],  'playingmusic':'',  'playmode':'随机播放', 'playingtime': 0, 'playhistory': {}, 'musicsec': 0,'volume'=1.0}
class ttt(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        mixer.init()
        self.initt()
    def initt(self):
        self.layv=QVBoxLayout()
        self.layv_h1=QHBoxLayout()  #top
        self.layv_h2=QHBoxLayout()   #bottom
        self.layv_h2_v1=QVBoxLayout()     #bottom left   歌单 总
        self.layv_h2_v1_h1=QHBoxLayout()    #歌单名称
        self.layv_h2_v1_h2=QHBoxLayout()     #歌单创建
        self.layv_h2_v1_h3 = QHBoxLayout()
        self.layv_h3=QHBoxLayout()   #歌单列表  #最低部，播放功能
        self.layv_h2_v2=QVBoxLayout()      #buttomright  歌曲列表
        self.layv_h2_v2_h1=QHBoxLayout()  #本地列表  扫描
        self.layv_h2_v2_h2=QHBoxLayout()  #复选磁盘
        self.layv_h2_v2_h3=QHBoxLayout()  #音乐列表和一个额外的列表
        self.layv_h2_v2_h3_v1=QVBoxLayout()  #额外的列表
        self.layv_h2_v2_h3_v2=QVBoxLayout()  #音乐列表
        self.box1=QPushButton('本地音乐')
        self.box1.setCheckable(False)
        self.box1.clicked.connect(self.box1f)
        #box1.setIcon(QIcon(QPixmap('12.jpg')))
        self.box2=QPushButton('。。。播放列表。。。')
        self.box2.setCheckable(True)
        self.box2.clicked.connect(self.box2f)
        self.layv_h1.addWidget(self.box1)
        #layv_h1.addStretch(0)
        self.layv_h1.addWidget(self.box2)
        #layv_h1.addStretch(0)
        self.layv.addLayout(self.layv_h1)
        self.layv.addStretch(0)
        self.layv.addWidget(QLabel('_'*500))  #分割线，后面再想办法美化
        self.all,self.playlist,self.plist={},[],{}
        self.readfile()

        self.al=All(self.all)

        self.label1=QLabel('歌单',self)
        self.addpl=QPushButton('+')
        self.addpl.setCheckable(False)
        self.addpl.clicked.connect(self.addplf)
        self.layv_h2_v1_h1.addWidget(self.label1)
        self.layv_h2_v1_h1.addWidget(self.addpl)
        self.pl = QListWidget()
        self.pl.setMinimumSize(100,350)
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(18)
        self.pl.setFont(self.font)
        self.pl.addItem('like')
        self.pl.addItems(self.playlist)
        self.pl.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pl.customContextMenuRequested.connect(self.plr)
        self.pl.doubleClicked.connect(self.dplf)
        self.layv_h2_v1_h3.addWidget(self.pl)

        self.mlabel=QLabel('播放列表',self)
        self.mlabel.setAlignment(Qt.AlignCenter)
        self.layv_h2_v2.addWidget(self.mlabel)
        self.layv_h2_v2.addStretch(0)
        split=QLabel('_'*80,self)
        split.setAlignment(Qt.AlignTop)
        self.layv_h2_v2.addWidget(split)
        self.layv_h2_v2.addStretch(0)
        self.layv_h2_v2.addLayout(self.layv_h2_v2_h1)
        self.layv_h2_v2.addLayout(self.layv_h2_v2_h2)

        self.layv_h2_v2_h3.addLayout(self.layv_h2_v2_h3_v1)
        self.layv_h2_v2_h3.addStretch(0)
        self.layv_h2_v2_h3.addLayout(self.layv_h2_v2_h3_v2)
        self.layv_h2_v2_h3.addStretch(10)
        self.layv_h2_v2.addLayout(self.layv_h2_v2_h3)
        self.layv_h2_v2.addStretch(100)
        self.ml=QTableWidget()
        self.ml.setColumnCount(5)
        self.ml.setRowCount(len(self.all['musiclist']))

        self.ml.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ml.resizeColumnsToContents()
        self.ml.resizeRowsToContents()
        self.ml.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ml.setShowGrid(False)
        self.ml.setMinimumSize(500,400)
        self.ml.setColumnWidth(0, 20)
        self.ml.setColumnWidth(1,300-50)
        self.ml.setColumnWidth(2, 80)
        self.ml.setColumnWidth(3, 80)
        self.ml.setColumnWidth(4, 50)
        self.ml.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ml.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ml.customContextMenuRequested.connect(self.mlmenu)
        self.ml.doubleClicked.connect(self.dmlf)
        self.musicitems1,self.musicitems2,self.musicitems3=[],[],[]
        self.musiclist(self.all['musiclist'])
        self.layv_h2_v2_h3_v2.addWidget(self.ml)
        self.layv_h2_v2_h3_v2.addStretch(10)
        self.ml.verticalHeader().setVisible(False)

        self.boxl=QPushButton('上一曲')
        self.boxc=QPushButton('播放')
        self.boxr=QPushButton('下一曲')
        self.timelc=QLabel('0:0')
        self.sec=self.all['playingtime']
        self.control=QSlider(Qt.Horizontal)  #播放进程
        self.musicname=QPushButton(pa.Path(self.all['playingmusic']).stem)
        self.musicmode=QLabel(self.all['playmode'])
        self.boxvol=QSlider(Qt.Horizontal)
        self.addtolike=QPushButton('☆')
        self.musicsec=QLabel(str(self.all['musicsec']//60)+':'+str(self.all['musicsec']%60))#()
        self.layv_h3_h1=QHBoxLayout()
        self.layv_h3_h1.addWidget(self.musicmode)
        self.layv_h3_h1.addWidget(QLabel('音量'))
        self.layv_h3_h1.addWidget(self.boxvol)
        self.layv_h3_h1.addStretch(0)
        self.layv_h3_h1.addWidget(self.addtolike)
        self.layv_h3_h1.addStretch(0)
        self.layv_h3_h1.addWidget(self.musicname)
        self.layv_h3_h1.addStretch(1)
        self.layv_h3.addWidget(self.boxl)
        self.layv_h3.addWidget(self.boxc)
        self.layv_h3.addWidget(self.boxr)
        self.layv_h3.addWidget(self.timelc)
        self.layv_h3.addWidget(self.control)
        self.layv_h3.addWidget(self.musicsec)
        self.boxl.clicked.connect(self.boxlf)
        self.boxc.clicked.connect(self.boxcf)
        self.boxr.clicked.connect(self.boxrf)
        self.control.setMaximum(self.all['musicsec'])
        self.control.setValue(self.all['playingtime'])
        self.control.sliderReleased.connect(self.controlf)
        self.boxvol.setMaximum(100)
        self.boxvol.setMaximumWidth(100)
        self.boxvol.setValue(int(self.al.volume*100))
        self.boxvol.sliderReleased.connect(self.volchange)
        self.addtolike.clicked.connect(self.addtolikef)

        if self.all['playingmusic'] in self.all['like']:
            self.addtolike.setText('★')
        com=QComboBox()
        fontpath=pa.Path('C:\Windows\Fonts')
        self.fonts=[]
        for x in fontpath.glob('**/*.ttf'):
            self.fonts.append(x.stem)
        com.addItems(self.fonts)
        com.currentIndexChanged.connect(self.comf)
        #self.layv_h2_v1.addWidget(com)

        com2=QComboBox()
        for x in range(10,35):
            com2.addItem(str(x))
        com2.currentIndexChanged.connect(self.com2f)
        com2.setCurrentText('15')
        #self.layv_h2_v1.addWidget(com2)
        
        self.layv_h2_v1_h3.addStretch(1)
        self.layv_h2_v1.addLayout(self.layv_h2_v1_h1)
        self.layv_h2_v1.addStretch(0)
        self.layv_h2_v1.addLayout(self.layv_h2_v1_h2)
        self.layv_h2_v1.addLayout(self.layv_h2_v1_h3)
        self.layv_h2_v1.addStretch(0)
        self.layv_h2.addLayout(self.layv_h2_v1)
        self.layv_h2.addStretch(0)
        #self.layv_h2.addWidget(QPushButton(''))
        #self.layv_h2.addStretch(0)
        self.layv_h2.addLayout(self.layv_h2_v2)
        self.layv_h2.addStretch(10)
        self.layv.addLayout(self.layv_h2)
        self.layv.addStretch(1)
        self.layv.addLayout(self.layv_h3_h1)
        self.layv.addStretch(0)
        self.layv.addLayout(self.layv_h3)
        self.layv.addStretch(0)
        self.setLayout(self.layv)
        self.show()

        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.test)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerf)
        self.timesec=QTimer()
        self.timesec.timeout.connect(self.timesecf)
    def comf(self,i):#设置歌单字体
        print(self.fonts[i])
        self.font.setFamily(self.fonts[i])
        self.pl.setFont(self.font)
    def com2f(self,i):#设置歌单字体大小
        self.font.setPointSize(int(i)+10)
        self.pl.setFont(self.font)
    def clicked(self,qModelIndex):
        QMessageBox.information(self,"ListWideget","You chooce:"+self.qlist[qModelIndex.row()])
    def clickeds(self,item):
        QMessageBox.information(self,"ListWideget","You chooce:"+item.text())
    def box1f(self):
        if not self.box1.isCheckable():
            self.box1.setText('。。。本地音乐。。。')
            self.box1.setCheckable(True)
            self.box2.setText('播放列表')
            self.box2.setCheckable(False)
            self.box1_1=QPushButton('扫描磁盘音乐')
            self.box1_1.clicked.connect(self.box1_1f)
            self.box1_1.setCheckable(False)
            self.box1_1.setToolTip('扫描文件')
            self.box1_2=QPushButton('添加文件路径')
            self.box1_2.clicked.connect(self.box1_2f)
            self.box1_2.setToolTip('添加文件路径')
            self.layv_h2_v2_h1.addWidget(self.box1_1)
            self.layv_h2_v2_h1.addWidget(self.box1_2)
            self.mlabel.setText('本地音乐列表')
            self.musiclist(self.all['allmusic'])

    def musiclist(self,list):
        self.ml.clear()
        self.ml.setHorizontalHeaderLabels(['like','歌曲', '歌手', '专辑','时长'])
        self.ml.setRowCount(len(list))
        for y, x in enumerate(list):
            try:
                if x in self.all['like']:
                    new0=QTableWidgetItem("★")
                else:
                    new0 = QTableWidgetItem("☆")
                if "-" in pa.Path(x).stem:
                    name=pa.Path(x).stem[pa.Path(x).stem.find('-')+1:]
                else:
                    name=pa.Path(x).stem
                new1 = QTableWidgetItem(name.strip())
                info = tinytag.TinyTag.get(x)
                new2 = QTableWidgetItem(info.artist)
                new3 = QTableWidgetItem(info.album)
                times=str(int(info.duration//60))+": "+str(int(info.duration)%60)
                new4= QTableWidgetItem(times)
                self.ml.setItem(y,0,new0)
                self.ml.setItem(y, 1, new1)
                self.ml.setItem(y, 2, new2)
                self.ml.setItem(y, 3, new3)
                self.ml.setItem(y,4,new4)
            except:
                list.remove(x)
            # print(y, x)
    def box2f(self):
        if not self.box2.isCheckable():
            if self.box1.isCheckable():
                self.layv_h2_v2_h1.removeWidget(self.box1_1)
                self.layv_h2_v2_h1.removeWidget(self.box1_2)
                sip.delete(self.box1_1)
                sip.delete(self.box1_2)
            self.box2.setCheckable(True)
            self.box1.setText('本地音乐')
            self.box1.setCheckable(False)
            self.box2.setText('。。。播放列表。。。')
            self.mlabel.setText('播放列表')
            self.musiclist(self.all['musiclist'])
    def readfile(self):
        self.savefilename='save_information.json'
        if os.path.exists(self.savefilename):
            print('exit')
            with open(self.savefilename,'r',encoding='gbk') as f:
                self.all=json.load(f)
            self.plist=self.all['playlist']
            if not len(self.plist) == 0:
                print(self.plist)
                self.playlist=[x for x in self.plist.keys() ]
            print(self.all)
            print(self.playlist)
        else:
            with open(self.savefilename,'w',encoding='gbk') as f:
                self.all={'like':[],'allmusic':[],'playlist':{},'musiclist':[],  'playingmusic':'',  'playmode':'随机播放', 'playingtime': 0, 'playhistory': {}, 'musicsec': 0,'volume':1.0}
                #喜欢音乐列表，歌单，本地音乐列表，播放列表，播放模式，正在播放的音乐，已经播放的时间
                # {'like':[],'playlist':{},'allmusic':[],'musiclist':[],'playmode':'随机播放','playingmusic':'','playingtime':0,'musicsec':'0.0','playhistory':{}}
                json.dump(self.all,f)
    def addplf(self):
        if self.addpl.isCheckable():
            print('T')
        else:
            print('f')
            self.addpl.setCheckable(True)
            self.plinput = QLineEdit()
            self.plinput.setPlaceholderText('歌单名称')
            self.okinput = QPushButton('OK')
            self.okinput.clicked.connect(self.okinputf)
            self.layv_h2_v1_h2.addWidget(self.plinput)
            self.layv_h2_v1_h2.addWidget(self.okinput)
    def okinputf(self):
        print(self.plinput.text())
        if not self.plinput.text()=='' and self.plinput.text() not in self.playlist and self.plinput.text()!='like':
            self.plist[self.plinput.text()]=[]
            self.playlist.append(self.plinput.text())
            self.all['playlist'][self.plinput.text()]=[]
            self.pl.addItem(self.plinput.text())
        elif self.plinput.text() in self.playlist:
            print('??')
        self.layv_h2_v1_h2.removeWidget(self.plinput)
        self.layv_h2_v1_h2.removeWidget(self.okinput)
        sip.delete(self.plinput)
        sip.delete(self.okinput)
        self.addpl.setCheckable(False)

    def plr(self):
        print('??')
        cmenu = QMenu(self)
        newAct = cmenu.addAction("New")
        delact = cmenu.addAction("delete")
        #quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(QCursor.pos())
        print('ss')
        if action == newAct:
            self.addplf()
        elif action == delact and self.pl.currentRow()>0:
            print(self.pl.currentRow())
            self.plist.pop(self.playlist[self.pl.currentRow()-1])#注意这里存在的问题
            self.playlist.pop(self.pl.currentRow()-1)#问题
            self.pl.takeItem(self.pl.currentRow())
    def box1_1f(self):
        if not self.box1_1.isCheckable():
            self.box2.setEnabled(False)
            self.box1_1.setCheckable(True)
            self.box1_2.setCheckable(True)
            d = psutil.disk_partitions()
            self.gb=QGroupBox('选择你想要扫描的磁盘')
            self.checkbox=QCheckBox()
            list=[]
            for xx in d:
                if not xx[3] == 'cdrom' and not xx[0][0]=='C':
                    print(xx[0])
                    list.append(xx)
            self.qc=[QCheckBox(xx[0][0],self) for xx in list]
            for x in self.qc:
                x.setChecked(False )
                self.layv_h2_v2_h2.addWidget(x)
            self.okscan=QPushButton('OK')
            self.okscan.clicked.connect(self.okscanf)
            self.layv_h2_v2_h2.addWidget(self.okscan)
            self.gb.setLayout(self.layv_h2_v2_h2)
            self.layv_h2_v2_h2.insertWidget(0,self.gb)
    def box1_2f(self):
        if not self.box1_2.isCheckable():
            self.box2.setEnabled(False)
            self.box1_2.setCheckable(True)
            self.box1_1.setCheckable(True) ##后面再设置否
            filed=QFileDialog()
            filed.setFileMode(QFileDialog.Directory)
            #filed.setFilter(QDir)
            name=str(filed.getExistingDirectory())
            print(name)
            self.scanpath(name)
    def okscanf(self):
        #if self.okscan.text()=='OK':
            print('xxx')
            for x in self.qc:
                print(x.isChecked())

            self.timer.start(100)
            self.okscan.setText('wait!!')
            self.okscan.setEnabled(False)
            self.box1_2.setEnabled(False)
    def timerf(self):
        self.timer.stop()
        print('????')
        self.okscan.setEnabled(True)
        for x in self.qc:
            if x.isChecked():
                path=x.text()+':\\'
                print(path)
                self.scanpath(path)
        #print(self.all['allmusic'])
        self.gb.setTitle('扫描完毕')
        self.layv_h2_v2_h2.removeWidget(self.gb)
        sip.delete(self.gb)
        for x in self.qc:
            self.layv_h2_v2_h2.removeWidget(x)
            sip.delete(x)
        self.layv_h2_v2_h2.removeWidget(self.okscan)
        self.okscan.setText('OK')
        sip.delete(self.okscan)
        self.box2.setEnabled(True)
        self.box1_2.setEnabled(True)
        self.box1_1.setCheckable(False)
        self.box1_2.setCheckable(False)
    def scanpath(self,path):
        for xx in pa.Path(path).glob('**/*'):
            #self.gb.setTitle('正在扫描：' + str(xx.root))
            if tinytag.TinyTag.is_supported(str(xx.name)):
                #print(xx)
                if (os.path.getsize(xx)) > 1 * 1024 * 1024 and (
                        os.path.getsize(xx)) < 50 * 1024 * 1024 and str(xx) not in self.all['allmusic']:
                    print(xx)
                    self.all['allmusic'].append(str(xx))
        self.musiclist(self.all['allmusic'])
        self.box2.setEnabled(True)
        self.box1_2.setEnabled(True)
        self.box1_1.setCheckable(False)
        self.box1_2.setCheckable(False)
    def mlmenu(self,pos):
        print(self.ml.currentRow())
        if self.ml.currentRow()>=0:
            menu=QMenu()
            item1=menu.addAction("播放")
            item2=menu.addAction("暂停")
            item3 =menu.addAction('下一曲')
            menu1=QMenu()
            menu1.setTitle('播放模式')
            m,modes=['顺序播放','列表循环','单曲循环','随机播放'],[]
            for x in m:
                if self.all['playmode']==x:
                    modes.append(menu1.addAction('✔'+x))
                else:
                    modes.append(menu1.addAction('   '+x))
            menu.addMenu(menu1)
            item4=menu.addAction('标记为喜欢')
            menu2=QMenu()
            menu2.setTitle('添加到歌单')
            menu.addMenu(menu2)
            menu3=QMenu()
            menu34 = QMenu()
            menu35 = QMenu()
            menu36 = QMenu()
            menu3.addMenu(menu34)
            menu3.addMenu(menu35)
            menu3.addMenu(menu36)
            menu.addMenu(menu3)
            menu3.setTitle('添加同')
            menu34.setTitle('歌手到')
            menu35.setTitle('专辑到')
            menu36.setTitle('文件夹到')
            menu4 = QMenu()
            menu.addMenu(menu4)
            menu4.setTitle('删除同')
            item41=menu4.addAction('歌手')
            item42=menu4.addAction('专辑')
            item43=menu4.addAction('文件夹')
            pls, pls34, pls35, pls36 = [], [menu34.addAction('like')], [menu35.addAction('like')],[menu36.addAction('like')]
            for x in self.all['playlist'].keys():
                pls.append(menu2.addAction(x))
                pls34.append(menu34.addAction(x))
                pls35.append(menu35.addAction(x))
                pls36.append(menu36.addAction(x))
            item5=menu.addAction('删除')
            item6=menu.addAction('在文件管理器中打开')
            action=menu.exec_(self.ml.mapToGlobal(pos))
            if action==item1:  #播放
                self.dmlf()
            elif action==item2:  #暂停
                mixer.music.pause()
                self.timer1.stop()
                self.boxc.setText('暂停')
                self.timesec.stop()
            elif action==item3:#下一曲
                self.test()
            elif action in modes:
                self.all['playmode']=m[modes.index(action)]
                self.musicmode.setText(self.all['playmode'])
            elif self.box2.isCheckable():#播放列表下
                self.operatorlist(action,self.all['musiclist'], pls, pls34, pls35, pls36, item4, item41, item42, item43,item5,item6)
            elif self.box1.isCheckable():
                self.operatorlist(action, self.all['allmusic'], pls, pls34, pls35, pls36, item4, item41, item42,item43,item5,item6)
            elif self.mlabel.text() in self.all['playlist'].keys():
                self.operatorlist(action, self.all['playlist'][self.mlabel.text()], pls, pls34, pls35, pls36, item4, item41, item42,item43,item5,item6)
            elif self.mlabel.text()=='like':
                self.operatorlist(action,self.all['like'], pls, pls34, pls35, pls36, item4,item41, item42,item43, item5,item6)
    def operatorlist(self,action,list,pls,pls34,pls35,pls36,item4,item41,item42,item43,item5,item6):
        ti = tinytag.TinyTag.get(list[self.ml.currentRow()])  # 音乐的所有信息全包括在内了
        parents = pa.Path(list[self.ml.currentRow()]).parent
        #print(action)
        if action in pls: #添加到指定歌单
            if list[self.ml.currentRow()] not in self.all['playlist'][self.playlist[pls.index(action)]]:
                self.all['playlist'][self.playlist[pls.index(action)]].append(
                    list[self.ml.currentRow()])
                print(self.all['playlist'])
        elif action in pls34:
            for x in list:
                tx = tinytag.TinyTag.get(x)
                if tx.artist == ti.artist and pls34.index(action) == 0 and x not in self.all['like']:
                    self.all['like'].insert(0, x)
                elif tx.artist == ti.artist and pls34.index(action) != 0 and x not in self.all['playlist'][self.playlist[pls34.index(action) - 1]]:
                    self.all['playlist'][self.playlist[pls34.index(action) - 1]].insert(0, x)
        elif action in pls35:
            for x in list:
                tx = tinytag.TinyTag.get(x)
                if tx.album == ti.album and pls35.index(action) == 0 and x not in self.all['like']:
                    self.all['like'].insert(0, x)
                elif tx.album == ti.album  and pls34.index(action) != 0 and x not in self.all['playlist'][self.playlist[pls35.index(action) - 1]]:
                    self.all['playlist'][self.playlist[pls35.index(action) - 1]].insert(0, x)
        elif action in pls36:
            for x in list:
                par = pa.Path(x).parent
                if par == parents and pls36.index(action) == 0 and x not in self.all['like']:
                    self.all['like'].insert(0, x)
                elif par == parents  and pls34.index(action) != 0 and x not in self.all['playlist'][self.playlist[pls36.index(action) - 1]]:
                    self.all['playlist'][self.playlist[pls36.index(action) - 1]].insert(0, x)
        elif action == item4:  # add to like
            if list[self.ml.currentRow()] not in self.all['like']:
                self.all['like'].append(list[self.ml.currentRow()])
                print(self.all['like'])
        elif action == item41:  ##????
            for x in list:
                tx = tinytag.TinyTag.get(x)
                if tx.artist == ti.artist:
                    list.remove(x)
        elif action == item42:
            for x in list:
                tx = tinytag.TinyTag.get(x)
                if tx.album == ti.album:
                    list.remove(x)
        elif action == item43:
            for x in list:
                par = pa.Path(x).parent
                if par == parents:
                    list.remove(x)
        elif action==item5:
            list.pop(self.ml.currentRow())
        elif action == item6:
            file = QFileDialog()
            name=file.getOpenFileName(self, 'open file',str(parents),"Music file(*.mp3 *.flac)")
            #print(name[0])
            #self.playmusic(name[0])
            #file.setFileMode(QFileDialog.AnyFile)
        self.musiclist(list)
    def addtolikef(self):
        if  self.all['playingmusic'] not in self.all['like']:
            self.all['like'].insert(0,self.all['playingmusic'])
            self.addtolike.setText('★')
        elif self.all['playingmusic']  in self.all['like']:
            self.all['like'].remove(self.all['playingmusic'])
            self.addtolike.setText('☆')
        if self.mlabel.text()=='like':
            self.musiclist(self.all['like'])
    def playmusic(self,filename,start=0):  #播放
            ting=mixer.music.load(filename)
            info=tinytag.TinyTag.get(filename)
            mixer.music.play(start=start)
            self.musicname.setText(str(pa.Path(filename).stem))
            self.musicsec.setText(str(int(info.duration)//60)+':'+str(int(info.duration)%60))
            self.timer1.start(int((info.duration-start)*1000))
            self.ml.selectRow(self.all['musiclist'].index(filename))
            self.boxc.setText('正在播放')
            self.all['playingmusic']=filename
            self.sec=start
            self.all['musicsec']=int(info.duration)
            self.timesec.start(1000)
            self.control.setMaximum(int(info.duration))
            self.control.setValue(start)
            print(self.all['playhistory'])
    def test(self):#下一曲
        if self.all['playmode']=='顺序播放':
            if self.all['playingmusic']!=self.all['musiclist'][-1]:
                file=self.all['musiclist'][self.all['musiclist'].index(self.all['playingmusic'])+1]
                #self.ml.setSelection()
        elif self.all['playmode']== '列表循环':
            file = self.all['musiclist'][self.all['musiclist'].index(self.all['playingmusic']) + 1]
        elif self.all['playmode'] == '单曲循环':
            file=self.all['playingmusic']
        else:
            file=self.all['musiclist'][numpy.random.randint(len(self.all['musiclist']))]
            print(file)
        self.playmusic(file)
    def last(self):  #上一曲
        if self.all['playmode']=='随机播放':
            file = self.all['musiclist'][numpy.random.randint(len(self.all['musiclist']))]
        else:
            file=self.all['musiclist'][self.all['musiclist'].index(self.all['playingmusic'])-1]
        self.playmusic(file)
    def dmlf(self):  #双击播放列表
        if self.box1.isCheckable() and not self.box2.isCheckable():
            self.all['musiclist'] = self.all['allmusic']
        elif not self.box1.isCheckable() and not self.box2.isCheckable():
            if self.mlabel.text()=='like':
                self.all['musiclist'] = self.all['like']
            else:
                self.all['musiclist'] = self.all['playlist'][self.mlabel.text()]
        #print(self.all['musiclist'])
        self.playmusic(self.all['musiclist'][self.ml.currentRow()])
    def dplf(self):
        if self.box2.isEnabled():
            if self.box1.isCheckable():
                self.layv_h2_v2_h1.removeWidget(self.box1_1)
                self.layv_h2_v2_h1.removeWidget(self.box1_2)
                sip.delete(self.box1_1)
                sip.delete(self.box1_2)
            self.box1.setText('本地列表')
            self.box2.setText('播放列表')
            self.box1.setCheckable(False)
            self.box2.setCheckable(False)
            if self.pl.currentRow() != 0:
                self.mlabel.setText(self.playlist[self.pl.currentRow()-1])
                self.musiclist(self.all['playlist'][self.playlist[self.pl.currentRow()-1]])
            else:
                self.mlabel.setText('like')
                self.musiclist(self.all['like'])
    def timesecf(self):
        self.sec+=1
        self.timelc.setText(str(self.sec // 60) + ':' + str(self.sec % 60))
        self.control.setValue(self.sec)
        if self.all['playingmusic'] in self.all['like']:
            self.addtolike.setText('★')
        else:
            self.addtolike.setText('☆')
        if self.sec==int(self.all['musicsec']/2):
            if self.all['playingmusic'] in self.all['playhistory']:
                self.all['playhistory'][self.all['playingmusic']]+=1
            else:
                self.all['playhistory'][self.all['playingmusic']]=1
    def boxlf(self):
        if self.all['playingmusic']!='' :
            #print(self.all['pla'])
            self.last()
    def boxcf(self) :
        if  self.boxc.text()=='播放':
            if self.all['playingmusic']!='':
                self.playmusic(self.all['playingmusic'],start=self.all['playingtime'])
            elif len(self.all['musiclist'])!=0:
                self.playmusic(self.musiclist[0])
        elif self.boxc.text()=='暂停':
            #self.playmusic(self.all['playingmusic'],start=self.sec)
            mixer.music.unpause()
            self.boxc.setText('正在播放')
            self.timesec.start(1000)
            self.timer1.start((self.all['musicsec']-self.sec)*1000)
        elif self.boxc.text()=='正在播放':
            self.timer1.stop()
            self.timesec.stop()
            mixer.music.pause()
            self.boxc.setText('暂停')
    def boxrf(self):
        if self.all['playingmusic'] != '':
            self.test()
    def controlf(self):
        self.playmusic(self.all['playingmusic'],start=self.control.value())
    def volchange(self):
        mixer.music.set_volume(float(self.boxvol.value())/100)
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initt()
    def initt(self):
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.save_quit)

        seta = QAction( '&Setting', self)
        seta.setStatusTip('设置')
        seta.triggered.connect(self.test)

        themea = QAction('&Theme', self)
        themea.setStatusTip('主题选择')
        # exitAction.triggered.connect(qApp.quit)
        usera = QAction('&User', self)
        usera.setStatusTip('个人中心')
        # exitAction.triggered.connect(qApp.quit)
        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(seta)
        self.toolbar.addAction(themea)
        self.toolbar.addAction(usera)
        la=QLabel()
        self.resize(800,600)  #500  400
        screen=QDesktopWidget().screenGeometry()
        size=self.geometry()
        self.move((screen.width()-size.width())/2,(screen.height()-size.height())/2)
        self.lay = ttt(self)
        self.lay.move(0,50)
        self.lay.resize(size.width(),size.height())
        self.setWindowTitle('音乐播放器')
        # self.show()
    def closeEvent(self,event):#关闭事件，(event!!!)
        self.save()
        event.accept()
    def save(self):
        print('exit')
        self.lay.all['playlist']=self.lay.plist
        self.lay.all['playingtime']=self.lay.sec
        self.lay.all['volume']=mixer.music.get_volume()
        print(self.lay.all)
        print(self.lay.savefilename)
        with open(self.lay.savefilename, 'w',encoding='gbk') as f:
            json.dump(self.lay.all, f)
            # self.all = {'like': [], 'playlist': {}, 'musiclist': [], 'playmode': 'mode 4', 'playingmusic': '','playingtime': 0}
            #like[]   playlist{}  playmode str   musiclist  []  playingmusic  str  playingtime  int   ,playhistory {}  playingsec?
            # 喜欢音乐列表，歌单，播放列表，播放模式，正在播放的音乐，已经播放的时间
    def save_quit(self):
        self.save()
        qApp.quit()
    def resizeEvent(self, evt):
        #print(self.lay.geometry())
        size = self.geometry()
        self.lay.resize(size.width(), size.height()-50)
        self.lay.ml.setMinimumSize( size.width()-300, size.height()-210)
        self.lay.pl.setMinimumHeight(size.height()-210)
    def test(self):
        print('test')

class DisplayThread(QThread):
    trigger = pyqtSignal(str)
    def __int__(self):
        super(DisplayThread, self).__init__()
    def run(self):
        try:
            # # 循环完毕后发出信号
            self.trigger.emit("success!")
        except Exception as e:
            self.trigger.emit("fail!")

class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r',  encoding='UTF-8') as file:
            return file.read()


if __name__ == "__main__":
    #print(sys.argv)
    style_file = 'destopPetInteraction/SpyBot.qss'
    style_sheet = QSSLoader.read_qss_file(style_file)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.setStyleSheet(style_sheet)
    window.show()
    sys.exit(app.exec_())
