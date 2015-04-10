from upl import lexer, parser, analyzer

if __name__ == "__main__":
    program = """
    def fib = (n: int) -> int {
        def result = if(n <= 1, 1, fib(n - 1) + fib(n - 2));
        result;
    }
    """
    tokens = lexer.tokenize_program(program)
    parse_tree = parser.Parser(tokens).parse()
    constants, names = analyzer.Analyzer(parse_tree).analyze()

    print constants
    print names
