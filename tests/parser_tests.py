import unittest
from tests_common import UPLTestCase
from upl import lexer, parser, parse_nodes
from upl.exceptions import ParserException
import json

INT_TYPE_NODE = "TokenType.KeywordInt"
BOOL_TYPE_NODE = "TokenType.KeywordBool"
REAL_TYPE_NODE = "TokenType.KeywordReal"

class TestParser(UPLTestCase):
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

    def test_binary_opertion_error(self):
        self.checkParseFails("1 * def;")
        self.checkParseFails("def * 1;")

    def test_binary_operator_priorities_1(self):
        self.checkParseTree("a @> b ** c @> d", {
            "statements": [
                {
                    "operator": "**",
                    "left_operand": {
                        "operator": "@>"
                    },
                    "right_operand": {
                        "operator": "@>"
                    }
                }
            ]
        })

    def test_binary_operator_priorities_2(self):
        for g1, g2 in zip(parser.operator_groups, parser.operator_groups[1:]):
            for op1 in g1:
                for op2 in g2:
                    self.checkParseTree(
                        "a {op2} b {op1} c {op2} d".format(op1=op1, op2=op2), {
                            "statements": [
                                {
                                    "operator": op1,
                                    "left_operand": {
                                        "operator": op2
                                    },
                                    "right_operand": {
                                        "operator": op2
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

    def test_unary_operation_error(self):
        self.checkParseFails("-def;")
        self.checkParseFails("--;")

    def test_nested_expressions(self):
        self.checkParseTree("-(1**(1||a))*(true+((f(a))))", {
            "statements": [
                {
                    "type": "BinaryOperationNode",
                    "operator": "*",
                    "left_operand": {
                        "type": "UnaryOperationNode",
                        "operator": "-",
                        "operand": {
                            "type": "BinaryOperationNode",
                            "operator": "**",
                            "left_operand": {"type": "IntLiteralNode"},
                            "right_operand": {
                                "type": "BinaryOperationNode",
                                "operator": "||",
                                "left_operand": {"type": "IntLiteralNode"},
                                "right_operand": {"type": "IdentifierNode"}
                            }
                        }

                    },
                    "right_operand": {
                        "type": "BinaryOperationNode",
                        "operator": "+",
                        "left_operand": {"type": "BoolLiteralNode"},
                        "right_operand": {
                            "type": "FuncCallNode",
                            "args": [
                                {"type": "IdentifierNode", "name": "a"}
                            ]
                        }
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
                }
            ]
        })

    def test_decl_error_1(self):
        self.checkParseFails("def a;")

    def test_decl_error_2(self):
        self.checkParseFails("def a: 12 = 1;")

    def test_decl_error_3(self):
        self.checkParseFails("def a: int = {}")

    def test_decl_error_4(self):
        self.checkParseFails("def;")

    def test_decl_error_5(self):
        self.checkParseFails("def 123 = 12;")

    def test_decl_error_6(self):
        self.checkParseFails("def a == 123;")

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

    def test_function_call_error_1(self):
        self.checkParseFails("F(,)")

    def test_function_call_error_2(self):
        self.checkParseFails("F(-)")

    def test_function_call_error_3(self):
        self.checkParseFails("F(()")

    def test_function_def_1(self):
        self.checkParseTree("()->int{}", {
            "statements": [
                {
                    "type": "FuncDefNode",
                    "args": [],
                    "return_type": INT_TYPE_NODE,
                    "statements": []
                }
            ]
        })

    def test_function_def_2(self):
        self.checkParseTree("(a: int)->int{}", {
            "statements": [
                {
                    "type": "FuncDefNode",
                    "args": [("a", INT_TYPE_NODE)],
                    "return_type": INT_TYPE_NODE,
                    "statements": []
                }
            ]
        })

    def test_function_def_3(self):
        self.checkParseTree("(a: int, b:bool,c: real)->int{}", {
            "statements": [
                {
                    "type": "FuncDefNode",
                    "args": [
                        ("a", INT_TYPE_NODE),
                        ("b", BOOL_TYPE_NODE), 
                        ("c", REAL_TYPE_NODE)
                    ],
                    "return_type": INT_TYPE_NODE,
                    "statements": []
                }
            ]
        })

    def test_function_def_4(self):
        self.checkParseTree("""
            (a: int, b:bool,c: real)->int{
                def a = 1 * 3 + 4;
                def b = 3 + a;
                c;
            }
        """, {
            "statements": [
                {
                    "type": "FuncDefNode",
                    "args": [
                        ("a", INT_TYPE_NODE),
                        ("b", BOOL_TYPE_NODE), 
                        ("c", REAL_TYPE_NODE)
                    ],
                    "return_type": INT_TYPE_NODE,
                    "statements": [
                        {"type": "DeclNode", "declarator": "TokenType.KeywordDef"},
                        {"type": "DeclNode", "declarator": "TokenType.KeywordDef"},
                        {"type": "IdentifierNode"}
                    ]
                }
            ]
        })

    def test_function_def_nested_1(self):
        self.checkParseTree("""
            def x = () -> int {
                def a = 1 * 3 + 4;
                def f = (c: int, d: bool) -> int {
                    c + d;
                };
                f(a);
            };
            x(1);
        """, {
            "statements": [
                {
                    "type": "DeclNode",
                    "expression": {
                        "type": "FuncDefNode",
                        "statements": [
                            {"type": "DeclNode"},
                            {
                                "type": "DeclNode",
                                "expression": {
                                    "type": "FuncDefNode",
                                    "args": [
                                        ("c", INT_TYPE_NODE),
                                        ("d", BOOL_TYPE_NODE)
                                    ],
                                    "return_type": INT_TYPE_NODE,
                                    "statements": [
                                        {"type": "BinaryOperationNode"}
                                    ]
                                }
                            },
                            {"type": "FuncCallNode"}
                        ]
                    }
                },
                {"type": "FuncCallNode"}
            ]
        })
    
    def test_function_def_nested_2(self):
        self.checkParseTree("()->int{()->int{}}", {
            "statements": [
                {
                    "type": "FuncDefNode",
                    "statements": [
                        {
                            "type": "FuncDefNode",
                            "statements": []
                        }
                    ]
                }
            ]
        })

    def test_function_def_error_1(self):
        self.checkParseFails("()->123{}")

    def test_function_def_error_2(self):
        self.checkParseFails("(a: 123)->int{}")

    def test_function_def_error_3(self):
        self.checkParseFails("(123)->int{}")

    def test_function_def_error_4(self):
        self.checkParseFails("()->int { +; }")

    def test_empty_statements(self):
        self.checkParseTree(";;;1;", {
            "statements": [{"type": "IntLiteralNode"}]
        })

    def checkParseFails(self, program):
        with self.assertRaises(ParserException):
            tokens = lexer.tokenize_program(program)
            parse_tree = parser.Parser(tokens).parse()

    def checkParseTree(self, program, partial_parse_tree):
        tokens = lexer.tokenize_program(program)
        parse_tree = parser.Parser(tokens).parse()
        self.assertIsNotNone(parse_tree)

        self.matchValues(parse_tree.to_dict(), partial_parse_tree)
