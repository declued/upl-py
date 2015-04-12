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

class AnalyzeNode(object):
    pass

class ConstantNode(AnalyzeNode):
    def __init__(self, index):
        self.index = index

class ContextVarNode(AnalyzeNode):
    def __init__(self, index):
        self.index = index

class Analyzer(object):
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree

    def analyze(self):
        constants = self.get_consts_program(self.parse_tree)
        constants = list(set(constants))
        names = self.get_names_program(self.parse_tree, ())

        return constants, names

    def get_consts_program(self, node):
        return list(chain(*[self.get_consts_statement(s) for s in node.statements]))

    def get_consts_statement(self, node):
        if isinstance(node, DeclNode):
            return self.get_consts_expression(node.expression)
        else:
            return self.get_consts_expression(node)

    def get_consts_expression(self, node):
        if isinstance(node, FuncDefNode):
            return list(chain(*[self.get_consts_statement(s) for s in node.statements]))
        
        elif isinstance(node, FuncCallNode):
            return list(chain(*[self.get_consts_expression(s) for s in node.args]))
        
        elif isinstance(node, BinaryOperationNode):
            return self.get_consts_expression(node.left_operand) +\
                   self.get_consts_expression(node.right_operand)

        elif isinstance(node, UnaryOperationNode):
            return self.get_consts_expression(node.operand)
        
        elif isinstance(node, BoolLiteralNode):
            return [(BasicType.Bool, node.value)]
        
        elif isinstance(node, IntLiteralNode):
            return [(BasicType.Int, node.value)]
        
        elif isinstance(node, RealLiteralNode):
            return [(BasicType.Real, node.value)]

        else:
            return []

    def get_names_program(self, node, ns):
        names = {}
        for s in node.statements:
            names.update(self.get_names_statement(s, ns))

        return names

    def get_names_statement(self, node, ns):
        if isinstance(node, DeclNode):
            return self.get_names_decl(node, ns)
        else:
            return {}

    def get_names_decl(self, node, ns):
        names = {ns + (node.identifier, ): node}

        if isinstance(node.expression, FuncDefNode):
            func_def = node.expression
            for s in func_def.statements:
                names.update(self.get_names_statement(s, ns + (node.identifier,)))
            for idx, arg in enumerate(func_def.type.arg_list):
                names[ns + (node.identifier, arg.name)] = ContextVarNode(idx)

        return names

