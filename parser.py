import os
from anytree import Node, RenderTree, PreOrderIter
from scanner import Scanner, SymbolTableManager
from semantic_analyser import SemanticAnalyser
from code_gen import CodeGen, MemoryManager

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script_dir = os.path.join(script_dir, "compiler-st")

non_terminal_to_missing_construct = {
    "Program"                       : "end",
    "Description"                   : "dim ID : integer",
    "Description-list"              : "dim ID : integer",
    "Statement-list"                : "ID as EXPR",
    "Statement"                     : "ID as EXPR",
    "Expression"                    : "NUM",
    "Operand"                       : "NUM",
    "Term"                          : "NUM",
    "Factor"                        : "NUM",
    "Identifier"                    : "ID",
    "Number"                        : "NUM",
    "LogicalConstant"               : "true",
    "Type"                          : "integer",
    "RelationalOperation"           : "EQ",
    "AdditiveOperation"             : "plus",
    "MultiplicativeOperation"       : "mult",
    "UnaryOperation"                : "~",
    "CompoundStatement"             : "ID as EXPR",
    "AssignmentStatement"           : "ID as EXPR",
    "ConditionalStatement"          : "if EXPR then STMT",
    "FixedLoopStatement"            : "for ID as EXPR to EXPR do STMT",
    "ConditionalLoopStatement"      : "while EXPR do STMT",
    "InputStatement"                : "read (ID)",
    "OutputStatement"               : "write (EXPR)",
}

productions = (
    "",                                                                  # Empty production
    "Description-list",                                                  # Description-list
    "Description Description-list",                                       # Description Description-list
    "EPSILON",                                                           # Epsilon
    "dim ID : Type",                                                     # Description
    "Statement-list",                                                     # Statement-list
    "Statement Statement-list",                                          # Statement Statement-list
    "EPSILON",                                                           # Epsilon
    "CompoundStatement",                                                  # CompoundStatement
    "AssignmentStatement",                                               # AssignmentStatement
    "ConditionalStatement",                                             # ConditionalStatement
    "FixedLoopStatement",                                                # FixedLoopStatement
    "ConditionalLoopStatement",                                         # ConditionalLoopStatement
    "InputStatement",                                                   # InputStatement
    "OutputStatement",                                                   # OutputStatement
    "ID as Expression",                                                  # AssignmentStatement
    "if Expression then Statement else Statement",                       # ConditionalStatement
    "for ID as Expression to Expression do Statement",                   # FixedLoopStatement
    "while Expression do Statement",                                      # ConditionalLoopStatement
    "read ( ID )",                                                       # InputStatement
    "write ( Expression )",                                             # OutputStatement
    "Expression",                                                        # Expression
    "Operand RelationalOperation Operand",                               # Expression
    "Operand",                                                           # Operand
    "Term AdditiveOperation Term",                                       # Operand
    "Term",                                                              # Term
    "Factor MultiplicativeOperation Factor",                            # Term
    "Factor",                                                            # Factor
    "Identifier",                                                        # Factor
    "Number",                                                            # Factor
    "LogicalConstant",                                                   # Factor
    "UnaryOperation Factor",                                             # Factor
    "( Expression )",                                                    # Factor
    "ID",                                                                # Identifier
    "NUM",                                                               # Number
    "true",                                                             # LogicalConstant
    "false",                                                             # LogicalConstant
    "integer",                                                          # Type
    "real",                                                              # Type
    "boolean",                                                           # Type
    "NE",                                                               # RelationalOperation
    "EQ",                                                               # RelationalOperation
    "LT",                                                               # RelationalOperation
    "LE",                                                               # RelationalOperation
    "GT",                                                               # RelationalOperation
    "GE",                                                               # RelationalOperation
    "plus",                                                              # AdditiveOperation
    "min",                                                              # AdditiveOperation
    "or",                                                               # AdditiveOperation
    "mult",                                                              # MultiplicativeOperation
    "div",                                                              # MultiplicativeOperation
    "and",                                                              # MultiplicativeOperation
    "~",                                                                # UnaryOperation
    "SYNCH",                                                             # Synchronization
    "EMPTY"                                                              # Empty
)

productions = tuple([p.split() for p in productions]) # split productions into arrays

