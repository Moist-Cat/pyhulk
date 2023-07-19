from enum import Enum

from pyhulk.log import logged

class Tokens(Enum):
    ID = "ID"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    EXP = "^"
    LPAREN = "("
    RPAREN = ")"
    ASSIGN = "="
    DOT = "."
    END = ";"
    EOF = None

    LET = "let"
    FLOAT_TYPE = "float"
    INT_TYPE = "int"
    FUNCTION = "function"
    QUOTATION = '"'
    COMMA = ","

LITERALS = {Tokens.STRING.name, Tokens.INTEGER.name, Tokens.FLOAT.name}

def token_from_value(value):
    for key, pair in Tokens.__members__.items():
        if value == pair.value:
            return Tokens.__getitem__(key)
    return None

@logged
class Token:
    def __init__(self, type_: "Tokens", value=None, lineno=None, column=None):
        self.type = type_.name
        self.value = value if value else type_.value
        self.logger.debug("Created token %s", self)
        self.lineno = lineno
        self.column = column

    def __hash__(self):
        return hash((self.type, self.value))

    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS, "+")
            Token(MUL, "*")
        """
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
        )

    def __eq__(self, other):
        return isinstance(other, Token) and other.type == self.type and other.value == self.value

    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {
    "let": Token(Tokens.LET),
    "int": Token(Tokens.INT_TYPE),
    "float": Token(Tokens.FLOAT_TYPE),
    "function": Token(Tokens.FUNCTION),
}

class LexingError(Exception):
    pass

# denotes end of a sentence
@logged
class Lexer:

    def __init__(self, text, line=1):
        self.text: str = text
        self.pos: int = 0
        self.current_char: str = self.text[self.pos]

        self.line = 1
        self.column = 1

    def error(self, exception):
        print(f"Error lexing line {self.line} col {self.column}")
        print(self.text)
        print(" "*(self.column) + "^")
        raise exception

    def get_result(self, condition):
        result = ""
        while self.current_char != Tokens.END.value and getattr(self.current_char, f"is{condition}")():
            result += self.current_char
            self.advance()
        return result

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        if self.current_char == '\n':
            self.lineno += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        self.get_result("space")

    def integer(self):
        """Return a (multidigit) integer consumed from the input."""
        # XXX you can use it twice to build a float
        # Ex.
        # 1234.431
        # 1234
        # parser notices the dot
        # gets the digits after the dot
        # new_num/((log(number)/log(10))*10)
        # number + new_num
        # or you can just add it as a string idc
        result = self.get_result("digit")
        self.logger.debug("Lexing number %s", result)

        return result

    def string(self):
        result = ""
        # End Of String
        while self.current_char != Tokens.QUOTATION.value and self.current_char is not None:
            result += self.current_char
            self.advance()

        if self.current_char is None:
            self.error(LexingError("Unterminated string literal"))
        self.logger.debug("Lexing string %s", result)
        return result

    def _id(self):
        """Handle identifiers and reserved keywords"""
        result = self.get_result("alnum")

        token = RESERVED_KEYWORDS.get(result, Token(Tokens.ID, result))
        self.logger.debug("Lexing identifier %s", token)
        return token


    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                _integer = self.integer()
                # could be float
                if self.current_char == Tokens.DOT.value and self.peek().isdigit():
                    self.advance()
                    _mantisa = self.integer()
                    return Token(Tokens.FLOAT, f"{_integer}.{_mantisa}")
                return Token(Tokens.INTEGER, _integer)

            if self.current_char == Tokens.QUOTATION.value:
                self.advance()
                return Token(Tokens.STRING, self.string())

            token = token_from_value(self.current_char)
            if not token:
                self.error(LexingError("Invalid character"))

            self.advance()
            return Token(token)

        return Token(Tokens.EOF)
