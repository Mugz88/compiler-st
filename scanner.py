import os

# Путь к директории скрипта
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script_dir = os.path.join(script_dir, "compiler-st")

# Класс для управления таблицей символов
class SymbolTableManager(object):
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
        cls.scope_stack = [0]
        cls.temp_stack = [0]
        cls.arg_list_stack = []
        cls.symbol_table = cls._global_funcs.copy()
        cls.declaration_flag = False
        cls.error_flag = False

    @classmethod
    def scope(cls):
        return len(cls.scope_stack) - 1

    @classmethod
    def insert(cls, lexim):
        cls.symbol_table.append({"lexim": lexim, "scope": cls.scope()})

    @classmethod
    def _exists(cls, lexim, scope):
        for row in cls.symbol_table:
            if row["lexim"] == lexim and row["scope"] == scope:
                return True
        return False

    @classmethod
    def findrow(cls, value, attr="lexim"):
        for i in range(len(cls.symbol_table) - 1, -1, -1):
            row = cls.symbol_table[i]
            if row[attr] == value:
                return row
        return None

    @classmethod
    def findrow_idx(cls, value, attr="lexim"):
        for i in range(len(cls.symbol_table) - 1, -1, -1):
            row = cls.symbol_table[i]
            if row[attr] == value:
                return i
        return None

    @classmethod
    def install_id(cls, lexim):
        if not cls.declaration_flag:
            i = cls.findrow_idx(lexim)
            if i is not None:
                return i
        return len(cls.symbol_table)

    @classmethod
    def get_enclosing_fun(cls, level=1):
        try:
            return cls.symbol_table[cls.scope_stack[-level] - 1]
        except IndexError:
            return None

# Таблица переходов DFA
char_to_col = {
    "WHITESPACE": 0,
    "DIGIT": 1,
    "LETTER": 2,
    "HEX_LETTER": 13,
    "*": 3,
    "=": 4,
    "SYMBOL": 5,
    "/": 6,
    "\n": 7,
    "OTHER": 8,
    "B": 9,
    "O": 10,
    "D": 11,
    "H": 12
}

state_to_token = {
    1: "WHITESPACE",
    3: "NUM_DEC",
    6: "ID_OR_KEYWORD",
    10: "SYMBOL",
    11: "SYMBOL",
    12: "SYMBOL",
    16: "COMMENT",
    18: "RAZD",
    19: "WHITESPACE",
    21: "SYMBOL",
    23: "NUM_BIN",
    24: "NUM_OCT",
    25: "NUM_DEC",
    26: "NUM_HEX",
    27: "NUM_SUFFIX",
    28: "NUM_BIN_SUFFIX",  # Новый токен для двоичных чисел с суффиксом
    29: "NUM_OCT_SUFFIX",  # Новый токен для восьмеричных чисел с суффиксом
    30: "NUM_HEX_SUFFIX",  # Новый токен для шестнадцатеричных чисел с суффиксом
}

state_to_error_message = {
    4: "illegal number",
    8: "unmatched */",
    20: "invalid input",
    22: "invalid input",
}

