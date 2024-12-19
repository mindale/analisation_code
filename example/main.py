from src.lexer import LexicalAnalyzer
from src.parser import SyntaxAnalyzer
from src.semantic_analyzer import SemanticAnalyzer
from src.interpreter import Interpreter

def process_file(file_path):
    """
    Обработка файла с программой на модельном языке
    """
    try:
        with open(file_path, 'r') as file:
            code = file.read()
        
        # Лексический анализ
        lexer = LexicalAnalyzer()
        tokens = lexer.tokenize(code)
        print("Лексический анализ завершен. Токены:")
        for token in tokens:
            print(f"{token.type}: {token.value}")

        # Синтаксический анализ
        parser = SyntaxAnalyzer(tokens)
        ast = parser.parse()
        print("\nАбстрактное синтаксическое дерево сформировано.")

        # Семантический анализ
        semantic_analyzer = SemanticAnalyzer(parser.symbol_table)
        is_semantically_valid = semantic_analyzer.analyze(ast)
        
        if not is_semantically_valid:
            print("\nОбнаружены семантические ошибки:")
            for error in semantic_analyzer.errors:
                print(f"- {error}")
            return

        # Интерпретация
        interpreter = Interpreter(parser.symbol_table)
        interpreter.interpret(ast)
        
        print("\nПрограмма успешно выполнена.")
        print("Значения переменных:")
        for var, value in interpreter.variable_values.items():
            print(f"{var}: {value}")

    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")

def main():
    sample_code = '''
    program var
        A int;
        B float;
        C bool;
        X int;
    begin
        A as 5;
        B as 3.14;
        C as true;
        {test comment}
        if A GT 3 then
            X as A mult 2
        else
            X as A div 2;

        [B as B plus 10.5;
        C as false];

        for X as 1 to 5 do
            write(X);

        while C do
            [X as X min 1;
            if X EQ 0 then
                C as false];
    end.
    '''


    lexer = LexicalAnalyzer()
    tokens = lexer.tokenize(sample_code)

    parser = SyntaxAnalyzer(tokens)
    ast = parser.parse()

    interpreter = Interpreter(parser.symbol_table)
    interpreter.interpret(ast)

    print("Значения переменных после интерпретации:")
    for var, value in interpreter.variable_values.items():
        print(f"{var}: {value}")

if __name__ == "__main__":
    main()