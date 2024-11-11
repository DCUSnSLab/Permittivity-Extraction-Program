import sys
from PyQt5.QtWidgets import *


class SetupWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.SetupUi()
        self.Setup()

    def initUI(self):
        self.setWindowTitle('유전율 추출 프로그램')
        self.show() # 화면 크기에 맞춰 자동 조절

    def SetupUi(self):
        # 파일 업로드 버튼
        self.FileOpenBtn = QPushButton('파일 업로드', self)
        self.FileOpenBtn.clicked.connect(self.FileOpen)
        self.FileOpenBtn.setMinimumHeight(70)
        self.FileOpenBtn.setMaximumWidth(300)

        # 파일 테이블
        self.Table = QTableWidget(self)
        self.Table.setColumnCount(2)
        self.Table.setHorizontalHeaderLabels(['Layer', '파일 이름'])
        self.Table.setMinimumWidth(1000)

        # 시작 버튼
        self.StartBtn = QPushButton('시작', self)
        self.StartBtn.clicked.connect(self.Start)
        self.StartBtn.setMinimumHeight(60)
        self.StartBtn.setMinimumWidth(300)

        #파일 위젯


    # 파일 업로드 및 테이블 반영
    def FileOpen(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*);;Text Files (*.txt)", options=options)

        if files:
            self.Table.setRowCount(len(files))

            for i, file in enumerate(files):
                filename = file.split('/')[-1]
                self.Table.setItem(i, 0, QTableWidgetItem('Layer'+ str(i+1)))
                self.Table.setItem(i, 1, QTableWidgetItem(filename))

    def Start(self):
        self.hide()
        self.result = ResultWindow()
        self.result.showMaximized()

    def Setup(self):
        layout1 = QHBoxLayout()
        layout1.addWidget(self.Table)
        layout1.addWidget(self.StartBtn)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.FileOpenBtn)
        layout2.addLayout(layout1)

        self.setLayout(layout2)
class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('My First Application')
        self.move(300, 300)
        self.resize(400, 200)
        self.show()

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = SetupWindow()
   sys.exit(app.exec_())