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
    'writeln': 'WRITELN',
    'to':'TO',
    'step':'STEP'
}

token_specification = [
    # Операторы:
    ('NEQ', r'!='),
    # ('EQ', r'=='),
    # ('EQ1', r'='),
    ('EQ', r'=='),
    ('LE', r'≤'),
    ('GE', r'≥'),
    ('LT', r'<'),
    ('GT', r'>'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('OR', r'\|\|'),
    ('MUL', r'\*'),
    ('DIV', r'/'),
    ('AND', r'&&'),
    ('NOT', r'!'),

    # Литералы:
    ('NUMBER', r'\d+(\.\d+)?'),  # Число (целое или с плавающей точкой)
    ('INDENT', r'[A-Za-z_][A-Za-z0-9_]*'),  # Идентификаторы

    # Прочие токены:
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t\r]+'),  # Пробелы, табы, возвраты каретки

    # Для наихудшего случая - любой неподходящий символ
    ('MISMATCH', r'.'),
]

# Компилируем одно большое регулярное выражение
token_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in token_specification))


def tokenize(code):
    line_num = 1
    line_start = 0
    for mo in token_re.finditer(code):
        kind = mo.lastgroup#Название группы, к которой отнеслось часть выражения
        value = mo.group()

        if kind == 'NUMBER':
            # Преобразуем строку числа в число (int или float)
            value = float(value) if '.' in value else int(value)

        elif kind == 'INDENT':
            # Проверяем, не является ли идентификатор ключевым словом
            if value in KEYWORDS:
                kind = KEYWORDS[value]

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