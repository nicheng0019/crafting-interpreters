# coding=utf-8

from typing import List
import Expr
import Stmt
import Pylox
import Token
from enum import Enum


class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1


class Resolver(Expr.Visitor, Stmt.Visitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.currentFunction = FunctionType.NONE

    def visitBlockStmt(self, stmt: Stmt.Block):
        self.beginScope()
        self.resolve(stmt.statements)
        self.endScope()

    def visitVarStmt(self, stmt: Stmt.Var):
        self.declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer)

        self.define(stmt.name)

    def resolve(self, statements):
        if isinstance(statements, list):
            for statement in statements:
                self.resolve(statement)
        elif isinstance(statements, Stmt.Stmt):
            statements.accept(self)
        elif isinstance(statements, Expr.Expr):
            statements.accept(self)

    def beginScope(self):
        self.scopes.append(dict())

    def endScope(self):
        self.scopes.pop()

    def declare(self, name):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope.keys():
            Pylox.Lox.error(token=name, message="Already variable with this name in this scope.")

        scope[name.lexeme] = False

    def define(self, name):
        if len(self.scopes) == 0:
            return

        self.scopes[-1][name.lexeme] = True

    def visitVariableExpr(self, expr):
        if len(self.scopes) > 0 and self.scopes[-1][expr.name.lexeme] == False:
            Pylox.Lox.error(token=expr.name, message="Can't read local variable in its own initializer.")

        self.resolveLocal(expr, expr.name)

    def resolveLocal(self, expr: Expr.Expr, name: Token.Token):
        for i in range(len(self.scopes), -1, -1):
            if name.lexeme in self.scopes[i].keys():
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def visitAssignExpr(self, expr: Expr.Assign):
        self.resolve(expr.value)
        self.resolveLocal(expr, expr.name)

    def visitFunctionStmt(self, stmt: Stmt.Function):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolveFunction(stmt, FunctionType.FUNCTION)

    def resolveFunction(self, func: Stmt.Function, type: FunctionType):
        enclosingFunction = self.currentFunction
        self.currentFunction = type

        self.beginScope()
        for param in func.params:
            self.declare(param)
            self.define(param)

        self.resolve(func.body)
        self.endScope()

        self.currentFunction = enclosingFunction

    def visitExpressionStmt(self, stmt: Stmt.Expression):
        self.resolve(stmt.expression)

    def visitIfStmt(self, stmt: Stmt.If):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if not stmt.elseBranch:
            self.resolve(stmt.elseBranch)

    def visitPrintStmt(self, stmt: Stmt.Print):
        self.resolve(stmt.expression)

    def visitReturnStmt(self, stmt: Stmt.Return):
        if self.currentFunction == FunctionType.NONE:
            Pylox.Lox.error(stmt.keyword, "Can't return from top-level code.")

        if not stmt.value:
            self.resolve(stmt.value)

    def visitWhileStmt(self, stmt: Stmt.While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visitBinaryExpr(self, expr: Expr.Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitCallExpr(self, expr: Expr.Call):
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

    def visitGroupingExpr(self, expr: Expr.Grouping):
        self.resolve(expr.expression)

    def visitLiteralExpr(self, expr: Expr.Literal):
        return

    def visitLogicalExpr(self, expr: Expr.Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitUnaryExpr(self, expr: Expr.Unary):
        self.resolve(expr.right)
