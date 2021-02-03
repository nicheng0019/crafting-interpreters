# coding=utf-8

import Expr
from TokenType import TokenType
import Pylox
from RuntimeError import PyloxRuntimeError


class Interpreter(Expr.Visitor):
    def __init__(self):
        self.binaryOp = dict()
        self.registerBinaryOp()
        self.checkOps_set = {TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL,
                             TokenType.MINUS, TokenType.SLASH, TokenType.STAR}

    def interpret(self, expression: Expr.Expr):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except PyloxRuntimeError as error:
            Pylox.Lox.runtimeError(error)

    def stringify(self, object):
        if object is None:
            return None

        if isinstance(object, float):
            text = str(object)
            if text.endswith(".0"):
                text = text[:len(text) - 2]

            return text

        return str(object)

    def visitLiteralExpr(self, expr: Expr.Literal):
        assert isinstance(expr, Expr.Literal)
        return expr.value

    def visitGroupingExpr(self, expr: Expr.Grouping):
        assert isinstance(expr, Expr.Grouping)
        return self.evaluate(expr.expression)

    def evaluate(self, expr):
        return expr.accept(self)

    def visitUnaryExpr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self.checkNumberOperands(expr.operator, right)
            return -float(right)

        elif expr.operator.type == TokenType.BANG:
            return not self.isTruthy(right)

        return None

    def isTruthy(self, object):
        if object is None:
            return False

        if isinstance(object, bool):
            return bool(object)

        return True

    def addOp(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return float(left) + float(right)

        if isinstance(left, str) and isinstance(right, str):
            return str(left) + str(right)

        raise PyloxRuntimeError(operator, "Operands must be two numbers or two strings.")

    def divisionOp(self, operator, left, right):
        if abs(right) < 1e-15:
            raise PyloxRuntimeError(operator, "Float division must be non-zero.")

        return left / right

    def registerBinaryOp(self):
        self.binaryOp[TokenType.GREATER] = lambda _, left, right: float(left) > float(right)
        self.binaryOp[TokenType.GREATER_EQUAL] = lambda _, left, right: float(left) >= float(right)
        self.binaryOp[TokenType.LESS] = lambda _, left, right: float(left) < float(right)
        self.binaryOp[TokenType.LESS_EQUAL] = lambda _, left, right: float(left) <= float(right)
        self.binaryOp[TokenType.MINUS] = lambda _, left, right: float(left) - float(right)
        self.binaryOp[TokenType.PLUS] = lambda _, left, right: float(left) + float(right)
        self.binaryOp[TokenType.SLASH] = self.divisionOp
        self.binaryOp[TokenType.STAR] = lambda _, left, right: float(left) * float(right)
        self.binaryOp[TokenType.STAR] = self.addOp
        self.binaryOp[TokenType.BANG_EQUAL] = lambda _, left, right: not (left == right)
        self.binaryOp[TokenType.EQUAL_EQUAL] = lambda _, left, right: left == right

    def visitBinaryExpr(self, expr: Expr.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        op = self.binaryOp.get(expr.operator.type, None)
        if op is None:
            return None

        if expr.operator.type in self.checkOps_set:
            self.checkNumberOperands(expr.operator, left, right)

        return op(expr.operator, left, right)

    def checkNumberOperands(self, operator, left, right=None):
        if isinstance(left, float) and (isinstance(right, float) or right is None):
            return

        raise PyloxRuntimeError(operator, "Operand must be a number.")

