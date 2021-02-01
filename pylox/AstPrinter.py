# coding=utf-8

from typing import Optional
import Expr
import Stmt


class AstPrinter(Expr.Visitor, Stmt.Visitor):
    def print(self, expr: Optional[Expr.Expr]):
        return expr.accept(self)

    def visitBinaryExpr(self, expr: Optional[Expr.Binary]):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitGroupingExpr(self, expr: Optional[Expr.Grouping]):
        return self.parenthesize("group", expr.expression)

    def visitLiteralExpr(self, expr: Optional[Expr.Literal]):
        if expr.value is None:
            return 'nil'

        return str(expr.value)

    def visitUnaryExpr(self, expr: Optional[Expr.Unary]):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *exprs):
        builder = "("

        builder += name
        for expr in exprs:
            builder += " "
            builder += expr.accept(self)

        builder += ")"

        return builder


if __name__ == "__main__":
    import Token
    import TokenType
    expression = Expr.Binary(Expr.Unary(Token.Token(TokenType.TokenType.MINUS, '-', None, 1), Expr.Literal(123)),
                             Token.Token(TokenType.TokenType.STAR, "*", None, 1),
                             Expr.Grouping(Expr.Literal(45.67)))

    print(AstPrinter().print(expression))
