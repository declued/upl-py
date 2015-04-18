from upl import lexer, parser, semantic_analyzer
from upl.semantic_analyze_nodes import BasicType, FuncDefAnalyzeNode
import json

if __name__ == "__main__":
    
    program = """
    def fib = (n: int) -> int {
     if n < 2 then n else fib(n - 1) + fib(n - 2);
    }
    """

    external_funcs = [
        FuncDefAnalyzeNode("+", [BasicType.Int, BasicType.Int], BasicType.Int),
        FuncDefAnalyzeNode("-", [BasicType.Int, BasicType.Int], BasicType.Int),
        FuncDefAnalyzeNode("<", [BasicType.Int, BasicType.Int], BasicType.Bool),
    ]

    tokens = lexer.tokenize_program(program)
    parse_tree = parser.Parser(tokens).parse()
    consts, funcs = semantic_analyzer.SemanticAnalyzer(parse_tree, external_funcs).analyze()
    for func in funcs:
        print json.dumps(func.to_dict(), indent=2)
        print ""

