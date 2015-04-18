from upl import lexer, parser, semantic_analyzer
import json

if __name__ == "__main__":
    program = """
    def add = (a: int, b: int) -> int {
        a;
    };
    def fib = (b: int) -> int {
        if true then 1 else 2
    };
    """
    tokens = lexer.tokenize_program(program)
    parse_tree = parser.Parser(tokens).parse()
    consts, funcs = semantic_analyzer.SemanticAnalyzer(parse_tree).analyze()
    for func in funcs:
        print json.dumps(func.to_dict(), indent=2)
        print ""

