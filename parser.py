from token import TokenType, Token
from lexer import tokenize_program
import json
from parse_nodes import ProgramNode, DeclNode, FuncDefNode, BoolLiteralNode,\
                        IntLiteralNode, RealLiteralNode, FuncCallNode,\
                        BinaryOperationNode, UnaryOperationNode

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
            statement = self.parse_expression()

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

        declaration := declarator identifier "=" expression;
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

        # match the expression
        expression = self.parse_expression()
        if expression is None:
            self.token_index = initial_token_index
            return None

        declaration = DeclNode(declarator, identifier, expression)
        return declaration

    def parse_expression(self):
        literal = self.parse_literal()
        return literal

    def parse_literal(self):
        literal = None
        token_to_node_type = {
            TokenType.BoolLiteral: BoolLiteralNode,
            TokenType.IntLiteral: IntLiteralNode,
            RealLiteralNode: RealLiteralNode
        }

        node_type = token_to_node_type.get(self.current_token_type())
        if node_type is not None:
            literal = node_type(self.current_token().value)
            self.token_index += 1

        return literal


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
    program = "var a = 1;int x = 10;bool v=true;"

    tokens = tokenize_program(program)
    parse_tree = Parser(tokens).parse()
    if parse_tree is None:
        print "parse error"
    else:
        print json.dumps(parse_tree.to_dict(), indent=2)
