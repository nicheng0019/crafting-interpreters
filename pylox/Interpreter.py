# coding=utf-8

from typing import Optional, List
import Expr
import TokenType


class Interpreter(Expr.Visitor):
    def __init__(self):
        self.binaryOp = dict()
        self.registerBinaryOp()

    def visitLiteralExpr(self, expr: Optional[Expr.Literal]):
        assert isinstance(expr, Expr.Literal)
        return expr.value

    def visitGroupingExpr(self, expr: Optional[Expr.Grouping]):
        assert isinstance(expr, Expr.Grouping)
        return self.evaluate(expr.expression)

    def evaluate(self, expr):
        return expr.accept(self)

    def visitUnaryExpr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.TokenType.MINUS:
            return -float(right)

        elif expr.operator.type == TokenType.TokenType.BANG:
            return not self.isTruthy(right)

        return None

    def isTruthy(self, object):
        if object is None:
            return False

        if isinstance(object, bool):
            return bool(object)

        return True

    def registerBinaryOp(self):
        self.binaryOp[TokenType.TokenType.GREATER] = lambda left, right: float(left) > float(right)
        self.binaryOp[TokenType.TokenType.GREATER_EQUAL] = lambda left, right: float(left) >= float(right)
        self.binaryOp[TokenType.TokenType.LESS] = lambda left, right: float(left) < float(right)
        self.binaryOp[TokenType.TokenType.LESS_EQUAL] = lambda left, right: float(left) <= float(right)
        self.binaryOp[TokenType.TokenType.MINUS] = lambda left, right: float(left) - float(right)
        self.binaryOp[TokenType.TokenType.PLUS] = lambda left, right: float(left) + float(right)
        self.binaryOp[TokenType.TokenType.SLASH] = lambda left, right: float(left) / float(right)
        self.binaryOp[TokenType.TokenType.STAR] = lambda left, right: float(left) * float(right)

        def addOp(left, right):
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)

            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)

        self.binaryOp[TokenType.TokenType.STAR] = addOp
        self.binaryOp[TokenType.TokenType.BANG_EQUAL] = lambda left, right: not (left == right)
        self.binaryOp[TokenType.TokenType.EQUAL_EQUAL] = lambda left, right: left == right

    def visitBinaryExpr(self, expr: Optional[Expr.Binary]):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        op = self.binaryOp.get(expr.operator.type, None)
        if op is None:
            return None

        return op(left, right)
