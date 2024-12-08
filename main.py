import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMenu
from PyQt6.QtGui import QAction

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

        # Верхняя часть с таблицами и полем для ввода кода
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        # Левая часть с таблицами
        left_layout = QVBoxLayout()
        top_layout.addLayout(left_layout)

        tables = ["Служебные слова", "Разделители", "Числа", "Идентификаторы"]
        self.tables = []
        for table_name in tables:
            table = QTableWidget(5, 2)
            table.setHorizontalHeaderLabels(["Ключ", "Значение"])
            left_layout.addWidget(QLabel(table_name))
            left_layout.addWidget(table)
            self.tables.append(table)

        # Центральная часть с полем для ввода кода
        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("Введите исходный текст...")
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
            [("if", "условие"), ("else", "иначе"), ("while", "пока"), ("for", "для"), ("return", "вернуть")],
            [(";", "точка с запятой"), (",", "запятая"), ("(", "открывающая скобка"), (")", "закрывающая скобка"), ("{", "открывающая фигурная скобка")],
            [("1", "один"), ("2", "два"), ("3", "три"), ("4", "четыре"), ("5", "пять")],
            [("x", "переменная"), ("y", "переменная"), ("z", "переменная"), ("a", "переменная"), ("b", "переменная")]
        ]

        for i, table in enumerate(self.tables):
            for j, (key, value) in enumerate(data[i]):
                table.setItem(j, 0, QTableWidgetItem(key))
                table.setItem(j, 1, QTableWidgetItem(value))

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
