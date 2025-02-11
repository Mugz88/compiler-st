import sys
import os
from time import sleep
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMenu
from PyQt6.QtGui import QAction
from compiler import compile
from scanner import SymbolTableManager, mainScanner
from grammer import mainGrammar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Анализатор кода")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Кнопка для отображения тестов
        self.test_button = QPushButton("Тесты")
        self.test_button.clicked.connect(self.show_tests)
        main_layout.addWidget(self.test_button)

        # Кнопка для запуска анализа
        self.run_button = QPushButton("Запуск")
        self.run_button.clicked.connect(self.run_analysis)
        main_layout.addWidget(self.run_button)

        self.run_button = QPushButton("Сканер")
        self.run_button.clicked.connect(self.run_scanner)
        main_layout.addWidget(self.run_button)

        # Верхняя часть с таблицами и полем для ввода кода
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        # Левая часть с таблицами
        left_layout = QVBoxLayout()
        top_layout.addLayout(left_layout)

        tables = ["Служебные слова", "Разделители", "Числа", "Идентификаторы"]
        self.tables = []
        for table_name in tables:
            table = QTableWidget(25, 1)  # Увеличиваем количество строк
            table.setHorizontalHeaderLabels(["Значение"])
            left_layout.addWidget(QLabel(table_name))
            left_layout.addWidget(table)
            self.tables.append(table)

        # Центральная часть с полем для ввода кода
        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("Введите исходный текст...")
        self.code_input.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)  # Отключение переноса строк
        top_layout.addWidget(self.code_input)

        # Правая часть с полем для отображения результата анализа
        right_layout = QVBoxLayout()
        top_layout.addLayout(right_layout)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Результат анализа...")
        right_layout.addWidget(self.result_output)

        # Нижняя часть с полем для отображения результата анализа
        self.bottom_result_output = QTextEdit()
        self.bottom_result_output.setReadOnly(True)
        self.bottom_result_output.setPlaceholderText("Результат анализа...")
        main_layout.addWidget(self.bottom_result_output)

        # Заполнение данных
        self.fill_tables()

    def fill_tables(self):
        # Пример данных для таблиц
        data = [
            ["end", "dim", "integer", "real", "boolean", "if", "then", "else", "for", "to", "do", "while", "read", "write", "true", "false"],
            ["NE", "EQ", "LT", "LE", "GT", "GE", "plus", "min", "or", "mult", "div", "and", "~", "+", "-", "as", ":", "{", "}", "(", ")", ".", ","],
            ["1", "2", "3", "4", "5"],
            ["x", "y", "z", "a", "b"]
        ]

        for i, table in enumerate(self.tables):
            for j, value in enumerate(data[i]):
                table.setItem(j, 0, QTableWidgetItem(value))

    def show_tests(self):
        # Создание всплывающего меню с названиями тестов
        menu = QMenu(self)
        tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
        for test_folder in os.listdir(tests_dir):
            if os.path.isdir(os.path.join(tests_dir, test_folder)):
                action = QAction(test_folder, self)
                action.triggered.connect(lambda checked, folder=test_folder: self.load_test(folder))
                menu.addAction(action)

        # Отображение всплывающего меню
        menu.exec(self.test_button.mapToGlobal(self.test_button.rect().bottomLeft()))

    def load_test(self, test_folder):
        # Загрузка файлов теста
        tests_dir = os.path.join(os.path.dirname(__file__), 'tests', test_folder)

        # Загрузка input.txt
        input_path = os.path.join(tests_dir, 'input.txt')
        if os.path.exists(input_path):
            with open(input_path, 'r') as file:
                self.code_input.setPlainText(file.read())

        # Загрузка semantic_errors.txt и syntax_errors.txt
        result_text = ""
        semantic_errors_path = os.path.join(tests_dir, 'semantic_errors.txt')
        syntax_errors_path = os.path.join(tests_dir, 'syntax_errors.txt')

        if os.path.exists(semantic_errors_path):
            with open(semantic_errors_path, 'r') as file:
                result_text += "Semantic Errors:\n" + file.read() + "\n"

        if os.path.exists(syntax_errors_path):
            with open(syntax_errors_path, 'r') as file:
                result_text += "Syntax Errors:\n" + file.read() + "\n"

        self.bottom_result_output.setPlainText(result_text)

    def run_analysis(self):
        # Создание файла main.txt и сохранение текста из поля для ввода кода
        code = self.code_input.toPlainText()
        source_file = os.path.join(os.path.dirname(__file__), 'main.txt')
        with open(source_file, 'w') as file:
            file.write(code)

        # Запуск функции compile с путем к файлу main.txt
        nums, ids = mainGrammar()
        #self.result_output.setPlainText(result)
        tokens_file = os.path.join(os.path.dirname(__file__), 'output', 'tokens.txt')
        if os.path.exists(tokens_file):
            with open(tokens_file, 'r') as file:
                tokens_content = file.read()
            self.result_output.setPlainText(tokens_content)
        else:
            self.result_output.setPlainText("Файл tokens.txt не найден.")

        self.combined_errors_content = ""   
        
        lex_errors_file = os.path.join(os.path.dirname(__file__), 'errors', 'lexical_errors.txt')
        if os.path.exists(lex_errors_file):
            with open(lex_errors_file, 'r') as file:
                self.combined_errors_content += file.read()
        else:
            self.combined_errors_content += "Файл lexical_errors.txt не найден.\n"

        # Read and accumulate syntax errors
        syn_errors_file = os.path.join(os.path.dirname(__file__), 'errors', 'syntax_errors.txt')
        if os.path.exists(syn_errors_file):
            with open(syn_errors_file, 'r') as file:
                self.combined_errors_content += file.read() + "\n"
        else:
            self.combined_errors_content += "Файл syntax_errors.txt не найден.\n"

        # Read and accumulate semantic errors
        sem_errors_file = os.path.join(os.path.dirname(__file__), 'errors', 'semantic_errors.txt')
        if os.path.exists(sem_errors_file):
            with open(sem_errors_file, 'r') as file:
                self.combined_errors_content += file.read() + "\n"
        else:
            self.combined_errors_content += "Файл semantic_errors.txt не найден.\n"

        # Set the combined content to the output widget
        self.bottom_result_output.setPlainText(self.combined_errors_content)
        
        self.fill_table(self.tables[3], ids)  # Идентификаторы
        self.fill_table(self.tables[2], nums)  # Числа

    def run_scanner(self):
        # Создание файла main.txt и сохранение текста из поля для ввода кода
        code = self.code_input.toPlainText()
        source_file = os.path.join(os.path.dirname(__file__), 'main.txt')
        with open(source_file, 'w') as file:
            file.write(code)

        # Запуск функции compile с путем к файлу main.txt
        SymbolTableManager.init()
        mainScanner(source_file)
        sleep(1)
        tokens_file = os.path.join(os.path.dirname(__file__), 'output', 'tokens.txt')
        if os.path.exists(tokens_file):
            with open(tokens_file, 'r') as file:
                tokens_content = file.read()
            self.result_output.setPlainText(tokens_content)
        else:
            self.result_output.setPlainText("Файл tokens.txt не найден.")

        lex_erorrs_file = os.path.join(os.path.dirname(__file__), 'errors', 'lexical_errors.txt')
        if os.path.exists(lex_erorrs_file):
            with open(lex_erorrs_file, 'r') as file:
                erorrs_content = file.read()
            self.bottom_result_output.setPlainText(erorrs_content)
        else:
            self.bottom_result_output.setPlainText("Файл lexical_errors.txt не найден.")
            
    def fill_table(self, table, values):
        table.clearContents()
        for i, value in enumerate(values):
            table.setItem(i, 0, QTableWidgetItem(value))
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