terminal_to_col = {
    "ID"        : 0,
    "NUM"       : 1,
    "end"       : 2,
    "dim"       : 3,
    "integer"   : 4,
    "real"      : 5,
    "boolean"   : 6,
    "if"        : 7,
    "then"      : 8,
    "else"      : 9,
    "for"       : 10,
    "to"        : 11,
    "do"        : 12,
    "while"     : 13,
    "read"      : 14,
    "write"     : 15,
    "true"      : 16,
    "false"     : 17,
    "NE"        : 18,
    "EQ"        : 19,
    "LT"        : 20,
    "LE"        : 21,
    "GT"        : 22,
    "GE"        : 23,
    "plus"      : 24,
    "min"       : 25,
    "or"        : 26,
    "mult"      : 27,
    "div"       : 28,
    "and"       : 29,
    "~"         : 30,
    "as"        : 31,
    ":"         : 32,
    "{"         : 33,
    "}"         : 34,
    "("         : 35,
    ")"         : 36,
    "."         : 37,
    ","         : 38,
    "$"         : 39
}

non_terminal_to_row = {
    "Program"                       : 0,
    "Description-list"              : 1,
    "Description"                   : 2,
    "Statement-list"                : 3,
    "Statement"                    : 4,
    "Expression"                    : 5,
    "Operand"                      : 6,
    "Term"                          : 7,
    "Factor"                        : 8,
    "Identifier"                    : 9,
    "Number"                        : 10,
    "LogicalConstant"               : 11,
    "Type"                          : 12,
    "RelationalOperation"           : 13,
    "AdditiveOperation"             : 14,
    "MultiplicativeOperation"      : 15,
    "UnaryOperation"                : 16,
    "CompoundStatement"            : 17,
    "AssignmentStatement"           : 18,
    "ConditionalStatement"         : 19,
    "FixedLoopStatement"            : 20,
    "ConditionalLoopStatement"      : 21,
    "InputStatement"                : 22,
    "OutputStatement"               : 23,
}

