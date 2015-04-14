from itertools import chain
from upl.token import TokenType, Token
from upl.parse_nodes import ProgramNode, DeclNode, FuncDefNode, BoolLiteralNode,\
                            IntLiteralNode, RealLiteralNode, FuncCallNode,\
                            BinaryOperationNode, UnaryOperationNode,\
                            IdentifierNode, ExpressionNode
from upl.semantic_analyze_nodes import BasicType, FuncDefAnalyzeNode,\
                                       FuncArgAnalyzeNode, ConstantAnalyzeNode,\
                                       FuncCallAnalyzeNode

class SemanticAnalyzer(object):
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree

    def analyze(self):
        self.func_defs = self.get_func_defs(self.parse_tree)
        symtab = self.initialize_symtab(self.func_defs)
        self.analyze_program(self.parse_tree, symtab)

        return self.func_defs

    def get_func_defs(self, node):
        func_defs = []
        for s in node.statements:
            if isinstance(s, DeclNode) and\
               isinstance(s.expression, FuncDefNode):
                name = s.identifier
                arg_types = [self.parse_to_analyze_type(arg.type)\
                             for arg in s.expression.arg_list]
                return_type = self.parse_to_analyze_type(s.expression.return_type)
                func_defs.append(FuncDefAnalyzeNode(name, arg_types, return_type))

        return func_defs

    def initialize_symtab(self, func_defs):
        symtab = {}
        for func_def in func_defs:
            if func_def.name not in symtab:
                symtab[func_def.name] = [func_def]
            else:
                symtab[func_def.name].append(func_def)
        return symtab

    def analyze_program(self, node, symtab):
        for s in node.statements:
            if not isinstance(s, DeclNode):
                continue

            if isinstance(s.expression, FuncDefNode):
                arg_types = [self.parse_to_analyze_type(arg.type)\
                             for arg in s.expression.arg_list]
                func_def = self.resolve_function(s.identifier, arg_types)
                func_body = self.analyze_function_body(s.expression,
                                                       symtab.copy())
                if self.resolve_type(func_body) != func_def.return_type:
                    raise Exception("Return type mismatch")
                func_def.body = func_body
            elif s.identifier in symtab:
                raise Exception("Duplicate identifier %s" % (s.identifier, ))
            else:
                symtab[s.identifier] = [self.analyze_expression(s.expression,
                                                                symtab.copy())]

    def analyze_function_body(self, node, symtab):
        if len(node.statements) == 0:
            raise Exception("Empty function body")

        for index, arg in enumerate(node.arg_list):
            if arg.name in symtab:
                raise Exception("Duplicate identifier %s" % (arg.name, ))
            type = self.parse_to_analyze_type(arg.type)
            symtab[arg.name] = [FuncArgAnalyzeNode(index, type)]
        
        for s in node.statements[:-1]:
            if not isinstance(s, DeclNode):
                continue

            if s.identifier in symtab:
                raise Exception("Duplicate identifier %s" % (s.identifier, ))
            if isinstance(s.expression, FuncDefNode):
                raise Exception("Nested functions are not supported")
            else:
                symtab[s.identifier] = [self.analyze_expression(s.expression,
                                                                symtab.copy())]

        if not isinstance(node.statements[-1], ExpressionNode):
            raise Exception("Return value must be an expression")

        result = self.analyze_expression(node.statements[-1], symtab.copy())
        result_type = self.resolve_type(result)

        if result_type != self.parse_to_analyze_type(node.return_type):
            raise Exception ("Expected %s, but received %s." % (str(node.return_type),
                                                                str(result_type)))

        return result

    def resolve_function(self, name, arg_types):
        for func_def in self.func_defs:
            if (func_def.name, func_def.arg_types) == (name, arg_types):
                return func_def
        
        raise Exception("Could not resolve function %s %s" % (name, str(arg_types)))

    def analyze_expression(self, node, symtab):
        if isinstance(node, BoolLiteralNode):
            return self.analyze_literal(BasicType.Bool, node.value)

        elif isinstance(node, IntLiteralNode):
            return self.analyze_literal(BasicType.Int, node.value)

        elif isinstance(node, RealLiteralNode):
            return self.analyze_literal(BasicType.Real, node.value)

        elif isinstance(node, IdentifierNode):
            return self.analyze_identifier(node.name, symtab)

        elif isinstance(node, FuncCallNode):
            return self.analyze_func_call(node.name, node.args, symtab)

        elif isinstance(node, BinaryOperationNode):
            args = [node.left_operand, node.right_operand]
            return self.analyze_func_call(node.operator, args, symtab)

        elif isinstance(node, UnaryOperationNode):
            args = [node.operand]
            return self.analyze_func_call(node.operator, args, symtab)

        else:
            raise Exception("Unexpected %s" % (str(node), ))


    def analyze_literal(self, type, value):
        return ConstantAnalyzeNode(type, value)

    def analyze_identifier(self, name, symtab):
        if name not in symtab:
            raise Exception("%s could not be resolved" % (name, ))

        if isinstance(symtab[name][0], FuncDefAnalyzeNode):
            raise Exception("%s references a function" % (name, ))

        return symtab[name][0]

    def analyze_func_call(self, name, args, symtab):
        analyzed_args = [self.analyze_expression(arg, symtab) for arg in args]
        arg_types = [self.resolve_type(arg) for arg in analyzed_args]
        resolved_func = self.resolve_function(name, arg_types)

        return FuncCallAnalyzeNode(resolved_func, analyzed_args)

    def parse_to_analyze_type(self, parse_type):
        if parse_type == TokenType.KeywordInt:
            return BasicType.Int
        elif parse_type == TokenType.KeywordBool:
            return BasicType.Bool
        elif parse_type == TokenType.KeywordReal:
            return BasicType.Real
        else:
            raise Exception("%s is not a valid type" % (parse_type, ))

    def resolve_type(self, node):
        if isinstance(node, FuncArgAnalyzeNode):
            return node.type

        elif isinstance(node, ConstantAnalyzeNode):
            return node.type

        elif isinstance(node, FuncCallAnalyzeNode):
            return node.function.return_type

        else:
            raise Exception("could not resolve type for %s" % (node, ))
