import sys
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from decimal import Decimal, ROUND_FLOOR
from functools import partial

# 시작화면
class SetupWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.file_data = []
        self.result_window = None
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

    # 파일 업로드 및 테이블 반영
    def FileOpen(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*);;Text Files (*.txt)", options=options)

        if files:
            new_files = [file for file in files if file not in self.file_data]
            self.file_data.extend(new_files)

            current_row_count = self.table.rowCount()
            self.table.setRowCount(current_row_count + len(new_files))

            for i, file in enumerate(new_files, start=current_row_count):
                delete_button = QPushButton('삭제', self)
                delete_button.clicked.connect(self.LayerDelete)
                self.table.setCellWidget(i, 0, delete_button)
                self.table.setItem(i, 1, QTableWidgetItem(f'Layer {i + 1}'))
                self.table.setItem(i, 2, QTableWidgetItem(file.split('/')[-1]))

                self.AddNewPage(file)

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

        self.file_table.addTab(text_edit, f.split('/')[-1])

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
            if self.table.cellWidget(row,0) == sender:
                file_name = self.table.item(row,2).text()
                self.table.removeRow(row)
                del self.file_data[row]

                for index in range(self.file_table.count()):
                    if self.file_table.tabText(index) == file_name:
                        self.file_table.removeTab(index)
                        break


            self.table.setItem(row, 1, QTableWidgetItem('Layer' + str(row + 1)))

    #layer 방향 선택(text)
    def Direction(self, index):
        if index == 1:
            current_text = self.table.horizontalHeaderItem(index).text()
            if current_text == '▼':
                self.table.horizontalHeaderItem(index).setText('▲')
            else:
                self.table.horizontalHeaderItem(index).setText('▼')

    def LayerSort(self, index):
        if index == 1:  # 두 번째 열 클릭 시만 작동
            # 현재 테이블 데이터를 추출하여 리스트로 저장
            data = []
            for row in range(self.table.rowCount()):
                row_data = self.table.item(row, 2).text()
                data.append(row_data)

            new_data = data[::-1]
            self.file_data.reverse()

            for row, value in enumerate(new_data):
                self.table.setItem(row, 2, QTableWidgetItem(value))

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

        self.all_frequency_btn = QPushButton('전체 주파수', self)
        self.all_frequency_btn.clicked.connect(self.AllFrequency)
        self.all_frequency_btn.setMinimumHeight(60)
        self.all_frequency_btn.setMinimumWidth(100)

    # 주파수 찾기
    def SearchFrequency(self):
        try:
            freq_input = Decimal(self.frequency_input.text().strip())
            if freq_input.as_tuple().exponent == 0:
                freq_input_trimmed = freq_input.quantize(Decimal('0'), rounding=ROUND_FLOOR)
                precision = Decimal('0')
            else:
                freq_input_trimmed = freq_input.quantize(Decimal('0.0'), rounding=ROUND_FLOOR)
                precision = Decimal('0.0')
        except (ValueError, ArithmeticError):
            QMessageBox.warning(self, "오류", "유효한 숫자를 입력하세요.")
            return

        found = False
        self.output_table.setRowCount(0)

        for path, content in self.file_cache.items():
            for line in content:
                columns = line.strip().split()
                if len(columns) > 1:
                    try:
                        file_freq = Decimal(columns[0])
                        file_freq_trimmed = file_freq.quantize(precision, rounding=ROUND_FLOOR)
                        if file_freq_trimmed == freq_input_trimmed:
                            if not found:
                                self.real_input.setText(columns[1])
                                self.imaginary_input.setText(columns[2])
                                found = True

                            row_position = self.output_table.rowCount()
                            self.output_table.insertRow(row_position)
                            self.output_table.setItem(row_position, 0, QTableWidgetItem(columns[0]))
                            self.output_table.setItem(row_position, 1, QTableWidgetItem(columns[1]))
                            self.output_table.setItem(row_position, 2, QTableWidgetItem(columns[2]))
                    except (ValueError, ArithmeticError):
                        continue

        if not found:
            self.real_input.setText(" ")
            self.imaginary_input.setText(" ")
            QMessageBox.information(self, "결과", "해당 주파수를 찾을 수 없습니다.")

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
            file_path, _ = QFileDialog.getSaveFileName(self, "Excel 파일로 저장", "", "Excel Files (*.xlsx);;All Files (*)",
                                                       options=options)

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

    def AllFrequency(self):
        self.output_table.setRowCount(0)
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

        for _, freq, real, imag in data:
            row_position = self.output_table.rowCount()
            self.output_table.insertRow(row_position)
            self.output_table.setItem(row_position, 0, QTableWidgetItem(freq))
            self.output_table.setItem(row_position, 1, QTableWidgetItem(real))
            self.output_table.setItem(row_position, 2, QTableWidgetItem(imag))


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

        layout4 = QVBoxLayout()
        layout4.addLayout(layout1)
        layout4.addLayout(layout2)
        layout4.addLayout(layout3)
        layout4.addWidget(self.output_header)
        layout4.addWidget(self.output_table)

        self.setLayout(layout4)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = SetupWindow()
   sys.exit(app.exec_())