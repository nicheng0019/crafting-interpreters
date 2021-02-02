# coding=utf-8

import Expr
import TokenType
import Pylox


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.discards_tokens = {TokenType.TokenType.CLASS, TokenType.TokenType.FUN, TokenType.TokenType.VAR,
                                TokenType.TokenType.FOR, TokenType.TokenType.IF, TokenType.TokenType.WHILE,
                                TokenType.TokenType.PRINT, TokenType.TokenType.RETURN}

    def parse(self):
        try:
            return self.expression()
        except RuntimeError:
            return None

    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.TokenType.BANG_EQUAL, TokenType.TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def match(self, *args):
        for tokentype in args:
            if self.check(tokentype):
                self.advance()
                return True

        return False

    def check(self, tokentype):
        if self.isAtEnd():
            return False

        return self.peek().type == tokentype

    def advance(self):
        if not self.isAtEnd():
            self.current += 1

        return self.previous()

    def isAtEnd(self):
        return self.peek().type == TokenType.TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def comparison(self):
        expr = self.term()

        while self.match(TokenType.TokenType.GREATER, TokenType.TokenType.GREATER_EQUAL,
                         TokenType.TokenType.LESS, TokenType.TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(TokenType.TokenType.MINUS, TokenType.TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.TokenType.SLASH, TokenType.TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match(TokenType.TokenType.BANG, TokenType.TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.TokenType.FALSE):
            return Expr.Literal(False)

        if self.match(TokenType.TokenType.TRUE):
            return Expr.Literal(True)

        if self.match(TokenType.TokenType.NIL):
            return Expr.Literal(None)

        if self.match(TokenType.TokenType.NUMBER, TokenType.TokenType.STRING):
            return Expr.Literal(self.previous().literal)

        if self.match(TokenType.TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")

    def consume(self, tokentype, message):
        if self.check(tokentype):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token, message):
        Pylox.Lox.error(token=token, message=message)
        return RuntimeError()

    def synchronize(self):
        self.advance()

        while not self.isAtEnd():
            if self.previous().type == TokenType.TokenType.SEMICOLON:
                return

            if self.peek().type in self.discards_tokens:
                return

            self.advance()




