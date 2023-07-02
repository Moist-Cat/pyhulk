import unittest
import unittest.mock
import time

from . import TEST_DIR
from pyhulk.lexer import Lexer, Tokens, Token, LexingError


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.cls = Lexer

    def tearDown(self):
        pass

    def test_integer(self):
        l = Lexer("le 5.;")
        l.get_next_token()
        self.assertEqual(Token(Tokens.INTEGER, "5"), l.get_next_token())

    def test_string(self):
        l = Lexer('blob doko "lorem" noger;')
        l.get_next_token()
        l.get_next_token()
        self.assertEqual(Token(Tokens.STRING, "lorem"), l.get_next_token())

    def test_bad_string(self):
        l = Lexer('blob doko "lorem noger;')
        l.get_next_token()
        l.get_next_token()
        with self.assertRaises(LexingError):
            self.assertEqual(Token(Tokens.STRING, "lorem"), l.get_next_token())

    def test_float(self):
        l = Lexer("2.71;")
        self.assertEqual(Token(Tokens.FLOAT, "2.71"), l.get_next_token())

    def test_assign(self):
        l = Lexer('let a = "hello world"')
        self.assertEqual(Token(Tokens.LET), l.get_next_token())
        self.assertEqual(Token(Tokens.ID, "a"), l.get_next_token())
        self.assertEqual(Token(Tokens.ASSIGN), l.get_next_token())
        self.assertEqual(Token(Tokens.STRING, "hello world"), l.get_next_token())



def main_suite() -> unittest.TestSuite:
    s = unittest.TestSuite()
    load_from = unittest.defaultTestLoader.loadTestsFromTestCase
    #s.addTests(load_from(TestAPI))
    #s.addTests(load_from(TestPopulate))

    return s


def run():
    t = unittest.TextTestRunner()
    t.run(main_suite())


if __name__ == "__main__":
    run()
