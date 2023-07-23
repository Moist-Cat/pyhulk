from typing import Union, List

from pyhulk.lexer import Lexer, Tokens, LITERALS, CONDITIONALS
from pyhulk.log import logged

class UnexpectedToken(SyntaxError):
    pass

class Context:

    _dict: dict

    def __init__(self, _dict=None):
        self._dict = _dict or {}

    def __setitem__(self, key, value):
        self._dict.__setitem__(key, value)

    def __getitem__(self, key):
        try:
            return self._dict.__getitem__(key)
        except KeyError as exc:
            raise NameError(str(exc) + " is not defined")

    def __str__(self):
        return self._dict.__str__()

    def __repr__(self):
        return self.__str__()

class AST:
    """
    Master class for expressions
    """

    def __call__(self, ctx: "Context"):
        return self.eval(ctx)

    def eval(self, ctx: "Context"):
        raise NotImplementedError()

    def __str__(self):
        return str(self(None))

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

class BookLiteral(Literal):
    _val: bool

class BinaryOperation(AST):

    operation: "Callable" = None

    def __init__(self, left: AST, right: AST):
        self.left = left
        self.right = right

    def eval(self, ctx):
        return self.operation(self.left(ctx), self.right(ctx))

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

class Equals(BinaryOperation):

    def operation(self, a, b):
        return a == b

class Higher(BinaryOperation):

    def operation(self, a, b):
        return a > b

class Lower(BinaryOperation):

    def operation(self, a, b):
        return a < b

class VariableDeclaration(AST):

    def __init__(self, name, expression: AST):
        self.name = name
        self.expression = expression

    def eval(self, ctx):
        ctx[self.name] = self.expression(ctx)
        return None

    def __str__(self):
        return f"<(VariableDeclaration) [name: {self.name}, value: {self.expression}]>"

class Variable(AST):

    def __init__(self, name):
        self.name = name

    def eval(self, ctx):
        return ctx[self.name]

    def __str__(self):
        return f"<(Variable) [name: {self.name}]>"

class BlockNode(AST):
    """
    QOL class to evaluate multiple statements
    """

    def __init__(self, blocks: List[AST]):
        self.blocks = blocks

    def eval(self, ctx):
        for block in self.blocks:
            bl = block(ctx)
        return bl

    def __str__(self):
        return self.blocks.__str__()

class FunctionDeclaration(AST):

    def __init__(self, name, args: List[str], block_node: AST):
        self.name = name
        self.args = args
        self.block_node = block_node

    def eval(self, ctx):
        ctx[self.name] = self
        return None

    def __str__(self):
        return f"<(FunctionDeclaration) [name: {self.name}, args: {self.args}, block_node: {self.block_node}]>"

class Function(AST):

    def __init__(self, name, args):
        self.name = name
        self.args = args

    def eval(self, ctx):
        fun_decl = ctx[self.name]
        fun_args = fun_decl.args

        _fun_ctx = {}
        for index, arg in enumerate(fun_args.blocks):
            _fun_ctx[arg.name] = self.args.blocks[index].eval(ctx)
        fun_ctx = Context(_fun_ctx)
        # allow recursivity
        fun_ctx[self.name] = fun_decl

        return fun_decl.block_node(fun_ctx)

    def __str__(self):
        return f"<(Function) [name: {self.name}, args: {self.args}]>"

class Lambda(AST):
    """
    let-in expression
    """

    def __init__(self, variables: List[str], block_statement: AST):
        self.variables = variables
        self.block_statement = block_statement

    def eval(self, ctx):
        local_ctx = Context()
        
        # https://github.com/matcom/programming/tree/main/projects/hulk#variables
        # "( ... ) Fuera de una expresión let-in las variables dejan de existir. ( ... )"
        # declare variables inside the scope of the lambda
        self.variables(local_ctx)

        res = self.block_statement(local_ctx)

        return res

