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

    def test_reference_to_constant(self):
        self.checkSemanticTree("""
            def some_constant = 10;
            def f = () -> int
            {
                some_constant;
            }
        """, [{
            "body": {
                "type": "ConstantAnalyzeNode"
            }
        }])

    def test_reference_to_arg(self):
        self.checkSemanticTree("""
            def f = (a: int) -> int
            {
                a;
            }
        """, [{
            "body": {
                "type": "FuncArgAnalyzeNode"
            }
        }])

    def test_call_to_another_func(self):
        self.checkSemanticTree("""
            def f = () -> int { 1; };
            def g = () -> int { f(); };
        """, [
            {"body": {"type": "ConstantAnalyzeNode"}},
            {"body": {"type": "FuncCallAnalyzeNode"}}
        ])

    def test_multi_statement_body(self):
        self.checkSemanticTree("""
            def f = () -> int {
                def a = 1;
                a;
            };
        """, [
            {"body": {"type": "ConstantAnalyzeNode"}}
        ])

    def checkSemanticTree(self, program, partial_semantic_tree):
        tokens = lexer.tokenize_program(program)
        parse_tree = parser.Parser(tokens).parse()
        self.assertIsNotNone(parse_tree)
        consts, funcs = semantic_analyzer.SemanticAnalyzer(parse_tree).analyze()
        semantic_tree_dict = [f.to_dict() for f in funcs]

        self.matchValues(semantic_tree_dict, partial_semantic_tree)
