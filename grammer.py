import os
from scanner import Scanner
from scanner import SymbolTableManager

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script_dir = os.path.join(script_dir, "compiler-st")

# Класс для представления токенов
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"({self.type}, {self.value})"

class SemanticError(Exception):
    pass

# Грамматический анализатор
class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.current_token = None
        self.flag = False
        self.advance()
        self.errors_file = os.path.join(script_dir, "errors", "syntax_errors.txt")

    def advance(self):
        token = self.scanner.get_next_token()
        type = token[0]
        value = token[1]
        print(f"Current token: {type} {value}")
        self.current_token = Token(type, value)

    def parse(self):
        try:
            return self.program()
        except SyntaxError as e:
            with open(self.errors_file, "w") as f:
                f.write("Syntax Error: " + str(e))
            print(f"Syntax Error: {e}")
            return None

    def program(self):
        self.match('KEYWORD', 'begin')
        statements = []
        while self.current_token and self.flag is False:
            
            statements.append(self.statement())
            if self.current_token and self.current_token.type == 'RAZD' and self.current_token.value == ';':
                self.match('RAZD', ';')
        self.match('KEYWORD', 'end')
        return statements

    def statement(self):
        if self.current_token.type == 'KEYWORD' and self.current_token.value == 'var':
            return self.declaration()
        elif self.current_token.type == 'ID':
            return self.assignment()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'write':
            return self.write_statement()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'read':
            return self.read_statement()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'if':
            return self.if_statement()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'while':
            return self.while_statement()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'for':
            return self.for_statement()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'end':
            with open(self.errors_file, "w") as f:
                f.write("No syntax error:)")
            print("End of program")
            self.flag = True
        elif self.current_token.type == 'EOF':
            raise SyntaxError("Not found end of program")
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")

    def declaration(self):
        self.match('KEYWORD', 'var')
        identifiers = [self.match('ID')]
        while self.current_token and self.current_token.type == 'RAZD' and self.current_token.value == ',':
            self.match('RAZD', ',')
            identifiers.append(self.match('ID'))
        self.match('RAZD', ':')
        type_ = self.match('KEYWORD')
        return ('declaration', identifiers, type_)

    def assignment(self):
        identifier = self.match('ID')
        self.match('RAZD', 'as')
        expression = self.expression()
        return ('assignment', identifier, expression)

    def write_statement(self):
        self.match('KEYWORD', 'write')
        self.match('RAZD', '(')
        expressions = [self.expression()]
        while self.current_token and self.current_token.type == 'RAZD' and self.current_token.value == ',':
            self.match('RAZD', ',')
            expressions.append(self.expression())
        self.match('RAZD', ')')
        return ('write', expressions)

    def read_statement(self):
        self.match('KEYWORD', 'read')
        self.match('RAZD', '(')
        identifiers = [self.match('ID')]
        while self.current_token and self.current_token.type == 'RAZD' and self.current_token.value == ',':
            self.match('RAZD', ',')
            identifiers.append(self.match('ID'))
        self.match('RAZD', ')')
        return ('read', identifiers)

    def if_statement(self):
        self.match('KEYWORD', 'if')
        condition = self.expression()
        self.match('KEYWORD', 'then')
        then_branch = self.statement()
        else_branch = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'else':
            self.match('KEYWORD', 'else')
            else_branch = self.statement()
        return ('if', condition, then_branch, else_branch)

    def while_statement(self):
        self.match('KEYWORD', 'while')
        condition = self.expression()
        self.match('KEYWORD', 'do')
        body = self.statement()
        return ('while', condition, body)

    def for_statement(self):
        self.match('KEYWORD', 'for')
        initialization = self.assignment()
        self.match('KEYWORD', 'to')
        condition = self.expression()
        self.match('KEYWORD', 'do')
        body = self.statement()
        return ('for', initialization, condition, body)

    def expression(self):
        operand = self.operand()
        while self.current_token and self.current_token.type == 'RAZD' and self.current_token.value in ['NEQ', 'EQV', 'LOWT', 'LOWE', 'GRT', 'GRE']:
            operator = self.match('RAZD')
            right_operand = self.operand()
            operand = ('binary_op', operator, operand, right_operand)
        return operand

    def operand(self):
        term = self.term()
        while self.current_token and self.current_token.type == 'RAZD' and self.current_token.value in ['add', 'disa', '||']:
            operator = self.match('RAZD')
            right_term = self.term()
            term = ('binary_op', operator, term, right_term)
        return term

    def term(self):
        factor = self.factor()
        while self.current_token and self.current_token.type == 'RAZD' and self.current_token.value in ['umn', 'del', '&&']:
            operator = self.match('RAZD')
            right_factor = self.factor()
            factor = ('binary_op', operator, factor, right_factor)
        return factor

    def factor(self):
        token = self.current_token
        if token.type == 'ID':
            self.advance()
            return ('identifier', token.value)
        elif token.type == 'NUM':
            self.advance()
            return ('number', token.value)
        elif token.type == 'KEYWORD' and token.value in ['true', 'false']:
            self.advance()
            return ('boolean', token.value)
        elif token.type == 'RAZD' and token.value == '^':
            self.advance()
            factor = self.factor()
            return ('unary_op', '^', factor)
        elif token.type == 'RAZD' and token.value == '(':
            self.advance()
            expr = self.expression()
            self.match('RAZD', ')')
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token}")

    def match(self, type, value=None):
        if self.current_token and self.current_token.type == type and (value is None or self.current_token.value == value):
            token = self.current_token
            self.advance()
            return token
        else:
            raise SyntaxError(f"Expected {type} {value}, but got {self.current_token}")

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = {}
        self.errors_file = os.path.join(script_dir, "errors", "semantic_errors.txt")

    def analyze(self):
        try:
            for statement in self.ast:
                self.visit(statement)
        except SemanticError as e:
            with open(self.errors_file, "w") as f:
                f.write("Semantic Error: " + str(e))
            print(f"Semantic Error: {e}")
            return 1

    def visit(self, node):
        if node is None:
            return
        method_name = 'visit_' + node[0]
        visitor = getattr(self, method_name, self.generic_visit)
        print(f"Visiting {node}")
        return visitor(node)

    def visit_declaration(self, node):
        _, identifiers, type_ = node
        for identifier in identifiers:
            if identifier.value in self.symbol_table:
                raise SemanticError(f"Identifier {identifier.value} already declared")
            self.symbol_table[identifier.value] = type_.value

    def visit_assignment(self, node):
        _, identifier, expression = node
        if identifier.value not in self.symbol_table:
            raise SemanticError(f"Identifier {identifier.value} not declared")

        declared_type = self.symbol_table[identifier.value]
        expr_type = self.visit(expression)  # Получаем тип выражения

        if declared_type != expr_type:
            raise SemanticError(f"Type mismatch: cannot assign {expr_type} to {declared_type}")

    def visit_write(self, node):
        _, expressions = node
        for expression in expressions:
            self.visit(expression)

    def visit_read(self, node):
        _, identifiers = node
        for identifier in identifiers:
            if identifier.value not in self.symbol_table:
                raise SemanticError(f"Identifier {identifier.value} not declared")

    def visit_if(self, node):
        _, condition, then_branch, else_branch = node
        self.visit(condition)
        self.visit(then_branch)
        if else_branch:
            self.visit(else_branch)

    def visit_while(self, node):
        _, condition, body = node
        self.visit(condition)
        self.visit(body)

    def visit_for(self, node):
        _, initialization, condition, body = node
        self.visit(initialization)
        self.visit(condition)
        self.visit(body)

    def visit_binary_op(self, node):
        _, operator, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Пример проверки типов в бинарных операциях
        if operator in ['add', 'disa', '||', 'umn', 'del', '&&']:
            if left_type != right_type:
                raise SemanticError(f"Type mismatch in binary operation: {left_type} {operator} {right_type}")
        return left_type  # Возвращаем тип результата операции

    def visit_unary_op(self, node):
        _, operator, operand = node
        operand_type = self.visit(operand)

        # Пример проверки типа для унарных операций
        if operator == '^' and operand_type != 'boolean':
            raise SemanticError(f"Type mismatch: expected boolean for '^', got {operand_type}")
        return operand_type

    def visit_identifier(self, node):
        _, value = node
        if value not in self.symbol_table:
            raise SemanticError(f"Identifier {value} not declared")
        return self.symbol_table[value]

    def visit_number(self, node):
        _, value = node
        # Вещественное число (например) будет типом "float", обычное - "int"
        if 'E' in value or 'e' in value or '.' in value:
            return '@'
        return '!'

    def visit_boolean(self, node):
        return 'boolean'

    def generic_visit(self, node):
        raise SemanticError(f"No visit_{node[0]} method")

def mainGrammar():
    input_file_path = os.path.join(os.path.dirname(__file__), 'main.txt')
    SymbolTableManager.init()
    scanner = Scanner(input_file_path)
    parser = Parser(scanner)
    ast = parser.parse()
    sem_errors_file = os.path.join(script_dir, "errors", "semantic_errors.txt")
    if ast is not None:
        print("Abstract Syntax Tree (AST):")
        print(ast)

        semantic_analyzer = SemanticAnalyzer(ast)
        sem = semantic_analyzer.analyze()
        if sem != 1:
            with open(sem_errors_file, "w") as f:
                f.write("No semantic error:)")
            print("Semantic analysis completed successfully.")
    else:
        print("Parsing failed.")
    scanner.save_symbol_table()
    scanner.save_lexical_errors()
    scanner.save_tokens()
    nums, ind = scanner.data()
    return nums, ind
if __name__ == "__main__":
    mainGrammar()
