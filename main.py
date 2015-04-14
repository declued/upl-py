from upl import lexer, parser, semantic_analyzer
import json

if __name__ == "__main__":
    program = """
    def add = (a: int, b: int) -> int {
        a;
    };
    def x = (b: int) -> int {
        var c = add(b, 4);
        add(c, 1);
    };
    """
    tokens = lexer.tokenize_program(program)
    parse_tree = parser.Parser(tokens).parse()
    funcs = semantic_analyzer.SemanticAnalyzer(parse_tree).analyze()
    for func in funcs:
        print json.dumps(func.to_dict(), indent=2)
        print ""

