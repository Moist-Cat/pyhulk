from typing import Union

from pyhulk.lexer import Lexer, Tokens, LITERALS
from pyhulk.log import logged

class TypeValidator:

    type_: type
    _val = None

    def __init__(self, type_):
        self.type_ = type_

    def __get__(self, obj, objtype=None):
        return self._val


    def __set__(self, obj, value):
        #if not isinstance(value, self.type_):
        #    raise ValueError(
        #        f"type {self.type_} expected found '{value.__class__.__name__}' for {value}"
        #    )
        self._val = self.type_(value)

class Context:

    _dict: dict

    def __init__(self):
        self._dict = {}

    def __setitem__(self, key, value):
        self._dict.__setitem__(key, value)

    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    def __str__(self):
        return self._dict.__str__()

class AST:
    """
    Master class for expressions
    """

    def eval(self, ctx: "Context"):
        raise NotImplementedError()


class Literal(AST):
    _val: Union[float, int, str]

    def __init__(self, value):
        self._val = value

    def eval(self, ctx):
        return self._val

class StrLiteral(Literal):
    _val: str = TypeValidator(str)

class IntLiteral(Literal):
    _val: int = TypeValidator(int)

class FloatLiteral(Literal):
    _val: float = TypeValidator(float)

class BinaryOperation(AST):

    openration: "Callable" = None

    def __init__(self, left: AST, right: AST):
        self.left = left
        self.right = right

    def eval(self):
        return self.operation(self.left.eval(), self.right.eval())

class Sum(BinaryOperation):

    operation = sum

def subs(a, b):
    # :D
    return sum(a, -b)
class Substraction(BinaryOperation):

    operation = subs


def div(a, b):
    return a / b
class Division(BinaryOperation):

    operation = div


def mult(a, b):
    return a * b
class Mult(BinaryOperation):

    operation = mult

class Variable(AST):

    def __init__(self, name):
        name: str = name

    def eval(self, ctx):
        return ctx[self.name]

class Parser:

    def __init__(self, lexer: Lexer, line=1):
        self.lexer = lexer
        self._old_token = None
        self.current_token = self.lexer.get_next_token()
        self.line = line

    def error(self, exception):
        print(f"Error parsing line {self.line} col {self.lexer.pos+1}")
        print(self.lexer.text)
        print(" "*(self.lexer.column) + "^")
        raise exception

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type.name:
            self._old_token = self.current_token
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(SyntaxError(f"Token types {self.current_token.type} and {token_type} differ"))

    def parse(self):
        node = self.program()
        if self.current_token.type != Tokens.END:
            self.error
        if self.current_token == Tokens.LET.value:
            self.error(EOFError("Unexpected EOF while parsing"))
        return node
    
    def funcion(self):
        """
        function : ID (LPAREN(expr1 COMMA expr2 COMMA ... COMMA exprn) RPAREN)
        """
        pass

    def variable(self):
        """
        variable : ID
        """
        pass
    
    def declare(self):
        pass

    def literal(self):
        """
        literal : (STRING|FLOAT|INT)
        """
        token = self.current_token
        if token.type == Tokens.STRING.name:
            self.eat(Tokens.STRING)
            return StrLiteral(token.value)
        elif token.type == Tokens.INTEGER.name:
            self.eat(Tokens.INTEGER)
            return IntLiteral(int(token.value))
        elif token.type == Tokens.FLOAT.name:
            self.eat(Tokens.FLOAT)
            return FloatLiteral(float(token.value))
        # else
        self.error(SyntaxError(f"Invalid literal {token.value} {token.type}"))


    def term(self):
        node = self.factor()

        while self.current_token.type in (
                Tokens.MULT,
                Tokens.DIV,
        ):
            token = self.current_token
            ast = None
            if token.type == Tokens.MULT:
                self.eat(Tokens.MULT)
                ast = Mult
            elif token.type == Tokens.DIV:
                self.eat(Tokens.DIV)
                ast = Division

            node = ast(left=node, right=self.factor())

        return node

    def factor(self):
        token = self.current_token
        if token.type in LITERALS:
            return self.literal()
        elif token.type == Tokens.LPAREN:
            self.eat(Tokens.LPAREN)
            node = self.expr()
            self.eat(Tokens.RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def expr(self):
        """
        """
        node = self.term()
        while self.current_token.type in (Tokens.PLUS, Tokens.MINUS):
            breakpoint()
            token = self.current_token
            ast = None
            if token.type == Tokens.PLUS:
                self.eat(Tokens.PLUS)
                ast = Sum
            elif token.type == Tokens.MINUS:
                self.eat(Tokens.MINUS)
                ast = Substraction

            node = ast(left=node, right=self.term())

        return node


    def program(self):
        # either an expression or a declaration or a function
        # declaration
        while self.current_token is not None:
            breakpoint()
            if self.current_token.type == Tokens.LET:
                node = self.declaration()
            elif self.current_token == Tokens.FUNCTION:
                node = self.function()
            else:
                node = self.expr()

class Interpreter:

    GLOBAL_SCOPE = Context()
    def __init__(self, parser: Parser):
        self.parser = parser

    def interpret(self):
        tree = self.parser.parse()
        if tree is None:
            return ""
        return tree.eval(self.GLOBAL_SCOPE)


def repl():
    import os
    while True:
        try:
            lexer = Lexer(input(">>> "))
            parser = Parser(lexer)
            interpreter = Interpreter(parser)
            result = interpreter.interpret()
            print(result)
            #print(interpreter.GLOBAL_SCOPE)
        except KeyboardInterrupt:
            os.system("clear")
        except EOFError:
            print()
            print("bye bye")
            break 
        except Exception as exc:
            print(exc)

if __name__ == "__main__":
    repl()
