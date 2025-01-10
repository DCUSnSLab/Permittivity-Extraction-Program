import sys
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from decimal import Decimal, ROUND_FLOOR

import numpy as np
from scipy.constants import pi
from cmath import cos, sin, sqrt

# 시작화면
class SetupWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.result_window = None
        self.file_a = []
        self.file_data = {}
        self.initUI()
        self.SetupUi()
        self.Setup()

    def initUI(self):
        self.setWindowTitle('Permittivity Extraction Program')

        pixmap1 = QPixmap('SL.png')
        self.la_img1 = QLabel()
        self.la_img1.setPixmap(pixmap1)

        pixmap2 = QPixmap('DCU.png')
        self.la_img2 = QLabel()
        self.la_img2.setPixmap(pixmap2)
        self.show()

    def SetupUi(self):
        # 파일 업로드 버튼
        self.file_open_btn = QPushButton('파일 업로드', self)
        self.file_open_btn.clicked.connect(self.FileOpen)
        self.file_open_btn.setMinimumHeight(60)
        self.file_open_btn.setMaximumWidth(300)

        # 파일 테이블
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['전체삭제','▼', '업로드된 파일'])
        self.table.horizontalHeader().sectionClicked.connect(self.AllDelete)
        self.table.horizontalHeader().sectionClicked.connect(self.Direction) # layer 방향 조절(text)
        self.table.horizontalHeader().sectionClicked.connect(self.LayerSort) # layer 방향 조절
        self.table.horizontalHeader().setStretchLastSection(True) # 가장 뒤에 있는 열을 끝까지 공간 채우기
        self.table.setSelectionMode(QTableWidget.NoSelection) # 헤더 클릭 시 내용 클릭x
        self.table.setMaximumHeight(600)
        self.table.setMaximumWidth(2500)

        # 시작 버튼
        self.start_btn = QPushButton('시작', self)
        self.start_btn.clicked.connect(self.Start)
        self.start_btn.setMinimumHeight(60)
        self.start_btn.setMinimumWidth(100)

        #파일 위젯
        self.file_table = QTabWidget(self)
        self.file_table.setTabPosition(QTabWidget.North)
        self.file_table.setStyleSheet("QTabBar::tab { Height: 40px; width: 180px; }")

    def FileOpen(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*);;Text Files (*.txt)", options=options)

        if files:
            for file in files:
                if file not in self.file_data:
                    self.file_data[file] = None
                    self.AddFileToTable(file)

    def AddFileToTable(self, file):
        current_row_count = self.table.rowCount()
        self.table.setRowCount(current_row_count + 1)

        # 삭제 버튼 추가
        delete_button = QPushButton('삭제', self)
        delete_button.clicked.connect(self.LayerDelete)
        self.table.setCellWidget(current_row_count, 0, delete_button)
        self.table.setItem(current_row_count, 1, QTableWidgetItem(f'Layer {current_row_count + 1}'))
        self.table.setItem(current_row_count, 2, QTableWidgetItem(file.split('/')[-1]))

        self.AddNewPage(file)

    def AddNewPage(self, file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                contents = f.read()
                self.file_data[file] = contents
        except Exception as e:
            QMessageBox.warning(self, "오류", f"파일 읽기 중 문제가 발생했습니다: {e}")
            return

        # 내용 표시를 위한 QTextEdit 추가
        text_edit = QTextEdit()
        text_edit.setText(contents)
        text_edit.setReadOnly(True)

        self.file_table.addTab(text_edit, file.split('/')[-1])

    #layer 전체 삭제
    def AllDelete(self, index):
        if index == 0:
            self.table.setRowCount(0)
            self.table.horizontalHeaderItem(1).setText('▼')
            if len(self.file_table) != 0:
                while len(self.file_table) != 0:
                    self.file_table.removeTab(0)
            self.file_data.clear()

    #layer 개별 삭제
    def LayerDelete(self):
        sender = self.sender()
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 0) == sender:
                file_name = self.table.item(row, 2).text()
                file_path = [key for key, value in self.file_data.items() if file_name in key]

                if file_path:
                    del self.file_data[file_path[0]]

                self.table.removeRow(row)

                for index in range(self.file_table.count()):
                    if self.file_table.tabText(index) == file_name:
                        self.file_table.removeTab(index)
                        break

                break

    #layer 방향 선택(text)
    def Direction(self, index):
        if index == 1:
            current_text = self.table.horizontalHeaderItem(index).text()
            if current_text == '▼':
                self.table.horizontalHeaderItem(index).setText('▲')
            else:
                self.table.horizontalHeaderItem(index).setText('▼')

    def LayerSort(self, index):
        if index == 1:
            current_keys = list(self.file_data.keys())
            sorted_keys = current_keys[::-1]

            self.file_data = {key: self.file_data[key] for key in sorted_keys}

            self.table.setRowCount(0)
            for file in sorted_keys:
                current_row_count = self.table.rowCount()
                self.table.setRowCount(current_row_count + 1)

                delete_button = QPushButton('삭제', self)
                delete_button.clicked.connect(self.LayerDelete)
                self.table.setCellWidget(current_row_count, 0, delete_button)
                self.table.setItem(current_row_count, 1, QTableWidgetItem(f'Layer {current_row_count + 1}'))
                self.table.setItem(current_row_count, 2, QTableWidgetItem(file.split('/')[-1]))

    def Start(self):
        self.result_window = ResultWindow(file_paths=self.file_data, setup_window=self)
        self.hide()
        self.result_window.resize(self.size())
        self.result_window.show()

    # gui 위치 조정
    def Setup(self):
        layout1 = QHBoxLayout()
        layout1.addWidget(self.file_open_btn)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout1.addItem(spacer)
        layout1.addWidget(self.la_img2, alignment=Qt.AlignRight)
        layout1.addWidget(self.la_img1, alignment=Qt.AlignRight)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.table)
        layout2.addWidget(self.start_btn, alignment=Qt.AlignBottom)

        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addWidget(self.file_table)

        self.setLayout(layout)

