from upl.token import TokenType, Token
from upl.lexer import tokenize_program
import json
from upl.parse_nodes import ProgramNode, DeclNode, FuncDefNode, BoolLiteralNode,\
                            IntLiteralNode, RealLiteralNode, FuncCallNode,\
                            BinaryOperationNode, UnaryOperationNode,\
                            IdentifierNode, FuncArgNode
from upl.exceptions import ParserException

operator_groups = (
    ('||', '^^', '&&'),
    ('|', '^', '&'),
    ('==', '!='),
    ('<', '<=', '>=', '>'),
    ('<<', '>>', '<<>', '>><'),
    ('+', '-'),
    ('*', '/', '%'),
    ('**',)
)

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        return self.parse_program(self.tokens)

    def parse_program(self, tokens):
        """
        On success returns a program, otherwise returns None.

        program := statement [| program];
        """
        statements = self.parse_statement_list(tokens)
        if statements is None:
            return None

        program = ProgramNode(statements)
        return program

    def parse_statement_list(self, tokens):
        """
        On success returns a list of statements, otherwise returns None.
        """
        statements = []

        while len(tokens) > 0:
            statement_tokens = self.get_first_statement(tokens)
            if len(statement_tokens) == 0:
                # skip the statement separator and continue with the rest
                tokens = tokens[1:]
                continue

            statement = self.parse_statement(statement_tokens)
            if statement is not None:
                statements.append(statement)
                tokens = tokens[len(statement_tokens) + 1:]
            else:
                raise ParserException("Couldn't parse statement",
                                      location=statement_tokens[0].location)

        return statements

    def parse_statement(self, tokens):
        """
        On success returns a statement and increments token_index, otherwise
        returns None.

        statement := declaration ";" | expression ";";
        """
        statement = self.parse_declaration(tokens) or\
                    self.parse_expression(tokens)

        return statement

    def parse_declaration(self, tokens):
        """
        On success returns a declaration and increments the token_index, otherwise
        returns None.

        declaration := "def" identifier "=" expression;
        """
        if len(tokens) < 4:
            return None

        # match the declarator
        if tokens[0].type != TokenType.KeywordDef:
            return None
        else:
            declarator = tokens[0].type

        # After matching the declarator we are pretty sure that the user intended
        # to have a declaration here, so we throw local exceptions to give more
        # useful errors to user.

        # match the identifier
        if tokens[1].type != TokenType.Identifier:
            raise ParserException("Expected identifier", 
                                  location=tokens[1].location)
        else:
            identifier = tokens[1].value

        # match the assignment sign
        if tokens[2].type != TokenType.Assignment:
            raise ParserException("Expected assignment sign",
                                  location=tokens[2].location)

        # match the expression
        expression = self.parse_expression(tokens[3:])
        if expression is None:
            raise ParserException("Expected expression",
                                  location=tokens[3].location)

        declaration = DeclNode(declarator, identifier, expression)
        return declaration

    def get_first_statement(self, tokens):
        """
        Returns the statement which starts at the current token.
        """
        separator_indices = self.find_delimiters(tokens, TokenType.StatementSep)

        if len(separator_indices) == 0:
            statement_tokens = tokens
        else:
            statement_tokens = tokens[:separator_indices[0]]

        return statement_tokens

    def parse_expression(self, tokens):
        """
        On success returns an expression, otherwise returns None.

        expression := binary_operation | unary_operation | func_call | func_def |
                      identifier | literal | "(" expression ")";
        """
        expression = self.parse_binary_operation(tokens) or\
                     self.parse_unary_operation(tokens) or\
                     self.parse_function_call(tokens) or\
                     self.parse_function_def(tokens) or\
                     self.parse_identifier(tokens) or\
                     self.parse_literal(tokens)

        if expression is None and\
           len(tokens) >= 2 and\
           tokens[0].type == TokenType.OpenParen and\
           tokens[-1].type == TokenType.CloseParen:
           expression = self.parse_expression(tokens[1:-1])

        return expression

    def parse_binary_operation(self, tokens):
        """
        On success returns a binary operation, otherwise returns None.

        binary_operation := expression operator expression;
        """
        # find highest priority operator
        operator_indices = self.find_delimiters(tokens, TokenType.Operator, 1)
        if len(operator_indices) == 0:
            return None

        operator_index = min(operator_indices,
                             key=lambda i: self.get_operator_priority(tokens[i].value))

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
        """
        On success returns a function call, otherwise returns None.

        function_call := identifier "(" arg_list ")";
        """
        if len(tokens) < 3 or\
           tokens[0].type != TokenType.Identifier or\
           tokens[1].type != TokenType.OpenParen or\
           tokens[-1].type != TokenType.CloseParen:
            return None

        name = tokens[0].value
        args = self.parse_function_call_args(tokens[2:-1])
        if args is None:
            return None

        function_call = FuncCallNode(name, args)
        return function_call

    def parse_function_call_args(self, tokens):
        """
        On success returns a list of expressions, otherwise returns None.

        arg_list := (empty) | expression ("," expression)*;
        """
        if len(tokens) == 0:
            return []

        separator_indices = self.find_delimiters(tokens, TokenType.ArgumentSep)
        separator_indices.append(len(tokens))

        start = 0
        arg_list = []
        for separator_index in separator_indices:
            arg = self.parse_expression(tokens[start:separator_index])
            if arg is None:
                return None

            arg_list.append(arg)
            start = separator_index + 1

        return arg_list

    def parse_function_def(self, tokens):
        """
        On success returns a function definition, otherwise returns None.

        function_def := function_type "{" function_body "}"
        """
        idxs = self.find_delimiters(tokens, TokenType.OpenBracket)
        if len(idxs) != 1 or tokens[-1].type != TokenType.CloseBracket:
            return None

        arg_list, return_type = self.parse_function_header(tokens[:idxs[0]])
        function_body = self.parse_statement_list(tokens[idxs[0] + 1:-1])

        if arg_list is None or\
           return_type is None or\
           function_body is None:
            return None

        function_def = FuncDefNode(arg_list, return_type, function_body)

        return function_def

    def parse_function_header(self, tokens):
        """
        On success returns a function type, otherwise returns None.

        function_type := "(" arg_list ")" "->" type;
        """
        idxs = self.find_delimiters(tokens, TokenType.ReturnsSep)
        if len(idxs) != 1 or idxs[0] < 2 or\
           tokens[0].type != TokenType.OpenParen or\
           tokens[idxs[0] - 1].type != TokenType.CloseParen or\
           tokens[idxs[0] + 1].type not in (TokenType.KeywordBool,
                                            TokenType.KeywordInt,
                                            TokenType.KeywordReal):
           return None, None

        arg_list = self.parse_function_def_args(tokens[1:idxs[0]-1])
        return_type = tokens[idxs[0]+1].type

        if arg_list is None or return_type is None:
            return None, None

        return arg_list, return_type

    def parse_function_def_args(self, tokens):
        """
        On success returns list of function definition args, otherwise
        returns None.

        arg_list := (empty) | arg ("," arg)*;
        """
        if len(tokens) == 0:
            return []

        separator_indices = self.find_delimiters(tokens, TokenType.ArgumentSep)
        separator_indices.append(len(tokens))

        start = 0
        arg_list = []
        for arg_index, separator_index in enumerate(separator_indices):
            arg_tokens = tokens[start: separator_index]
            
            arg = self.parse_function_def_arg(arg_tokens, arg_index)
            if arg is None:
                return None

            arg_list.append(arg)
            start = separator_index + 1

        return arg_list

    def parse_function_def_arg(self, tokens, index):
        """
        On success returns a FuncArgNode, otherwise returns None.

        function_def_arg := identifier ":" type;
        """
        if len(tokens) != 3 or\
           tokens[0].type != TokenType.Identifier or\
           tokens[1].type != TokenType.TypeSep or\
           tokens[2].type not in (TokenType.KeywordBool,
                                  TokenType.KeywordInt,
                                  TokenType.KeywordReal):
           return None

        type = tokens[2].type
        identifier = tokens[0].value
        typed_var = FuncArgNode(identifier, type, index)

        return typed_var

    def parse_identifier(self, tokens):
        """
        On success returns an identifier, otherwise returns None.
        """
        if len(tokens) != 1 or tokens[0].type != TokenType.Identifier:
            return None

        identifier = IdentifierNode(tokens[0].value)
        return identifier

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
            TokenType.RealLiteral: RealLiteralNode
        }

        node_type = token_to_node_type.get(tokens[0].type)
        if node_type is not None:
            literal = node_type(tokens[0].value)

        return literal

    def find_delimiters(self, tokens, type, skip=0):
        """
        Returns the indices at which tokens can be split by tokens of given type.
        """
        result = []
        balance = 0
        for i, token in enumerate(tokens):
            if token.type == type and balance == 0 and i >= skip:
                result.append(i)

            if token.type in (TokenType.OpenParen, TokenType.OpenBracket):
                balance += 1
            elif token.type in (TokenType.CloseParen, TokenType.CloseBracket):
                balance -= 1

        return result

    def get_operator_priority(self, operator):
        """
        Returns the priority of the given operator.
        """
        for priority, group in enumerate(operator_groups):
            if operator in group:
                return priority
        return 100
