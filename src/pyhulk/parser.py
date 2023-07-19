from typing import Union

from pyhulk.lexer import Lexer, Tokens, LITERALS
from pyhulk.log import logged

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

    def __str__(self):
        return str(self.eval(None))

    def __repr__(self):
        return self.__str__()


class Literal(AST):
    _val: Union[float, int, str]

    def __init__(self, value):
        self._val = value

    def eval(self, ctx):
        return self._val

class StrLiteral(Literal):
    _val: str

class IntLiteral(Literal):
    _val: int

class FloatLiteral(Literal):
    _val: float

class BinaryOperation(AST):

    operation: "Callable" = None

    def __init__(self, left: AST, right: AST):
        self.left = left
        self.right = right

    def eval(self, ctx):
        return self.operation(self.left.eval(ctx), self.right.eval(ctx))

    def __str__(self):
        return str(self.left) + self.__class__.__name__ + str(self.right)

class Sum(BinaryOperation):

    def operation(self, a, b):
        return a + b

class Substraction(BinaryOperation):

    def operation(self, a, b):
        return a + -b


class Division(BinaryOperation):

    def operation(self, a, b):
        return a / b


class Mult(BinaryOperation):

    def operation(self, a, b):
        return a * b

class Modulo(BinaryOperation):

    def operation(self, a, b):
        return a % b

class Exp(BinaryOperation):

    def operation(self, a, b):
        return a**b

class Variable(AST):

    def __init__(self, name):
        name: str = name

    def eval(self, ctx):
        return ctx[self.name]

class Parser:

    def __init__(self, lexer: Lexer, line=1):
        self.lexer = lexer
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
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(SyntaxError(f"Token types {self.current_token.type} and {token_type} differ"))

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
        if token.type == Tokens.STRING:
            self.eat(Tokens.STRING)
            return StrLiteral(token.value)
        elif token.type == Tokens.INTEGER:
            self.eat(Tokens.INTEGER)
            return IntLiteral(int(token.value))
        elif token.type == Tokens.FLOAT:
            self.eat(Tokens.FLOAT)
            return FloatLiteral(float(token.value))
        # else
        self.error(SyntaxError(f"Invalid literal {token.value} {token.type}"))


    def term(self):
        node = self.factor()

        while self.current_token.type in (
                Tokens.MULT,
                Tokens.DIV,
                Tokens.MODULO,
                Tokens.EXP,
        ):
            token = self.current_token
            ast = None
            if token.type == Tokens.MULT:
                self.eat(Tokens.MULT)
                ast = Mult
            elif token.type == Tokens.DIV:
                self.eat(Tokens.DIV)
                ast = Division
            elif token.type == Tokens.MODULO:
                self.eat(Tokens.MODULO)
                ast = Modulo
            elif token.type == Tokens.EXP:
                self.eat(Tokens.EXP)
                ast = Exp

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


    def parse(self):
        # either an expression or a declaration or a function
        # declaration
        nodes = []
        while self.current_token.type != Tokens.EOF:
            if self.current_token.type == Tokens.LET:
                node = self.declaration()
            elif self.current_token == Tokens.FUNCTION:
                node = self.function()
            else:
                node = self.expr()
            if self.current_token.type != Tokens.END:
                raise self.error(SyntaxError("Expected ';'"))
            self.eat(Tokens.END)
            nodes.append(node)
        return nodes

class Interpreter:

    GLOBAL_SCOPE = Context()
    def __init__(self, parser: Parser):
        self.parser = parser
        self._tree = None

    @property
    def tree(self):
        if self._tree is None:
            self._tree = self.parser.parse()
        return self._tree

    def interpret(self):
        if not self.tree:
            return ""
        node = self.tree.pop()
        return node.eval(self.GLOBAL_SCOPE)

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
