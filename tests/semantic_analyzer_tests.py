import unittest
from tests_common import UPLTestCase
from upl import lexer, parser, semantic_analyzer, semantic_analyze_nodes
from upl.semantic_analyze_nodes import FuncDefAnalyzeNode, BasicType
from upl.exceptions import SemanticAnalyzerException
import json

TYPE_INT = "BasicType.Int"
TYPE_BOOL = "BasicType.Bool"
TYPE_REAL = "BasicType.Real"

STDLIB = (
    # Arithmetic
    FuncDefAnalyzeNode("+", [BasicType.Int, BasicType.Int], BasicType.Int),
    FuncDefAnalyzeNode("-", [BasicType.Int, BasicType.Int], BasicType.Int),
    FuncDefAnalyzeNode("-", [BasicType.Int], BasicType.Int),

    # Comparison
    FuncDefAnalyzeNode("<", [BasicType.Int, BasicType.Int], BasicType.Bool),
)

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
            def int_const = 10;
            def bool_const = true;
            def real_const = 10.0;
            def int_func = () -> int { int_const; };
            def bool_func = () -> bool { bool_const; };
            def real_func = () -> real { real_const; };
        """, [
            {"body": { "type": "ConstantAnalyzeNode", "value_type": TYPE_INT }},
            {"body": { "type": "ConstantAnalyzeNode", "value_type": TYPE_BOOL }},
            {"body": { "type": "ConstantAnalyzeNode", "value_type": TYPE_REAL }}
        ])

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

    def test_binary_operation(self):
        self.checkSemanticTree("""
            def f = () -> int { 1 + 1; };
        """, [
            {"body": {"type": "FuncCallAnalyzeNode"}}
        ])

    def test_unary_operation(self):
        self.checkSemanticTree("""
            def f = () -> int { -1; };
        """, [
            {"body": {"type": "FuncCallAnalyzeNode"}}
        ])

    def test_conditional(self):
        self.checkSemanticTree("""
            def f = (a: int) -> int { if a < 2 then a else f(a-1) + f(a-2);};
        """, [
            {"body": {"type": "ConditionalAnalyzeNode"}}
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

    def test_conditional_error_1(self):
        self.checkAnalyzeFails("""
            def f = () -> int { if 1 then 2 else 3; };
        """)

    def test_conditional_error_2(self):
        self.checkAnalyzeFails("""
            def f = () -> int { if 1 < 2 then 2 else 3.0; };
        """)

    def test_identifier_error_1(self):
        self.checkAnalyzeFails("""
            def f = () -> int { b; };
        """)

    def test_identifier_error_2(self):
        self.checkAnalyzeFails("""
            def f = () -> int { 0; };
            def g = () -> int { f; };
        """)

    def test_ignorable_expression_1(self):
        self.checkSemanticTree("""
            1 + 1;
        """, [])

    def test_ignorable_expression_2(self):
        self.checkSemanticTree("""
            def f = () -> int {
                1 + 1;
                5;
            }
        """, [
            {"body": {"type": "ConstantAnalyzeNode"}}
        ])

    def test_duplicate_function(self):
        self.checkAnalyzeFails("""
            def f = () -> int {1;};
            def f = () -> int {2;};
        """)

    def test_duplicate_identifier_1(self):
        self.checkAnalyzeFails("""
            def a = 1;
            def a = 2;
            def f = () -> int { a; };
        """)

    def test_duplicate_identifier_2(self):
        self.checkAnalyzeFails("""
            def f = () -> int {
                def a = 1;
                def a = 2;
                a;
            };
        """)

    def test_return_type_check(self):
        self.checkAnalyzeFails("""
            def f = () -> bool { 1; };
        """)

    def test_empty_function(self):
        self.checkAnalyzeFails("""
            def f = () -> bool {};
        """)

    def test_nested_function(self):
        self.checkAnalyzeFails("""
            def f = () -> bool {
                def g = () -> bool {true;};
                g();
            }
        """)

    def test_invalid_return_value(self):
        self.checkAnalyzeFails("""
            def f = () -> bool {
                def a = true;
            }
        """)

    def checkSemanticTree(self, program, partial_semantic_tree):
        tokens = lexer.tokenize_program(program)
        parse_tree = parser.Parser(tokens).parse()
        self.assertIsNotNone(parse_tree)
        consts, funcs = semantic_analyzer.SemanticAnalyzer(parse_tree,
                                                           STDLIB).analyze()
        semantic_tree_dict = [f.to_dict() for f in funcs]

        self.matchValues(semantic_tree_dict, partial_semantic_tree)

    def checkAnalyzeFails(self, program):
        tokens = lexer.tokenize_program(program)
        parse_tree = parser.Parser(tokens).parse()
        self.assertIsNotNone(parse_tree)

        with self.assertRaises(SemanticAnalyzerException):
            consts, funcs = semantic_analyzer.SemanticAnalyzer(parse_tree,
                                                               STDLIB).analyze()
