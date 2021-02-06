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
            #statements.append(self.statement())
            statements.append(self.declaration())

        return statements

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.varDeclaration()

            return self.statement()
        #except ParseError as error:
        except:
            self.synchronize()
            return None

    def varDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)

    def expression(self):
        #return self.equality()
        return self.assignment()

    def assignment(self):
        #expr = self.equality()
        expr = self.orexpression()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                name = expr.name
                return Expr.Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def orexpression(self):
        expr = self.andexpression()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.andexpression()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def andexpression(self):
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def ifStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        thenBranch = self.statement()
        elseBranch = None
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()

        return Stmt.If(condition, thenBranch, elseBranch)

    def statement(self):
        if self.match(TokenType.FOR):
            return self.forStatement()

        if self.match(TokenType.IF):
            return self.ifStatement()

        if self.match(TokenType.PRINT):
            return self.printStatement()

        if self.match(TokenType.WHILE):
            return self.whileStatement()

        if self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expressionStatement()

    def whileStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")

        body = self.statement()

        return Stmt.While(condition, body)

    def block(self):
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def printStatement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)

    def expressionStatement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)

    def forStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()
        if increment:
            body = Stmt.Block([body, Stmt.Expression(increment)])

        if not condition:
            condition = Expr.Literal(True)

        body = Stmt.While(condition, body)

        if initializer:
            body = Stmt.Block([initializer, body])

        return body

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

        #return self.primary()
        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            else:
                break

        return expr

    def finishCall(self, callee):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())

        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Expr.Call(callee, paren, arguments)

    def primary(self):
        if self.match(TokenType.FALSE):
            return Expr.Literal(False)

        if self.match(TokenType.TRUE):
            return Expr.Literal(True)

        if self.match(TokenType.NIL):
            return Expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Expr.Variable(self.previous())

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

    expression = Expr.Binary(Expr.Unary(Token.Token(TokenType.MINUS, '-', None, 1), Expr.Literal(123)),
                             Token.Token(TokenType.STAR, "*", None, 1),
                             Expr.Grouping(Expr.Literal(45.67)))

    #-123 * (45.67)
    tokens = [Token.Token(TokenType.MINUS, '-', None, 1),
              Token.Token(TokenType.NUMBER, "123", 123, 1),
              Token.Token(TokenType.STAR, "*", None, 1),
              Token.Token(TokenType.LEFT_PAREN, "(", None, 1),
              Token.Token(TokenType.NUMBER, "45.67", 45.67, 1),
              Token.Token(TokenType.RIGHT_PAREN, ")", None, 1),
              Token.Token(TokenType.EOF, "", "", 1)]

    parser = Parser(tokens)
    expr = parser.parse()
    print(expr, expr.left, expr.left.operator, expr.left.right,
          expr.operator, expr.right, expr.right.expression, expr.right.expression.value)


