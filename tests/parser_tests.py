import unittest
from upl import lexer, parser, parse_nodes
import json

class TestParser(unittest.TestCase):
    def test_literal_expressions(self):
        self.checkParseTree("""
            1;
            true;
            3.14;
            """, {
            "statements": [
                dict(type="IntLiteralNode"),
                dict(type="BoolLiteralNode"),
                dict(type="RealLiteralNode"),
            ]
        })

    def checkParseTree(self, program, partial_parse_tree):
        tokens = lexer.tokenize_program(program)
        parse_tree = parser.Parser(tokens).parse()
        self.assertIsNotNone(parse_tree)

        self.matchValues(parse_tree.to_dict(), partial_parse_tree)

    def matchValues(self, full_value, partial_value):
        self.assertEqual(type(full_value), type(partial_value))

        if isinstance(full_value, dict):
            self.matchDicts(full_value, partial_value)
        elif isinstance(full_value, list) or isinstance(partial_value, tuple):
            self.matchLists(full_value, partial_value)
        else:
            self.assertEqual(full_value, partial_value)

    def matchDicts(self, full_dict, partial_dict):
        for k, v in partial_dict.items():
            self.matchValues(full_dict.get(k), v)

    def matchLists(self, full_list, partial_list):
        self.assertEqual(len(partial_list), len(full_list))
        for v1, v2 in zip(full_list, partial_list):
            self.matchValues(v1, v2)