token_dfa = (
    (1, 2, 5, 7, 9, 12, 13, 19, 20, 23, 24, 25, 26, 26),
    (1, None, None, None, None, None, None, 1, None, None, None, None, None, None),
    (3, 2, 4, 3, 3, 3, 3, 3, 4, 23, 24, 25, 26, 26),
    (None, 3, 27, None, None, None, None, None, None, 23, 24, 25, 26, 26),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (6, 5, 5, 6, 6, 6, 6, 6, 20, 23, 24, 25, 26, 26),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (21, 21, 21, 21, 21, 21, 8, 21, 20, 21, 21, 21, 21, 21),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (11, 11, 11, 11, 10, 11, 11, 11, 20, 11, 11, 11, 11, 11),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (22, 22, 22, 14, 22, 22, 17, 22, 22, 22, 22, 22, 22, 22),
    (14, 14, 14, 15, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14),
    (14, 14, 14, 15, 14, 14, 16, 14, 14, 14, 14, 14, 14, 14),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (17, 17, 17, 17, 17, 17, 17, 18, 17, 17, 17, 17, 17, 17),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (19, None, None, None, None, None, None, 19, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (23, 23, None, None, None, None, None, None, None, None, None, None, None, None),
    (24, 24, None, None, None, None, None, None, None, None, None, None, None, None),
    (25, 25, None, None, None, None, None, None, None, None, None, None, None, None),
    (26, 26, 26, None, None, None, None, None, None, None, None, None, None, 26),
    (28, 28, None, None, None, None, None, None, None, None, None, None, None, None),  # Новое состояние для суффиксов
    (29, 29, None, None, None, None, None, None, None, None, None, None, None, None),  # Новое состояние для суффиксов
    (30, 30, None, None, None, None, None, None, None, None, None, None, None, None),  # Новое состояние для суффиксов
)

F = {1, 3, 6, 10, 11, 12, 16, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30}
Fstar = {3, 6, 11, 21, 23, 24, 25, 26, 27, 28, 29, 30}
unclosed_comment_states = {14, 15, 17}

whitespaces = {' ', '\r', '\t', '\v', '\f'}

class Scanner(object):
    def __init__(self, input_file, chunk_size=8192, max_state_size=float("inf")):
        assert chunk_size >= 16, "Минимальный поддерживаемый размер чанка - 16!"
        if not os.path.isabs(input_file):
            input_file = os.path.join(script_dir, input_file)
        self.input_file = input_file
        print(self.input_file)
        self.line_number = 1
        self.first_line = 1
        self._lexical_errors = []
        self.tokens = {}
        self.tokens[self.line_number] = []
        self.max_state_size = max_state_size

        self.tokens_file = os.path.join(script_dir, "output", "tokens.txt")
        self.symbol_file = os.path.join(script_dir, "output", "symbol_table.txt")

        self.errors_file = os.path.join(script_dir, "errors", "lexical_errors.txt")

        self.chunk_size = chunk_size
        self.file_pointer = 0
        self.max_unclosed_comment_size = 15
        self.input = ""
        self.read_input()

        self._symbols = {',', ';', ':', '(', ')', '{', '}', '+', '-','^','#','@','&','.','|'}
        self.letters = {chr(i) for i in range(65, 91)} | {chr(i) for i in range(97, 123)}
        self.digits = {str(i) for i in range(0, 10)}
        self.hex_digits = self.digits | {chr(i) for i in range(ord('A'), ord('F') + 1)} | {chr(i) for i in range(ord('a'), ord('f') + 1)}
        self.symbols = self._symbols | {"*", "="}

        razd = [
            "NEQ",
            "EQV",
            "LOWT",
            "LOWE",
            "GRT",
            "GRE",
            "add",
            "disa",
            "||",
            "umn",
            "del",
            "&&",
            "^",
            "+",
            "-",
            "as",
            ":",
            "(",
            ")",
            ".",
            ",",
            ";",
            "#",
        ]
        self.identifiers = razd
        self.razd = set(razd)

        keywords = [
            "begin",
            "end",
            "var",
            "if",
            "then",
            "else",
            "for",
            "to",
            "false",
            "do",
            "next",
            "read",
            "write",
            "while",
            "true",
            "@",
            "#",
            "&",
        ]
        self.identifiers = keywords
        self.keywords = set(keywords)

    @property
    def lexical_errors(self):
        lexical_errors = []
        if self._lexical_errors:
            for lineno, lexim, error in self._lexical_errors:
                lexical_errors.append(f"#{lineno} : Lexical Error! '{lexim}' rejected, reason: {error}.\n")
        else:
            lexical_errors.append("There is no lexical errors.\n")
        return "".join(lexical_errors)

    def save_lexical_errors(self):
        if self.max_state_size > 0:
            with open(self.errors_file, "w") as f:
                f.write(self.lexical_errors)

    def id_to_lexim(self, token_id):
        return SymbolTableManager.symbol_table[token_id]['lexim']

    def token_to_str(self, token):
        if token[0] == "ID":
            return f"({token[0]}, {self.id_to_lexim(token[1])})"
        else:
            return "({}, {})".format(*token)

    def read_input(self):
        with open(self.input_file, "rb") as f:
            f.seek(self.file_pointer)
            chunk = f.read(self.chunk_size)
        if not chunk:
            raise EOFError
        self.input += chunk.decode()
        self.file_pointer += self.chunk_size

    def _resolve_dfa_table_column(self, input_char):
        if input_char in whitespaces:
            return char_to_col["WHITESPACE"]
        if input_char in self.letters:
            return char_to_col["LETTER"]
        if input_char in self.digits:
            return char_to_col["DIGIT"]
        if input_char in self.hex_digits:
            return char_to_col["HEX_LETTER"]
        if input_char in self._symbols:
            return char_to_col["SYMBOL"]

        try:
            return char_to_col[input_char.upper()]
        except KeyError:
            return char_to_col["OTHER"]

    def save_symbol_table(self):
        with open(self.symbol_file, "w") as f:
            for i, symbol in enumerate(self.identifiers):
                f.write(f"{i+1}.\t{symbol}\n")

    def save_tokens(self):
        if self.max_state_size > 0:
            with open(self.tokens_file, "w") as f:
                for lineno, tokens in self.tokens.items():
                    if tokens:
                        f.write(f"{lineno}.\t{' '.join([f'({t}, {l})' for t, l in tokens])}\n")

    def _switch_line(self, num_lines):
        if num_lines > 0:
            for i in range(num_lines):
                self.tokens[self.line_number + i + 1] = []
            self.line_number += num_lines
            self.input = self.input.lstrip(" ").lstrip("\t")

    def update_symbol_table(self, lexim):
        symbol_id = SymbolTableManager.install_id(lexim)
        if symbol_id == len(SymbolTableManager.symbol_table):
            SymbolTableManager.insert(lexim)
        return symbol_id

    def get_next_token(self):
        save_state = None
        error_occurred = False
        input_ended = False
        s = 0

        if len(self.tokens.keys()) > self.max_state_size:
            self.tokens.pop(self.first_line, None)
            self.first_line += 1

        if len(self._lexical_errors) > self.max_state_size:
            self._lexical_errors.pop(0)

        while True:
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

            for i in range(len(self.input) + 1):
                try:
                    a = self.input[i]
                except IndexError:
                    a = self.input[-1]
                col = self._resolve_dfa_table_column(a)
                next_s = token_dfa[s][col]

                if s in state_to_error_message:
                    if s == 22:
                        i -= 1
                    lexim, error = self.input[:i], state_to_error_message[s]
                    if self.max_state_size > 0:
                        SymbolTableManager.error_flag = True
                        self._lexical_errors.append((self.line_number, lexim, error))
                    else:
                        print(f"Lexical Error in line {self.line_number}: {error} '{lexim}'")
                    self.input = self.input[i:]
                    error_occurred = True
                    break

                if s in F:
                    if s in Fstar:
                        token_candidates.append((s, self.input[:i-1]))
                    else:
                        token_candidates.append((s, self.input[:i]))

                if next_s is None:
                    break
                elif i >= len(self.input):
                    if next_s not in F:
                        save_state = next_s
                    input_ended = True
                    break

                s = next_s

            if error_occurred or input_ended:
                continue

            if token_candidates:
                max_token = token_candidates[-1]
                state, lexim = max_token
                self.input = self.input[len(lexim):]
                token = state_to_token[state]

                if token == "WHITESPACE" or token == "COMMENT":
                    self._switch_line(lexim.count("\n"))
                    continue

                if lexim == "&":
                    if len(self.input) > 0 and self.input[0] == "&":
                        self.input = self.input[1:]
                        token = "RAZD"
                        lexim = "&&"
                    else:
                        token = "KEYWORD"

                elif lexim == "|":
                    if len(self.input) > 0 and self.input[0] == "|":
                        self.input = self.input[1:]
                        token = "RAZD"
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
                    self.tokens[self.line_number].append((token, lexim))

                if token == "ID":
                    if lexim not in self.identifiers:
                        self.identifiers.append(lexim)
                    lexim = self.update_symbol_table(lexim)

                # Добавление логики для обработки чисел с суффиксами
                if token == "NUM_DEC":
                    if len(self.input) > 0 and self.input[0] in {'B', 'b'}:
                        self.input = self.input[1:]
                        token = "NUM_BIN"
                    elif len(self.input) > 0 and self.input[0] in {'O', 'o'}:
                        self.input = self.input[1:]
                        token = "NUM_OCT"
                    elif len(self.input) > 0 and self.input[0] in {'H', 'h'}:
                        self.input = self.input[1:]
                        token = "NUM_HEX"

                if token == "NUM_BIN":
                    if len(self.input) > 0 and self.input[0] in {'B', 'b'}:
                        self.input = self.input[1:]
                        token = "NUM_BIN_SUFFIX"

                if token == "NUM_OCT":
                    if len(self.input) > 0 and self.input[0] in {'O', 'o'}:
                        self.input = self.input[1:]
                        token = "NUM_OCT_SUFFIX"

                if token == "NUM_HEX":
                    if len(self.input) > 0 and self.input[0] in {'H', 'h'}:
                        self.input = self.input[1:]
                        token = "NUM_HEX_SUFFIX"

                return (token, lexim)
            else:
                print(f"[Panic Mode] Dropping '{self.input[:1]}' from input!")
                self.input = self.input[1:]

def mainScanner(input_path):
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
    input_path = os.path.join(script_dir, "input", "input_simple.c")
    mainScanner(input_path)
