# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
from enum import Enum

class Tokens(Enum):
    ID = "ID"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    LPAREN = "("
    RPAREN = ")"
    ASSIGN = "="
    DOT = "."
    END = ";"
    LET = "let"
    FLOAT_TYPE = "float"
    INT_TYPE = "int"
    QUOTATION = "\""

def token_from_value(value):
    for key, pair in Tokens.__members__.items():
        if value == pair.value:
            return Tokens.__getitem__(key)
    return None

class Token:
    def __init__(self, type_: "Tokens", value=None):
        self.type = type_.name
        self.value = value if value else type_.value

    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS, "+")
            Token(MUL, "*")
        """
        return "Token({type_}, {value})".format(
            type_=self.type,
            value=repr(self.value)
        )

    def __eq__(self, other):
        return isinstance(other, Token) and other.type == self.type and other.value == self.value

    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {
    "let": Token(Tokens.LET),
    "int": Token(Tokens.INT_TYPE),
    "float": Token(Tokens.FLOAT_TYPE),
}

# denotes end of a sentence
class Lexer:

    def __init__(self, text, line=1):
        self.text: str = text
        self.line: int = line
        self.pos: int = 0
        self.current_char: str = self.text[self.pos]

    def error(self, exception):
        print(f"Error parsing line {self.line} col {self.pos+1}")
        print(self.text)
        print(" "*(self.pos+1) + "^")
        raise exception

    def get_result(self, condition):
        result = ""
        while self.current_char != Tokens.END.value and getattr(self.current_char, f"is{condition}")():
            result += self.current_char
            self.advance()
        return result

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.error(SyntaxError("Unexpected EOF while parsing")) # No ";"--explode
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

        return result

    def string(self):
        result = ""
        # nothing fancy here
        # End Of String
        while self.current_char != Tokens.QUOTATION.value:
            result += self.current_char
            self.advance()

        if self.current_char is not Tokens.QUOTATION.value:
            self.error("Unterminated string literal")
        return result

    def _id(self):
        """Handle identifiers and reserved keywords"""
        result = self.get_result("alnum")

        token = RESERVED_KEYWORDS.get(result, Token(Tokens.ID, result))
        return token


    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char != Tokens.END.value:
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
                breakpoint()
                self.error(SyntaxError("Invalid syntax"))

            self.advance()
            return Token(token)

        return Token(Tokens.END)
