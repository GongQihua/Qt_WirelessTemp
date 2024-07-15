import sys, time, struct
import sqlite3

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHeaderView, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import Dialog, InfoBar, InfoBarIcon, InfoBarPosition
from Ui_login import Ui_Form1
from Mainpage1 import Ui_Form2

from pymodbus.client import ModbusTcpClient
import datetime
import numpy as np
import pandas as pd
from pyqtgraph.graphicsItems.DateAxisItem import DateAxisItem


class LoginWindow(FramelessWindow, Ui_Form1):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()
        self.resize(1260, 618)

        #居中显示
        #desktop = QApplication.desktop().availableGeometry()
        desktop = QApplication.instance().screens()[0].size()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

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
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.thread1 = Worker()
        self.thread1.result_signal.connect(self.slotAdd)
        self.thread2 = Date_worker("")
        self.is_recording = False

        self.model = None

        self.PrimaryToolButton.clicked.connect(self.button1_clicked)
        self.ToolButton.clicked.connect(self.button2_clicked)
        self.PrimaryPushButton.clicked.connect(self.start_recording)
        self.PushButton.clicked.connect(self.stop_recording)
        self.PrimaryPushButton_2.clicked.connect(self.load_data)
        self.ComboBox.clicked.connect(self.load_table_names)
        self.PrimaryToolButton_2.clicked.connect(self.export_data)

    def button1_clicked(self):
        client = ModbusTcpClient("127.0.0.1", "502")
        client.connect()
        if client.connect():
            print("Modbus RTU Client Connected")

            self.LineEdit_4.setText("3E97")
            self.LineEdit_7.setText("9R12")
            self.LineEdit_15.setText("4T54")
            self.LineEdit_18.setText("7A2B")

            self.LineEdit_6.setText("GOOD")
            self.LineEdit_9.setText("GOOD")
            self.LineEdit_14.setText("GOOD")
            self.LineEdit_17.setText("GOOD")

            self.createInfoInfoBar1()
            client.close()
            if not self.thread1.isRunning():
                self.thread1.start()
        else:
            print("Failed to connect to Modbus RTU Client")
            self.createWarning1()
            client.close()
            return

    def slotAdd(self, result):
        # 向列表控件中添加条目
        self.LineEdit_5.setText(f"{result[0] / 100}°")
        self.LineEdit_8.setText(f"{result[1] / 100}°")
        self.LineEdit_13.setText(f"{result[2] / 100}°")
        self.LineEdit_16.setText(f"{result[3] / 100}°")

    def button2_clicked(self):
        if self.thread1.isRunning():
            self.thread1.stop()
            self.thread1.wait()
        if not self.thread1.isRunning():
            self.LineEdit_5.clear()
            self.LineEdit_8.clear()
            self.LineEdit_13.clear()
            self.LineEdit_16.clear()

            self.LineEdit_4.clear()
            self.LineEdit_7.clear()
            self.LineEdit_15.clear()
            self.LineEdit_18.clear()

            self.LineEdit_6.clear()
            self.LineEdit_9.clear()
            self.LineEdit_14.clear()
            self.LineEdit_17.clear()

        self.createInfoInfoBar2()

    #消息弹窗
    def createInfoInfoBar1(self):
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title='Success',
            content="Real-Time Sensor Monitor On",
            orient=Qt.Vertical,  # vertical layout
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )
        w.show()

    def createWarning1(self):
        w = InfoBar(
            icon=InfoBarIcon.WARNING,
            title='Warning',
            content="Failed to connect to Modbus RTU Client",
            orient=Qt.Vertical,
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
            orient=Qt.Vertical,  # vertical layout
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )
        w.show()

    def start_recording(self):

        if self.is_recording:
            InfoBar.warning(
                title='Warning',
                content="Recording Already Started!",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                # position='Custom',   # NOTE: use custom info bar manager
                duration=5000,
                parent=self
            )
            return
        if self.PasswordLineEdit.text() != "123":
            self.createWarningInfoBar()
            return

        Batch_text = self.LineEdit.text()
        self.thread2 = Date_worker(Batch_text)
        self.thread2.start()
        self.is_recording = True
        print("Start Recording")
        self.createSuccessInfoBar()

    def stop_recording(self):
        if self.thread2.isRunning():
            self.thread2.stop()
            self.thread2.wait()
        self.is_recording = False
        print("Stop Recording")
        self.createStopInfoBar()

    def createSuccessInfoBar(self):
        # convenient class mothod
        InfoBar.success(
            title='Recording Start',
            content="Start Status Success",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration= 5000,
            parent=self
        )

    def createStopInfoBar(self):
        # convenient class mothod
        InfoBar.success(
            title='Recording Stop',
            content="Recording Stop Success",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration= 5000,
            parent=self
        )

    def createWarningInfoBar(self):
        InfoBar.warning(
            title='Warning',
            content="Recording Start Failed",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=5000,
            parent=self
        )

    def load_table_names(self):

        self.ComboBox.clear()

        db_name = QSqlDatabase.addDatabase("QSQLITE")
        db_name.setDatabaseName("Sensor_data.db")  # 替换为你的SQLite数据库文件名

        if not db_name.open():
            print("Database Error:", db_name.lastError().text())
            return

        # 获取数据库中的所有表名
        table_names = db_name.tables()

        # 过滤掉sqlite_sequence表
        filtered_table_names = [name for name in table_names if name != "sqlite_sequence"]

        # 添加表名到ComboBox
        self.ComboBox.addItems(filtered_table_names)
        self.ComboBox.setCurrentIndex(-1)

        db_name.close()

    def load_data(self):

        # 先清空
        self.TableView.setModel(None)
        self.model = None

        # 获取用户选择的表名
        table_name = self.ComboBox.currentText()

        # 设置数据库连接
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("Sensor_data.db")  # 替换为你的SQLite数据库文件名

        if not db.open():
            print("Database Error:", db.lastError().text())
            return

        # 设置模型
        self.model = QSqlTableModel(self, db)
        self.model.setTable(table_name)  # 替换为你的表名
        self.model.select()

        # 将模型设置到TableView中
        self.TableView.setModel(self.model)

        # 样式设置
        self.TableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.TableView.verticalHeader().setVisible(False)

        self.load_graph_data(table_name, db)

        #db.close()

    def load_graph_data(self, table_name, db):
        # Query to fetch data from the specified table
        query = QSqlQuery(db)
        query.prepare(f"SELECT * FROM {table_name}")
        if not query.exec_():
            print("Query Error:", query.lastError().text())
            return

        dates = []
        temp1 = []
        temp2 = []
        temp3 = []
        temp4 = []

        while query.next():
            date_str = query.value(1)
            try:
                date_time = datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
                dates.append(date_time.timestamp())
            except ValueError:
                print(f"Date format error: {date_str}")
                continue

            temp1.append(query.value(3))  # Assuming the fourth column is temperature
            temp2.append(query.value(4))  # Assuming the fifth column is temperature
            temp3.append(query.value(5))  # Assuming the sixth column is temperature
            temp4.append(query.value(6))  # Assuming the seventh column is temperature

            # Convert lists to numpy arrays
        dates = np.array(dates)
        temp1 = np.array(temp1, dtype=float)
        temp2 = np.array(temp2, dtype=float)
        temp3 = np.array(temp3, dtype=float)
        temp4 = np.array(temp4, dtype=float)

        # Plotting the graph
        self.plot_graph(dates, temp1, temp2, temp3, temp4)

        db.close()

    def plot_graph(self, dates, temp1, temp2, temp3, temp4):

        # Remove previous plot widgets if they exist
        layout = self.widget_10.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        # # Create a PlotWidget with DateAxisItem
        # date_axis = DateAxisItem(orientation='bottom')
        # plot_widget = PlotWidget(axisItems={'bottom': date_axis})

        # Create a PlotWidget with DateAxisItem
        self.plot_widget = PlotWidget(axisItems={'bottom': DateAxisItem(orientation='bottom')}, parent=self.widget_10)

        # Set the background color to white
        self.plot_widget.setBackground('w')

        # Add the PlotWidget to the layout
        if layout is None:
            layout = QVBoxLayout(self.widget_10)
            self.widget_10.setLayout(layout)
        layout.addWidget(self.plot_widget)

        # Plot data
        self.plot_widget.plot(x=dates, y=temp1, pen='r', name='Temperature 1')
        self.plot_widget.plot(x=dates, y=temp2, pen='g', name='Temperature 2')
        self.plot_widget.plot(x=dates, y=temp3, pen='b', name='Temperature 3')
        self.plot_widget.plot(x=dates, y=temp4, pen='m', name='Temperature 4')

        # Adding legend
        self.plot_widget.addLegend()

        # Set Style
        self.plot_widget.getAxis('left').setLabel('Temperature', units='°C')
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_widget.setTitle('Wireless Temp Curve')
        self.plot_widget.showGrid(x=True, y=True)

    def export_data(self):
        # 读取 TableView 中的数据
        model2 = self.TableView.model()
        if not model2:
            QMessageBox.warning(self, "错误", "未找到数据模型！")
            return

        # 将数据导出到 Excel 文件
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "Excel 文件 (*.xlsx)")
            if file_path:
                
                headers = []
                for column in range(model2.columnCount()):
                    header = model2.headerData(column, Qt.Horizontal)
                    headers.append(header)

                # 创建一个空的列表来保存数据
                data = []

                # 读取并添加数据
                for row in range(model2.rowCount()):
                    row_data = []
                    for column in range(model2.columnCount()):
                        index = model2.index(row, column)
                        value = model2.data(index)
                        row_data.append(value)
                    data.append(row_data)

                # 创建 DataFrame
                df = pd.DataFrame(data, columns=headers)

                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "成功", f"数据已成功导出到 {file_path}!")
            else:
                QMessageBox.warning(self, "警告", "未选择文件路径！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出数据时发生错误：{str(e)}")
            #print(str(e))


