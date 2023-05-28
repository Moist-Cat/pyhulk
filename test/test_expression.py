import unittest
import unittest.mock
import time

from . import TEST_DIR


class TestExpression(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dorino(self):
        pass

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
