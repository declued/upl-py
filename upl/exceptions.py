
class UPLException(Exception):
    """Root exception for all exceptions that happen in UPL"""

    def __init__(self, description, location=(0, 0)):
        super(UPLException, self).__init__(description)
        self.location = location

class LexerException(UPLException):
    """Exceptions that happen while lexing"""

class ParserException(UPLException):
    """Exceptions that happen while parsing"""

class SemanticAnalyzerException(UPLException):
    """Exceptions that happen while semantic analysis"""