parsing_table = (
    # 0    1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18   19   20   21   22   23   24   25   26   27   28   29   30   31   32   33   34   35   36   37   38   39
    #ID  NUM end dim integer real boolean if then else for to do while read write true false NE EQ LT LE GT GE plus min or mult div and ~ as : { } ( ) . , $
    (54,  54,  54,   2,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 1  Program
    ( 3,   3,  54,   2,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,   3), # 2  Description-list
    (53,  53,  54,   4,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 3  Description
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 4  Statement-list
    (53,  53,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 5  Statement
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 6  Expression
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 7  Operand
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 8  Term
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 9  Factor
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 10 Identifier
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 11 Number
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 12 LogicalConstant
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 13 Type
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 14 RelationalOperation
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 15 AdditiveOperation
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 16 MultiplicativeOperation
    (54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 17 UnaryOperation
    (53,  53,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 18 CompoundStatement
    (53,  53,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 19 AssignmentStatement
    (53,  53,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 20 ConditionalStatement
    (53,  53,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 21 FixedLoopStatement
    (53,  53,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 22 ConditionalLoopStatement
    (53,  53,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 23 InputStatement
    (53,  53,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  54,  53), # 24 OutputStatement
)

class Parser(object):
    def __init__(self, input_file):
        if not os.path.isabs(input_file):
            input_file = os.path.join(script_dir, input_file)
        print("Parsing", input_file)
        self.scanner = Scanner(input_file)
        self.semantic_analyzer = SemanticAnalyser()
        self.code_generator = CodeGen()
        self._syntax_errors = []
        self.root = Node("Program") # Start symbol
        self.parse_tree = self.root
        self.stack = [Node("$"), self.root]

        self.parse_tree_file = os.path.join(script_dir, "output", "parse_tree.txt")
        self.syntax_error_file = os.path.join(script_dir, "errors", "syntax_errors.txt")

    @property
    def syntax_errors(self):
        syntax_errors = []
        if self._syntax_errors:
            for lineno, error in self._syntax_errors:
                syntax_errors.append(f"#{lineno} : Syntax Error! {error}\n")
        else:
            syntax_errors.append("There is no syntax error.\n")
        return "".join(syntax_errors)

    def save_parse_tree(self):
        with open(self.parse_tree_file, "w", encoding="utf-8") as f:
            for pre, _, node in RenderTree(self.parse_tree):
                if hasattr(node, "token"):
                    f.write(f"{pre}{node.token}\n")
                else:
                    f.write(f"{pre}{node.name}\n")

    def save_syntax_errors(self):
        with open(self.syntax_error_file, "w") as f:
            f.write(self.syntax_errors)

    def _remove_node(self, node):
        try:
            # remove node from the parse tree
            parent = list(node.iter_path_reverse())[1]
            parent.children = [c for c in parent.children if c != node]
        except IndexError:
            pass

    def _clean_up_tree(self):
        ''' remove non terminals and unmet terminals from leaf nodes '''
        remove_nodes = []
        for node in PreOrderIter(self.parse_tree):
            if not node.children and not hasattr(node, "token") and node.name != "EPSILON":
                remove_nodes.append(node)

        for node in remove_nodes:
            self._remove_node(node)

    def parse(self):
        clean_up_needed = False
        token = self.scanner.get_next_token()
        print(f"token: {token}")
        new_nodes = []
        self.code_generator.code_gen("INIT_PROGRAM", None)
        while True:
            token_type, a = token
            if token_type in ("ID", "NUM"):   # parser won't understand the lexim input in this case
                a = token_type

            current_node = self.stack[-1]     # check the top of the stack
            X = current_node.name

            if X.startswith("#SA"):             # X is an action symbol for semantic analyzer
                if X == "#SA_DEC_SCOPE" and a == "ID":
                    curr_lexim = self.scanner.id_to_lexim(token[1])
                self.semantic_analyzer.semantic_check(X, token, self.scanner.line_number)
                self.stack.pop()
                if X == "#SA_DEC_SCOPE" and a == "ID":
                    token = (token[0], self.scanner.update_symbol_table(curr_lexim))
            elif X.startswith("#CG"):           # X is an action symbol for code generator
                self.code_generator.code_gen(X, token)
                self.stack.pop()
            elif X in terminal_to_col.keys():   # X is a terminal
                if X == a:
                    if X == "$":
                        break
                    self.stack[-1].token = self.scanner.token_to_str(token)
                    self.stack.pop()
                    token = self.scanner.get_next_token()
                else:
                    SymbolTableManager.error_flag = True
                    if X == "$": # parse stack unexpectedly exhausted
                        # self._clean_up_tree()
                        break
                    self._syntax_errors.append((self.scanner.line_number, f'Missing "{X}"'))
                    self.stack.pop()
                    clean_up_needed = True
            else:                               # X is non-terminal
                # look up parsing table which production to use
                col = terminal_to_col[a]
                row = non_terminal_to_row[X]
                prod_idx = parsing_table[row][col]

                # Check if prod_idx is within the valid range
                if prod_idx < 0 or prod_idx >= len(productions):
                    pass
                    #raise IndexError(f"prod_idx {prod_idx} is out of range for productions")

                rhs = productions[prod_idx]

                if "SYNCH" in rhs:
                    SymbolTableManager.error_flag = True
                    if a == "$":
                        self._syntax_errors.append((self.scanner.line_number, "Unexpected EndOfFile"))
                        # self._clean_up_tree()
                        clean_up_needed = True
                        break
                    missing_construct = non_terminal_to_missing_construct[X]
                    self._syntax_errors.append((self.scanner.line_number, f'Missing "{missing_construct}"'))
                    self._remove_node(current_node)
                    self.stack.pop()
                elif "EMPTY" in rhs:
                    SymbolTableManager.error_flag = True
                    self._syntax_errors.append((self.scanner.line_number, f'Illegal "{a}"'))
                    token = self.scanner.get_next_token()
                else:
                    self.stack.pop()
                    for symbol in rhs:
                        if not symbol.startswith("#"):
                            new_nodes.append(Node(symbol, parent=current_node))
                        else:
                            new_nodes.append(Node(symbol))

                    for node in reversed(new_nodes):
                        if node.name != "EPSILON":
                            self.stack.append(node)

                print(f"{X} -> {' '.join(rhs)}")  # prints out the productions used
                new_nodes = []

        self.semantic_analyzer.eof_check(self.scanner.line_number)
        if clean_up_needed:
            self._clean_up_tree()
        self.code_generator.code_gen("FINISH_PROGRAM", None)

def main(input_path):
    import time
    SymbolTableManager.init()
    MemoryManager.init()
    parser = Parser(input_path)
    start = time.time()
    parser.parse()
    stop = time.time() - start
    print(f"Parsing took {stop:.6f} s")
    parser.save_parse_tree()
    parser.save_syntax_errors()
    parser.scanner.save_lexical_errors()
    parser.scanner.save_symbol_table()
    parser.scanner.save_tokens()
    parser.semantic_analyzer.save_semantic_errors()
    parser.code_generator.save_output()

if __name__ == "__main__":
    input_path = os.path.join(script_dir, "input/input_simple.c")
    main(input_path)
