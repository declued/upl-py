from itertools import chain
from upl.token import TokenType, Token
from upl.parse_nodes import ProgramNode, DeclNode, FuncDefNode, BoolLiteralNode,\
                            IntLiteralNode, RealLiteralNode, FuncCallNode,\
                            BinaryOperationNode, UnaryOperationNode,\
                            IdentifierNode, ExpressionNode, ConditionalNode
from upl.semantic_analyze_nodes import BasicType, FuncDefAnalyzeNode,\
                                       FuncArgAnalyzeNode, ConstantAnalyzeNode,\
                                       FuncCallAnalyzeNode, ConditionalAnalyzeNode
from upl.exceptions import SemanticAnalyzerException

class SemanticAnalyzer(object):
    def __init__(self, parse_tree, external_functions=None):
        self.parse_tree = parse_tree
        self.external_functions = external_functions or []

    def analyze(self):
        self.func_defs = self.get_func_defs(self.parse_tree,
                                            self.external_functions)
        self.consts = self.get_consts(self.parse_tree)
        self.consts = list(set(self.consts))
        symtab = self.initialize_symtab(self.func_defs)
        self.analyze_program(self.parse_tree, symtab)

        self.func_defs = [f for f in self.func_defs if f.body is not None]

        return self.consts, self.func_defs

    def get_func_defs(self, node, external_functions):
        func_defs = external_functions
        for s in node.statements:
            if isinstance(s, DeclNode) and\
               isinstance(s.expression, FuncDefNode):
                name = s.identifier
                arg_types = [self.parse_to_analyze_type(arg.type)\
                             for arg in s.expression.arg_list]
                return_type = self.parse_to_analyze_type(s.expression.return_type)

                try:
                    self.resolve_function(func_defs, name, arg_types)
                except SemanticAnalyzerException:
                    func_def_node = FuncDefAnalyzeNode(name, arg_types,
                                                       return_type)
                    func_defs.append(func_def_node)
                else:
                    print func_defs
                    raise SemanticAnalyzerException("Duplicate function %s" %\
                                                    (name, ))

        return func_defs

    def get_consts(self, node):
        if isinstance(node, ProgramNode):
            return list(chain(*[self.get_consts(s) for s in node.statements]))

        elif isinstance(node, DeclNode):
            return self.get_consts(node.expression)

        elif isinstance(node, FuncDefNode):
            return list(chain(*[self.get_consts(s) for s in node.statements]))
        
        elif isinstance(node, FuncCallNode):
            return list(chain(*[self.get_consts(s) for s in node.args]))
        
        elif isinstance(node, ConditionalNode):
            return self.get_consts(node.condition) +\
                   self.get_consts(node.on_true) +\
                   self.get_consts(node.on_false)

        elif isinstance(node, BinaryOperationNode):
            return self.get_consts(node.left_operand) +\
                   self.get_consts(node.right_operand)

        elif isinstance(node, UnaryOperationNode):
            return self.get_consts(node.operand)
        
        elif isinstance(node, BoolLiteralNode):
            return [(BasicType.Bool, node.value)]
        
        elif isinstance(node, IntLiteralNode):
            return [(BasicType.Int, node.value)]
        
        elif isinstance(node, RealLiteralNode):
            return [(BasicType.Real, node.value)]

        else:
            return []

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
                func_def = self.resolve_function(self.func_defs,
                                                 s.identifier, arg_types)
                func_body = self.analyze_function_body(s.expression,
                                                       symtab.copy())
                if self.resolve_type(func_body) != func_def.return_type:
                    raise SemanticAnalyzerException("Return type mismatch",
                                                    s.location)
                func_def.body = func_body
            elif s.identifier in symtab:
                raise SemanticAnalyzerException("Duplicate identifier %s"\
                                                 % (s.identifier, ), s.location)
            else:
                symtab[s.identifier] = [self.analyze_expression(s.expression,
                                                                symtab.copy())]

    def analyze_function_body(self, node, symtab):
        if len(node.statements) == 0:
            raise SemanticAnalyzerException("Empty function body", node.location)

        for index, arg in enumerate(node.arg_list):
            if arg.name in symtab:
                raise SemanticAnalyzerException("Duplicate identifier %s" % (arg.name, ),
                                                arg.location)
            type = self.parse_to_analyze_type(arg.type)
            symtab[arg.name] = [FuncArgAnalyzeNode(index, type)]
        
        for s in node.statements[:-1]:
            if not isinstance(s, DeclNode):
                continue

            if s.identifier in symtab:
                raise SemanticAnalyzerException("Duplicate identifier %s"\
                                                % (s.identifier, ), s.location)
            if isinstance(s.expression, FuncDefNode):
                raise SemanticAnalyzerException("Nested functions are not supported",
                                                s.location)
            else:
                symtab[s.identifier] = [self.analyze_expression(s.expression,
                                                                symtab.copy())]

        if not isinstance(node.statements[-1], ExpressionNode):
            raise SemanticAnalyzerException("Return value must be an expression")

        result = self.analyze_expression(node.statements[-1], symtab.copy())
        result_type = self.resolve_type(result)

        if result_type != self.parse_to_analyze_type(node.return_type):
            raise SemanticAnalyzerException ("Expected %s, but received %s."\
                                             % (str(node.return_type), str(result_type)),
                                             node.statements[-1].location)

        return result

    def resolve_function(self, func_defs, name, arg_types):
        for func_def in func_defs:
            if (func_def.name, func_def.arg_types) == (name, arg_types):
                return func_def
        
        raise SemanticAnalyzerException("Could not resolve function %s %s" % (name, str(arg_types)))

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

        elif isinstance(node, ConditionalNode):
            return self.analyze_conditional(node, symtab)

        else:
            raise SemanticAnalyzerException("Unexpected %s" % (str(node), ),
                                            node.location)


    def analyze_literal(self, type, value):
        return ConstantAnalyzeNode(self.consts.index((type, value)),
                                   self.consts)

    def analyze_identifier(self, name, symtab):
        if name not in symtab:
            raise SemanticAnalyzerException("%s could not be resolved" % (name, ))

        if isinstance(symtab[name][0], FuncDefAnalyzeNode):
            raise SemanticAnalyzerException("%s references a function" % (name, ))

        return symtab[name][0]

    def analyze_func_call(self, name, args, symtab):
        analyzed_args = [self.analyze_expression(arg, symtab) for arg in args]
        arg_types = [self.resolve_type(arg) for arg in analyzed_args]
        resolved_func = self.resolve_function(self.func_defs, name, arg_types)

        return FuncCallAnalyzeNode(resolved_func, analyzed_args)

    def analyze_conditional(self, node, symtab):
        condition = self.analyze_expression(node.condition, symtab)
        on_true = self.analyze_expression(node.on_true, symtab)
        on_false = self.analyze_expression(node.on_false, symtab)

        if self.resolve_type(condition) != BasicType.Bool:
            raise SemanticAnalyzerException("Expected boolean condition",
                                            node.condition.location)

        if self.resolve_type(on_true) != self.resolve_type(on_false):
            raise SemanticAnalyzerException("Branch types do not match",
                                            node.location)

        return ConditionalAnalyzeNode(condition, on_true, on_false)

    def parse_to_analyze_type(self, parse_type):
        if parse_type == TokenType.KeywordInt:
            return BasicType.Int
        elif parse_type == TokenType.KeywordBool:
            return BasicType.Bool
        elif parse_type == TokenType.KeywordReal:
            return BasicType.Real
        else:
            raise SemanticAnalyzerException("%s is not a valid type" % (parse_type, ))

    def resolve_type(self, node):
        if isinstance(node, FuncArgAnalyzeNode):
            return node.type

        elif isinstance(node, ConstantAnalyzeNode):
            return self.consts[node.index][0]

        elif isinstance(node, FuncCallAnalyzeNode):
            return node.function.return_type

        elif isinstance(node, ConditionalAnalyzeNode):
            return self.resolve_type(node.on_true)

        else:
            raise SemanticAnalyzerException("could not resolve type for %s" % (node, ))
