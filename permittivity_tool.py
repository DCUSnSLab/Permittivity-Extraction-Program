import sys
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from decimal import Decimal, ROUND_FLOOR

# 시작화면
class SetupWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.file_data = []
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
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['▼', '업로드된 파일'])
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
            self.table.setRowCount(len(files))
            self.file_data = []

            for i, file in enumerate(files):
                self.file_data.append(file)
                self.table.setItem(i, 0, QTableWidgetItem('Layer'+ str(i+1)))
                self.table.setItem(i, 1, QTableWidgetItem(file.split('/')[-1]))

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

        self.file_table.addTab(text_edit, f.split('/')[-1])

    #layer 방향 선택(text)
    def Direction(self, index):
        if index == 0:
            current_text = self.table.horizontalHeaderItem(index).text()
            if current_text == '▼':
                self.table.horizontalHeaderItem(index).setText('▲')
            else:
                self.table.horizontalHeaderItem(index).setText('▼')

    def LayerSort(self, index):
        if index == 0:  # 두 번째 열 클릭 시만 작동
            # 현재 테이블 데이터를 추출하여 리스트로 저장
            data = []
            for row in range(self.table.rowCount()):
                row_data = self.table.item(row, 1).text()
                data.append(row_data)

            new_data = data[::-1]
            be_file_data = self.file_data
            self.file_data = be_file_data[::-1]

            for row, value in enumerate(new_data):
                self.table.setItem(row, 1, QTableWidgetItem(value))

    def Start(self):
        self.hide()
        self.result = ResultWindow(file_paths=self.file_data)
        self.result.resize(self.size())
        self.result.show()

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
    def __init__(self, file_paths=None):
        super().__init__()
        self.file_paths = file_paths
        self.file_cache = {}
        self.initUI()
        self.SetupUi()
        self.Setup()

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
        for path in self.file_paths:
            if path in self.file_cache:
                content = self.file_cache[path]
                for line in content:
                    columns = line.strip().split()
                    if len(columns) > 2:
                        try:
                            frequency = Decimal(columns[0])
                            data.append((frequency, columns[0], columns[1], columns[2]))
                        except (ValueError, ArithmeticError):
                            continue

        self.output_table.setRowCount(0)

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
        self.info_header.setMaximumWidth(890)
        self.info_header.setMinimumWidth(790)
        self.info_header.setStyleSheet("background-color: #E8E8E8;")

        self.info_header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

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
        self.frequency_input.returnPressed.connect(self.SearchAndDisplayResults)

        self.ghz_label = QLabel('GHz')

        self.real = QLabel('Real')
        self.real.setAlignment(Qt.AlignCenter)
        self.real.setMinimumHeight(20)
        self.real.setMaximumHeight(40)
        self.real.setMaximumWidth(310)
        self.real.setMinimumWidth(90)
        self.real.setStyleSheet("background-color: #E8E8E8;")

        self.real_input = QLineEdit()
        self.real_input.setMinimumHeight(20)
        self.real_input.setMaximumHeight(40)
        self.real_input.setMinimumWidth(90)
        self.real_input.setMaximumWidth(290)
        self.real_input.setStyleSheet("background-color: white")
        self.real_input.returnPressed.connect(self.SearchAndDisplayResults)

        self.imaginary = QLabel('Imaginary')
        self.imaginary.setAlignment(Qt.AlignCenter)
        self.imaginary.setMinimumHeight(20)
        self.imaginary.setMaximumHeight(40)
        self.imaginary.setMaximumWidth(310)
        self.imaginary.setMinimumWidth(90)
        self.imaginary.setStyleSheet("background-color: #E8E8E8;")

        self.imaginary_input = QLineEdit()
        self.imaginary_input.setMinimumHeight(20)
        self.imaginary_input.setMaximumHeight(40)
        self.imaginary_input.setMinimumWidth(90)
        self.imaginary_input.setMaximumWidth(290)
        self.imaginary_input.setStyleSheet("background-color: white")
        self.imaginary_input.returnPressed.connect(self.SearchAndDisplayResults)

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

        self.check_box1 = QCheckBox('frequency', self)
        self.check_box2 = QCheckBox('real', self)
        self.check_box3 = QCheckBox('imaginary', self)

    def SearchFrequency(self):
        if not self.check_box1.isChecked():
            return []

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
            return []

        results = []
        for path, content in self.file_cache.items():
            for line in content:
                columns = line.strip().split()
                if len(columns) > 1:
                    try:
                        file_freq = Decimal(columns[0])
                        if file_freq.quantize(precision, rounding=ROUND_FLOOR) == freq_input_trimmed:
                            results.append((columns[0], columns[1], columns[2]))
                    except (ValueError, ArithmeticError):
                        continue
        return results

    def SearchReal(self):
        if not self.check_box2.isChecked():
            return []

        try:
            real_value = Decimal(self.real_input.text().strip())
            if real_value.as_tuple().exponent == 0:
                real_value_trimmed = real_value.quantize(Decimal('0'), rounding=ROUND_FLOOR)
                precision = Decimal('0')
            elif real_value.as_tuple().exponent == -1:
                real_value_trimmed = real_value.quantize(Decimal('0.0'), rounding=ROUND_FLOOR)
                precision = Decimal('0.0')
            else:
                real_value_trimmed = real_value.quantize(Decimal('0.00'), rounding=ROUND_FLOOR)
                precision = Decimal('0.00')
        except (ValueError, ArithmeticError):
            QMessageBox.warning(self, "오류", "유효한 숫자를 입력하세요.")
            return []

        results = []
        for path, content in self.file_cache.items():
            for line in content:
                columns = line.strip().split()
                if len(columns) > 2:
                    try:
                        file_real = Decimal(columns[1])
                        if file_real.quantize(precision, rounding=ROUND_FLOOR) == real_value_trimmed:
                            results.append((columns[0], columns[1], columns[2]))
                    except (ValueError, ArithmeticError):
                        continue
        return results

    def SearchImaginary(self):
        if not self.check_box3.isChecked():
            return []

        try:
            imaginary_value = Decimal(self.imaginary_input.text().strip()) / Decimal(100)
            precision = Decimal('0.000')

            imaginary_value_trimmed = imaginary_value.quantize(precision, rounding=ROUND_FLOOR)
        except (ValueError, ArithmeticError):
            QMessageBox.warning(self, "오류", "유효한 숫자를 입력하세요.")
            return []

        results = []
        for path, content in self.file_cache.items():
            for line in content:
                columns = line.strip().split()
                if len(columns) > 2:
                    try:
                        file_imaginary = Decimal(columns[2])
                        if file_imaginary.quantize(precision, rounding=ROUND_FLOOR) == imaginary_value_trimmed:
                            results.append((columns[0], columns[1], columns[2]))
                    except (ValueError, ArithmeticError):
                        continue
        return results

    def SearchAndDisplayResults(self):
        if not (self.check_box1.isChecked() or self.check_box2.isChecked() or self.check_box3.isChecked()):
            QMessageBox.warning(self, "오류", "검색을 원하는 박스에 체크해주세요.")
            return

        frequency_results = self.SearchFrequency() if self.check_box1.isChecked() else None
        real_results = self.SearchReal() if self.check_box2.isChecked() else None
        imaginary_results = self.SearchImaginary() if self.check_box3.isChecked() else None

        if frequency_results is not None and real_results is not None and imaginary_results is not None:
            intersected_results = [result for result in frequency_results if result in real_results and result in imaginary_results]
        elif frequency_results is not None and real_results is not None:
            intersected_results = [result for result in frequency_results if result in real_results]
        elif frequency_results is not None and imaginary_results is not None:
            intersected_results = [result for result in frequency_results if result in imaginary_results]
        elif real_results is not None and imaginary_results is not None:
            intersected_results = [result for result in real_results if result in imaginary_results]
        else:
            intersected_results = frequency_results or real_results or imaginary_results

        self.DisplayResults(intersected_results)

    def DisplayResults(self, results):
        self.output_table.setRowCount(0)
        if results:
            for result in results:
                row_position = self.output_table.rowCount()
                self.output_table.insertRow(row_position)
                self.output_table.setItem(row_position, 0, QTableWidgetItem(result[0]))
                self.output_table.setItem(row_position, 1, QTableWidgetItem(result[1]))
                self.output_table.setItem(row_position, 2, QTableWidgetItem(result[2]))

    def Back(self):
        self.hide()
        self.start = SetupWindow()
        self.start.file_data = []
        self.start.table.setRowCount(0)
        self.start.file_table.clear()
        self.start.resize(self.size())
        self.start.move(self.pos())
        self.start.show()

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
            file_path, _ = QFileDialog.getSaveFileName(self, "텍스트 파일로 저장", "", "Text Files (*.txt);;All Files (*)", options=options)

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

        check_input_layout = QVBoxLayout()
        check_input_layout.addWidget(self.check_box1)
        check_input_layout.addWidget(self.check_box2)
        check_input_layout.addWidget(self.check_box3)

        check_box = QGroupBox()
        check_box.setLayout(check_input_layout)
        check_box.setStyleSheet("background-color: #E8E8E8")
        freq_box.setMinimumWidth(150)
        freq_box.setMaximumWidth(450)
        freq_box.setMaximumHeight(60)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.frequency)
        layout2.addWidget(freq_box)
        layout2.addWidget(check_box, alignment=Qt.AlignLeft)
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