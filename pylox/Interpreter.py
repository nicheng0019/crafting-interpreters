# coding=utf-8

import time
from typing import List
import Expr
import Stmt
from TokenType import TokenType
import Pylox
from RuntimeError import PyloxRuntimeError
import Environment
import LoxFunction
from Return import Return
from LoxClass import LoxClass, LoxInstance


class ClockFunc(LoxFunction.LoxCallable):
    def arity(self):
        return 0

    def __call__(self, interpreter, arguments: List[object]):
        return time.time()

    def __repr__(self):
        return "<native fn>"


class Interpreter(Expr.Visitor, Stmt.Visitor):
    def __init__(self):
        self.binaryOp = dict()
        self.registerBinaryOp()
        self.checkOps_set = {TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL,
                             TokenType.MINUS, TokenType.SLASH, TokenType.STAR}
        self.globals = Environment.Environment()
        self.environment = self.globals

        self.globals.define("clock", LoxFunction.LoxCallable())
        self.locals = dict()

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)

        except PyloxRuntimeError as error:
            Pylox.Lox.runtimeError(error)

    def execute(self, stmt):
        stmt.accept(self)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def stringify(self, obj):
        if obj is None:
            return None

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:len(text) - 2]

            return text

        return str(obj)

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

    def isTruthy(self, obj):
        if obj is None:
            return False

        if isinstance(obj, bool):
            return bool(obj)

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
        #return self.environment.get(expr.name)
        return self.lookUpVariable(expr.name, expr)

    def lookUpVariable(self, name, expr):
        distance = self.locals.get(expr, None)
        if distance:
            return self.environment.getAt(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def visitAssignExpr(self, expr: Expr.Assign):
        value = self.evaluate(expr.value)

        distance = self.locals.get(expr, None)
        if distance:
            self.environment.assignAt(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
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

    def visitCallExpr(self, expr: Expr.Call):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxFunction.LoxCallable):
            raise PyloxRuntimeError(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity:
            raise PyloxRuntimeError(expr.paren, "Expected " +
                                    str(callee.arity) + " arguments but got " +
                                    str(len(arguments)) + ".")

        return callee(self, arguments)

    def visitFunctionStmt(self, stmt: Stmt.Function):
        func = LoxFunction.LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, func)

    def visitReturnStmt(self, stmt: Stmt.Return):
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)

        raise Return(value)

    def visitClassStmt(self, stmt: Stmt.Class):
        superclass = None
        if stmt.superclass:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise PyloxRuntimeError(stmt.superclass.name, "Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass:
            self.environment = Environment.Environment(self.environment)
            self.environment.define("super", superclass)

        methods = dict()
        for method in stmt.methods:
            func = LoxFunction.LoxFunction(method, self.environment, method.name.lexeme is "init")
            methods[method.name.lexeme] = func

        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        if superclass:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, klass)

    def visitGetExpr(self, expr: Expr.Get):
        obj = self.evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise PyloxRuntimeError(expr.name, "Only instances have properties.")

    def visitSetExpr(self, expr: Expr.Set):
        obj = self.evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise PyloxRuntimeError(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visitThisExpr(self, expr: Expr.This):
        return self.lookUpVariable(expr.keyword, expr)

    def visitSuperExpr(self, expr: Expr.Super):
        distance = self.locals[expr]
        superclass = self.environment.getAt(distance, "super")

        obj = self.environment.getAt(distance - 1, "this")

        method = superclass.findMethod(expr.method.lexeme)

        if not method:
            raise PyloxRuntimeError(expr.method, "Undefined property '" + expr.method.lexeme + "'.")

        return method.bind(obj)



