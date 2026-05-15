# ==========================================
# URDU LANGUAGE LEXER USING PLY
# ==========================================
# Requirements:
# pip install ply
#
# Run:
# python lexer.py
#
# Then enter:
# test.urdu
# ==========================================

import ply.lex as lex

lexical_errors = []

# ==========================================
# RESERVED KEYWORDS
# ==========================================

reserved = {

    # PROGRAM STRUCTURE
    'shuru': 'START',
    'khatam': 'END',

    # DATA TYPES
    'ginti': 'INT_TYPE',
    'decimal': 'FLOAT_TYPE',
    'text': 'TEXT_TYPE',
    'harf': 'CHAR_TYPE',
    'sachjhoot': 'BOOL_TYPE',

    # CONDITIONS
    'agar': 'IF',
    'warna': 'ELSE',
    'then': 'THEN',
    'bas': 'BLOCK_END',

    # LOOPS
    'bar_bar': 'FOR',
    'jabtak': 'WHILE',

    # FUNCTIONS
    'kaam': 'FUNCTION',
    'wapas': 'RETURN',

    # INPUT / OUTPUT
    'dikhao': 'PRINT',
    'lo': 'INPUT',
    'likho': 'INPUT',

    # LISTS
    'list': 'LIST',
    'dalo': 'ADD',
    'nikalo': 'REMOVE',

    # BOOLEAN VALUES
    'sach': 'TRUE',
    'jhoot': 'FALSE',

    # LOGICAL OPERATORS
    'aur': 'AND',
    'ya': 'OR',
    'nahi': 'NOT',

    # LOOP RANGE
    'se': 'FROM',
    'tak': 'TO'
}

# ==========================================
# TOKEN LIST
# ==========================================

tokens = [

    # IDENTIFIERS + LITERALS
    'IDENTIFIER',
    'INTEGER',
    'FLOAT_NUMBER',
    'STRING',

    # ARITHMETIC OPERATORS
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'MODULO',

    # ASSIGNMENT / COMPARISON
    'ASSIGN',
    'EQUAL',
    'NOT_EQUAL',

    'GREATER',
    'LESS',
    'GREATER_EQUAL',
    'LESS_EQUAL',

    # SYMBOLS
    'LPAREN',
    'RPAREN',

    'LBRACKET',
    'RBRACKET',

    'COMMA'

] + list(dict.fromkeys(reserved.values()))

# ==========================================
# OPERATORS
# ==========================================

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'

# IMPORTANT:
# Longer operators FIRST

t_EQUAL = r'=='
t_NOT_EQUAL = r'!='

t_GREATER_EQUAL = r'>='
t_LESS_EQUAL = r'<='

t_GREATER = r'>'
t_LESS = r'<'

t_ASSIGN = r'='

# ==========================================
# SYMBOLS
# ==========================================

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_LBRACKET = r'\['
t_RBRACKET = r'\]'

t_COMMA = r','

# ==========================================
# IGNORE SPACES/TABS
# ==========================================

t_ignore = ' \t'

# ==========================================
# SINGLE LINE COMMENTS
# Example:
# # this is comment
# ==========================================

def t_COMMENT(t):
    r'\#.*'
    pass

# ==========================================
# MULTI LINE COMMENTS
# Example:
# ###
# hello
# ###
# ==========================================

def t_MULTILINE_COMMENT(t):
    r'\#\#\#(.|\n)*?\#\#\#'
    t.lexer.lineno += t.value.count('\n')
    pass

# ==========================================
# FLOAT NUMBERS
# ==========================================

def t_FLOAT_NUMBER(t):
    r'\d+\.\d+'

    t.value = float(t.value)

    return t

# ==========================================
# INTEGER NUMBERS
# ==========================================

def t_INTEGER(t):
    r'\d+'

    t.value = int(t.value)

    return t

# ==========================================
# STRING
# Example:
# "Hello"
# ==========================================

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'

    # remove quotes
    t.value = t.value[1:-1]

    return t

# ==========================================
# IDENTIFIERS / RESERVED WORDS
# ==========================================

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'

    # check reserved keywords
    t.type = reserved.get(t.value, 'IDENTIFIER')

    return t

# ==========================================
# NEWLINES
# ==========================================

def t_newline(t):
    r'\n+'

    t.lexer.lineno += len(t.value)

# ==========================================
# ERROR HANDLING
# ==========================================

def t_error(t):
    line_start = t.lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
    column = (t.lexpos - line_start) + 1
    message = (
        f"Lexer Error: Invalid character '{t.value[0]}' "
        f"at line {t.lineno}, column {column}"
    )

    lexical_errors.append(message)
    print(message)

    t.lexer.skip(1)

# ==========================================
# BUILD LEXER
# ==========================================

lexer = lex.lex()

# ==========================================
# MAIN DRIVER
# ==========================================

if __name__ == "__main__":

    print("\n\033[94m===== URDU LANGUAGE LEXER =====\033[0m\n")

    filename = input("Enter source file name (.urdu only): ").strip()

    # Check file extension
    if not filename.endswith(".urdu"):
        print("\n\033[91mError: Only '.urdu' files are allowed\033[0m")
        exit()

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = file.read()

    except FileNotFoundError:
        print(f"\n\033[91mError: File '{filename}' not found\033[0m")
        exit()

    # feed source code to lexer
    lexer.input(data)

    print("\n\033[94m===== TOKENS =====\033[0m\n")

    # tokenize input
    while True:

        token = lexer.token()

        if not token:
            break

        print(
            f"\033[96mLine {token.lineno:<3} | "
            f"{token.type:<15} | "
            f"{token.value}\033[0m"
        )

    print("\n\033[94m===== LEXICAL ANALYSIS COMPLETED =====\033[0m\n")