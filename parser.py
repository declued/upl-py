from token import TokenType, Token
from lexer import tokenize_program
import json
from parse_nodes import ProgramNode, DeclNode, FuncDefNode, BoolLiteralNode,\
                        IntLiteralNode, RealLiteralNode, FuncCallNode,\
                        BinaryOperationNode, UnaryOperationNode,\
                        FuncTypeNode, BasicTypeNode

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

    def parse(self):
        return self.parse_program(tokens)

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
            statement = self.parse_statement(statement_tokens)
            if statement is not None:
                statements.append(statement)
                tokens = tokens[len(statement_tokens) + 1:]
            else:
                return None

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

        declaration := declarator identifier "=" expression;
        declarator := "def" | "var" | typename;
        typename := "bool" | "int" | "real";
        """
        if len(tokens) < 4:
            return None

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

        # match the expression
        expression = self.parse_expression(tokens[3:])
        if expression is None:
            return None

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
                      literal | "(" expression ")";
        """
        expression = self.parse_binary_operation(tokens) or\
                     self.parse_unary_operation(tokens) or\
                     self.parse_function_call(tokens) or\
                     self.parse_function_def(tokens) or\
                     self.parse_literal(tokens)

        if expression is None and\
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

        function_type = self.parse_function_type(tokens[:idxs[0]])
        function_body = self.parse_statement_list(tokens[idxs[0] + 1:-1])

        if function_type is None or function_body is None:
            return None

        function_def = FuncDefNode(function_type, function_body)

        return function_def

    def parse_function_type(self, tokens):
        """
        On success returns a function type, otherwise returns None.

        function_type := "(" arg_list ")" "->" type;
        """
        idxs = self.find_delimiters(tokens, TokenType.ReturnsSep)
        if len(idxs) != 1 or idxs[0] < 2 or\
           tokens[0].type != TokenType.OpenParen or\
           tokens[idxs[0] - 1].type != TokenType.CloseParen:
           return None

        arg_list = self.parse_function_def_args(tokens[1:idxs[0]-1])
        return_type = self.parse_basic_type(tokens[idxs[0]+1:])

        function_type = FuncTypeNode(arg_list, return_type)

        return function_type

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
        for separator_index in separator_indices:
            arg_tokens = tokens[start: separator_index]
            
            arg = self.parse_typed_var(arg_tokens)
            if arg is None:
                return None

            arg_list.append(arg)
            start = separator_index + 1

        return arg_list

    def parse_typed_var(self, tokens):
        """
        On success returns a identifier/type pair, otherwise returns None.

        typed_var := identifier ":" type;
        """
        if len(tokens) < 3 or\
           tokens[0].type != TokenType.Identifier or\
           tokens[1].type != TokenType.TypeSep:
           return None

        type = self.parse_basic_type(tokens[2:])
        if type is None:
            return None

        identifier = tokens[0].value
        typed_var = (identifier, type)

        return typed_var

    def parse_basic_type(self, tokens):
        """
        On success returns a basic type, otherwise returns None.

        basic_type := "bool" | "int" | "real";
        """
        if len(tokens) != 1 or\
           tokens[0].type not in (TokenType.KeywordBool, TokenType.KeywordInt,
                                  TokenType.KeywordReal):
            return None
        
        basic_type = BasicTypeNode(tokens[0].type)

        return basic_type

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

if __name__ == "__main__":
    program = """
        var f = (a: int) -> int { 4 + 1; }
    """

    tokens = tokenize_program(program)
    parse_tree = Parser(tokens).parse()
    if parse_tree is None:
        print "parse error"
    else:
        print json.dumps(parse_tree.to_dict(), indent=2, sort_keys=True)
