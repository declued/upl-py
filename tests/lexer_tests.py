import unittest
from upl import lexer
from upl.token import Token, TokenType

class TestLexer(unittest.TestCase):
    def test_simple_definition(self):
        self.checkTokenTypes("def x = 42 + 8.0 * 98 + a;", 
                             [TokenType.KeywordDef, TokenType.Identifier,
                              TokenType.Assignment, TokenType.IntLiteral,
                              TokenType.Operator, TokenType.RealLiteral,
                              TokenType.Operator, TokenType.IntLiteral,
                              TokenType.Operator, TokenType.Identifier,
                              TokenType.StatementSep])

    def test_simple_program(self):
        self.checkTokenTypes("""
            def abs = (v: int) -> int { # Calculates absolute value
                def result = if(v>0,v,-v);
                result;
            }
            """, [
            TokenType.KeywordDef, TokenType.Identifier, TokenType.Assignment,
            TokenType.OpenParen, TokenType.Identifier, TokenType.TypeSep,
            TokenType.KeywordInt, TokenType.CloseParen, TokenType.ReturnsSep,
            TokenType.KeywordInt, TokenType.OpenBracket, TokenType.KeywordDef,
            TokenType.Identifier, TokenType.Assignment, TokenType.Identifier,
            TokenType.OpenParen, TokenType.Identifier, TokenType.Operator,
            TokenType.IntLiteral, TokenType.ArgumentSep, TokenType.Identifier,
            TokenType.ArgumentSep, TokenType.Operator, TokenType.Identifier,
            TokenType.CloseParen, TokenType.StatementSep, TokenType.Identifier,
            TokenType.StatementSep, TokenType.CloseBracket])

    def test_bool_literal_types(self):
        self.checkTokenTypes("true false truex falsex",
                             [TokenType.BoolLiteral, TokenType.BoolLiteral,
                              TokenType.Identifier, TokenType.Identifier])

    def test_bool_literal_values(self):
        self.checkTokenValues("true false", [True, False])

    def test_real_literals_types(self):
        self.checkTokenTypes("1.0 12.3e4 12.3e+44 12.3e-44",
                              [TokenType.RealLiteral] * 4)

    def test_real_literals_values(self):
        self.checkTokenValues("1.0 12.3e4 12.3e+44 12.3e-44",
                              [1.0, 12.3e4, 12.3e44, 12.3e-44])

    def test_int_literals_types(self):
        self.checkTokenTypes("1 -1 12 292929",
                             [TokenType.IntLiteral, TokenType.Operator,
                              TokenType.IntLiteral, TokenType.IntLiteral,
                              TokenType.IntLiteral])

    def test_int_literals_values(self):
        self.checkTokenValues("1 12 1000000000 0", [1, 12, 1000000000, 0])

    def test_special_operators(self):
        self.checkTokenTypes("{}()=;,->:",
                             [TokenType.OpenBracket, TokenType.CloseBracket,
                              TokenType.OpenParen, TokenType.CloseParen,
                              TokenType.Assignment, TokenType.StatementSep,
                              TokenType.ArgumentSep, TokenType.ReturnsSep,
                              TokenType.TypeSep])

    def test_operators_1(self):
        self.checkTokenTypes("|| ^^ && | ^ & == !=",
                             [TokenType.Operator] * 8)

    def test_operators_2(self):
        self.checkTokenTypes("< <= >= > << >> <<> >><",
                             [TokenType.Operator] * 8)

    def test_operators_3(self):
        self.checkTokenTypes("+ - * / % ** ! ~",
                             [TokenType.Operator] * 8)

    def test_operators_4(self):
        self.checkTokenTypes("++ -- ! @ $ @> <@",
                             [TokenType.Operator] * 7)

    def test_operator_values(self):
        self.checkTokenValues("|| < <> + ~ ** @>",
                              ["||", "<", "<>", "+", "~", "**", "@>"])

    def test_keywords(self):
        self.checkTokenTypes("def var bool int real defx varx boolx intx realx",
                             [TokenType.KeywordDef, TokenType.KeywordVar,
                              TokenType.KeywordBool, TokenType.KeywordInt,
                              TokenType.KeywordReal] + [TokenType.Identifier] * 5)

    def test_identifiers(self):
        self.checkTokenTypes("a_variable a123 A123 a__ aaa CamelCase",
                             [TokenType.Identifier] * 6)

    def test_identifier_values(self):
        self.checkTokenValues("a_variable a123 CamelCase",
                              ["a_variable", "a123", "CamelCase"])

    def test_errors(self):
        self.checkTokenTypes("`123 440400 4",
                             [TokenType.Error])

    def test_location_info(self):
        tokens = lexer.tokenize_program("1  2\n3 4 #comment\n\n  5;")
        locations = [t.location for t in tokens]
        self.assertEqual(locations, [(1, 1), (1, 4), (2, 1), (2, 3),
                                     (4, 3), (4, 4)])

    def test_token_to_str(self):
        token1 = Token(type=TokenType.Operator, value="**")
        token2 = Token(type=TokenType.KeywordInt)
        self.assertIn("**", str(token1))
        self.assertIn(str(TokenType.Operator), str(token1))
        self.assertIn(str(TokenType.KeywordInt), str(token2))

    def checkTokenTypes(self, program, expected_token_types):
        tokens = lexer.tokenize_program(program)
        self.assertEqual(len(tokens), len(expected_token_types))

        for token, expected_token_type in zip(tokens, expected_token_types):
            self.assertEqual(token.type, expected_token_type)

    def checkTokenValues(self, program, expected_token_values):
        tokens = lexer.tokenize_program(program)
        self.assertEqual(len(tokens), len(expected_token_values))

        for token, expected_token_value in zip(tokens, expected_token_values):
            self.assertEqual(token.value, expected_token_value)
