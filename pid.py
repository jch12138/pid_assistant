import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
from dialog import Ui_Dialog
import re
import time

class Pyqt5_Serial(QtWidgets.QWidget, Ui_Dialog):
    def __init__(self):
        super(Pyqt5_Serial, self).__init__()

        self.track_list = [
            "none",
            "center",
            "stop",
            "leftt",
            "rightt",
            "centerleft",
            "upbridge",
            "bridge",
            "wave",
            "seesaw",
            "round",
            "slow",
            "back"
        ]
        self.track_mode = 'none'
        self.setupUi(self)
        self.init()
        self.setWindowTitle("串口pid调试助手")
        self.ser = serial.Serial()
        self.rxBuff = ''
        self.pattern = re.compile(u'msh />show_parameter([\s\S]*)msh >')
        self.port_check()


    def init(self):
        # 串口检测按钮
        self.s1__box_1.clicked.connect(self.port_check)

        # 串口信息显示
        self.s1__box_2.currentTextChanged.connect(self.port_imf)

        self.comboBox.currentIndexChanged.connect(self.changmode)

        # 打开串口按钮
        self.open_button.clicked.connect(self.port_open)

        # 关闭串口按钮
        self.close_button.clicked.connect(self.port_close)

        self.comboBox.addItems(self.track_list)
        self.pushButton.clicked.connect(self.senddata)
        self.pushButton_12.clicked.connect(self.save_para)
        self.pushButton_2.clicked.connect(self.show_para)

        self.lineEdit.setText('0')
        self.lineEdit_2.setText('0')

        # 定时器接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)



    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1__box_2.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1__box_2.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.state_label.setText(" 无串口")

    # 串口信息
    def port_imf(self):
        # 显示选定的串口的详细信息
        imf_s = self.s1__box_2.currentText()
        if imf_s != "":
            self.state_label.setText(self.Com_Dict[self.s1__box_2.currentText()])

    # 打开串口
    def port_open(self):
        self.ser.port = self.s1__box_2.currentText()
        self.ser.baudrate = 115200
        self.ser.bytesize = 8
        self.ser.stopbits = 1
        self.ser.parity = 'N'

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None

        # 打开串口接收定时器，周期为2ms
        self.timer.start(1)

        if self.ser.isOpen():
            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.formGroupBox.setTitle("串口状态（已开启）")
            self.ser.write('\n'.encode('utf-8'))
            self.ser.write('show_parameter\n'.encode('utf-8'))

        # 关闭串口
    def save_para(self):
        self.ser.write('save_parameters\n'.encode('utf-8'))

    def show_para(self):
        self.ser.write('show_parameter\n'.encode('utf-8'))


    def port_close(self):
        self.timer.stop()
        try:
            self.ser.close()
        except:
            pass
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)
        self.lineEdit_3.setEnabled(True)
        self.formGroupBox.setTitle("串口状态（已关闭）")

    def parse_data(self,data):
        data = data.split()
        data = data[2:-4]
        data = [data[i] for i in range(2,len(data),3)]
        return data

    def changmode(self):
        self.track_mode  = self.comboBox.currentText()

    def senddata(self):
        kp = self.lineEdit.text()
        kd = self.lineEdit_2.text()
        sendbuffer = ('set {} {} {}\n'.format(self.track_list.index(self.track_mode),kp,kd)).encode('utf-8')
        self.ser.write(sendbuffer)
        time.sleep(0.1)
        self.ser.write('show_parameter\n'.encode('utf-8'))

    # 接收数据
    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0:
            data = self.ser.read(num).decode('utf-8')
            self.rxBuff += data
            if(self.pattern.search(self.rxBuff)):
                start,end= self.pattern.search(self.rxBuff).span()
                re_data = self.rxBuff[start:end]
                self.rxBuff = ''
            self.s2__receive_text.insertPlainText(data)
            # 获取到text光标
            textCursor = self.s2__receive_text.textCursor()
            # 滚动到底部
            textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
            self.s2__receive_text.setTextCursor(textCursor)
        else:
            pass


    def receive_data_clear(self):
        self.s2__receive_text.setText("")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    myshow.show()
    sys.exit(app.exec_())
