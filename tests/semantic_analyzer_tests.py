import unittest
from tests_common import UPLTestCase
from upl import lexer, parser, semantic_analyzer, semantic_analyze_nodes
import json

TYPE_INT = "BasicType.Int"

class TestSemanticAnalyzer(UPLTestCase):
    def test_constant_function(self):
        self.checkSemanticTree("""
        def f = () -> int { 2; }
        """, [{
            "type": "FuncDefAnalyzeNode",
            "name": "f",
            "arg_types": [],
            "return_type": TYPE_INT,
            "body": {
                "type": "ConstantAnalyzeNode"
            }
        }])

    def checkSemanticTree(self, program, partial_semantic_tree):
        tokens = lexer.tokenize_program(program)
        parse_tree = parser.Parser(tokens).parse()
        self.assertIsNotNone(parse_tree)
        semantic_tree = semantic_analyzer.SemanticAnalyzer(parse_tree).analyze()
        semantic_tree_dict = [f.to_dict() for f in semantic_tree]

        self.matchValues(semantic_tree_dict, partial_semantic_tree)
