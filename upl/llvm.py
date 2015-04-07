from upl.parse_nodes import ProgramNode, DeclNode, FuncDefNode, BoolLiteralNode,\
                            IntLiteralNode, RealLiteralNode, FuncCallNode,\
                            BinaryOperationNode, UnaryOperationNode,\
                            FuncTypeNode, BasicTypeNode, InferredTypeNode,\
                            IdentifierNode

class LLVMGenerator:
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree

    def generate(self):
        if self.parse_tree is None or\
           not isinstance(self.parse_tree, ProgramNode):
            return None

        result = self.generate_program(self.parse_tree)
        return result

    def generate_program(self, parse_tree):
        return []
