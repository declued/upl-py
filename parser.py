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
        """
        On success returns a program, otherwise returns None.

        program := statement [| program];
        """
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

        statement := declaration ";" | expression ";";
        """
        statement_tokens = self.get_current_statement()

        # a statement is a declaration or an expression
        statement = self.parse_declaration(statement_tokens)
        if statement is None:
            statement = self.parse_expression(statement_tokens)

        if statement is None:
            # if we couldn't match a declaration or an expression, it's an error
            self.error = True
            result = None
        else:
            # all is good
            self.token_index += len(statement_tokens) + 1
            result = statement

        return result

    def parse_declaration(self, tokens):
        """
        On success returns a declaration and increments the token_index, otherwise
        returns None.

        declaration := declarator identifier "=" expression;
        declarator := "def" | "var" | typename;
        typename := "bool" | "int" | "real";
        """
        if len(tokens) < 4:
            return None

        initial_token_index = self.token_index
        declarator = None
        identifier = None
        expression = None

        # match the declarator
        if tokens[0].type not in (TokenType.KeywordDef, TokenType.KeywordVar,
                                  TokenType.KeywordBool, TokenType.KeywordInt,
                                  TokenType.KeywordReal):
            return None
        else:
            declarator = tokens[0].type

        # match the identifier
        if tokens[1].type != TokenType.Identifier:
            return None
        else:
            identifier = tokens[1].value

        # match the assignment sign
        if tokens[2].type != TokenType.Assignment:
            return None

        # match the right hand side
        rhs = self.parse_expression(tokens[3:])
        if rhs is None:
            return None

        declaration = DeclNode(declarator, identifier, rhs)
        return declaration

    def get_current_statement(self):
        """
        Returns the statement which starts at the current token.
        """
        tokens = []
        balance = 0
        for token in self.tokens[self.token_index:]:
            if token.type == TokenType.StatementSep and balance == 0:
                break

            tokens.append(token)

            if token.type == TokenType.OpenBracket:
                balance += 1
            elif token.type == TokenType.CloseBracket:
                balance -= 1

        return tokens

    def parse_expression(self, tokens):
        """
        On success returns an expression, otherwise returns None.

        expression := binary_operation | unary_operation | func_call | func_def | literal;
        """
        expression = self.parse_binary_operation(tokens) or\
                     self.parse_unary_operation(tokens) or\
                     self.parse_function_call(tokens) or\
                     self.parse_function_def(tokens) or\
                     self.parse_literal(tokens)

        return expression

    def parse_binary_operation(self, tokens):
        """
        On success returns a binary operation, otherwise returns None.

        binary_operation := expression operator expression;
        """
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

        # parse left operand and right operand
        operator = tokens[operator_index].value
        left_operand = self.parse_expression(tokens[:operator_index])
        right_operand = self.parse_expression(tokens[operator_index + 1:])

        if left_operand is None or right_operand is None:
            return None

        # create the result
        binary_operation = BinaryOperationNode(operator, left_operand, right_operand)

        return binary_operation

    def parse_unary_operation(self, tokens):
        """
        On success returns a unary operation, otherwise returns None.

        unary_operation := operator expression;
        """
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

    def parse_function_def(self, tokens):
        return None

    def parse_literal(self, tokens):
        """
        On success returns a literal, otherwise returns None.

        literal := bool_literal | int_literal | real_literal;
        """
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

if __name__ == "__main__":
    program = "var a = -1+5;int x = 10;bool v=true;1+3;"

    tokens = tokenize_program(program)
    parse_tree = Parser(tokens).parse()
    if parse_tree is None:
        print "parse error"
    else:
        print json.dumps(parse_tree.to_dict(), indent=2)
