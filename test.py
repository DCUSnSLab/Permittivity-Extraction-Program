import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5.QtCore import Qt


class Main(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.SetupUi()
        self.Setup()

    def initUI(self):
        self.setWindowTitle('유전율 추출 프로그램')
        self.setGeometry(100, 100, 800, 600)

    def SetupUi(self):
        self.FileOpenBtn = QPushButton('파일 업로드', self)
        self.FileOpenBtn.clicked.connect(self.FileOpen)
        self.FileOpenBtn.setFixedHeight(90)

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['계층', '업로드된 파일'])
        self.table.setSortingEnabled(True)  # 테이블 정렬 기능 활성화

    def FileOpen(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*);;Text Files (*.txt)", options=options)

        if files:
            self.table.setRowCount(len(files))

            for i, file in enumerate(files):
                filename = file.split('/')[-1]  # 파일 이름 추출
                self.table.setItem(i, 0, QTableWidgetItem(f'Layer {i + 1}'))
                self.table.setItem(i, 1, QTableWidgetItem(filename))

    def Setup(self):
        layout = QVBoxLayout()
        layout.addWidget(self.FileOpenBtn)
        layout.addWidget(self.table)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
