from enum import Enum

_next_parse_node_id = 0

class ParseNode(object):
    def __init__(self):
        global _next_parse_node_id
        self.id = _next_parse_node_id
        _next_parse_node_id += 1

class ProgramNode(ParseNode):
    def __init__(self, statements):
        super(ProgramNode, self).__init__()
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
        super(DeclNode, self).__init__()
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

class ConditionalNode(ExpressionNode):
    def __init__(self, condition, on_true, on_false):
        self.condition = condition
        self.on_true = on_true
        self.on_false = on_false

    def to_dict(self):
        return dict(
            type = "ConditionalNode",
            condition = self.condition.to_dict(),
            on_true = self.on_true.to_dict(),
            on_false = self.on_false.to_dict()
        )

class FuncDefNode(ExpressionNode):
    def __init__(self, arg_list, return_type, statements):
        super(FuncDefNode, self).__init__()
        self.statements = statements
        self.arg_list = arg_list
        self.return_type = return_type

    def to_dict(self):
        return dict(
            type = "FuncDefNode",
            statements = [s.to_dict() for s in self.statements],
            return_type = str(self.return_type),
            args = [(a.name, str(a.type)) for a in self.arg_list]
        )

class FuncArgNode(ParseNode):
    def __init__(self, name, type, index):
        super(FuncArgNode, self).__init__()
        self.name = name
        self.type = type
        self.index = index

class LiteralNode(ExpressionNode):
    pass

class BoolLiteralNode(LiteralNode):
    def __init__(self, value):
        super(BoolLiteralNode, self).__init__()
        self.value = value

    def to_dict(self):
        return dict(
            type = "BoolLiteralNode",
            value = self.value
        )

class IntLiteralNode(LiteralNode):
    def __init__(self, value):
        super(IntLiteralNode, self).__init__()
        self.value = value

    def to_dict(self):
        return dict(
            type = "IntLiteralNode",
            value = self.value
        )

class RealLiteralNode(LiteralNode):
    def __init__(self, value):
        super(RealLiteralNode, self).__init__()
        self.value = value

    def to_dict(self):
        return dict(
            type = "RealLiteralNode",
            value = self.value
        )

class IdentifierNode(ExpressionNode):
    def __init__(self, name):
        super(IdentifierNode, self).__init__()
        self.name = name

    def to_dict(self):
        return dict(
            type = "IdentifierNode",
            name = self.name
        )

class FuncCallNode(ExpressionNode):
    def __init__(self, name, args):
        super(FuncCallNode, self).__init__()
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
        super(BinaryOperationNode, self).__init__()
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
        super(UnaryOperationNode, self).__init__()
        self.operator = operator
        self.operand = operand

    def to_dict(self):
        return dict(
            type = "UnaryOperationNode",
            operator = self.operator,
            operand = self.operand.to_dict()
        )
