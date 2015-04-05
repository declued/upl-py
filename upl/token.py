from enum import Enum

class TokenType(Enum):
    Error           = -1
    EOI             = 0
    BoolLiteral     = 1
    IntLiteral      = 2
    RealLiteral     = 3
    StringLiteral   = 4
    Identifier      = 5
    OpenBracket     = 6
    CloseBracket    = 7
    OpenParen       = 8
    CloseParen      = 9
    Assignment      = 10
    StatementSep    = 11
    ArgumentSep     = 12
    ReturnsSep      = 13
    Operator        = 14
    KeywordDef      = 15
    KeywordVar      = 16
    KeywordBool     = 17
    KeywordInt      = 18
    KeywordReal     = 19
    TypeSep         = 20


class Token:
    def __init__(self, type, value=None, uncooked=None, location=None):
        self.type = type
        self.value = value
        self.uncooked = uncooked
        self.location = location

    def __str__(self):
        if self.value:
            return "%s, %s" % (str(self.type), self.value)
        else:
            return str(self.type)
