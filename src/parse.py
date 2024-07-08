"""Recursive descent parser for C - converts source code to AST representation"""

from lex import Token, TokenType
from syntax_tree import AST

"""
Grammar

<program> ::= <function>
<function> ::= "int" <identifier> "(" "void" ")" "{" <statement> "}"
<statement> ::= "return" <exp> ";"
<exp> ::= <int>
<identifier> ::= ? An identifier token ?
<int> ::= ? A constant token ?
"""


class BadSyntax(Exception):
    pass


class Parser:
    
    def expect_token(expected, toks):
        actual = next(toks)
        if (not actual) or (actual != expected):
            raise BadSyntax(f"Expected {expected} but got {actual}")
        return actual
    
    def expect_type(expected_type, toks):
        actual = next(toks)
        if (not actual) or (actual.tok_type != expected_type):
            raise BadSyntax(f"Expected type {expected_type} but got {actual}")
        return actual
    
    def expect_end(toks):
        try:
            actual = next(toks)
            raise BadSyntax(f"Expected end of input but got {actual}")
        except StopIteration:
            pass
        
    def program(toks):
        func = Parser.function(toks)
        Parser.expect_end(toks)
        return AST.Program(func)
    
    def function(toks):
        Parser.expect_token(Token(TokenType.KEYWORD, "int"), toks)
        name_tok = Parser.expect_type(TokenType.IDENTIFIER, toks)
        Parser.expect_token(Token(TokenType.LPAREN, "("), toks)
        Parser.expect_token(Token(TokenType.KEYWORD, "void"), toks)
        Parser.expect_token(Token(TokenType.RPAREN, ")"), toks)
        Parser.expect_token(Token(TokenType.LBRACE, "{"), toks)
        body = Parser.statement(toks)
        Parser.expect_token(Token(TokenType.RBRACE, "}"), toks)
        return AST.Function(name_tok.value, body)
    
    def statement(toks):
        Parser.expect_token(Token(TokenType.KEYWORD, "return"), toks)
        return_exp = Parser.exp(toks)
        Parser.expect_token(Token(TokenType.SEMICOLON, ";"), toks)
        return AST.Return(return_exp)
    
    def exp(toks):
        constant_tok = Parser.expect_type(TokenType.CONSTANT, toks)
        return AST.Constant(constant_tok.value)


def parse(toks):
    return Parser.program(toks)

 # type: ignore