import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import Dialog, InfoBar, InfoBarIcon, InfoBarPosition
from Ui_login import Ui_Form1
from Ui_mainpage import Ui_Form2

class LoginWindow(FramelessWindow, Ui_Form1):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()
        self.resize(1260,618)

        #居中显示
        #desktop = QApplication.desktop().availableGeometry()
        desktop = QApplication.instance().screens()[0].size()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        #button clicked
        self.PrimaryPushButton.clicked.connect(self.Login_Button)
    
    def Login_Button(self):
        user = self.LineEdit_2.text()
        password = self.PasswordLineEdit.text()
        if user == '1' and password == '1':
            print('login Successful')
            self.loginsuccess()
        else:
            self.showDialog()

    def showDialog(self):
        title = 'Login Failed'
        content = """Wrong Username or Password, Please Try Again."""
        w = Dialog(title, content, self)
        w.exec()
        # if w.exec():
        #     print('Yes button is pressed')
        # else:
        #     print('Cancel button is pressed')
    
    def loginsuccess(self):
        w.hide()
        w2 = MainWindow()
        w2.show()

class MainWindow(FramelessWindow, Ui_Form2):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()
        #self.resize(1024,768)

        #居中显示
        #desktop = QApplication.desktop().availableGeometry()
        desktop = QApplication.instance().screens()[0].size()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.PrimaryToolButton.clicked.connect(self.createInfoInfoBar1)
        self.ToolButton.clicked.connect(self.createInfoInfoBar2)
        self.CheckBox_2.stateChanged.connect(self.createSuccessInfoBar)

    #消息弹窗
    def createInfoInfoBar1(self):
        content = "Real-Time Sensor Monitor On"
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title='Success',
            content=content,
            orient=Qt.Vertical,    # vertical layout
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )
        w.show()

    def createInfoInfoBar2(self):
        content = "Real-Time Sensor Monitor Off"
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title='Success',
            content=content,
            orient=Qt.Vertical,    # vertical layout
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )
        w.show()

    def createSuccessInfoBar(self):
        # convenient class mothod
        InfoBar.success(
            title='Page2',
            content="Page2 Status Checked",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=-1,
            parent=self
        )

if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    w = LoginWindow()
    w.show()
    app.exec()