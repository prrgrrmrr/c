"""Regular expressions and code to fetch next token from input"""

from enum import Enum
import re


class TokenType(Enum):
    """Enum of possible token types"""

    WHITESPACE = 0
    KEYWORD = 10
    IDENTIFIER = 20
    LPAREN = 30
    RPAREN = 40
    LBRACE = 50
    RBRACE = 60
    SEMICOLON = 70
    CONSTANT = 80
    HYPHEN = 90
    DECREMENT = 100
    TILDE = 110
    PLUS = 120
    ASTERISK = 130
    SLASH = 140
    PERCENT = 150
    EXCLAMATION_POINT = 160
    TWO_AMPERSANDS = 170
    TWO_VERTICAL_BARS = 180
    TWO_EQUAL_SIGNS = 190
    EXCLAMATION_POINT_EQUAL_SIGN = 200
    LESS_THAN = 210
    GREATER_THAN = 220
    LESS_THAN_OR_EQUAL = 230
    GREATER_THAN_OR_EQUAL = 240
    EQUAL_SIGN = 250


class Token:
    """Token representation"""

    def __init__(self, tok_type, value):
        self.tok_type = tok_type
        self.value = value

    def __eq__(self, other: object) -> bool:
        """Equality check"""
        return (
            isinstance(other, Token)
            and self.tok_type == other.tok_type
            and self.value == other.value
        )

    def __str__(self):
        """Sting representation of token"""
        return f"Token<type={self.tok_type}, value={repr(self.value)}>"


KEYWORDS = ("return", "int", "void")

TOKEN_TYPES = (
    # Two things to be aware of
    # 1. Need two backslash characters because otherwise python will use single backslash to escape next character. This way, python escapes the backslash itself and we end up with a single backslash character
    # 2. Groups in these regular expression should be non-capturing or better avoid using groups if possible
    ("\\s+", TokenType.WHITESPACE),
    # Identifiers and keywords
    ("[a-zA-Z_][a-zA-Z0-9_]*\\b", TokenType.IDENTIFIER),
    # Special characters
    ("\\(", TokenType.LPAREN),
    ("\\)", TokenType.RPAREN),
    ("\\{", TokenType.LBRACE),
    ("\\}", TokenType.RBRACE),
    (";", TokenType.SEMICOLON),
    ("--", TokenType.DECREMENT),
    ("-", TokenType.HYPHEN),
    ("~", TokenType.TILDE),
    ("\\+", TokenType.PLUS),
    ("\\*", TokenType.ASTERISK),
    ("/", TokenType.SLASH),
    ("%", TokenType.PERCENT),
    # Constants
    ("[0-9]+\\b", TokenType.CONSTANT),
    # Logical and relational operators
    ("&&", TokenType.TWO_AMPERSANDS),
    ("\\|\\|", TokenType.TWO_VERTICAL_BARS),
    ("==", TokenType.TWO_EQUAL_SIGNS),
    ("!=", TokenType.EXCLAMATION_POINT_EQUAL_SIGN),
    ("!", TokenType.EXCLAMATION_POINT),
    ("<=", TokenType.LESS_THAN_OR_EQUAL),
    (">=", TokenType.GREATER_THAN_OR_EQUAL),
    ("<", TokenType.LESS_THAN),
    (">", TokenType.GREATER_THAN),
    ("=", TokenType.EQUAL_SIGN),
)

TOKENIZER_RE = ""
for token_type in TOKEN_TYPES:
    exp = token_type[0]
    if len(TOKENIZER_RE) == 0:
        TOKENIZER_RE = f"({exp})"
    else:
        TOKENIZER_RE = f"{TOKENIZER_RE}|({exp})"
TOKENIZER_P = re.compile(TOKENIZER_RE)


class UnknownToken(Exception):
    pass


def tokens(s: str):
    """Generates list of tokens"""
    end = 0
    for m in re.finditer(TOKENIZER_P, s):
        if not m or m.start() != end:
            raise UnknownToken()
        end = m.end()
        if m.lastindex - 1 > 0:  # Skip whitespace
            tok_type = TOKEN_TYPES[m.lastindex - 1][1]
            value = m.group()
            if tok_type == TokenType.IDENTIFIER and value in KEYWORDS:
                tok_type = TokenType.KEYWORD
            yield Token(tok_type, value)
