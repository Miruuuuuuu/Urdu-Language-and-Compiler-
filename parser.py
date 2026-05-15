import ply.yacc as yacc
from lexer import lexical_errors, tokens, lexer
from semantic import SemanticAnalyzer
from urdu_ast import *

syntax_errors = []
source_lines = []

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
)

# ==========================================
# PROGRAM
# ==========================================

def p_program(p):
    "program : START statement_list END"
    p[0] = Program(p[2])
    if not syntax_errors:
        print("\nProgram parsed successfully!\n")


# ==========================================
# STATEMENT LIST
# ==========================================

def p_statement_list(p):
    """statement_list : statement_list statement
                      | empty"""
    if len(p) == 3:
        p[0] = p[1]
        if p[2] is not None:
            p[0].append(p[2])
    else:
        p[0] = []


# ==========================================
# STATEMENTS
# ==========================================

def p_statement(p):
    """statement : var_decl
                 | assign_stmt
                 | print_stmt
                 | if_stmt
                 | loop_stmt
                 | func_def
                 | list_decl
                 | list_add
                 | list_remove
                 | return_stmt
                 | function_call
                 | input_call"""
    p[0] = p[1]


# ==========================================
# VARIABLE DECLARATION
# ==========================================

def p_var_decl(p):
    "var_decl : type IDENTIFIER assign_opt"
    p[0] = VarDecl(p[1], p[2], p[3])

def p_var_decl_error(p):
    "var_decl : type IDENTIFIER ASSIGN error"
    parser.errok()
    p[0] = None

def p_type(p):
    """type : INT_TYPE
            | FLOAT_TYPE
            | TEXT_TYPE
            | CHAR_TYPE
            | BOOL_TYPE"""
    p[0] = p[1]

def p_assign_opt(p):
    """assign_opt : ASSIGN expr
                  | empty"""
    p[0] = p[2] if len(p) == 3 else None


# ==========================================
# ASSIGNMENT
# ==========================================

def p_assign_stmt(p):
    "assign_stmt : IDENTIFIER ASSIGN expr"
    p[0] = Assign(p[1], p[3])

def p_assign_stmt_error(p):
    "assign_stmt : IDENTIFIER ASSIGN error"
    parser.errok()
    p[0] = None


# ==========================================
# PRINT
# ==========================================

def p_print_stmt(p):
    "print_stmt : PRINT LPAREN print_items RPAREN"
    p[0] = Print(p[3])

def p_print_stmt_error(p):
    "print_stmt : PRINT error"
    parser.errok()
    p[0] = None

def p_print_items(p):
    """print_items : expr print_tail
                   | empty"""
    p[0] = [p[1]] + p[2] if len(p) == 3 else []

def p_print_tail(p):
    """print_tail : COMMA expr print_tail
                  | empty"""
    p[0] = [p[2]] + p[3] if len(p) == 4 else []


# ==========================================
# EXPRESSIONS
# ==========================================

def p_expr(p):
    """expr : expr PLUS term
            | expr MINUS term
            | term"""
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_term(p):
    """term : term MULTIPLY factor
            | term DIVIDE factor
            | term MODULO factor
            | factor"""
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_factor(p):
    """factor : INTEGER
              | FLOAT_NUMBER
              | STRING
              | TRUE
              | FALSE
              | IDENTIFIER
              | list_access
              | function_call
              | input_call
              | LPAREN expr RPAREN"""
    if len(p) == 2 and isinstance(p[1], (FunctionCall, Input, ListAccess)):
        p[0] = p[1]
    elif len(p) == 2 and p.slice[1].type == 'IDENTIFIER':
        p[0] = ('var', p[1])
    elif len(p) == 2 and p.slice[1].type == 'TRUE':
        p[0] = True
    elif len(p) == 2 and p.slice[1].type == 'FALSE':
        p[0] = False
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_factor_group_error(p):
    "factor : LPAREN error RPAREN"
    parser.errok()
    p[0] = None

def p_input_call(p):
    "input_call : INPUT LPAREN print_items RPAREN"
    p[0] = Input(p[3])


