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

class TestParser(unittest.TestCase):
    def test_literal_expressions(self):
        self.checkParseTree("""
            1;
            true;
            3.14;
            """, {
            "statements": [
                dict(type="IntLiteralNode", value=1),
                dict(type="BoolLiteralNode", value=True),
                dict(type="RealLiteralNode", value=3.14),
            ]
        })

    def test_identifier_expressions(self):
        self.checkParseTree("a; b;", {
            "statements": [
                dict(type="IdentifierNode", name="a"),
                dict(type="IdentifierNode", name="b")
            ]
        })

    def test_binary_operations(self):
        self.checkParseTree("1 + 2 + 3; 4 * 5 + 6 * 7;", {
            "statements": [
                {
                    "type": "BinaryOperationNode",
                    "operator": "+",
                    "left_operand": dict(type="IntLiteralNode", value=1),
                    "right_operand": {
                        "type": "BinaryOperationNode",
                        "left_operand": dict(type="IntLiteralNode", value=2),
                        "right_operand": dict(type="IntLiteralNode", value=3)
                    }
                },
                {
                    "operator": "+",
                    "left_operand": {
                        "type": "BinaryOperationNode",
                        "operator": "*",
                        "left_operand": dict(type="IntLiteralNode", value=4),
                        "right_operand": dict(type="IntLiteralNode", value=5)
                    },
                    "right_operand": {
                        "type": "BinaryOperationNode",
                        "operator": "*",
                        "left_operand": dict(type="IntLiteralNode", value=6),
                        "right_operand": dict(type="IntLiteralNode", value=7)
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
                            "operand": dict(type="IntLiteralNode", value=1)
                        },
                        "right_operand": dict(type="IntLiteralNode", value=2)
                    }
                }
            ]
        })

    def test_function_call_1(self):
        self.checkParseTree("F()", {
            "statements": [
                dict(type="FuncCallNode", name="F", args=[])
            ]
        })

    def test_function_call_2(self):
        self.checkParseTree("F(1)", {
            "statements": [
                dict(type="FuncCallNode", args=[dict(type="IntLiteralNode")])
            ]
        })

    def test_function_call_3(self):
        self.checkParseTree("F(1,2,3,4)", {
            "statements": [
                {
                    "args": [dict(type="IntLiteralNode")] * 4
                }
            ]
        })

    def test_function_call_4(self):
        self.checkParseTree("F(1 * 2, G(3), -4)", {
            "statements": [
                {
                    "args": [
                        dict(type="BinaryOperationNode"),
                        dict(type="FuncCallNode", args=[dict()]),
                        dict(type="UnaryOperationNode")
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

