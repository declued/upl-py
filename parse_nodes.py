from enum import Enum

class ParseNode:
    pass

class ProgramNode(ParseNode):
    def __init__(self, statements):
        self.statements = statements

class StatementNode(ParseNode):
    pass

class DeclNode(StatementNode):
    def __init__(self, declarator, identifier, expression):
        self.declarator = declarator
        self.identifier = identifier
        self.expression = expression

class ExpressionNode(StatementNode):
    pass

class FuncDefNode(ExpressionNode):
    def __init__(self, arg_list, return_type, statements):
        self.arg_list = arg_list
        self.return_type = return_type
        self.statements = statements

class LiteralType(Enum):
    Boolean     = 0
    Integer     = 1
    Real        = 2

class LiteralNode(ExpressionNode):
    def __init__(self, type, value):
        self.type = type
        self.value = value

class FuncCallNode(ExpressionNode):
    def __init_(self, name, args):
        self.name = name
        self.args = args

class BinaryOperationNode(ExpressionNode):
    def __init__(self, operator, left_operand, right_operand):
        self.operator = operator
        self.left_operand = left_operand
        self.right_operand = right_operand

class UnaryOperationNode(ExpressionNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand
