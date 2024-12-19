from typing import List, Dict, Any
from src.lexer import Token, TokenType

class ASTNode:
    def __init__(self, type: str, value: Dict[str, Any] = None, children: List['ASTNode'] = None):
        self.type = type
        self.value = value or {}
        self.children = children or []

class SyntaxAnalyzer:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_token_index = 0
        self.symbol_table: Dict[str, Dict] = {}

    def parse(self) -> ASTNode:
        """
        Основной метод парсинга программы
        """
        return self.parse_program()

    def parse_program(self) -> ASTNode:
        """
        Парсинг структуры программы
        """
        self.consume_token('KEYWORD', 'program')
        self.consume_token('KEYWORD', 'var')
        
        # Парсинг объявлений переменных
        variable_declarations = self.parse_variable_declarations()
        
        self.consume_token('KEYWORD', 'begin')
        
        # Парсинг блока операторов
        statement_block = self.parse_statement_block()
        
        self.consume_token('KEYWORD', 'end.')
        
        return ASTNode('Program', children=[
            variable_declarations,
            statement_block
        ])

    def parse_block(self) -> ASTNode:
        """
        Парсинг блока операторов в квадратных скобках
        """
        self.consume_token('DELIMITER', '[')
        block_statements = ASTNode('Block')
        
        while not self.is_token('DELIMITER', ']'):
            statement = self.parse_statement()
            block_statements.children.append(statement)
            
            if self.is_token('DELIMITER', ';'):
                self.consume_token('DELIMITER', ';')
        
        self.consume_token('DELIMITER', ']')
        return block_statements

    def parse_comparison(self) -> ASTNode:
        """
        Парсинг сравнений (GT, LT, EQ и т.д.)
        """
        left = self.parse_expression()
        
        if self.is_token('OPERATOR') and self.current_token().value in {'GT', 'LT', 'EQ', 'GE', 'LE', 'NE'}:
            op = self.current_token().value
            self.consume_token('OPERATOR')
            right = self.parse_expression()
            
            return ASTNode('Comparison', 
                        value={'operator': op},
                        children=[left, right])
        
        return left

    def parse_variable_declarations(self) -> ASTNode:
        """
        Парсинг объявлений переменных
        """
        declarations = ASTNode('VariableDeclarations')
    
        while self.current_token().type == TokenType.IDENTIFIER:
            identifier = self.current_token().value
            self.consume_token('IDENTIFIER')  # Имя переменной
            
            self.consume_token('KEYWORD')  # Тип переменной (int, float, bool)
            var_type = self.tokens[self.current_token_index - 1].value
            
            self.consume_token('DELIMITER', ';')  # Конец объявления
            
            # Добавление в таблицу символов
            self.symbol_table[identifier] = {'type': var_type}
            
            declarations.children.append(
                ASTNode('VariableDeclaration', 
                        value={'identifier': identifier, 'type': var_type})
            )
    
        return declarations

    def parse_for_loop(self) -> ASTNode:
        """
        Парсинг цикла for
        """
        self.consume_token('KEYWORD', 'for')
        
        # Инициализация счетчика
        initialization = self.parse_assignment()
        
        self.consume_token('KEYWORD', 'to')
        
        # Предел цикла
        limit = self.parse_expression()
        
        self.consume_token('KEYWORD', 'do')
        
        # Тело цикла
        body = self.parse_statement()
        
        return ASTNode('ForLoop', 
                    children=[initialization, limit, body])

    def parse_while_loop(self) -> ASTNode:
        """
        Парсинг цикла while
        """
        self.consume_token('KEYWORD', 'while')
        
        # Условие цикла
        condition = self.parse_expression()
        
        self.consume_token('KEYWORD', 'do')
        
        # Тело цикла
        body = self.parse_statement()
        
        return ASTNode('WhileLoop', 
                    children=[condition, body])

    def parse_statement_block(self) -> ASTNode:
        """
        Парсинг блока операторов
        """
        statements = ASTNode('StatementBlock')
        
        while not self.is_token('KEYWORD', 'end.'):  # Завершаем, если встречаем 'end.'
            statement = self.parse_statement()
            statements.children.append(statement)
            
            # Условие для разделителя между операторами
            if self.is_token('DELIMITER', ';'):
                self.consume_token('DELIMITER', ';')
            else:
                break
        
        return statements


    def parse_statement(self) -> ASTNode:
        """
        Парсинг отдельного оператора с поддержкой различных типов операторов
        """
        # Вызов функции write
        if self.is_token('KEYWORD', 'write'):
            return self.parse_write_statement()

        # Условный оператор
        if self.is_token('KEYWORD', 'if'):
            return self.parse_conditional()
        
        # Присваивание
        if self.is_token('IDENTIFIER'):
            return self.parse_assignment()
        
        # Цикл for
        if self.is_token('KEYWORD', 'for'):
            return self.parse_for_loop()
        
        # Цикл while
        if self.is_token('KEYWORD', 'while'):
            return self.parse_while_loop()
        
        # Блок операторов в квадратных скобках
        if self.is_token('DELIMITER', '['):
            return self.parse_block()
        
        raise SyntaxError(f"Неожиданный токен: {self.current_token().value}")

    def parse_assignment(self) -> ASTNode:
        """
        Парсинг операции присваивания
        """
        identifier = self.current_token().value
        self.consume_token('IDENTIFIER')
        
        self.consume_token('OPERATOR', 'as')
        
        expression = self.parse_expression()
        
        return ASTNode('Assignment', 
                       value={'identifier': identifier},
                       children=[expression])

    def parse_expression(self) -> ASTNode:
        """
        Парсинг выражения с поддержкой арифметических операций
        """
        # Логическая константа
        if self.is_token('KEYWORD', 'true') or self.is_token('KEYWORD', 'false'):
            value = self.current_token().value
            self.consume_token('KEYWORD')
            return ASTNode('BooleanConstant', value=value)

        # Число
        if self.is_token('NUMBER'):
            value = self.current_token().value
            self.consume_token('NUMBER')
            return ASTNode('Number', value=value)

        # Идентификатор
        if self.is_token('IDENTIFIER'):
            value = self.current_token().value
            self.consume_token('IDENTIFIER')
            
            # Проверка на арифметическую операцию
            if self.is_token('OPERATOR') and self.current_token().value in {'mult', 'div', 'plus', 'min'}:
                op = self.current_token().value
                self.consume_token('OPERATOR')
                right = self.parse_expression()
                
                return ASTNode('BinaryOperation', 
                            value={'operator': op},
                            children=[
                                ASTNode('Identifier', value=value),
                                right
                            ])
            
            return ASTNode('Identifier', value=value)

        # Если ничего не подошло
        raise SyntaxError(f"Неожиданный токен в выражении: {self.current_token().value}")

    def parse_write_statement(self) -> ASTNode:
        """
        Парсинг оператора write()
        """
        self.consume_token('KEYWORD', 'write')  # Исправлено с IDENTIFIER на KEYWORD
        self.consume_token('DELIMITER', '(')
        
        # Разрешаем передачу выражений в write
        expression = self.parse_expression()
        
        self.consume_token('DELIMITER', ')')
        
        return ASTNode('WriteStatement', children=[expression])


    def current_token(self) -> Token:
        """
        Получение текущего токена
        """
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        raise SyntaxError("Неожиданный конец токенов")

    def consume_token(self, expected_type: str = None, expected_value: str = None):
        current = self.current_token()
        print(f"Проверяется токен: {current.type}, значение: {current.value}")  # Для отладки
        if expected_type and current.type != TokenType[expected_type]:
            raise SyntaxError(f"Ожидался токен типа {expected_type}, получен {current.type}")
        if expected_value and current.value != expected_value:
            raise SyntaxError(f"Ожидалось значение '{expected_value}', получено '{current.value}'")
        self.current_token_index += 1

    def parse_conditional(self) -> ASTNode:
        """
        Парсинг условного оператора if-then-else с расширенной поддержкой
        """
        self.consume_token('KEYWORD', 'if')
        
        # Условие
        condition = self.parse_comparison()
        
        self.consume_token('KEYWORD', 'then')
        
        # Ветвь then
        true_branch = self.parse_statement()
        
        # Необязательная ветвь else
        false_branch = None
        if self.is_token('KEYWORD', 'else'):
            self.consume_token('KEYWORD', 'else')
            false_branch = self.parse_statement()
        
        return ASTNode('ConditionalStatement', 
                    children=[condition, true_branch, false_branch] if false_branch else [condition, true_branch])


    def is_token(self, token_type: str, token_value: str = None) -> bool:
        """
        Проверка текущего токена
        """
        current = self.current_token()
        
        if current.type != TokenType[token_type]:
            return False
        
        if token_value and current.value != token_value:
            return False
        
        return True