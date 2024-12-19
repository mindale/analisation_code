from typing import Dict, Any
from src.parser import ASTNode
from src.semantic_analyzer import SemanticAnalyzer

class Interpreter:
    def __init__(self, symbol_table: Dict[str, Dict]):
        self.symbol_table = symbol_table
        self.variable_values: Dict[str, Any] = {}

    def interpret(self, ast: ASTNode):
        """
        Интерпретация абстрактного синтаксического дерева
        """
        semantic_analyzer = SemanticAnalyzer(self.symbol_table)
        
        # Продолжаем интерпретацию даже при наличии предупреждений
        semantic_analyzer.analyze(ast)
        
        self.execute_node(ast)

    def execute_node(self, node: ASTNode):
        """
        Рекурсивное выполнение узлов AST
        """
        if node.type == 'Program':
            for child in node.children:
                self.execute_node(child)
        
        elif node.type == 'VariableDeclarations':
            self.initialize_variables(node)
        
        elif node.type == 'StatementBlock':
            for statement in node.children:
                self.execute_statement(statement)

    def initialize_variables(self, node: ASTNode):
        """
        Инициализация переменных с нулевыми значениями
        """
        for decl in node.children:
            identifier = decl.value['identifier']
            var_type = decl.value['type']
            
            default_values = {
                'int': 0,
                'float': 0.0,
                'bool': False
            }
            
            self.variable_values[identifier] = default_values.get(var_type)

    def execute_statement(self, node: ASTNode):
        """
        Выполнение различных типов операторов
        """
        if node.type == 'Assignment':
            self.execute_assignment(node)
        elif node.type == 'ConditionalStatement':
            self.execute_conditional(node)
        elif node.type == 'ForLoop':
            self.execute_for_loop(node)
        elif node.type == 'WhileLoop':
            self.execute_while_loop(node)
        elif node.type == 'Block':
            for statement in node.children:
                self.execute_statement(statement)
        elif node.type == 'WriteStatement':
            self.execute_write(node)

    def execute_write(self, node: ASTNode):
        """
        Выполнение оператора write()
        """
        expression_value = self.evaluate_expression(node.children[0])
        print(f"WRITE: {expression_value}")  # Базовая реализация вывода

    def execute_assignment(self, node: ASTNode):
        """
        Выполнение операции присваивания
        """
        identifier = node.value['identifier']
        expression_value = self.evaluate_expression(node.children[0])
        self.variable_values[identifier] = expression_value

    def execute_conditional(self, node: ASTNode):
        """
        Выполнение условного оператора
        """
        condition_result = self.evaluate_expression(node.children[0])
        
        if condition_result:
            self.execute_statement(node.children[1])
        elif len(node.children) > 2 and node.children[2]:
            self.execute_statement(node.children[2])

    def execute_for_loop(self, node: ASTNode):
        """
        Выполнение цикла for
        """
        # Инициализация счетчика
        self.execute_statement(node.children[0])
        
        # Получаем имя переменной-счетчика
        counter_var = node.children[0].value['identifier']
        
        # Предел цикла
        limit = self.evaluate_expression(node.children[1])
        
        # Тело цикла
        body = node.children[2]
        
        while self.variable_values[counter_var] <= limit:
            self.execute_statement(body)
            # Инкремент счетчика
            self.variable_values[counter_var] += 1

    def execute_while_loop(self, node: ASTNode):
        """
        Выполнение цикла while
        """
        condition = node.children[0]
        body = node.children[1]
        
        while self.evaluate_expression(condition):
            self.execute_statement(body)

    def evaluate_expression(self, node: ASTNode):
        """
        Вычисление значения выражения
        """
        if node.type == 'Number':
            return float(node.value)
        elif node.type == 'BooleanConstant':
            return node.value == 'true'
        elif node.type == 'Identifier':
            return self.variable_values.get(node.value)
        elif node.type == 'Comparison':
            op = node.value['operator']
            left = self.evaluate_expression(node.children[0])
            right = self.evaluate_expression(node.children[1])
            
            # Реализация операторов сравнения
            if op == 'GT':
                return left > right
            elif op == 'LT':
                return left < right
            elif op == 'EQ':
                return left == right
            elif op == 'GE':
                return left >= right
            elif op == 'LE':
                return left <= right
            elif op == 'NE':
                return left != right
        elif node.type == 'BinaryOperation':
            op = node.value['operator']
            left = self.evaluate_expression(node.children[0])
            right = self.evaluate_expression(node.children[1])
            
            if op == 'mult':
                return left * right
            elif op == 'div':
                return left / right
            elif op == 'plus':
                return left + right
            elif op == 'min':
                return left - right

        return None