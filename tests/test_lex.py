from lex import tokens
from lex import TokenType
from lex import Token

def test_tokens():
    """Check that tokenizer returns correct sequence of tokens"""
    s = "int main(void) { return 0; }"
    toks = tokens(s) # Important to first store iterator in a variable and then call next on it
    
    assert next(toks) == Token(TokenType.KEYWORD, "int")
    assert next(toks) == Token(TokenType.IDENTIFIER, "main")
    assert next(toks) == Token(TokenType.LPAREN, "(")
    assert next(toks) == Token(TokenType.KEYWORD, "void")
    assert next(toks) == Token(TokenType.RPAREN, ")")
    assert next(toks) == Token(TokenType.LBRACE, "{")
    assert next(toks) == Token(TokenType.KEYWORD, "return")
    assert next(toks) == Token(TokenType.CONSTANT, "0")
    assert next(toks) == Token(TokenType.SEMICOLON, ";")
    assert next(toks) == Token(TokenType.RBRACE, "}")

def test_tokens_fails():
    """Check that tokenizer fails when presented with an incorrect program"""
    s = "123abc"
    toks = tokens(s)
    try:
        next(toks)
        assert False
    except StopIteration:
        assert True
