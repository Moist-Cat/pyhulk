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


class Variable(AST):

    def __init__(self, name):
        name: str = name

    def eval(self, ctx):
        return ctx[self.name]

# XXX finish parser
# it's just adding the methods who handle other cases
# literal : EOF
#         | (OPERATION (expr))
class Parser:

    def __init__(self, lexer: Lexer, line=1):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.line = line

    def error(self, exception):
        print(f"Error parsing line {self.line} col {self.lexer.pos+1}")
        print(self.lexer.text)
        print(" "*(self.lexer.pos+1) + "^")
        raise exception

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(SyntaxError("???"))

    def parse(self):
        # statements
        if self.current_token == Tokens.LET.value:
            node = self.declare()
            return node
        return self.expr()
    
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
            return StrLiteral(token.value)
        elif token.type == Tokens.INTEGER.name:
            return IntLiteral(int(token.value))
        elif token.type == Tokens.FLOAT.name:
            return FloatLiteral(float(token.value))
        # else
        self.error(SyntaxError(f"Invalid literal {token.value} {token.type}"))


    def term(self):
        """
        term : (function|variable)
        """
        return 

    def operation(self):
        """
        operation: (PLUS|MINUS|MULT|DIV|EXP)
        """
        pass

    def expr(self):
        """
        expr : LPAREN expr RPAREN
             | term
             | term operation expr
             | expr (PLUT)
        """
        node = None
        # expressions
        elif self.current_token == Tokens.LPAREN.value:
            self.eat(Tokens.LPAREN)
            node = self.expr()
        elif self.current_token.type in LITERALS:
            return self.literal()
        elif self.current_token.type == Tokens.ID.value:
            return self.term()

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
