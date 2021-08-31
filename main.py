# -*- coding: utf-8 -*-
"""一个设置视频成动态壁纸的工具
"""
__author__ = "zc"

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QLocalSocket,QLocalServer
from wallpaper import Wallpaper

if __name__ == '__main__':
    app = QApplication(sys.argv)
    serverName = 'wallpaper'
    socket = QLocalSocket()
    socket.connectToServer(serverName)
    # 如果连接成功，表明server已经存在，当前已有实例在运行
    if socket.waitForConnected(500):
        app.quit()
    else:
        localServer = QLocalServer()  # 没有实例运行，创建服务器
        localServer.listen(serverName)
        # 关闭所有窗口,也不关闭应用程序
        mes = Wallpaper()
        mes.show()
        sys.exit(app.exec_())
