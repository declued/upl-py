from enum import Enum

class ParseNode:
    pass

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
    def __init__(self, type, statements):
        self.type = type
        self.statements = statements

    def to_dict(self):
        return dict(
            type = "FuncDefNode",
            func_type = self.type.to_dict(),
            statements = [s.to_dict() for s in self.statements]
        )

class TypeNode(ParseNode):
    pass

class FuncTypeNode(TypeNode):
    def __init__(self, arg_list, return_type):
        self.arg_list = arg_list
        self.return_type = return_type

    def to_dict(self):
        return dict(
            type = "FuncTypeNode",
            return_type = str(self.return_type),
            args = [(a.name, str(a.type)) for a in self.arg_list]
        )

class FuncArgNode(ParseNode):
    def __init__(self, name, type):
        self.name = name
        self.type = type

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

class IdentifierNode(ExpressionNode):
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return dict(
            type = "IdentifierNode",
            name = self.name
        )

class FuncCallNode(ExpressionNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def to_dict(self):
        return dict(
            type = "FuncCallNode",
            name = self.name,
            args = [arg.to_dict() for arg in self.args]
        )

class BinaryOperationNode(ExpressionNode):
    def __init__(self, operator, left_operand, right_operand):
        self.operator = operator
        self.left_operand = left_operand
        self.right_operand = right_operand

    def to_dict(self):
        return dict(
            type = "BinaryOperationNode",
            operator = self.operator,
            left_operand = self.left_operand.to_dict(),
            right_operand = self.right_operand.to_dict()
        )

class UnaryOperationNode(ExpressionNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def to_dict(self):
        return dict(
            type = "UnaryOperationNode",
            operator = self.operator,
            operand = self.operand.to_dict()
        )
