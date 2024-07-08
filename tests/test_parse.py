from parse import Token, TokenType, parse
from syntax_tree import AST

def test_parse():
    toks = (
        tok for tok in (
            Token(TokenType.KEYWORD, "int"),
            Token(TokenType.IDENTIFIER, "main"),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.KEYWORD, "void"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.LBRACE, "{"),
            Token(TokenType.KEYWORD, "return"),
            Token(TokenType.CONSTANT, "0"),
            Token(TokenType.SEMICOLON, ";"),
            Token(TokenType.RBRACE, "}")
        )
    )
    ast = parse(toks)
    assert ast == AST.Program(AST.Function("main", AST.Return(AST.Constant("0"))))