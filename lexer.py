import re
from token import TokenType, Token

token_lex_info_list = (
    (TokenType.BoolLiteral, r"(false|true)", lambda v: v == "true"),
    (TokenType.IntLiteral, r"\d+", lambda v: int(v)),
    (TokenType.RealLiteral, r"\d+\.\d+(e[-+]?\d+)?", lambda v: float(v)),
    (TokenType.StringLiteral, r'\"(\\.|[^\\"])*\"', lambda v: eval(v)),
    (TokenType.Identifier, r"[A-Za-z][A-Za-z0-9]*", lambda v: v),
    (TokenType.OpenParen, r"\(", None),
    (TokenType.CloseParen, r"\)", None),
    (TokenType.Assignment, r"=", None),
    (TokenType.StatementSep, r";", None),
    (TokenType.ArgumentSep, r",", None),
    (TokenType.ReturnsSep, r"->", None),
    (TokenType.Operator, r"[!@#$%^&*-+/=<>]+", lambda v: v),
    (TokenType.KeywordDef, r"def", None),
    (TokenType.KeywordVar, r"var", None),
    (TokenType.KeywordBool, r"bool", None),
    (TokenType.KeywordInt, r"int", None),
    (TokenType.KeywordReal, r"real", None),
    (TokenType.KeywordFunc, r"func", None),
)


def tokenize_program(program):
    """
    tokenize splits the give program into tokens and returns the result as
    a list.
    """
    result = []

    for line in program.split("\n"):
        result += tokenize_line(line)

    return result


def tokenize_line(line):
    """
    tokenize splits the give line into tokens and returns the result as
    a list.
    """
    if len(line) == 0:
        return []

    # skip spaces
    if line[0].isspace():
        return tokenize_line(line[1:])

    # check for comments
    if line[0] == '#':
        return []

    first_token = None

    # check for the first token
    for token_type, token_regex, value_func in token_lex_info_list:
        match = re.match(token_regex, line)
        if match is None:
            continue

        uncooked = match.group(0)

        if value_func is not None:
            value = value_func(uncooked)
        else:
            value = None

        first_token = Token(token_type, value, uncooked)

    if first_token is None:
        return [Token(TokenType.Error)]
    else:
        line_tail = line[len(first_token.uncooked):]
        return [first_token] + tokenize_line(line_tail)


if __name__ == "__main__":
    for token in tokenize_program("def x = 42;"):
        print token

