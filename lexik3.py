import re
#не рассматривать в качестве регулярных выражений -> рассматривать в качестве состояний
#В качетсве регулярных выражений можно проверять состояния буферов и тп
# Список ключевых слов
KEYWORDS = {
    'begin': 'BEGIN',
    'if': 'IF',
    'end': 'END',
    'for': 'FOR',
    'while': 'WHILE',
    'next': 'NEXT',
    'readln': 'READLN',
    'writeln': 'WRITELN'
}

# Обновленные спецификации токенов с учётом комментариев и новых форм чисел
token_specification = [
    # Комментарии вида (* ... *), которые могут быть многострочными
    # Используем DOTALL, чтобы '.' матчился с переводом строки.
    ('COMMENT',    r'\(\*.*?\*\)'),

    # Операторы:
    ('NEQ',       r'≠'),
    ('EQ',        r'='),
    ('LE',        r'≤'),
    ('GE',        r'≥'),
    ('LT',        r'<'),
    ('GT',        r'>'),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('OR',        r'\|\|'),
    ('MUL',       r'\*'),
    ('DIV',       r'/'),
    ('AND',       r'&&'),
    ('NOT',       r'!'),

    # Числа различных систем счисления:
    # Двоичное: [01]+[Bb]
    # Восьмеричное: [0-7]+[Oo]
    # Десятичное: \d+[Dd]?
    # Шестнадцатеричное: [0-9A-Fa-f]+[Hh]
    ('NUMBER',    r'[01]+[Bb]|[0-7]+[Oo]|\d+[Dd]?|[0-9A-Fa-f]+[Hh]'),

    # Идентификаторы:
    ('ID',        r'[A-Za-z_][A-Za-z0-9_]*'),

    # Пропуски:
    ('NEWLINE',   r'\n'),
    ('SKIP',      r'[ \t\r]+'),

    # Любой непредвиденный символ:
    ('MISMATCH',  r'.'),
]

# Компилируем одно большое регулярное выражение
token_re = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification), re.DOTALL)


def tokenize(code):
    line_num = 1
    line_start = 0
    for mo in token_re.finditer(code):
        kind = mo.lastgroup#Название группы, к которой отнеслось часть выражения
        value = mo.group()
        # print(value, kind, "\n")
        if kind == 'COMMENT':
            # Пропускаем комментарии, не выдавая токен
            continue



        elif kind == 'NUMBER':

            num_str = value

            last_char = num_str[-1]

            if last_char in ('B', 'b'):

                # Двоичное

                digits = num_str[:-1]

                if not all(ch in '01' for ch in digits):
                    raise RuntimeError(f'Недопустимый символ в двоичном числе {value!r} на строке {line_num}')

            elif last_char in ('O', 'o'):

                # Восьмеричное

                digits = num_str[:-1]

                if not all(ch in '01234567' for ch in digits):
                    raise RuntimeError(f'Недопустимый символ в восьмеричном числе {value!r} на строке {line_num}')

            elif last_char in ('D', 'd'):

                # Десятичное с суффиксом

                digits = num_str[:-1]

                if not all(ch.isdigit() for ch in digits):
                    raise RuntimeError(f'Недопустимый символ в десятичном числе {value!r} на строке {line_num}')

            elif last_char in ('H', 'h'):

                # Шестнадцатеричное

                digits = num_str[:-1]

                if not all(ch in '0123456789ABCDEFabcdef' for ch in digits):
                    raise RuntimeError(f'Недопустимый символ в шестнадцатеричном числе {value!r} на строке {line_num}')

            else:

                # Десятичное без суффикса

                digits = num_str

                if not all(ch.isdigit() for ch in digits):
                    raise RuntimeError(f'Недопустимый символ в десятичном числе {value!r} на строке {line_num}')

        elif kind == 'ID':
            # Проверяем, не является ли идентификатор ключевым словом
            if value.lower() in KEYWORDS:
                kind = KEYWORDS[value.lower()]

        elif kind == 'NEWLINE':
            # Подсчёт строк
            line_start = mo.end()
            line_num += 1
            continue

        elif kind == 'SKIP':
            # Пропускаем пробелы и табуляции
            continue

        elif kind == 'MISMATCH':
            # Если встретился символ, не подходящий под никакие шаблоны
            raise RuntimeError(f'Неожиданный символ {value!r} на строке {line_num}')

        # Возвращаем токен в формате (тип, значение, номер строки, позиция в строке)
        yield kind, value, line_num, mo.start() - line_start





f = open("input.txt").readlines()
code = ""
for i in range(len(f)):
    code+=str(f[i])
# print(code)
fe = open("output_lexer.txt", "w")
try:
    for token in tokenize(code):
        print(token)
        fe.write(str(token) + '\n')
except ValueError as e:
    print(f"Error: {e}")