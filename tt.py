from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QFileDialog
import sys

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # QTabWidget 생성
        self.tabs = QTabWidget()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # 파일 추가 버튼
        self.load_button = QPushButton('Load File', self)
        self.load_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_button)

        self.setWindowTitle('Dynamic Page Addition')
        self.resize(800, 600)

    def load_file(self):
        # 파일 다이얼로그를 통해 파일 선택
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*);;CSV Files (*.csv)', options=options)

        if file_name:
            self.add_new_page(file_name)

    def add_new_page(self, file_name):
        # 새로운 테이블 위젯 생성
        table = QTableWidget()
        table.setRowCount(5)  # 예시로 임의의 데이터 추가
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['Column 1', 'Column 2', 'Column 3'])

        for row in range(5):
            for col in range(3):
                item = QTableWidgetItem(f"Data {row}, {col}")
                table.setItem(row, col, item)

        # 새 탭에 테이블 추가
        self.tabs.addTab(table, f"Page {self.tabs.count() + 1}: {file_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