# 결과화면
class ResultWindow(QWidget):
    def __init__(self, file_paths=None, setup_window=None):
        super().__init__()
        self.file_paths = file_paths
        self.file_cache = {}
        self.setup_window = setup_window
        self.initUI()
        self.SetupUi()
        self.Setup()

        self.LoadFileData()

    def LoadFileData(self):
        self.file_cache.clear()

        if self.file_paths:
            for path in self.file_paths:
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        self.file_cache[path] = file.readlines()
                except Exception as e:
                    print(f"파일 읽기 오류: {path} - {e}")

            self.DisplayAllData()

    def DisplayAllData(self):
        data = []
        for path, content in self.file_cache.items():
            for line in content:
                columns = line.strip().split()
                if len(columns) > 2:
                    try:
                        frequency = Decimal(columns[0])
                        data.append((frequency, columns[0], columns[1], columns[2]))
                    except (ValueError, ArithmeticError):
                        continue

        data.sort(key=lambda x: x[0])

        self.output_table.setRowCount(0)  # 테이블 초기화
        for _, freq, real, imag in data:
            row_position = self.output_table.rowCount()
            self.output_table.insertRow(row_position)
            self.output_table.setItem(row_position, 0, QTableWidgetItem(freq))
            self.output_table.setItem(row_position, 1, QTableWidgetItem(real))
            self.output_table.setItem(row_position, 2, QTableWidgetItem(imag))


    def initUI(self):
        self.setWindowTitle('Permittivity Extraction Program')
        pixmap1 = QPixmap('SL.png')
        self.la_img1 = QLabel()
        self.la_img1.setPixmap(pixmap1)

        pixmap2 = QPixmap('DCU.png')
        self.la_img2 = QLabel()
        self.la_img2.setPixmap(pixmap2)

    def SetupUi(self):
        self.info_header = QLabel('정보')
        self.info_header.setAlignment(Qt.AlignCenter)
        self.info_header.setMinimumHeight(40)
        self.info_header.setMaximumHeight(60)
        self.info_header.setMaximumWidth(800)
        self.info_header.setMinimumWidth(760)
        self.info_header.setStyleSheet("background-color: #E8E8E8;")

        self.frequency = QLabel('주파수 설정')
        self.frequency.setAlignment(Qt.AlignCenter)
        self.frequency.setMinimumHeight(40)
        self.frequency.setMaximumHeight(60)
        self.frequency.setMinimumWidth(150)
        self.frequency.setMaximumWidth(300)
        self.frequency.setStyleSheet("background-color: #E8E8E8;")

        self.frequency_input = QLineEdit()
        self.frequency_input.setMinimumHeight(20)
        self.frequency_input.setMaximumHeight(40)
        self.frequency_input.setMinimumWidth(150)
        self.frequency_input.setMaximumWidth(450)
        self.frequency_input.setStyleSheet("background-color: white")
        self.frequency_input.returnPressed.connect(self.SearchFrequency)

        self.ghz_label = QLabel('GHz')

        self.real = QLabel('Real')
        self.real.setAlignment(Qt.AlignCenter)
        self.real.setMinimumHeight(20)
        self.real.setMaximumHeight(40)
        self.real.setMaximumWidth(300)
        self.real.setMinimumWidth(110)
        self.real.setStyleSheet("background-color: #E8E8E8;")

        self.real_input = QLabel()
        self.real_input.setMinimumHeight(20)
        self.real_input.setMaximumHeight(40)
        self.real_input.setMinimumWidth(250)
        self.real_input.setMaximumWidth(290)
        self.real_input.setStyleSheet("background-color: white")

        self.imaginary = QLabel('Imaginary')
        self.imaginary.setAlignment(Qt.AlignCenter)
        self.imaginary.setMinimumHeight(20)
        self.imaginary.setMaximumHeight(40)
        self.imaginary.setMaximumWidth(300)
        self.imaginary.setMinimumWidth(120)
        self.imaginary.setStyleSheet("background-color: #E8E8E8;")

        self.imaginary_input = QLabel()
        self.imaginary_input.setMinimumHeight(20)
        self.imaginary_input.setMaximumHeight(40)
        self.imaginary_input.setMinimumWidth(250)
        self.imaginary_input.setMaximumWidth(290)
        self.imaginary_input.setStyleSheet("background-color: white")

        self.back_btn = QPushButton('뒤로', self)
        self.back_btn.clicked.connect(self.Back)
        self.back_btn.setMinimumHeight(60)
        self.back_btn.setMinimumWidth(100)

        self.save_excel_btn = QPushButton('Excel로 저장', self)
        self.save_excel_btn.clicked.connect(self.SaveExcel)
        self.save_excel_btn.setMinimumHeight(60)
        self.save_excel_btn.setMinimumWidth(100)

        self.save_txt_btn = QPushButton('txt로 저장', self)
        self.save_txt_btn.clicked.connect(self.SaveTxt)
        self.save_txt_btn.setMinimumHeight(60)
        self.save_txt_btn.setMinimumWidth(100)

        self.output_header = QLabel('출력데이터')
        self.output_header.setAlignment(Qt.AlignCenter)
        self.output_header.setStyleSheet("background-color: #E8E8E8;")
        self.output_header.setMinimumHeight(50)

        self.output_table = QTableWidget()
        self.output_table.setColumnCount(3)
        self.output_table.setHorizontalHeaderLabels(['Frequency [GHz]', 'Real', 'Imaginary'])
        self.output_table.setSelectionMode(QTableWidget.NoSelection)
        self.output_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.synthesis1 = QLabel('합성행렬')
        self.synthesis1.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.synthesis1.setMinimumHeight(100)
        self.synthesis1.setMinimumWidth(700)
        self.synthesis1.setStyleSheet("border: 1px solid black; background-color: white; font-size: 20px;")
        self.synthesis1.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.synthesis2 = QLabel('합성유전율')
        self.synthesis2.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.synthesis2.setMinimumHeight(100)
        self.synthesis2.setMinimumWidth(700)
        self.synthesis2.setStyleSheet("border: 1px solid black; background-color: white; font-size: 20px;")
        self.synthesis2.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.all_frequency_btn = QPushButton('전체 주파수', self)
        self.all_frequency_btn.clicked.connect(self.AllFrequency)
        self.all_frequency_btn.setMinimumHeight(60)
        self.all_frequency_btn.setMinimumWidth(100)

    def calculator(self, data_f):
        f = 76.51 * 10**9
        lam = (3 * 10**8) / f
        z0 = 367.73
        m = []
        m_total = np.array([[1, 0], [0, 1]])
        d_total = 0

        row_position = self.output_table.rowCount()

        for i in range(len(data_f)):
            er = data_f[i][0]
            ei = data_f[i][1]
            d0 = data_f[i][2]

            th = d0 * 10 ** (-3)

            k1 = ((2 * pi) / lam) * sqrt(er - ei * 1j)
            p1 = k1 * th
            z1 = z0 * sqrt(1 / (er - ei * 1j))

            a1 = cos(p1)
            b1 = z1 * sin(p1) * 1j
            c1 = (sin(p1) * 1j) / z1
            d1 = cos(p1)
            m0 = np.array([[a1, b1], [c1, d1]])
            m_total = m_total @ m0

            d_total = d_total + th

            a_total = m_total[0,0]
            e_total = ( ( lam / (2*pi) ) * ( np.arccos(a_total) / d_total) )**2

            er_total = e_total.real
            ei_total = e_total.imag

            self.output_table.insertRow(row_position)
            self.output_table.setItem(row_position, 0, QTableWidgetItem(f"{data_f[i][3]}"))
            self.output_table.setItem(row_position, 1, QTableWidgetItem(str(er_total)))
            self.output_table.setItem(row_position, 2, QTableWidgetItem(str(ei_total)))
            row_position += 1

            self.output_table.resizeRowsToContents()
            self.output_table.resizeColumnsToContents()

        return m_total, e_total

    # 주파수 찾기
    def SearchFrequency(self):
        try:
            freq_input = Decimal(self.frequency_input.text().strip())
        except (ValueError, ArithmeticError):
            QMessageBox.warning(self, "오류", "유효한 숫자를 입력하세요.")
            return

        self.output_table.setRowCount(0)
        self.freq_cal = []

        for file_path, content in self.file_cache.items():
            closest_freq = None
            closest_row = None
            min_diff = Decimal('Infinity')
            thickness = None

            for line in content:
                columns = line.strip().split()
                try:
                    if "!thickness" in line:
                        thickness = float(line.strip().split("=")[1])
                        continue

                    file_freq = Decimal(columns[0])
                    diff = abs(file_freq - freq_input)
                    if diff < min_diff:
                        min_diff = diff
                        closest_freq = file_freq
                        closest_row = columns
                except (ValueError, ArithmeticError):
                    continue

            if closest_row and thickness is not None:
                input_dd = [float(closest_row[1]), float(closest_row[2]), thickness, float(closest_row[0])]
                self.freq_cal.append(input_dd)

        closest_real, closest_imag = None, None
        min_diff = float('inf')
        for real, imag, _, freq in self.freq_cal:
            diff = abs(freq - float(freq_input))
            if diff < min_diff:
                min_diff = diff
                closest_real = real
                closest_imag = imag
                self.real_input.setText(f"{closest_real}")
                self.imaginary_input.setText(f"{closest_imag}")

        m_total, e_total= self.calculator(self.freq_cal)
        self.synthesis1.setText(f"합성행렬\n\n{m_total}")
        self.synthesis2.setText(f"합성유전율\n\n{e_total}")

    def Back(self):
        self.hide()
        self.setup_window.resize(self.size())
        self.setup_window.show()

    def SaveExcel(self):
        if self.output_table.rowCount() > 0:
            data = []
            for row in range(self.output_table.rowCount()):
                row_data = []
                for column in range(self.output_table.columnCount()):
                    item = self.output_table.item(row, column)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            df = pd.DataFrame(data, columns=['Frequency [GHz]', 'Real', 'Imaginary'])

            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Excel 파일로 저장", "", "Excel Files (*.xlsx);;All Files (*)", options=options)

            if file_path:
                try:
                    df.to_excel(file_path, index=False, engine='openpyxl')
                    QMessageBox.information(self, "성공", "데이터가 Excel 파일로 저장되었습니다.")
                except Exception as e:
                    QMessageBox.warning(self, "오류", f"Excel 파일 저장 중 오류가 발생했습니다: {e}")
        else:
            QMessageBox.warning(self, "오류", "저장할 출력 데이터가 없습니다.")

    def SaveTxt(self):
        if self.output_table.rowCount() > 0:
            data = []

            headers = [self.output_table.horizontalHeaderItem(column).text() for column in range(self.output_table.columnCount())]
            data.append(" ".join(headers))

            for row in range(self.output_table.rowCount()):
                row_data = []
                for column in range(self.output_table.columnCount()):
                    item = self.output_table.item(row, column)
                    row_data.append(item.text() if item else "")
                data.append(" ".join(row_data))

            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "텍스트 파일로 저장", "", "Text Files (*.txt);;All Files (*)",options=options)

            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        for line in data:
                            file.write(line + '\n')
                    QMessageBox.information(self, "성공", "데이터가 txt 파일로 저장되었습니다.")
                except Exception as e:
                    QMessageBox.warning(self, "오류", f"txt 파일 저장 중 오류가 발생했습니다: {e}")
        else:
            QMessageBox.warning(self, "오류", "저장할 출력 데이터가 없습니다.")

    # 전체 주파수 출력
    def AllFrequency(self):
        self.output_table.setRowCount(0)
        self.all_frequencies = {}

        for path, content in self.file_cache.items():
            file_data = []
            thickness = None

            for line in content:
                columns = line.strip().split()
                try:
                    if "!thickness" in line:
                        thickness = float(line.strip().split("=")[1])
                        continue

                    if len(columns) > 2:
                        frequency = Decimal(columns[0])
                        real = float(columns[1])
                        imag = float(columns[2])

                        file_data.append((real, imag, thickness, float(frequency)))

                except (ValueError, ArithmeticError):
                    continue

            self.all_frequencies[path] = file_data

        m_total, e_total= self.calculator(file_data)
        self.real_input.setText(f" ")
        self.imaginary_input.setText(f" ")
        self.synthesis1.setText(f"합성행렬\n\n{m_total}")
        self.synthesis2.setText(f"합성유전율\n\n{e_total}")

    def Setup(self):
        layout1 = QHBoxLayout()
        layout1.addWidget(self.info_header)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout1.addItem(spacer)
        layout1.addWidget(self.la_img2, alignment=Qt.AlignRight)
        layout1.addWidget(self.la_img1, alignment=Qt.AlignRight)

        freq_input_layout = QHBoxLayout()
        freq_input_layout.addWidget(self.frequency_input, alignment=Qt.AlignLeft)
        freq_input_layout.addWidget(self.ghz_label, alignment=Qt.AlignLeft)

        freq_box = QGroupBox()
        freq_box.setLayout(freq_input_layout)
        freq_box.setStyleSheet("background-color: #E8E8E8")
        freq_box.setMinimumWidth(100)
        freq_box.setMaximumWidth(450)
        freq_box.setMaximumHeight(40)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.frequency)
        layout2.addWidget(freq_box)
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout2.addItem(spacer)
        layout2.addWidget(self.all_frequency_btn, alignment=Qt.AlignRight)
        layout2.addWidget(self.back_btn, alignment=Qt.AlignRight)

        layout3 = QHBoxLayout()
        layout3.addWidget(self.real)
        layout3.addWidget(self.real_input)
        layout3.addWidget(self.imaginary)
        layout3.addWidget(self.imaginary_input)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout3.addItem(spacer)

        layout3.addWidget(self.save_excel_btn, alignment=Qt.AlignRight)
        layout3.addWidget(self.save_txt_btn, alignment=Qt.AlignRight)

        synthesis_layout = QVBoxLayout()
        synthesis_layout.addWidget(self.synthesis1)
        synthesis_layout.addWidget(self.synthesis2)

        result = QHBoxLayout()
        result.addWidget(self.output_table)
        result.addLayout(synthesis_layout)

        layout4 = QVBoxLayout()
        layout4.addLayout(layout1)
        layout4.addLayout(layout2)
        layout4.addLayout(layout3)
        layout4.addWidget(self.output_header)
        layout4.addLayout(result)

        self.setLayout(layout4)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = SetupWindow()
   sys.exit(app.exec_())