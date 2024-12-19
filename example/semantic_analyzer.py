from typing import Dict, Any
from src.parser import ASTNode, TokenType

class SemanticAnalyzer:
    def __init__(self, symbol_table: Dict[str, Dict]):
        self.symbol_table = symbol_table
        self.errors = []

    def analyze(self, ast: ASTNode):
        """
        Основной метод семантического анализа
        """
        self.validate_node(ast)
        
        # Вместо остановки, просто выводим ошибки
        if self.errors:
            for error in self.errors:
                print(f"Semantic Error: {error}")
            return False
        return True

    def validate_node(self, node: ASTNode):
        """
        Рекурсивный обход AST для семантической проверки
        """
        if node.type == 'Program':
            for child in node.children:
                self.validate_node(child)
        
        elif node.type == 'VariableDeclarations':
            self.validate_variable_declarations(node)
        
        elif node.type == 'StatementBlock':
            for statement in node.children:
                self.validate_statement(statement)
        
        elif node.type == 'Block':
            for statement in node.children:
                self.validate_statement(statement)

    def validate_variable_declarations(self, node: ASTNode):
        """
        Проверка корректности объявления переменных
        """
        declared_identifiers = set()
        for decl in node.children:
            identifier = decl.value['identifier']
            var_type = decl.value['type']
            
            # Проверка на повторное объявление
            if identifier in declared_identifiers:
                self.errors.append(f"Переменная {identifier} объявлена дважды")
            declared_identifiers.add(identifier)

    def validate_statement(self, node: ASTNode):
        """
        Проверка корректности операторов
        """
        if node.type == 'Assignment':
            self.validate_assignment(node)
        elif node.type == 'ConditionalStatement':
            self.validate_conditional(node)
        elif node.type == 'ForLoop':
            self.validate_for_loop(node)
        elif node.type == 'WhileLoop':
            self.validate_while_loop(node)
        elif node.type == 'Block':
            for statement in node.children:
                self.validate_statement(statement)
        elif node.type == 'WriteStatement':
            self.validate_write_statement(node)

    def validate_write_statement(self, node: ASTNode):
        """
        Проверка корректности оператора write()
        """
        expression_type = self.infer_expression_type(node.children[0])
        
        # Проверяем, что тип выражения допустим для вывода
        allowed_types = ['int', 'float', 'bool']
        if expression_type not in allowed_types:
            self.errors.append(
                f"Недопустимый тип для write(): {expression_type}. "
                f"Разрешены: {', '.join(allowed_types)}"
            )

    def validate_assignment(self, node: ASTNode):
        """
        Проверка корректности присваивания
        """
        identifier = node.value['identifier']
        
        # Проверка, что переменная объявлена
        if identifier not in self.symbol_table:
            self.errors.append(f"Необъявленная переменная {identifier}")
            return

        var_type = self.symbol_table[identifier]['type']
        expression_type = self.infer_expression_type(node.children[0])
        
        if not self.is_type_compatible(var_type, expression_type):
            self.errors.append(
                f"Несовместимые типы при присваивании. "
                f"Переменная {identifier} типа {var_type}, "
                f"выражение типа {expression_type}"
            )

    def validate_conditional(self, node: ASTNode):
        """
        Проверка корректности условного оператора
        """
        # Проверка условия
        condition = node.children[0]
        if condition.type == 'Comparison':
            self.validate_comparison(condition)
        
        # Проверка веток then и else
        for branch in node.children[1:]:
            if branch:
                self.validate_statement(branch)

    def validate_comparison(self, node: ASTNode):
        """
        Проверка корректности сравнения
        """
        left_type = self.infer_expression_type(node.children[0])
        right_type = self.infer_expression_type(node.children[1])
        
        if not self.is_numeric_type(left_type) or not self.is_numeric_type(right_type):
            self.errors.append(f"Сравнение не может быть выполнено для типов {left_type} и {right_type}")

    def validate_for_loop(self, node: ASTNode):
        """
        Проверка корректности цикла for
        """
        initialization = node.children[0]
        limit = node.children[1]
        body = node.children[2]
        
        # Проверка инициализации
        if initialization.type == 'Assignment':
            self.validate_assignment(initialization)
        
        # Проверка предела цикла
        limit_type = self.infer_expression_type(limit)
        if not self.is_numeric_type(limit_type):
            self.errors.append(f"Предел цикла должен быть числом, получен тип {limit_type}")
        
        # Проверка тела цикла
        self.validate_statement(body)

    def validate_while_loop(self, node: ASTNode):
        """
        Проверка корректности цикла while
        """
        condition = node.children[0]
        body = node.children[1]
        
        condition_type = self.infer_expression_type(condition)
        if condition_type != 'bool':
            self.errors.append(f"Условие цикла должно быть булевым, получен тип {condition_type}")
        
        # Проверка тела цикла
        self.validate_statement(body)

    def infer_expression_type(self, node: ASTNode) -> str:
        """
        Определение типа выражения
        """
        if node.type == 'Number':
            return 'float' if '.' in node.value else 'int'
        elif node.type == 'Identifier':
            # Возвращаем тип из таблицы символов
            return self.symbol_table.get(node.value, {}).get('type')
        elif node.type == 'BooleanConstant':
            return 'bool'
        elif node.type == 'Comparison':
            return 'bool'
        elif node.type == 'BinaryOperation':
            left_type = self.infer_expression_type(node.children[0])
            right_type = self.infer_expression_type(node.children[1])
            
            if self.is_numeric_type(left_type) and self.is_numeric_type(right_type):
                return 'float' if 'float' in [left_type, right_type] else 'int'
        
        return 'unknown'

    def is_type_compatible(self, var_type: str, expr_type: str) -> bool:
        """
        Проверка совместимости типов
        """
        type_compatibility = {
            'int': ['int'],
            'float': ['int', 'float'],
            'bool': ['bool']
        }
        return expr_type in type_compatibility.get(var_type, [])

    def is_numeric_type(self, type_name: str) -> bool:
        """
        Проверка, является ли тип числовым
        """
        return type_name in ['int', 'float']