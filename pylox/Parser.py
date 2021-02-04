# coding=utf-8

import Expr
import Stmt
from TokenType import TokenType
import Pylox


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.discards_tokens = {TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR, TokenType.IF,
                                TokenType.WHILE, TokenType.PRINT, TokenType.RETURN}

    def parse(self):
        # try:
        #     return self.expression()
        # except RuntimeError:
        #     return None

        statements = []
        while not self.isAtEnd():
            statements.append(self.statement())

        return statements

    def expression(self):
        return self.equality()

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.printStatement()

        return self.expressionStatement()

    def printStatement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)

    def expressionStatement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
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
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL,
                         TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return Expr.Literal(False)

        if self.match(TokenType.TRUE):
            return Expr.Literal(True)

        if self.match(TokenType.NIL):
            return Expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
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
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in self.discards_tokens:
                return

            self.advance()


if __name__ == "__main__":
    import Token
    import TokenType

    expression = Expr.Binary(Expr.Unary(Token.Token(TokenType.TokenType.MINUS, '-', None, 1), Expr.Literal(123)),
                             Token.Token(TokenType.TokenType.STAR, "*", None, 1),
                             Expr.Grouping(Expr.Literal(45.67)))

    #-123 * (45.67)
    tokens = [Token.Token(TokenType.TokenType.MINUS, '-', None, 1),
              Token.Token(TokenType.TokenType.NUMBER, "123", 123, 1),
              Token.Token(TokenType.TokenType.STAR, "*", None, 1),
              Token.Token(TokenType.TokenType.LEFT_PAREN, "(", None, 1),
              Token.Token(TokenType.TokenType.NUMBER, "45.67", 45.67, 1),
              Token.Token(TokenType.TokenType.RIGHT_PAREN, ")", None, 1),
              Token.Token(TokenType.TokenType.EOF, "", "", 1)]

    parser = Parser(tokens)
    expr = parser.parse()
    print(expr, expr.left, expr.left.operator, expr.left.right,
          expr.operator, expr.right, expr.right.expression, expr.right.expression.value)


