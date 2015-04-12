from enum import Enum
from itertools import chain
from upl.token import TokenType, Token
from upl.parse_nodes import ProgramNode, DeclNode, FuncDefNode, BoolLiteralNode,\
                            IntLiteralNode, RealLiteralNode, FuncCallNode,\
                            BinaryOperationNode, UnaryOperationNode,\
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
        self.analyzed_nodes = {}

    def analyze(self):
        constants = self.get_consts_program(self.parse_tree)
        self.constants = list(set(constants))
        self.names = self.get_names_program(self.parse_tree, ())
        self.analyze_program(self.parse_tree, ())

        return self.constants, self.names

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
            for arg in func_def.arg_list:
                names[ns + (node.identifier, arg.name)] = arg

        return names

    def analyze_memoizer(analyze_func):
        def memoizer(self, node, ns):
            if node.id not in self.analyzed_nodes:
                self.analyzed_nodes[node.id] = analyze_func(self, node, ns)
            return self.analyzed_nodes[node.id]
        return memoizer

    def analyze_program(self, node, ns):
        for s in node.statements:
            if isinstance(s, DeclNode):
                self.analyze_declaration(s, ns)
    
    @analyze_memoizer
    def analyze_declaration(self, node, ns):
        return self.analyze_expression(node.expression, ns)

    @analyze_memoizer
    def analyze_expression(self, node, ns):
        if isinstance(node, BoolLiteralNode):
            return self.analyze_bool_literal(node, ns)

        elif isinstance(node, IntLiteralNode):
            return self.analyze_int_literal(node, ns)

        elif isinstance(node, RealLiteralNode):
            return self.analyze_real_literal(node, ns)

        elif isinstance(node, IdentifierNode):
            return self.analyze_identifier(node, ns)

        elif isinstance(node, FuncCallNode):
            return self.analyze_func_call(node, ns)

        elif isinstance(node, BinaryOperationNode):
            return self.analyze_binary_operation(node, ns)

        elif isinstance(node, UnaryOperationNode):
            return self.analyze_unary_operation(node, ns)

        elif isinstance(node, FuncDefNode):
            return self.analyze_func_def(node, ns)

        else:
            return None

    @analyze_memoizer
    def analyze_bool_literal(self, node, ns):
        index = self.constants.index((BasicType.Bool, node.value))
        return ConstantNode(index)

    @analyze_memoizer
    def analyze_int_literal(self, node, ns):
        index = self.constants.index((BasicType.Int, node.value))
        return ConstantNode(index)

    @analyze_memoizer
    def analyze_real_literal(self, node, ns):
        index = self.constants.index((BasicType.Real, node.value))
        return ConstantNode(index)

    @analyze_memoizer
    def analyze_identifier(self, node, ns):
        pass

    @analyze_memoizer
    def analyze_func_call(self, node, ns):
        pass

    @analyze_memoizer
    def analyze_binary_operation(self, node, ns):
        pass

    @analyze_memoizer
    def analyze_unary_operation(self, node, ns):
        pass

    @analyze_memoizer
    def analyze_func_def(self, node, ns):
        pass

