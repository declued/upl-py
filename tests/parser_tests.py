import unittest
from upl import lexer, parser, parse_nodes
import json

INT_TYPE_NODE = {
    "type": "BasicTypeNode",
    "type_name": "TokenType.KeywordInt"
}

BOOL_TYPE_NODE = {
    "type": "BasicTypeNode",
    "type_name": "TokenType.KeywordBool"
}

REAL_TYPE_NODE = {
    "type": "BasicTypeNode",
    "type_name": "TokenType.KeywordReal"
}

INFERRED_TYPE_NODE = {
    "type": "InferredTypeNode"
}

class TestParser(unittest.TestCase):
    def test_literal_expressions(self):
        self.checkParseTree("""
            1;
            true;
            3.14;
            """, {
            "statements": [
                {"type": "IntLiteralNode", "value": 1},
                {"type": "BoolLiteralNode", "value": True},
                {"type": "RealLiteralNode", "value": 3.14},
            ]
        })

    def test_identifier_expressions(self):
        self.checkParseTree("a; b;", {
            "statements": [
                {"type": "IdentifierNode", "name": "a"},
                {"type": "IdentifierNode", "name": "b"}
            ]
        })

    def test_binary_operations(self):
        self.checkParseTree("1 + 2 + 3; 4 * 5 + 6 * 7;", {
            "statements": [
                {
                    "type": "BinaryOperationNode",
                    "operator": "+",
                    "left_operand": {"type": "IntLiteralNode", "value": 1},
                    "right_operand": {
                        "type": "BinaryOperationNode",
                        "left_operand": {"type": "IntLiteralNode", "value": 2},
                        "right_operand": {"type": "IntLiteralNode", "value": 3}
                    }
                },
                {
                    "operator": "+",
                    "left_operand": {
                        "type": "BinaryOperationNode",
                        "operator": "*",
                        "left_operand": {"type": "IntLiteralNode", "value": 4},
                        "right_operand": {"type": "IntLiteralNode", "value": 5}
                    },
                    "right_operand": {
                        "type": "BinaryOperationNode",
                        "operator": "*",
                        "left_operand": {"type": "IntLiteralNode", "value": 6},
                        "right_operand": {"type": "IntLiteralNode", "value": 7}
                    }
                }
            ]
        })

    def test_unary_operations(self):
        self.checkParseTree("~(-1 + 2);", {
            "statements": [
                {
                    "type": "UnaryOperationNode",
                    "operator": "~",
                    "operand": {
                        "type": "BinaryOperationNode",
                        "left_operand": {
                            "type": "UnaryOperationNode",
                            "operator": "-",
                            "operand": {"type": "IntLiteralNode", "value": 1}
                        },
                        "right_operand": {"type": "IntLiteralNode", "value": 2}
                    }
                }
            ]
        })

    def test_decl_1(self):
        self.checkParseTree("def a = 1;", {
            "statements": [
                {
                    "type": "DeclNode",
                    "declarator": "TokenType.KeywordDef",
                    "identifier": "a",
                    "identifier_type": INFERRED_TYPE_NODE
                }
            ]
        })

    def test_decl_2(self):
        self.checkParseTree("def a: int = 1;", {
            "statements": [
                {
                    "type": "DeclNode",
                    "declarator": "TokenType.KeywordDef",
                    "identifier": "a",
                    "identifier_type": INT_TYPE_NODE
                }
            ]
        })

    def test_decl_3(self):
        self.checkParseTree("var a = 1;", {
            "statements": [
                {
                    "type": "DeclNode",
                    "declarator": "TokenType.KeywordVar"
                }
            ]
        })

    def test_decl_error_1(self):
        self.checkParseFails("var a;")

    def test_decl_error_2(self):
        self.checkParseFails("var a: 12 = 1;")

    def test_decl_error_3(self):
        self.checkParseFails("var a: int = {}")

    def test_decl_error_4(self):
        self.checkParseFails("var;")

    def test_function_call_1(self):
        self.checkParseTree("F()", {
            "statements": [
                {"type": "FuncCallNode", "name": "F", "args": []}
            ]
        })

    def test_function_call_2(self):
        self.checkParseTree("F(1)", {
            "statements": [
                {"type": "FuncCallNode", "args": [{"type": "IntLiteralNode"}]}
            ]
        })

    def test_function_call_3(self):
        self.checkParseTree("F(1,2,3,4)", {
            "statements": [
                {
                    "args": [{"type": "IntLiteralNode"}] * 4
                }
            ]
        })

    def test_function_call_4(self):
        self.checkParseTree("F(1 * 2, G(3), -4)", {
            "statements": [
                {
                    "args": [
                        {"type": "BinaryOperationNode"},
                        {"type": "FuncCallNode", "args": [{}]},
                        {"type": "UnaryOperationNode"}
                    ]
                }
            ]
        })

    def test_function_call_5(self):
        self.checkParseTree("F(G(H()))", {
            "statements": [
                {"args": [
                    {"args": [
                        {"args": []}
                    ]}
                ]}
            ]
        })

    def test_function_def_1(self):
        self.checkParseTree("()->int{}", {
            "statements": [
                {
                    "type": "FuncDefNode",
                    "func_type": {
                        "args": [],
                        "return_type": INT_TYPE_NODE
                    },
                    "statements": []
                }
            ]
        })

    def test_function_def_2(self):
        self.checkParseTree("(a: int)->int{}", {
            "statements": [
                {
                    "type": "FuncDefNode",
                    "func_type": {
                        "args": [("a", INT_TYPE_NODE)],
                        "return_type": INT_TYPE_NODE
                    },
                    "statements": []
                }
            ]
        })

    def test_function_def_3(self):
        self.checkParseTree("(a: int, b:bool,c: real)->int{}", {
            "statements": [
                {
                    "type": "FuncDefNode",
                    "func_type": {
                        "args": [
                            ("a", INT_TYPE_NODE),
                            ("b", BOOL_TYPE_NODE), 
                            ("c", REAL_TYPE_NODE)
                        ],
                        "return_type": INT_TYPE_NODE
                    },
                    "statements": []
                }
            ]
        })

    def checkParseFails(self, program):
        tokens = lexer.tokenize_program(program)
        parse_tree = parser.Parser(tokens).parse()
        self.assertIsNone(parse_tree)

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

