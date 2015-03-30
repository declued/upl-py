from token import TokenType, Token
from lexer import tokenize_program
import json
from parse_nodes import ProgramNode, DeclNode, FuncDefNode, BoolLiteralNode,\
                        IntLiteralNode, RealLiteralNode, FuncCallNode,\
                        BinaryOperationNode, UnaryOperationNode

operator_groups = (
    ('||', '^^', '&&'),
    ('|', '^', '&'),
    ('==', '!='),
    ('<', '<=', '>=', '>'),
    ('<<', '>>', '<<>', '>><'),
    ('+', '-'),
    ('*', '/', '%'),
    ('**'),
    ('!', '~')
)

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = 0

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        statements = []
        error = False

        while self.token_index < len(self.tokens):
            statement = self.parse_statement()
            if statement is not None:
                statements.append(statement)
            else:
                error = True
                break

        if error:
            result = None
        else:
            result = ProgramNode(statements)

        return result

    def parse_statement(self):
        """
        On success returns a statement and increments token_index, otherwise
        returns None.

        statement := declaration | expression;
        """
        # a statement is a declaration or an expression
        statement = self.parse_declaration()

        if statement is None:
            # if we couldn't match a declaration or an expression, it's an error
            self.error = True
            result = None
        elif self.current_token_type() != TokenType.StatementSep:
            # if statement delimiter was not found, it's an error
            self.error = True
            result = None
        else:
            # all is good
            self.token_index += 1
            result = statement

        return result

    def parse_declaration(self):
        """
        On success returns a declaration and increments the token_index, otherwise
        returns None.

        declaration := declarator identifier "=" expression | func_def;
        declarator := "def" | "var" | typename;
        typename := "bool" | "int" | "real";
        """
        initial_token_index = self.token_index
        declarator = None
        identifier = None
        expression = None

        # match the declarator
        if self.current_token_type() not in (TokenType.KeywordDef,
                                             TokenType.KeywordVar,
                                             TokenType.KeywordBool,
                                             TokenType.KeywordInt,
                                             TokenType.KeywordReal):
            self.token_index = initial_token_index
            return None
        else:
            declarator = self.current_token_type()

        self.token_index += 1

        # match the identifier
        if self.current_token_type() != TokenType.Identifier:
            self.token_index = initial_token_index
            return None
        else:
            identifier = self.current_token().value

        self.token_index += 1

        # match the assignment sign
        if self.current_token_type() != TokenType.Assignment:
            self.token_index = initial_token_index
            return None

        self.token_index += 1

        # match the rhs
        rhs = self.parse_func_def()
        if rhs is None:
            statement_tokens = self.get_current_statement()
            rhs = self.parse_expression(statement_tokens)
            self.token_index += len(statement_tokens)

        if rhs is None:
            self.token_index = initial_token_index
            return None

        declaration = DeclNode(declarator, identifier, rhs)
        return declaration

    def parse_func_def(self):
        return None

    def get_current_statement(self):
        tokens = []
        for token in self.tokens[self.token_index:]:
            if token.type != TokenType.StatementSep:
                tokens.append(token)
            else:
                break

        return tokens

    def parse_expression(self, tokens):
        expression = self.parse_binary_operation(tokens) or\
                     self.parse_unary_operation(tokens) or\
                     self.parse_function_call(tokens) or\
                     self.parse_literal(tokens)

        return expression

    def parse_binary_operation(self, tokens):
        # find highest priority operator
        operator_index = None
        operator_priority = 100
        balance = 0

        for i, token in enumerate(tokens):
            if token.type == TokenType.OpenParen:
                balance += 1
            elif token.type == TokenType.CloseParen:
                balance -= 1
            elif token.type == TokenType.Operator and balance == 0 and i > 0:
                priority = self.get_operator_priority(token.value)
                if priority < operator_priority:
                    operator_index = i
                    operator_priority = priority

        if operator_index is None:
            return None

        operator = tokens[operator_index].value
        left_operand = self.parse_expression(tokens[:operator_index])
        right_operand = self.parse_expression(tokens[operator_index + 1:])

        if left_operand is None or right_operand is None:
            return None

        binary_operation = BinaryOperationNode(operator, left_operand, right_operand)

        return binary_operation

    def parse_unary_operation(self, tokens):
        if len(tokens) == 0 or tokens[0].type != TokenType.Operator:
            return None

        operator = tokens[0].value
        operand = self.parse_expression(tokens[1:])

        if operand is None:
            return None

        unary_operation = UnaryOperationNode(operator, operand)

        return unary_operation

    def parse_function_call(self, tokens):
        return None

    def parse_literal(self, tokens):
        if len(tokens) != 1:
            return None

        literal = None
        token_to_node_type = {
            TokenType.BoolLiteral: BoolLiteralNode,
            TokenType.IntLiteral: IntLiteralNode,
            RealLiteralNode: RealLiteralNode
        }

        node_type = token_to_node_type.get(tokens[0].type)
        if node_type is not None:
            literal = node_type(tokens[0].value)

        return literal

    def get_operator_priority(self, operator):
        return 1

    def current_token(self):
        """
        If a token is available, returns it, otherwise retursn None.
        """
        if self.token_index >= len(self.tokens):
            return None
        else:
            return self.tokens[self.token_index]

    def current_token_type(self):
        """
        If a token is available, returns its type, otherwise returns None.
        """
        if self.current_token() is None:
            return None
        else:
            return self.current_token().type

if __name__ == "__main__":
    program = "var a = -1+5;int x = 10;bool v=true;"

    tokens = tokenize_program(program)
    parse_tree = Parser(tokens).parse()
    if parse_tree is None:
        print "parse error"
    else:
        print json.dumps(parse_tree.to_dict(), indent=2)