class Worker(QThread):
    result_signal = pyqtSignal(list)

    def __init__(self):
        # 初始化线程
        super(Worker, self).__init__()
        self.running = True

    def run(self):
        client = ModbusTcpClient("127.0.0.1", "502")
        client.connect()
        connection = True
        self.running = True
        while connection and self.running:
            result = client.read_holding_registers(0, 5, slave=1)
            # read_holding_registers读不出负值，得用struct转换一步
            signed_values = [struct.unpack('h', struct.pack('H', reg))[0] for reg in result.registers]
            #print(result.registers)
            #print(signed_values)
            self.result_signal.emit(signed_values)
            self.sleep(2)  # 读取延迟
        client.close()

    def stop(self):
        self.running = False


class Date_worker(QThread):

    def __init__(self, Batch_text):
        # 初始化线程
        super(Date_worker, self).__init__()
        self.data_text = Batch_text
        self.running = True

    def run(self):
        client2 = ModbusTcpClient("127.0.0.1", "502")
        client2.connect()

        conn = sqlite3.connect('Sensor_data.db')
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS batch{self.data_text} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Time TEXT NOT NULL,
                Batch TEXT NOT NULL,
                Sensor1 INTEGER NOT NULL,
                Sensor2 INTEGER NOT NULL,
                Sensor3 INTEGER NOT NULL,
                Sensor4 INTEGER NOT NULL
            )
        ''')

        self.running = True

        while client2.connected and self.running:
            dataset = client2.read_holding_registers(0, 4, slave=1)
            result_values = [struct.unpack('h', struct.pack('H', reg))[0] for reg in dataset.registers]
            timestamp = time.time()
            local_time = time.localtime(timestamp)
            current_time = time.strftime("%Y/%m/%d %H:%M:%S", local_time)
            cursor.execute(f'''
                   INSERT INTO batch{self.data_text} (Time, Batch, sensor1, sensor2, sensor3, sensor4)
                   VALUES (?, ?, ?, ?, ?, ?)
               ''', (
            current_time, self.data_text, result_values[0]/100, result_values[1]/100, result_values[2]/100, result_values[3]/100))

            self.sleep(5)

        conn.commit()
        conn.close()
        client2.close()

    def stop(self):
        self.running = False


if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = LoginWindow()
    w.show()
    app.exec()
