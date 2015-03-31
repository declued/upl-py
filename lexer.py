import re
from token import TokenType, Token

DEFAULT_VALUE_FUNC = lambda v: None

# Regular expressions and uncooked->value functions. Note that order matters here.
token_lex_info_list = (
    (TokenType.BoolLiteral, r"(false|true)", lambda v: v == "true"),
    (TokenType.RealLiteral, r"\d+\.\d+(e[-+]?\d+)?", lambda v: float(v)),
    (TokenType.IntLiteral, r"\d+", lambda v: int(v)),
    (TokenType.StringLiteral, r'\"(\\.|[^\\"])*\"', lambda v: eval(v)),
    (TokenType.OpenBracket, r"{", DEFAULT_VALUE_FUNC),
    (TokenType.CloseBracket, r"}", DEFAULT_VALUE_FUNC),
    (TokenType.OpenParen, r"\(", DEFAULT_VALUE_FUNC),
    (TokenType.CloseParen, r"\)", DEFAULT_VALUE_FUNC),
    (TokenType.Assignment, r"=", DEFAULT_VALUE_FUNC),
    (TokenType.StatementSep, r";", DEFAULT_VALUE_FUNC),
    (TokenType.ArgumentSep, r",", DEFAULT_VALUE_FUNC),
    (TokenType.ReturnsSep, r"->", DEFAULT_VALUE_FUNC),
    (TokenType.Operator, r"[!@#$%^&*\-+/=<>]+", lambda v: v),
    (TokenType.KeywordDef, r"def", DEFAULT_VALUE_FUNC),
    (TokenType.KeywordVar, r"var", DEFAULT_VALUE_FUNC),
    (TokenType.KeywordBool, r"bool", DEFAULT_VALUE_FUNC),
    (TokenType.KeywordInt, r"int", DEFAULT_VALUE_FUNC),
    (TokenType.KeywordReal, r"real", DEFAULT_VALUE_FUNC),
    (TokenType.KeywordFunc, r"func", DEFAULT_VALUE_FUNC),
    (TokenType.Identifier, r"[A-Za-z][A-Za-z0-9_]*", lambda v: v),
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
        if match is not None:
            uncooked = match.group(0)
            first_token = Token(type = token_type,
                                value = value_func(uncooked),
                                uncooked = uncooked)
            break

    if first_token is None:
        return [Token(TokenType.Error)]
    else:
        line_tail = line[len(first_token.uncooked):]
        return [first_token] + tokenize_line(line_tail)


if __name__ == "__main__":
    for token in tokenize_program("def x = 42+8.0 * 98+a;"):
        print token

