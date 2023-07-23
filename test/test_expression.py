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
        result = self._interpret('5 + 10;')
        self.assertEqual(result, 15)

        result = self._interpret('5 + 10.1;')
        self.assertEqual(result, 15.1)

        result = self._interpret('5 - 10;')
        self.assertEqual(result, -5)

        result = self._interpret('10 / 5;')
        self.assertEqual(result, 2)

        result = self._interpret('5 % 10;')
        self.assertEqual(result, 5)

        result = self._interpret('5 * 10;')
        self.assertEqual(result, 50)
       
        result = self._interpret('5 ^ 2;')
        self.assertEqual(result, 25)

    def test_complex_operation(self):
        result = self._interpret('((5 * 2) + 10);')
        self.assertEqual(result, 20)

        result = self._interpret('(5 ^ 2) + (10 / 2);')
        self.assertEqual(result, 30)

    def test_builtins(self):
        return
        result = self._interpret("log(2);")
        self.assertEqual(result, log(2))

    def test_asignment(self):
        result = self._interpret("var a = 5; a;")

        self.assertEqual(5, result)

    def test_lamba(self):
        result = self._interpret("7 + (let x = 2 in x * x);")

        self.assertEqual(result, 11)

    def test_finline(self):
        result = self._interpret("function blob(x) => x*x; blob(5);")

        self.assertEqual(result, 25)

    def test_conditional(self):
        result = self._interpret('if (0) "blob" else "doko";')

        self.assertEqual(result, "doko")

    def test_boolean(self):
        result = self._interpret('if (1 > 0) "blob" else "doko";')

        self.assertEqual(result, "blob")

        result = self._interpret('if (1 == 0) "blob" else "doko";')

        self.assertEqual(result, "doko")

    def test_recursive(self):
        result = self._interpret('function fib(n) => if (n > 1) fib(n-1) + fib(n-2) else 1;(fib(5));')

        self.assertEqual(result, 8)

    def test_fn_without_args(self):
        result = self._interpret('function blob() => "doko"; blob();')

        self.assertEqual(result, "doko")

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
