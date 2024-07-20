"""Recursive descent parser for C - converts source code to AST representation"""

import itertools
from c.lex import Token, TokenType
from c.syntax_tree import AST

"""
Grammar

<program> ::= <function>
<function> ::= "int" <identifier> "(" "void" ")" "{" <statement> "}"
<statement> ::= "return" <exp> ";"
<exp> ::= <int> | <unop> <exp> | "(" <exp> ")"
<unop> ::= "-" | "~"
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
    
    def peek(toks):
        t = next(toks)
        return t, itertools.chain((t,), toks)
    
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
        tok, toks = Parser.peek(toks)
        if tok.tok_type == TokenType.LPAREN:
            Parser.expect_type(TokenType.LPAREN, toks)
            exp = Parser.exp(toks)
            Parser.expect_type(TokenType.RPAREN, toks)
            return exp
        elif tok.tok_type in (TokenType.TILDE, TokenType.HYPHEN):
            unary_operator =  Parser.unop(toks)
            exp = Parser.exp(toks)
            return AST.UnaryOperation(unary_operator, exp)
        else:
            constant_tok = Parser.expect_type(TokenType.CONSTANT, toks)
            return AST.Constant(constant_tok.value)
    
    def unop(toks):
        op = next(toks)
        if op.tok_type == TokenType.TILDE:
            return AST.Complement()
        elif op.tok_type == TokenType.HYPHEN:
            return AST.Negation()


def parse(toks):
    return Parser.program(toks)

 # type: ignore
