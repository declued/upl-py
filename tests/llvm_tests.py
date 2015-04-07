import unittest
from upl import lexer, parser, llvm

class TestLLVM(unittest.TestCase):
    def test_program_error(self):
        self.checkCode("*some invalid code", None)

    def test_empty_program(self):
        self.checkCode("", [])

    def checkCode(self, program, expected_code):
        tokens = lexer.tokenize_program(program)
        parse_tree = parser.Parser(tokens).parse()
        code = llvm.LLVMGenerator(parse_tree).generate()

        if code is None:
            self.assertIsNone(code)
        else:
            self.assertEqual(code, expected_code)