class Conditional(AST):

    def __init__(
        self,
        hipotesis: AST,
        tesis: BlockNode,
        antitesis: BlockNode
    ):
        self.hipotesis = hipotesis
        self.tesis = tesis
        self.antitesis = antitesis

    def eval(self, ctx):
        res = bool(self.hipotesis(ctx))
        if res:
            return self.tesis(ctx)
        return self.antitesis(ctx)

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
            self.error(UnexpectedToken(f"Expected {token_type} found {self.current_token.type}."))

    def arguments(self):
        if self.current_token.type != Tokens.LPAREN:
            return None

        self.eat(Tokens.LPAREN)
        args = []
        args.append(self.expr())
        while self.current_token.type == Tokens.COMMA:
            self.eat(Tokens.COMMA)
            args.append(self.expr())
        self.eat(Tokens.RPAREN)

        return BlockNode(args)

    def namespace(self):
        """
        variable : ID
        """
        name = self.current_token
        self.eat(Tokens.ID)
        args = self.arguments()
        if args:
            node = Function(name, args)
        else:
            node = Variable(name)
        return node

    def letin(self):
        self.eat(Tokens.LET)
        variables = self.assignment()
        self.eat(Tokens.IN)

        return Lambda(variables, self.expr())
    
    def assignment(self):
        names = []
        variables = []

        name = self.current_token
        names.append(name)

        self.eat(Tokens.ID)
        self.eat(Tokens.ASSIGN)
        val = self.expr()

        var = VariableDeclaration(name, val)
        variables.append(var)

        while self.current_token == Tokens.COMMA:
            self.eat(Tokens.COMMA)
            name = self.current_token
            names.append(name)
            
            self.eat(Tokens.ID)
            self.eat(Tokens.ASSIGN)
            val = self.expr()

            var = VariableDeclaration(name, val)
            variables.append(var)

        multi_decl = BlockNode(variables)

        return multi_decl

    def declaration(self):
        self.eat(Tokens.VAR)
        return self.assignment()

    def function(self):
        self.eat(Tokens.FUNCTION)
        name = self.current_token
        self.eat(Tokens.ID)
        args = self.arguments()

        if self.current_token.type == Tokens.FINLINE:
            self.eat(Tokens.FINLINE)
            return FunctionDeclaration(name, args, self.expr())
        return None

    def conditional(self):
        self.eat(Tokens.IF)

        self.eat(Tokens.LPAREN)
        hipotesis = self.expr()
        self.eat(Tokens.RPAREN)

        tesis = self.expr()

        self.eat(Tokens.ELSE)

        antitesis = self.expr()

        return Conditional(
            hipotesis,
            BlockNode([tesis]),
            BlockNode([antitesis]),
        )

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

        while self.current_token.type in {
                Tokens.MULT,
                Tokens.DIV,
                Tokens.MODULO,
                Tokens.EXP,
        }:
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
            node = self.literal()
        elif token.type == Tokens.LET:
            node = self.letin()
        elif token.type == Tokens.LPAREN:
            self.eat(Tokens.LPAREN)
            node = self.expr()
            self.eat(Tokens.RPAREN)
        elif token.type == Tokens.IF:
            node = self.conditional()
        elif token.type == Tokens.ID:
            node = self.namespace()
        else:
            raise self.error(SyntaxError(token))

        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in {Tokens.PLUS, Tokens.MINUS}.union(CONDITIONALS):
            token = self.current_token
            ast = None
            if token.type == Tokens.PLUS:
                self.eat(Tokens.PLUS)
                ast = Sum
            elif token.type == Tokens.MINUS:
                self.eat(Tokens.MINUS)
                ast = Substraction
            elif token.type == Tokens.EQUALS:
                self.eat(Tokens.EQUALS)
                ast = Equals
            elif token.type == Tokens.HIGHER:
                self.eat(Tokens.HIGHER)
                ast = Higher
            elif token.type == Tokens.LOWER:
                self.eat(Tokens.LOWER)
                ast = Lower
            else:
                raise Exception("Ehhhh???")


            node = ast(left=node, right=self.term())

        return node


    def _parse(self):
        if self.current_token.type == Tokens.VAR:
            node = self.declaration()
        elif self.current_token.type == Tokens.FUNCTION:
            node = self.function()
        else:
            node = self.expr()
        if self.current_token.type != Tokens.END:
            raise self.error(SyntaxError("Expected ';'"))

        return node

    def parse(self):
        # either an expression or a declaration or a function
        # declaration
        nodes = []
        while self.current_token.type != Tokens.EOF:
            node = self._parse()
            self.eat(Tokens.END)
            nodes.append(node)

        return BlockNode(nodes)

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
        return self.tree(self.GLOBAL_SCOPE)

def repl():
    import os
    while True:
        try:
            lexer = Lexer(input(">>> "))
            parser = Parser(lexer)
            print(Interpreter(parser).interpret())
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
