import os

# Класс для представления токенов
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"({self.type}, {self.value})"

# Грамматический анализатор
class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.current_token = None
        self.advance()

    def advance(self):
        self.current_token = self.scanner.get_next_token()

    def parse(self):
        try:
            return self.program()
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            return None

    def program(self):
        statements = []
        while self.current_token:
            statements.append(self.statement())
        return statements

    def statement(self):
        if self.current_token.type == 'KEYWORD' and self.current_token.value == 'dim':
            return self.declaration()
        elif self.current_token.type == 'ID':
            return self.assignment()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'write':
            return self.write_statement()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")

    def declaration(self):
        self.match('KEYWORD', 'dim')
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

    def expression(self):
        operand = self.operand()
        while self.current_token and self.current_token.type == 'RAZD' and self.current_token.value in ['NE', 'EQ', 'LT', 'LE', 'GT', 'GE']:
            operator = self.match('RAZD')
            right_operand = self.operand()
            operand = ('binary_op', operator, operand, right_operand)
        return operand

    def operand(self):
        term = self.term()
        while self.current_token and self.current_token.type == 'RAZD' and self.current_token.value in ['plus', 'min', 'or']:
            operator = self.match('RAZD')
            right_term = self.term()
            term = ('binary_op', operator, term, right_term)
        return term

    def term(self):
        factor = self.factor()
        while self.current_token and self.current_token.type == 'RAZD' and self.current_token.value in ['mult', 'div', 'and']:
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
        elif token.type == 'RAZD' and token.value == '~':
            self.advance()
            factor = self.factor()
            return ('unary_op', '~', factor)
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

# Семантический анализатор
class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = {}

    def analyze(self):
        try:
            for statement in self.ast:
                self.visit(statement)
        except SemanticError as e:
            print(f"Semantic Error: {e}")

    def visit(self, node):
        method_name = 'visit_' + node[0]
        visitor = getattr(self, method_name, self.generic_visit)
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
        self.visit(expression)

    def visit_write(self, node):
        _, expressions = node
        for expression in expressions:
            self.visit(expression)

    def visit_binary_op(self, node):
        _, operator, left, right = node
        self.visit(left)
        self.visit(right)

    def visit_unary_op(self, node):
        _, operator, operand = node
        self.visit(operand)

    def visit_identifier(self, node):
        _, value = node
        if value not in self.symbol_table:
            raise SemanticError(f"Identifier {value} not declared")

    def visit_number(self, node):
        pass

    def visit_boolean(self, node):
        pass

    def generic_visit(self, node):
        raise SemanticError(f"No visit_{node[0]} method")

# Основная функция для выполнения анализа
def main():
    input_file_path = os.path.join(os.path.dirname(__file__), 'main.txt')
    
    from scanner import Scanner

    scanner = Scanner(input_file_path)
    parser = Parser(scanner)
    ast = parser.parse()
    if ast is not None:
        print("Abstract Syntax Tree (AST):")
        print(ast)

        semantic_analyzer = SemanticAnalyzer(ast)
        semantic_analyzer.analyze()
        print("Semantic analysis completed successfully.")
    else:
        print("Parsing failed.")

if __name__ == "__main__":
    main()
