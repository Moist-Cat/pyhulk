import unittest
import unittest.mock
import time

from . import TEST_DIR
from pyhulk.lexer import Lexer
from pyhulk.parser import Parser, Interpreter


class TestExpression(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _prepare(self, text):
        lexer = Lexer(text)
        parser = Parser(lexer)

        return Interpreter(parser)

    def _interpret(self, text):
        return self._prepare(text).interpret()

    def test_literal(self):
        result = self._interpret("5;")
        self.assertEqual(result, 5)

        result = self._interpret('"blob";')
        self.assertEqual(result, "blob")

        result = self._interpret('7.03;')
        self.assertEqual(result, 7.03)

    def test_basic_operation(self):
        result = self._interpret('"5 + 10"')
        self.assertEqual(result, 15)

        result = self._interpret('"5 + 10.1"')
        self.assertEqual(result, 15.1)

        result = self._interpret('"5 - 10"')
        self.assertEqual(result, -5)

        result = self._interpret('"10 / 5"')
        self.assertEqual(result, 2)

        result = self._interpret('"5 % 10"')
        self.assertEqual(result, 5)

        result = self._interpret('"5 * 10"')
        self.assertEqual(result, 50)
       
        result = self._interpret('"5 ^ 2"')
        self.assertEqual(result, 25)


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
