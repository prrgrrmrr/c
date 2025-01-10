from c.lex import tokens
from c.lex import TokenType
from c.lex import Token
from c.lex import UnknownToken


def test_tokens():
    """Check that tokenizer returns correct sequence of tokens"""
    s = "int main(void) { return ~( -2 ); }"
    toks = tokens(
        s
    )  # Important to first store iterator in a variable and then call next on it

    assert next(toks) == Token(TokenType.KEYWORD, "int")
    assert next(toks) == Token(TokenType.IDENTIFIER, "main")
    assert next(toks) == Token(TokenType.LPAREN, "(")
    assert next(toks) == Token(TokenType.KEYWORD, "void")
    assert next(toks) == Token(TokenType.RPAREN, ")")
    assert next(toks) == Token(TokenType.LBRACE, "{")
    assert next(toks) == Token(TokenType.KEYWORD, "return")
    assert next(toks) == Token(TokenType.TILDE, "~")
    assert next(toks) == Token(TokenType.LPAREN, "(")
    assert next(toks) == Token(TokenType.HYPHEN, "-")
    assert next(toks) == Token(TokenType.CONSTANT, "2")
    assert next(toks) == Token(TokenType.RPAREN, ")")
    assert next(toks) == Token(TokenType.SEMICOLON, ";")
    assert next(toks) == Token(TokenType.RBRACE, "}")
    try:
        next(toks)
        assert False
    except StopIteration:
        pass


def test_tokens_fails():
    """Check that lexer fails when presented with an incorrect program"""
    s = "123abc"
    toks = tokens(s)
    try:
        next(toks)
        assert False
    except UnknownToken:
        pass
