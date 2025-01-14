import os
import re

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script_dir = os.path.join(script_dir, "compiler-st")

print(script_dir)
class SymbolTableManager(object):
    ''' Управляет таблицей символов компилятора,
    которая используется в различных модулях '''
    _global_funcs = [{
        "lexim": "output",
        "scope": 0,
        "type": "void",
        "role": "function",
        "arity": 1,
        "params": ["int"]
    }]

    @classmethod
    def init(cls):
        ''' Инициализирует таблицу символов '''
        cls.scope_stack = [0]
        cls.temp_stack = [0]
        cls.arg_list_stack = []
        cls.symbol_table = cls._global_funcs.copy()
        cls.declaration_flag = False
        cls.error_flag = False

    @classmethod
    def scope(cls):
        ''' Возвращает текущий уровень области видимости '''
        return len(cls.scope_stack) - 1

    @classmethod
    def insert(cls, lexim):
        ''' Вставляет новый символ в таблицу символов '''
        cls.symbol_table.append({"lexim": lexim, "scope": cls.scope()})

    @classmethod
    def _exists(cls, lexim, scope):
        ''' Проверяет, существует ли символ в таблице символов '''
        for row in cls.symbol_table:
            if row["lexim"] == lexim and row["scope"] == scope:
                return True
        return False

    @classmethod
    def findrow(cls, value, attr="lexim"):
        ''' Находит строку в таблице символов по значению атрибута '''
        for i in range(len(cls.symbol_table) - 1, -1, -1):
            row = cls.symbol_table[i]
            if row[attr] == value:
                return row
        return None

    @classmethod
    def findrow_idx(cls, value, attr="lexim"):
        ''' Находит индекс строки в таблице символов по значению атрибута '''
        for i in range(len(cls.symbol_table) - 1, -1, -1):
            row = cls.symbol_table[i]
            if row[attr] == value:
                return i
        return None

    @classmethod
    def install_id(cls, lexim):
        ''' Устанавливает идентификатор для символа '''
        if not cls.declaration_flag:
            i = cls.findrow_idx(lexim)
            if i is not None:
                return i
        return len(cls.symbol_table)

    @classmethod
    def get_enclosing_fun(cls, level=1):
        ''' Возвращает охватывающую функцию на заданном уровне '''
        try:
            return cls.symbol_table[cls.scope_stack[-level] - 1]
        except IndexError:
            return None

char_to_col = {        # сокращения в DFA
    "WHITESPACE": 0,  # w
    "DIGIT": 1,      # d
    "LETTER": 2,     # l
    "*": 3,          # *
    "=": 4,          # =
    "SYMBOL": 5,     # s
    "#": 6,          # /
    "\n": 7,         # \n
    "OTHER": 8 ,     # o (Любой другой символ, допустимый только внутри блока комментариев) 
    "E": 9,
    "e": 10,
    "+": 11,
    "-": 12,
    ".": 13,


}

state_to_token = {
    1: "WHITESPACE",
    3: "NUM",
    6: "ID_OR_KEYWORD",
    10: "SYMBOL",
    11: "SYMBOL",
    12: "SYMBOL",
    16: "COMMENT",

 

    19: "WHITESPACE",
    21: "SYMBOL",

    23: "RAZD" ,
    24: "NUM exp" ,
    31: "Nbodh" ,


   
    

}

state_to_error_message = {
    4: "illegal number",
    8: "unmatched #",
    20: "invalid input",
    22: "invalid input", 
    50: "",
   
}

