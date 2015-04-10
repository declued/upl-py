from enum import Enum
from itertools import chain
from upl.token import TokenType, Token
from upl.parse_nodes import ProgramNode, DeclNode, FuncDefNode, BoolLiteralNode,\
                            IntLiteralNode, RealLiteralNode, FuncCallNode,\
                            BinaryOperationNode, UnaryOperationNode,\
                            FuncTypeNode, BasicTypeNode, InferredTypeNode,\
                            IdentifierNode, ExpressionNode

class BasicType(Enum):
    Bool        = 0
    Int         = 1
    Real        = 2


class Analyzer(object):
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree

    def analyze(self):
        constants = self.get_constants_program(self.parse_tree)
        constants = list(set(constants))
        return constants

    def get_constants_program(self, node):
        return list(chain(*[self.get_constants_statement(s) for s in node.statements]))

    def get_constants_statement(self, node):
        if isinstance(node, DeclNode):
            return self.get_constants_expression(node.expression)
        else:
            return self.get_constants_expression(node)

    def get_constants_expression(self, node):
        if isinstance(node, FuncDefNode):
            return list(chain(*[self.get_constants_statement(s) for s in node.statements]))
        
        elif isinstance(node, FuncCallNode):
            return list(chain(*[self.get_constants_expression(s) for s in node.args]))
        
        elif isinstance(node, BinaryOperationNode):
            return self.get_constants_expression(node.left_operand) +\
                   self.get_constants_expression(node.right_operand)

        elif isinstance(node, UnaryOperationNode):
            return self.get_constants_expression(node.operand)
        
        elif isinstance(node, BoolLiteralNode):
            return [(BasicType.Bool, node.value)]
        
        elif isinstance(node, IntLiteralNode):
            return [(BasicType.Int, node.value)]
        
        elif isinstance(node, RealLiteralNode):
            return [(BasicType.Real, node.value)]

        else:
            return []

