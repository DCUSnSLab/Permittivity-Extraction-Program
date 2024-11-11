import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

# 시작화면
class SetupWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.SetupUi()
        self.Setup()

    def initUI(self):
        self.setWindowTitle('Permittivity Extraction Program')
        pixmap = QPixmap('SL.png')
        self.la_img = QLabel()
        self.la_img.setPixmap(pixmap)
        self.show()

    def SetupUi(self):
        # 파일 업로드 버튼
        self.FileOpenBtn = QPushButton('파일 업로드', self)
        self.FileOpenBtn.clicked.connect(self.FileOpen)
        self.FileOpenBtn.setMinimumHeight(60)
        self.FileOpenBtn.setMaximumWidth(300)

        # 파일 테이블
        self.Table = QTableWidget(self)
        self.Table.setColumnCount(2)
        self.Table.setHorizontalHeaderLabels(['▼', '업로드된 파일'])
        self.Table.horizontalHeader().sectionClicked.connect(self.Direction) # layer 방향 조절(text)
        self.Table.horizontalHeader().sectionClicked.connect(self.LayerSort) # layer 방향 조절
        self.Table.horizontalHeader().setStretchLastSection(True) # 가장 뒤에 있는 열을 끝까지 공간 채우기
        self.Table.setSelectionMode(QTableWidget.NoSelection) # 헤더 클릭 시 내용 클릭x
        self.Table.setMaximumHeight(600)
        self.Table.setMaximumWidth(1500)

        # 시작 버튼
        self.StartBtn = QPushButton('시작', self)
        self.StartBtn.clicked.connect(self.Start)
        self.StartBtn.setMinimumHeight(60)
        self.StartBtn.setMinimumWidth(100)

        #파일 위젯
        self.FileTable = QTabWidget(self)


    # 파일 업로드 및 테이블 반영
    def FileOpen(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*);;Text Files (*.txt)", options=options)

        if files:
            self.Table.setRowCount(len(files))

            for i, file in enumerate(files):
                self.Table.setItem(i, 0, QTableWidgetItem('Layer'+ str(i+1)))
                self.Table.setItem(i, 1, QTableWidgetItem(file.split('/')[-1]))

            for f in files:
                self.AddNewPage(f)

    # 파일 내용 출력
    def AddNewPage(self, f):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                contents = file.read()
        except FileNotFoundError:
            print('파일이 존재하지 않거나 경로가 잘못되었습니다.')
            return
        except PermissionError:
            print('파일에 대한 접근 권한이 없습니다.')
            return
        except UnicodeDecodeError:
            print('파일의 인코딩이 맞지 않습니다.')
            return
        except IOError:
            print('파일 읽기 중 문제가 발생하였습니다.')
            return

        text_edit = QTextEdit()
        text_edit.setText(contents)
        text_edit.setReadOnly(True)

        self.FileTable.addTab(text_edit, f.split('/')[-1])

    #layer 방향 선택(text)
    def Direction(self, index):
        if index == 0:
            current_text = self.Table.horizontalHeaderItem(index).text()
            if current_text == '▼':
                self.Table.horizontalHeaderItem(index).setText('▲')
            else:
                self.Table.horizontalHeaderItem(index).setText('▼')

    def LayerSort(self, index):
        if index == 0:  # 두 번째 열 클릭 시만 작동
            # 현재 테이블 데이터를 추출하여 리스트로 저장
            data = []
            for row in range(self.Table.rowCount()):
                rowData = self.Table.item(row, 1).text()
                data.append(rowData)

            newData = data[::-1]

            for row, value in enumerate(newData):
                self.Table.setItem(row, 1, QTableWidgetItem(value))

    def Start(self):
        self.hide()
        self.result = ResultWindow()
        self.result.show()

    # gui 위치 조정
    def Setup(self):
        layout1 = QHBoxLayout()
        layout1.addWidget(self.FileOpenBtn)
        layout1.addWidget(self.la_img, alignment=Qt.AlignRight)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.Table)
        layout2.addWidget(self.StartBtn, alignment=Qt.AlignBottom)


        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addWidget(self.FileTable)

        self.setLayout(layout)

# 결과화면
class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.SetupUi()
        self.Setup()

    def initUI(self):
        self.setWindowTitle('Permittivity Extraction Program')
        pixmap = QPixmap('SL.png')
        self.la_img = QLabel()
        self.la_img.setPixmap(pixmap)

    def SetupUi(self):
        pass

    def Setup(self):
        pass

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = SetupWindow()
   sys.exit(app.exec_())