token_dfa = (
    # Input character types
    #   w     d     l     *     =     s     #    \n     o    E      e       +        -    .                                 всего 14 символов
    #   0     1     2     3     4     5     6     7     8    9      10      11      12      13
    (   1,    2,    5,    7,    9,   12,   14,   19,   20,   5,     5,      23 ,     23, 27 ), # State 0 (initial state)
    (   1, None, None, None, None, None, None,    1, None, None, None,  None,  None,  None), # State 1 (whitespace)
    (   3,    2,    24,    3,    3,    3,    3,    3, 4,   24, 24, 4,  4,27), # State 2 
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 3 (number)
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 4 (illegal number)
    (   6,    5,    5,    6,    6,    6,    6,    6,   20,   5,  5, 20, 20,20), # State 5 
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 6 (id or keyword)
    (  21,   21,   21,   21,   21,   21,    8,   21,   20), # State 7 хз что это
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 8 (unmatched */)
    (  11,   11,   11,   11,   10,   11,   11,   11,   20), # State 9 хз 
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 10 (symbol ==)
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 11 (symbol =)
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 12 (symbol)
    (  22,   22,   22,   14,   22,   22,   17,   22,   22,   22,   22,   22,   22,   22), # State 13
    (  14,   14,   14,   14,   14,   14,   16,   14,   14,   14,   14,   14,   14,   14), # State 14           
    (  14,   14,   14,   15,   14,   14,   16,   14,   14,   14,   14,   14,   14,   14), # State 15
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 16 (# comment #)
    (  17,   17,   17,   17,   17,   17,   17,   18,   17,   17,   17,   17,   17,   17), # State 17 
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 18 (// comment\n)
    (  19, None, None, None, None, None, None,   19, None, None, None, None, None, None), # State 19 (newline + whitespace)
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 20 (invalid input)
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 21 (symbol *)
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 22 (invalid comment)
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 23 RAZD
    (31, 2, 29, 4, 4, 4, 4, 31, 4, 4, 4, 25, 25,4), # State 24 NUM exp part
    (4, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,4), # State 25 NUM exp 
    (   3,    26,    4,    3,    3,    3,    3,    3,    4,  4, 4, 4,  4,4), # State 26 number exp 
    (   4,    28,    4,    3,    3,    3,    3,    3,    4,  4, 4, 4,  4,4), # State 27 number with .
    (   3,    28,    24,    3,    3,    3,    3,    3,    24,  24, 4, 4,  4,4), # State 28 number with .  end .
    (   31,    30,    29,    31,    31,    31,    31,    31,    29,  29, 4, 4,  4,4), # State 29 number HEx
    (   4,    30,    29,    4,    4,   4,    4,    4,    29,  29, 4, 4,  4,4), # State 30 number end dig
    ( None, None, None, None, None, None, None, None, None, None, None, None, None, None), # State 31 Nbodh


)

F = {1, 3, 6, 10, 11, 12, 16, 18, 19, 20, 21,23,31} # all accepting states
Fstar = {3, 6, 11, 21}                        # accepting states that require the last character to be returned to the input stream
unclosed_comment_states = {14, 15, 17}       

whitespaces = {' ', '\r', '\t', '\v', '\f'} # \n исключен, так как имеет специальное значение в однострочных комментариях

class Scanner(object):
    ''' Лексический анализатор, который токенизирует входной исходный файл
        в соответствии с лексической спецификацией C минус '''

    def __init__(self, input_file, chunk_size=8192, max_state_size=float("inf")):
        ''' Инициализирует сканер '''
        assert chunk_size >= 16, "Минимальный поддерживаемый размер чанка - 16!"
        if not os.path.isabs(input_file):
            input_file = os.path.join(script_dir, input_file)
        self.input_file = input_file
        print(self.input_file)
        self.line_number = 1
        self.first_line = 1
        self._lexical_errors = []
        self.tokens = {} # доступ к токенам по номеру строки
        self.tokens[self.line_number] = []
        self.max_state_size = max_state_size # сколько строк токенов мы хотим держать в памяти (по умолчанию: неограниченно)

        self.tokens_file = os.path.join(script_dir, "output", "tokens.txt")
        self.symbol_file = os.path.join(script_dir, "output", "symbol_table.txt")

        self.errors_file = os.path.join(script_dir, "errors", "lexical_errors.txt")

        self.chunk_size = chunk_size
        self.file_pointer = 0
        self.max_unclosed_comment_size = 15
        self.input = ""
        self.read_input()

        # лексическая спецификация
        self._symbols = {',', ';', ':', '(', ')', '{', '}','^','@','&','|','!'} # = и * исключены
        self.letters = {chr(i) for i in range(65, 91)} | {chr(i) for i in range(97, 123)}
        self.digits = {str(i) for i in range(0, 10)}
        self.symbols = self._symbols | {"*", "."}
        
        

        razd = [
            "NEQ",       # 0
            "EQV",       # 1
            "LOWT",      # 2
            "LOWE",      # 3
            "GRT",       # 4
            "GRE",       # 5
            "add",       # 6
            "disa",      # 7
            "||",        # 8
            "umn",       # 9
            "del",       # 10
            "&&",        # 11
            "^",         # 12
            "+",         # 13
            "-",         # 14
            "as",        # 15
            ":",         # 16
            "(",         # 17
            ")",         # 18
            ".",         # 19
            ",",         # 20
            ";",         # 21
            "#",         # 22
        ]
        self.identifiers = razd
        self.razd = set(razd)

        #
        keywords = [
            "begin",     # 0
            "end",       # 1
            "var",       # 2
            "if",        # 3
            "then",      # 4
            "else",      # 5
            "for",       # 6
            "to",        # 7
            "false",     # 8
            "do",        # 9
            "next",      # 10
            "read",      # 11
            "write",     # 12
            "while",     # 13
            "true",      # 14
            "@",      # 15
            "!",      # 16
            "&",      # 17
        ]
        self.identifiers = keywords
        self.keywords = set(keywords)

    @property
    def lexical_errors(self):
        ''' Возвращает строку с лексическими ошибками '''
        lexical_errors = []
        if self._lexical_errors:
            for lineno, lexim, error in self._lexical_errors:
                lexical_errors.append(f"#{lineno} : Lexical Error! '{lexim}' rejected, reason: {error}.\n")
        else:
            lexical_errors.append("There is no lexical errors.\n")
        return "".join(lexical_errors)

    def save_lexical_errors(self):
        ''' Сохраняет лексические ошибки в файл '''
        if self.max_state_size > 0:
            with open(self.errors_file, "w") as f:
                f.write(self.lexical_errors)

    def id_to_lexim(self, token_id):
        ''' Возвращает лексиму по идентификатору токена '''
        return SymbolTableManager.symbol_table[token_id]['lexim']

    def token_to_str(self, token):
        ''' Преобразует токен в строку '''
        if token[0] == "ID":
            return f"({token[0]}, {self.id_to_lexim(token[1])})"
        else:
            return "({}, {})".format(*token)

    def read_input(self):
        ''' Читает входной файл по чанкам '''
        with open(self.input_file, "rb") as f:
            f.seek(self.file_pointer)
            chunk = f.read(self.chunk_size)
        if not chunk:
            raise EOFError
        self.input += chunk.decode()
        self.file_pointer += self.chunk_size

    def _resolve_dfa_table_column(self, input_char):
        ''' Определяет столбец таблицы DFA для данного символа '''
        if input_char in whitespaces:
            return char_to_col["WHITESPACE"]
        if input_char in self.letters:
            return char_to_col["LETTER"]
        if input_char in self.digits:
            return char_to_col["DIGIT"]
        if input_char in self._symbols:
            return char_to_col["SYMBOL"]
        

        try:
            return char_to_col[input_char]
        except KeyError:
            return char_to_col["OTHER"]

    def save_symbol_table(self):
        ''' Сохраняет таблицу символов в файл '''
        with open(self.symbol_file, "w") as f:
            for i, symbol in enumerate(self.identifiers):
                f.write(f"{i+1}.\t{symbol}\n")

    def save_tokens(self):
        ''' Сохраняет токены в файл '''
        if self.max_state_size > 0:
            with open(self.tokens_file, "w") as f:
                for lineno, tokens in self.tokens.items():
                    if tokens:
                        f.write(f"{lineno}.\t{' '.join([f'({t}, {l})' for t, l in tokens])}\n")

    def _switch_line(self, num_lines):
        ''' Переключает строку и обновляет номер строки '''
        if num_lines > 0:
            for i in range(num_lines):
                self.tokens[self.line_number + i + 1] = []
            self.line_number += num_lines
            # удаляет начальные пробелы из следующей строки
            # (ожидаются символы новой строки, так как они нужны для расчетов номера строки)
            self.input = self.input.lstrip(" ").lstrip("\t")

    def update_symbol_table(self, lexim):
        ''' Обновляет таблицу символов новым символом '''
        symbol_id = SymbolTableManager.install_id(lexim)
        if symbol_id == len(SymbolTableManager.symbol_table):
            SymbolTableManager.insert(lexim)
        return symbol_id

    def get_next_token(self):
        save_state = None
        error_occurred = False
        input_ended = False
        s = 0  # начальное состояние

        if len(self.tokens.keys()) > self.max_state_size:
            self.tokens.pop(self.first_line, None)
            self.first_line += 1

        if len(self._lexical_errors) > self.max_state_size:
            self._lexical_errors.pop(0)

        while True:  # Цикл до тех пор, пока не найдем корректный токен
            if not self.input or input_ended:
                try:
                    self.read_input()
                except EOFError:
                    if s in unclosed_comment_states:
                        mucs = self.max_unclosed_comment_size
                        err_token = self.input[:mucs]
                        if len(self.input) > len(err_token):
                            err_token = err_token + " ..."
                        SymbolTableManager.error_flag = True
                        self._lexical_errors.append((self.line_number, err_token, "unclosed comment"))
                    self.line_number += self.input.count("\n")
                    self.input = ""
                    return ("EOF", "$")

            token_candidates = []
            error_occurred = False
            input_ended = False

            s = 0 if save_state is None else save_state
            save_state = None

            # проходим по DFA, пока можем с оставшимся вводом
            for i in range(len(self.input) + 1):
                try:
                    a = self.input[i]
                except IndexError:
                    a = self.input[-1]
                col = self._resolve_dfa_table_column(a)
                next_s = token_dfa[s][col]
            

                if s in state_to_error_message:  # находимся ли мы в состоянии ошибки?
                    if s == 22:
                        i -= 1  # это состояние ошибки просмотра вперед (некорректный комментарий)
                    lexim, error = self.input[:i], state_to_error_message[s]
                    if self.max_state_size > 0:
                        SymbolTableManager.error_flag = True
                        self._lexical_errors.append((self.line_number, lexim, error))
                    else:
                        print(f"Lexical Error in line {self.line_number}: {error} '{lexim}'")
                    self.input = self.input[i:]  # пропускаем некорректный токен (режим паники)
                    error_occurred = True
                    break

                if s in F:  # находимся ли мы в принимающем состоянии?
                    if s in Fstar:
                        token_candidates.append((s, self.input[:i-1]))
                    else:
                        token_candidates.append((s, self.input[:i]))

                if next_s is None:  # можем ли мы продолжать проход по DFA?
                    break
                elif i >= len(self.input):  # достаточно ли у нас ввода для этого?
                    # это происходит только для больших файлов или маленького размера чанка
                    if next_s not in F:
                        save_state = next_s
                    input_ended = True
                    break
                print(s)       
                s = next_s

            if error_occurred or input_ended:
                continue

            if token_candidates:
                max_token = token_candidates[-1]  # выбираем максимальный токен
                state, lexim = max_token
                self.input = self.input[len(lexim):]  # продвигаемся во вводе
                token = state_to_token[state]

                if token == "WHITESPACE" or token == "COMMENT":  # эти токены не будут возвращены
                    self._switch_line(lexim.count("\n"))  # обновляем номер строки и т.д.
                    continue  # переходим к следующему токену

                if token == "NUM":
                    # Разрешаем цифры, символы '+' и '-', а также 'e' или 'E', но не другие буквы или символы
                    if re.search(r'[^0-9eE\+\-\.]', lexim):  
                        SymbolTableManager.error_flag = True
                        self._lexical_errors.append((self.line_number, lexim, "e number without e"))

                        continue
                        
                        
                if token == "Nbodh":  
                    if lexim[-2] == 'b' or lexim[-2] == 'B':
                        # Возвращаемся к началу слова и проверяем его на наличие только 0, 1, b, B
                        if re.search(r'[^01 ]', lexim[:-2]): #пробел важен 
                            SymbolTableManager.error_flag = True
                            self._lexical_errors.append((self.line_number, lexim, "Invalid binary number"))
                            continue  # Пропускаем токен и продолжаем 
                        else:
                            token = "NUM"
                            

                if token == "Nbodh":   
                    if lexim[-2] == 'o' or lexim[-2] == 'O':
                        # Возвращаемся к началу слова и проверяем его на наличие только 0, 1, b, B
                        if re.search(r'[^0-7 ]', lexim[:-2]): #пробел важен 
                            SymbolTableManager.error_flag = True
                            self._lexical_errors.append((self.line_number, lexim, "Invalid octa number"))
                            continue  # Пропускаем токен и продолжаем 
                        else:
                            token = "NUM"

                if token == "Nbodh":  
                    if lexim[-2] == 'D' or lexim[-2] == 'd':
                        # Возвращаемся к началу слова и проверяем его на наличие только 0, 1, b, B
                        if re.search(r'[^0-9 ]', lexim[:-2]): #пробел важен 
                            SymbolTableManager.error_flag = True
                            self._lexical_errors.append((self.line_number, lexim, "Invalid deca number"))
                            continue  # Пропускаем токен и продолжаем 
                        else:
                            token = "NUM"

                if token == "Nbodh":  
                    if lexim[-2] == 'H' or lexim[-2] == 'h':
                        # Возвращаемся к началу слова и проверяем его на наличие только 0, 1, b, B
                        if re.search(r'[^0-9A-F ]', lexim[:-2]): #пробел важен 
                            SymbolTableManager.error_flag = True
                            self._lexical_errors.append((self.line_number, lexim, "Invalid hex number"))
                            continue  # Пропускаем токен и продолжаем 
                        else:
                            token = "NUM"
                      

                if lexim == "&":  # если символ — это одиночный &
                     if len(self.input) > 0 and self.input[0] == "&":  # проверяем следующий символ
                         self.input = self.input[1:]  # убираем второй & из потока
                         token = "RAZD"  # это разделитель &&
                         lexim = "&&"
                     else:
                        token = "KEYWORD"  # если это одиночный символ, то ключевое слово

                elif lexim == "|":  
                    if len(self.input) > 0 and self.input[0] == "|":  # проверяем следующий символ
                         self.input = self.input[1:]  # убираем второй & из потока
                         token = "RAZD"  # это разделитель &&
                         lexim = "||"
                    else:
                        
                        SymbolTableManager.error_flag = True
                        self._lexical_errors.append((self.line_number, lexim, 'invalid input'))
                        continue

                

                if token == "SYMBOL":
                    token = "KEYWORD" if lexim in self.keywords else "SYMBOL"  
 
                if token == "SYMBOL":
                    token = "RAZD" if lexim in self.razd else "SYMBOL"      
                   
                if token == "ID_OR_KEYWORD":  
                    token = "KEYWORD" if lexim in self.keywords else "ID"

                if token == "ID":  
                    token = "RAZD" if lexim in self.razd else "ID"

                if self.max_state_size > 0:
                    self.tokens[self.line_number].append((token, lexim))  # сохраняем токены для последующей печати

                if token == "ID":
                    if lexim not in self.identifiers:
                        self.identifiers.append(lexim)
                    lexim = self.update_symbol_table(lexim)

                return (token, lexim)
            else:
                print(f"[Panic Mode] Dropping '{self.input[:1]}' from input!")
                self.input = self.input[1:]  # сбрасываем некорректный символ в случае ошибки


def mainScanner(input_path):
    ''' Основная функция для запуска сканера '''
    import time
    scanner = Scanner(input_path)
    start = time.time()
    token = scanner.get_next_token()
    while token[0] != "EOF":
        token = scanner.get_next_token()
    stop = time.time() - start
    print(f"Scanning took {stop:.6f} s")
    scanner.save_symbol_table()
    scanner.save_lexical_errors()
    scanner.save_tokens()

if __name__ == "__main__":
    SymbolTableManager.init()
    input_path = os.path.join(script_dir, "input/input_simple.c")
    mainScanner(input_path)
