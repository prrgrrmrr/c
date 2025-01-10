from c.parse import Token, TokenType, parse
from c.syntax_tree import AST


def test_parse():
    toks = (
        tok
        for tok in (
            Token(TokenType.KEYWORD, "int"),
            Token(TokenType.IDENTIFIER, "main"),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.KEYWORD, "void"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.LBRACE, "{"),
            Token(TokenType.KEYWORD, "return"),
            Token(TokenType.CONSTANT, "0"),
            Token(TokenType.SEMICOLON, ";"),
            Token(TokenType.RBRACE, "}"),
        )
    )
    ast = parse(toks)
    assert ast == AST.Program(AST.Function("main", AST.Return(AST.Constant("0"))))


def test_parse_unop():

    toks = (
        tok
        for tok in (
            Token(TokenType.KEYWORD, "int"),
            Token(TokenType.IDENTIFIER, "main"),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.KEYWORD, "void"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.LBRACE, "{"),
            Token(TokenType.KEYWORD, "return"),
            Token(TokenType.TILDE, "~"),
            Token(TokenType.HYPHEN, "-"),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.CONSTANT, "10"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.SEMICOLON, ";"),
            Token(TokenType.RBRACE, "}"),
        )
    )
    ast = parse(toks)
    assert ast == AST.Program(
        AST.Function(
            "main",
            AST.Return(
                AST.UnaryOperation(
                    AST.Complement(),
                    AST.UnaryOperation(AST.Negation(), AST.Constant("10")),
                )
            ),
        )
    )


def test_parse_binop():
    toks = (
        tok
        for tok in (
            Token(TokenType.KEYWORD, "int"),
            Token(TokenType.IDENTIFIER, "main"),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.KEYWORD, "void"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.LBRACE, "{"),
            Token(TokenType.KEYWORD, "return"),
            Token(TokenType.CONSTANT, "1"),
            Token(TokenType.ASTERISK, "*"),
            Token(TokenType.CONSTANT, "2"),
            Token(TokenType.HYPHEN, "-"),
            Token(TokenType.CONSTANT, "2"),
            Token(TokenType.ASTERISK, "*"),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.CONSTANT, "2"),
            Token(TokenType.PLUS, "+"),
            Token(TokenType.CONSTANT, "4"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.SEMICOLON, ";"),
            Token(TokenType.RBRACE, "}"),
        )
    )

    ast = parse(toks)
    assert ast == AST.Program(
        AST.Function(
            "main",
            AST.Return(
                AST.BinaryOperation(
                    AST.Subtraction(),
                    AST.BinaryOperation(
                        AST.Multiplication(), AST.Constant("1"), AST.Constant("2")
                    ),
                    AST.BinaryOperation(
                        AST.Multiplication(),
                        AST.Constant("2"),
                        AST.BinaryOperation(
                            AST.Addition(), AST.Constant("2"), AST.Constant("4")
                        ),
                    ),
                )
            ),
        )
    )
