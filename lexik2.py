import re

# Определите токены
TOKENS = [
    ("NUMBER", r"\d+"),         # Числа
    ("IDEN", r"[a-zA-Z_][a-zA-Z0-9_]*"),  # Идентификаторы
    ('NOT_EQUAL', r'≠'),
    ('EQUAL', r'=='),
    ('LESS_EQUAL', r'<='),
    ('LESS_THAN', r'<'),
    ('GREATER_EQUAL', r'>='),
    ('GREATER_THAN', r'>'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MULTIPLY', r'\*'),
    ('LOGICAL_OR', r'\|\|'),
    ('DIVIDE', r'/'),
    ('LOGICAL_AND', r'&&'),
    ('LOGICAL_NOT', r'!'),
    ("SPACE", r"\s+"),     # Пробелы (будем игнорировать)
]


# Компилируем регулярные выражения
token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKENS)
compiled_re = re.compile(token_regex)

def lexer(text):
    tokens = []
    for match in compiled_re.finditer(text):
        token_type = match.lastgroup
        value = match.group(token_type)#
        if token_type != "SPACE":#Не пробел
            tokens.append((token_type, value))

    return tokens

# Пример использования
# source_code = "x = 42 + (y * 7)"

f = open("input.txt").readlines()
inp_file = ""
for i in range(len(f)):
    inp_file+=str(f[i])
try:
    print(lexer(inp_file))
except ValueError as e:
    print(f"Error: {e}")
