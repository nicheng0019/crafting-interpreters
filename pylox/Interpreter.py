# coding=utf-8

from typing import List
import Expr
import Stmt
from TokenType import TokenType
import Pylox
from RuntimeError import PyloxRuntimeError
import Environment


class Interpreter(Expr.Visitor, Stmt.Visitor):
    def __init__(self):
        self.binaryOp = dict()
        self.registerBinaryOp()
        self.checkOps_set = {TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL,
                             TokenType.MINUS, TokenType.SLASH, TokenType.STAR}
        self.environment = Environment.Environment()

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)

        except PyloxRuntimeError as error:
            Pylox.Lox.runtimeError(error)

    def execute(self, stmt):
        stmt.accept(self)

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

    def visitExpressionStmt(self, stmt: Stmt.Expression):
        self.evaluate(stmt.expression)

    def visitPrintStmt(self, stmt: Stmt.Print):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visitVarStmt(self, stmt: Stmt.Var):
        value = None
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visitVariableExpr(self, expr: Expr.Variable):
        return self.environment.get(expr.name)

    def visitAssignExpr(self, expr: Expr.Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visitBlockStmt(self, stmt):
        self.executeBlock(stmt.statements, Environment.Environment(self.environment))

    def executeBlock(self, statements: List[Stmt.Stmt], environment: Environment.Environment):
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visitIfStmt(self, stmt: Stmt.If):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch is not None:
            self.execute(stmt.elseBranch)

        return None

    def visitLogicalExpr(self, expr: Expr.Logical):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.isTruthy(left):
                return left
            else:
                if not self.isTruthy(left):
                    return left

        return self.evaluate(expr.right)

    def visitWhileStmt(self, stmt: Stmt.While):
        while self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)


