import cv2
import time
import win32gui
from PyQt5.QtWidgets import QMainWindow,QFileDialog,QLabel,QMessageBox,QApplication,QMenu,QAction,QSystemTrayIcon,QShortcut
from PyQt5.QtCore import QThread,QUrl,Qt,QCoreApplication
from PyQt5.QtGui import QImage, QPixmap,QIcon,QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer,QMediaContent,QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget

from gui import Ui_MainWindow
import image_rc

QICON = ":/xiaolingdang.jpg"

class Wallpaper():
    """主窗口类"""
    def __init__(self):
        self.path = ""
        self.w = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.w)
        self.initUI()

    def show(self):
        self.w.show()

    def initUI(self):
        QShortcut(QKeySequence(self.w.tr("Ctrl+Q")), self.w, self.quitApp)
        self.w.setWindowIcon(QIcon(QICON))
        self.ui.pushButton_3.clicked.connect(self.openfile)
        self.ui.pushButton.clicked.connect(self.setwallpaper)
        self.trayicon()

    def openfile(self):
        path, filetype = QFileDialog.getOpenFileName(None, "选择文件", '.',
                                                         "视频文件(*.AVI;*.mov;*.rmvb;*.rm;*.FLV;*.mp4;*.3GP)")  # ;;All Files (*)
        if not path:
            return
        self.path = path
        self.vidio = ReadVideo(path,self.w)
        self.vidio.start()

    def setwallpaper(self):
        if not self.path:
            self.messageDialog("请选取一个视频文件")
            return
        desktop = QApplication.desktop()
        screen_count = desktop.screenCount()

        for i in range(screen_count):
            h = self.gethandle()
            self.__setattr__("vidiowidget_"+str(i),VideoWidget())
            vidiowidget = self.__getattribute__("vidiowidget_"+str(i))
            vidiowidget.setGeometry(desktop.screenGeometry(i))
            # self.w.showFullScreen()
            vidiowidget.show()
            self.__setattr__("player_" + str(i), QMediaPlayer())
            player = self.__getattribute__("player_"+str(i))
            player.setNotifyInterval(10000)
            player.setMuted(bool(1 - player.isMuted()))
            player.setMedia(QMediaContent(QUrl(self.path)))
            player.setVideoOutput(vidiowidget)
            self.__setattr__("mplayList_" + str(i), QMediaPlaylist())
            mplayList = self.__getattribute__("mplayList_"+str(i))
            mplayList.addMedia(QMediaContent(QUrl.fromLocalFile(self.path)))
            player.setPlaylist(mplayList)
            mplayList.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
            # win32gui.SetParent(int(self.w.winId()),self.gethandle())
            # win32gui.SetParent(int(vidiowidget.winId()), self.gethandle())
            # win32gui.SetParent(int(vidiowidget.winId()), int(self.w.winId()))
            video_h = int(vidiowidget.winId())
            win_hwnd = int(self.w.winId())
            # win32gui.SetParent(win_hwnd, h)
            win32gui.SetParent(video_h, h)
            # win32gui.SetParent(video_h, win_hwnd)
            player.play()


    def gethandle(self):
        hwnd = win32gui.FindWindow("Progman", "Program Manager")
        a = win32gui.SendMessageTimeout(hwnd, 0x052C, 0, None, 0, 0x03E8)
        print("发送结果：",a)
        hwnd_WorkW = None
        while 1:
            hwnd_WorkW = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
            # print("hwnd_WorkW: ",hwnd_WorkW)
            if not hwnd_WorkW:
                continue
            hView = win32gui.FindWindowEx(hwnd_WorkW, None, "SHELLDLL_DefView", None)
            # print('hwmd_hView: ', hView)
            if not hView:#这个WorkerW下没有shell
                continue
            h = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
            while h:
                win32gui.SendMessage(h, 0x0010, 0, 0)  # WM_CLOSE
                h = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
            break
        return hwnd


    def messageDialog(self, msg):
        # 核心功能代码就两行，可以加到需要的地方
        msg_box = QMessageBox.warning(self.w, "警告", msg,QMessageBox.Yes)

    def quitApp(self):
        QCoreApplication.instance().quit()
        self.tp = None

    def trayicon(self):

        self.menu = QMenu(self.w)
        self.showAction1 = QAction("&退出", self.w, triggered=self.quitApp)
        self.menu.addAction(self.showAction1)
        self.tp = QSystemTrayIcon(self.w)
        self.menu.setStyleSheet("QMenu {background-color: white;border: 1px solid white;}" "QMenu::item {background-color: transparent;padding:8px 32px;margin:0px 8px;border-bottom:1px solid #DBDBDB;}" "QMenu::item:selected {background-color: #2dabf9;}")
        self.tp.setIcon(QIcon(QICON))
        self.tp.setContextMenu(self.menu)
        self.tp.setToolTip("动态壁纸")
        self.tp.show()


class ReadVideo(QThread):
    # signal_time = QtCore.pyqtSignal(str, int)  # 信号

    def __init__(self,path,parent=None):
        super(ReadVideo, self).__init__(parent)
        self.path = path
        self.w = parent

    def run(self):
        try:
            self.label = self.w.findChild(QLabel, "label_2")
            if self.path:
                self.cap = cv2.VideoCapture(self.path)
                while True:
                    self.showpic()
                    time.sleep(0.05)
        except:
            self.label.setText("视频出错")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            self.quit()

    def showpic(self):
        if (self.cap.isOpened()):
            ret, self.frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                # if self.detectFlag == True:
                #     # 检测代码self.frame
                #     self.label_num.setText("There are " + str(5) + " people.")
                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                q_image = QImage(frame.data, width, height, bytesPerLine,
                                 QImage.Format_RGB888).scaled(self.label.width(), self.label.height())
                self.label.setPixmap(QPixmap.fromImage(q_image))
            else:

                self.run()


class VideoWidget(QVideoWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
