
class UPLException(Exception):
    """Root exception for all exceptions that happen in UPL"""

    def __init__(self, description, row=0, col=0):
        super(UPLException, self).__init__(description)
        self.row = row
        self.col = col

class LexerException(UPLException):
    """Exceptions that happen while lexing"""

class ParserException(UPLException):
    """Exceptions that happen while parsing"""

class SemanticAnalyzerException(UPLException):
    """Exceptions that happen while semantic analysis"""
