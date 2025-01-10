"""Recursive descent parser for C - converts source code to AST representation"""

import itertools
from collections import defaultdict
from c.lex import Token, TokenType
from c.syntax_tree import AST

"""
Grammar

<program> ::= <function>
<function> ::= "int" <identifier> "(" "void" ")" "{" <statement> "}"
<statement> ::= "return" <exp> ";"
<exp> ::= <factor> | <exp> <binop> <exp>
<factor> ::= <int> | <unop> <factor> | "(" <exp> ")"
<unop> ::= "-" | "~" | "!"
<binop> ::= "-" | "+" | "*" | "/" | "%" | "&&" | "||" | "==" | "!=" | "<" | "<=" | ">" | ">="
<identifier> ::= ? An identifier token ?
<int> ::= ? A constant token ?
"""


class BadSyntax(Exception):
    pass


class Parser:

    # Stream of tokens
    toks = None

    # Precedence levels of binary operators
    precedence = defaultdict(lambda: -1)
    precedence[TokenType.PLUS] = 45
    precedence[TokenType.HYPHEN] = 45
    precedence[TokenType.ASTERISK] = 50
    precedence[TokenType.SLASH] = 50
    precedence[TokenType.PERCENT] = 50
    precedence[TokenType.LESS_THAN] = 35
    precedence[TokenType.GREATER_THAN] = 35
    precedence[TokenType.LESS_THAN_OR_EQUAL] = 35
    precedence[TokenType.GREATER_THAN_OR_EQUAL] = 35
    precedence[TokenType.TWO_EQUAL_SIGNS] = 30
    precedence[TokenType.EXCLAMATION_POINT_EQUAL_SIGN] = 30
    precedence[TokenType.TWO_AMPERSANDS] = 10
    precedence[TokenType.TWO_VERTICAL_BARS] = 5

    @staticmethod
    def expect_token(expected):
        actual = next(Parser.toks)
        if (not actual) or (actual != expected):
            raise BadSyntax(f"Expected {expected} but got {actual}")
        return actual

    @staticmethod
    def expect_type(expected_type):
        actual = next(Parser.toks)
        if (not actual) or (actual.tok_type != expected_type):
            raise BadSyntax(f"Expected type {expected_type} but got {actual}")
        return actual

    @staticmethod
    def peek():
        t = next(Parser.toks)
        Parser.toks = itertools.chain((t,), Parser.toks)
        return t

    @staticmethod
    def expect_end():
        try:
            actual = next(Parser.toks)
            raise BadSyntax(f"Expected end of input but got {actual}")
        except StopIteration:
            pass

    @staticmethod
    def program():
        func = Parser.function()
        Parser.expect_end()
        return AST.Program(func)

    @staticmethod
    def function():
        Parser.expect_token(Token(TokenType.KEYWORD, "int"))
        name_tok = Parser.expect_type(TokenType.IDENTIFIER)
        Parser.expect_token(Token(TokenType.LPAREN, "("))
        Parser.expect_token(Token(TokenType.KEYWORD, "void"))
        Parser.expect_token(Token(TokenType.RPAREN, ")"))
        Parser.expect_token(Token(TokenType.LBRACE, "{"))
        body = Parser.statement()
        Parser.expect_token(Token(TokenType.RBRACE, "}"))
        return AST.Function(name_tok.value, body)

    @staticmethod
    def statement():
        Parser.expect_token(Token(TokenType.KEYWORD, "return"))
        return_exp = Parser.exp()
        Parser.expect_token(Token(TokenType.SEMICOLON, ";"))
        return AST.Return(return_exp)

    @staticmethod
    def exp(min_prec=0):
        # print(f"min prec {min_prec}")
        left = Parser.factor()
        next_tok = Parser.peek()
        # print(f"next tok {next_tok}")
        while Parser.precedence[next_tok.tok_type] >= min_prec:
            binary_operator = Parser.binop()
            right = Parser.exp(Parser.precedence[next_tok.tok_type] + 1)
            left = AST.BinaryOperation(binary_operator, left, right)
            next_tok = Parser.peek()
            # print(f"next tok {next_tok}")
        return left

    @staticmethod
    def factor():
        tok = Parser.peek()
        if tok.tok_type == TokenType.LPAREN:
            Parser.expect_type(TokenType.LPAREN)
            exp = Parser.exp()
            Parser.expect_type(TokenType.RPAREN)
            return exp
        elif tok.tok_type in (
            TokenType.TILDE,
            TokenType.HYPHEN,
            TokenType.EXCLAMATION_POINT,
        ):
            unary_operator = Parser.unop()
            exp = Parser.factor()
            return AST.UnaryOperation(unary_operator, exp)
        else:
            constant_tok = Parser.expect_type(TokenType.CONSTANT)
            return AST.Constant(constant_tok.value)

    @staticmethod
    def unop():
        op = next(Parser.toks)
        if op.tok_type == TokenType.TILDE:
            return AST.Complement()
        elif op.tok_type == TokenType.HYPHEN:
            return AST.Negation()
        elif op.tok_type == TokenType.EXCLAMATION_POINT:
            return AST.Not()

    @staticmethod
    def binop():
        op = next(Parser.toks)
        if op.tok_type == TokenType.HYPHEN:
            return AST.Subtraction()
        elif op.tok_type == TokenType.PLUS:
            return AST.Addition()
        elif op.tok_type == TokenType.ASTERISK:
            return AST.Multiplication()
        elif op.tok_type == TokenType.SLASH:
            return AST.Division()
        elif op.tok_type == TokenType.PERCENT:
            return AST.Remainder()
        elif op.tok_type == TokenType.TWO_AMPERSANDS:
            return AST.And()
        elif op.tok_type == TokenType.TWO_VERTICAL_BARS:
            return AST.Or()
        elif op.tok_type == TokenType.TWO_EQUAL_SIGNS:
            return AST.Equal()
        elif op.tok_type == TokenType.EXCLAMATION_POINT_EQUAL_SIGN:
            return AST.NotEqual()
        elif op.tok_type == TokenType.LESS_THAN:
            return AST.LessThan()
        elif op.tok_type == TokenType.LESS_THAN_OR_EQUAL:
            return AST.LessOrEqual()
        elif op.tok_type == TokenType.GREATER_THAN:
            return AST.GreaterThan()
        elif op.tok_type == TokenType.GREATER_THAN_OR_EQUAL:
            return AST.GreaterOrEqual()


def parse(toks):
    Parser.toks = toks
    return Parser.program()


# type: ignore
