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
    INITIALIZER = 2
    METHOD = 3


class ClassType(Enum):
    NONE = 0
    CLASS = 1
    SUBCLASS = 2


class Resolver(Expr.Visitor, Stmt.Visitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.currentFunction = FunctionType.NONE
        self.currentClass = ClassType.NONE

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
        for i in range(len(self.scopes) - 1, -1, -1):
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
            if self.currentFunction == FunctionType.INITIALIZER:
                Pylox.Lox.error(stmt.keyword, "Can't return a value from an initializer.")
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

    def visitClassStmt(self, stmt: Stmt.Class):
        enclosingClass = self.currentClass
        self.currentClass = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass and (stmt.name.lexeme == stmt.superclass.name.lexeme):
            Pylox.Lox.error(stmt.superclass.name, "A class can't inherit from itself.")

        if stmt.superclass:
            self.currentClass = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass:
            self.beginScope()
            self.scopes[-1]["super"] = True

        self.beginScope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme is "init":
                declaration = FunctionType.INITIALIZER

            self.resolveFunction(method, declaration)

        self.endScope()

        if stmt.superclass:
            self.endScope()

        self.currentClass = enclosingClass

    def visitGetExpr(self, expr: Expr.Get):
        self.resolve(expr.object)

    def visitSetExpr(self, expr: Expr.Set):
        self.resolve(expr.value)
        self.resolve(expr.object)

    def visitThisExpr(self, expr: Expr.This):
        if self.currentClass == ClassType.NONE:
            Pylox.Lox.error(expr.keyword, "Can't use 'this' outside of a class.")

        self.resolveLocal(expr, expr.keyword)

    def visitSuperExpr(self, expr: Expr.Super):
        if self.currentClass == ClassType.NONE:
            Pylox.Lox.error(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.currentClass != ClassType.SUBCLASS:
            Pylox.Lox.error(expr.keyword, "Can't use 'super' in a class with no superclass.")
        self.resolveLocal(expr, expr.keyword)