# ==========================================
# CONDITIONS
# ==========================================

def p_if_stmt(p):
    "if_stmt : IF condition THEN statement_list else_part BLOCK_END"
    p[0] = If(p[2], p[4], p[5])

def p_if_stmt_error(p):
    "if_stmt : IF error BLOCK_END"
    parser.errok()
    p[0] = None

def p_else_part(p):
    """else_part : ELSE statement_list
                 | empty"""
    p[0] = p[2] if len(p) == 3 else []

def p_condition_binary(p):
    """condition : condition AND condition
                 | condition OR condition"""
    p[0] = (p[2], p[1], p[3])

def p_condition_not(p):
    "condition : NOT condition"
    p[0] = ('nahi', p[2])

def p_condition_group(p):
    "condition : LPAREN condition RPAREN"
    p[0] = p[2]

def p_condition_relation(p):
    "condition : expr relation expr"
    p[0] = (p[2], p[1], p[3])

def p_condition_error(p):
    "condition : error"
    parser.errok()
    p[0] = None

def p_relation(p):
    """relation : GREATER
                | LESS
                | GREATER_EQUAL
                | LESS_EQUAL
                | EQUAL
                | NOT_EQUAL"""
    p[0] = p[1]


# ==========================================
# LOOPS
# ==========================================

def p_loop_stmt(p):
    """loop_stmt : FOR IDENTIFIER ASSIGN expr FROM expr TO statement_list BLOCK_END
                 | WHILE condition statement_list BLOCK_END
                 | FOR statement_list WHILE condition BLOCK_END"""
    if len(p) == 10:
        p[0] = Loop(p[2], p[4], p[6], p[8], kind="for")
    elif p.slice[1].type == 'WHILE':
        p[0] = Loop(None, p[2], None, p[3], kind="while")
    else:
        p[0] = Loop(None, p[4], None, p[2], kind="do_while")

def p_loop_stmt_error(p):
    """loop_stmt : FOR error BLOCK_END
                 | WHILE error BLOCK_END"""
    parser.errok()
    p[0] = None


# ==========================================
# FUNCTIONS
# ==========================================

def p_func_def(p):
    """func_def : FUNCTION IDENTIFIER LPAREN param_list RPAREN statement_list BLOCK_END"""
    p[0] = Function(p[2], p[4], p[6])

def p_func_def_error(p):
    "func_def : FUNCTION error BLOCK_END"
    parser.errok()
    p[0] = None

def p_param_list(p):
    """param_list : IDENTIFIER param_tail
                  | empty"""
    p[0] = [p[1]] + p[2] if len(p) == 3 else []

def p_param_tail(p):
    """param_tail : COMMA IDENTIFIER param_tail
                  | empty"""
    p[0] = [p[2]] + p[3] if len(p) == 4 else []

def p_return_stmt(p):
    "return_stmt : RETURN expr"
    p[0] = Return(p[2])

def p_function_call(p):
    "function_call : IDENTIFIER LPAREN arg_list RPAREN"
    p[0] = FunctionCall(p[1], p[3])

def p_arg_list(p):
    """arg_list : expr arg_tail
                | empty"""
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_arg_tail(p):
    """arg_tail : COMMA expr arg_tail
                | empty"""
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

# ==========================================
# LIST DECLARATION (FIXED)
# ==========================================

def p_list_decl(p):
    "list_decl : LIST IDENTIFIER ASSIGN LBRACKET list_items RBRACKET"
    p[0] = ListNode(p[2], p[5])

def p_list_decl_error(p):
    "list_decl : LIST IDENTIFIER ASSIGN LBRACKET error RBRACKET"
    parser.errok()
    p[0] = None

def p_list_items(p):
    """list_items : expr list_tail
                  | empty"""
    p[0] = [p[1]] + p[2] if len(p) == 3 else []

def p_list_tail(p):
    """list_tail : COMMA expr list_tail
                 | empty"""
    p[0] = [p[2]] + p[3] if len(p) == 4 else []

