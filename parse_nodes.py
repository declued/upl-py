from enum import Enum

class ParseNode:
    def to_dict(self):
        return None

class ProgramNode(ParseNode):
    def __init__(self, statements):
        self.statements = statements

    def to_dict(self):
        return dict(
            type = "ProgramNode",
            statements = [s.to_dict() for s in self.statements]
        )

class StatementNode(ParseNode):
    pass

class DeclNode(StatementNode):
    def __init__(self, declarator, identifier, expression):
        self.declarator = declarator
        self.identifier = identifier
        self.expression = expression

    def to_dict(self):
        return dict(
            type = "DeclNode",
            declarator = str(self.declarator),
            identifier = self.identifier,
            expression = self.expression.to_dict()
        )

class ExpressionNode(StatementNode):
    pass

class FuncDefNode(ExpressionNode):
    def __init__(self, arg_list, return_type, statements):
        self.arg_list = arg_list
        self.return_type = return_type
        self.statements = statements

    def to_dict(self):
        # TODO
        return None

class LiteralNode(ExpressionNode):
    pass

class BoolLiteralNode(LiteralNode):
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return dict(
            type = "BoolLiteralNode",
            value = self.value
        )

class IntLiteralNode(LiteralNode):
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return dict(
            type = "IntLiteralNode",
            value = self.value
        )

class RealLiteralNode(LiteralNode):
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return dict(
            type = "RealLiteralNode",
            value = self.value
        )

class FuncCallNode(ExpressionNode):
    def __init_(self, name, args):
        self.name = name
        self.args = args

    def to_dict(self):
        # TODO
        return None

class BinaryOperationNode(ExpressionNode):
    def __init__(self, operator, left_operand, right_operand):
        self.operator = operator
        self.left_operand = left_operand
        self.right_operand = right_operand

    def to_dict(self):
        # TODO
        return None

class UnaryOperationNode(ExpressionNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def to_dict(self):
        # TODO
        return None
