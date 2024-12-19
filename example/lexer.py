import enum
from typing import List, NamedTuple

class TokenType(enum.Enum):
    KEYWORD = 1
    IDENTIFIER = 2
    NUMBER = 3
    OPERATOR = 4
    DELIMITER = 5
    BOOLEAN = 6
    COMMENT = 7

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

class LexicalAnalyzer:
    def __init__(self):
        self.keywords = {
            'program', 'var', 'begin', 'end', 'int', 'float', 'bool',
            'if', 'then', 'else', 'for', 'to', 'do', 'while', 
            'true', 'false', 'write'  # Добавлен 'write'
        }
        self.relation_ops = {'NE', 'EQ', 'LT', 'LE', 'GT', 'GE'}
        self.addition_ops = {'plus', 'min', 'or'}
        self.multiplication_ops = {'mult', 'div', 'and'}

    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        lines = code.split('\n')

        multi_char_ops = self.relation_ops.union(
            self.addition_ops).union(self.multiplication_ops).union({'as'})

        for line_num, line in enumerate(lines, 1):
            column = 0
            while column < len(line):
                if line[column].isspace():
                    column += 1
                    continue

                # Комментарии
                if line[column:column+1] == '{':
                    end_comment = line.find('}', column)
                    if end_comment != -1:
                        column = end_comment + 1
                        continue
                    else:
                        raise SyntaxError(f"Незакрытый комментарий на строке {line_num}")

                # Специальный случай: end.
                if line[column:].startswith('end.'):
                    tokens.append(Token(TokenType.KEYWORD, 'end.', line_num, column))
                    column += len('end.')
                    continue

                # Многосимвольные операторы
                for op in multi_char_ops:
                    if line[column:].startswith(op):
                        tokens.append(Token(TokenType.OPERATOR, op, line_num, column))
                        column += len(op)
                        break
                else:
                    # Идентификаторы и ключевые слова
                    if line[column].isalpha():
                        start = column
                        while column < len(line) and (line[column].isalnum()):
                            column += 1
                        value = line[start:column]
                        token_type = (TokenType.KEYWORD if value in self.keywords 
                                      else TokenType.IDENTIFIER)
                        tokens.append(Token(token_type, value, line_num, start))
                        continue

                    # Числа
                    if line[column].isdigit() or (line[column] == '.' and column + 1 < len(line) and line[column + 1].isdigit()):
                        start = column
                        has_dot = False
                        while (column < len(line) and 
                               (line[column].isdigit() or (line[column] == '.' and not has_dot))):
                            if line[column] == '.':
                                has_dot = True
                            column += 1
                        value = line[start:column]
                        tokens.append(Token(TokenType.NUMBER, value, line_num, start))
                        continue

                    # Простые операторы и разделители
                    simple_ops = {'+', '-', '*', '/', '(', ')', ':', ';', '[', ']'}
                    if line[column] in simple_ops:
                        tokens.append(Token(
                            TokenType.DELIMITER if line[column] in '();:[]' else TokenType.OPERATOR,
                            line[column], line_num, column))
                        column += 1
                        continue

                    # Неизвестный символ
                    raise SyntaxError(f"Неизвестный символ: {line[column]} на строке {line_num}, позиция {column}")

        return tokens


def main():
    sample_code = '''
    program var
    A int;
    B float;
    begin
        A as 10;
        B as 3.14
    end.
    '''
    
    lexer = LexicalAnalyzer()
    tokens = lexer.tokenize(sample_code)

    for token in tokens:
        print(f"{token.type}: {token.value} (line {token.line}, column {token.column})")

if __name__ == "__main__":
    main()