def p_list_access(p):
    "list_access : IDENTIFIER LBRACKET expr RBRACKET"
    p[0] = ListAccess(p[1], p[3])

def p_list_add(p):
    "list_add : ADD IDENTIFIER expr"
    p[0] = ListAdd(p[2], p[3])

def p_list_remove(p):
    "list_remove : REMOVE IDENTIFIER expr"
    p[0] = ListRemove(p[2], p[3])


# ==========================================
# EMPTY RULE
# ==========================================

def p_empty(p):
    "empty :"
    p[0] = None


# ==========================================
# ERROR HANDLING
# ==========================================

def find_column(token):
    line_start = token.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


def source_trace(line, column):
    if line <= 0 or line > len(source_lines):
        return ""

    text = source_lines[line - 1].rstrip('\n')
    pointer = " " * max(column - 1, 0) + "^"
    return f"    {text}\n    {pointer}"


def record_syntax_error(token, skipped=None):
    skipped = skipped or []

    if token:
        column = find_column(token)
        skipped_text = ""

        if skipped:
            skipped_preview = ", ".join(
                f"{tok.type}({tok.value!r})" for tok in skipped[:5]
            )
            if len(skipped) > 5:
                skipped_preview += ", ..."
            skipped_text = f"\n  skipped while recovering: {skipped_preview}"

        message = (
            f"Syntax Error #{len(syntax_errors) + 1}: unexpected "
            f"{token.type}({token.value!r}) at line {token.lineno}, column {column}"
            f"\n{source_trace(token.lineno, column)}"
            f"{skipped_text}"
        )
    else:
        message = f"Syntax Error #{len(syntax_errors) + 1}: unexpected EOF"

    syntax_errors.append(message)
    print(message)


def p_error(p):
    if p:
        record_syntax_error(p)
    else:
        record_syntax_error(None)


# ==========================================
# BUILD PARSER
# ==========================================

parser = yacc.yacc(write_tables=False, errorlog=yacc.NullLogger())


# ==========================================
# FUNCTION TO DISPLAY TOKENS
# ==========================================
def display_tokens(data):
    """Display all tokens from the lexer"""
    print("\n===== LEXICAL ANALYSIS (TOKENS) =====\n")
    
    # Reset lexer and feed the data
    lexer.input(data)
    
    token_list = []
    while True:
        token = lexer.token()
        if not token:
            break
        token_list.append(token)
        print(
            f"Line {token.lineno:<3} | "
            f"{token.type:<15} | "
            f"{token.value}"
        )
    
    print("\n===== LEXICAL ANALYSIS COMPLETED =====\n")
    return token_list


# ==========================================
# RUNNER
# ==========================================
if __name__ == "__main__":

    filename = input("Enter Urdu source file: ")

    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()

    syntax_errors.clear()
    lexical_errors.clear()
    source_lines[:] = data.splitlines(True)
    lexer.lineno = 1

    # Display tokens from lexer first
    display_tokens(data)

    print("\n\033[94m===== PARSING STARTED =====\033[0m\n")

    ast = parser.parse(data, lexer=lexer)

    error_count = len(syntax_errors) + len(lexical_errors)

    if error_count:
        print(f"\n\033[91m===== {error_count} ERROR(S) FOUND =====")
        print(f"Syntax errors: {len(syntax_errors)}")
        print(f"Lexer errors: {len(lexical_errors)}\033[0m\n")
        print("\n\033[94m===== PARSING COMPLETED =====\033[0m\n")
        raise SystemExit

    print("\n\033[94m===== PARSING COMPLETED =====\033[0m\n")

    print("\n\033[94m===== SEMANTIC ANALYSIS =====\033[0m\n")
    try:
        SemanticAnalyzer().analyze(ast)
    except Exception as error:
        print(f"\033[91m{error}\033[0m")
        raise SystemExit

    print("\n\033[94m===== EXECUTION START =====\033[0m\n")
    from interpreter import Interpreter

    try:
        Interpreter().run(ast)
    except Exception as error:
        print(f"\033[91m{error}\033[0m")

    print("\n\033[94m===== EXECUTION END =====\033[0m\n")
