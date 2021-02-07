# coding=utf-8

from Interpreter import Interpreter
from typing import List
import Stmt
import Environment
from Return import Return


class LoxCallable:
    def __init__(self):
        pass

    def __call__(self, interpreter: Interpreter, arguments: List[object]):
        return None

    @property
    def arity(self):
        return 0


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment.Environment):
        super(LoxCallable, self).__init__()
        self.closure = closure
        self.declaration = declaration

    def __call__(self, interpreter: Interpreter, arguments: List[object]):
        environment = Environment.Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as returnValue:
            return returnValue

        return None

    def arity(self):
        return len(self.declaration.params)

    def __repr__(self):
        return "<fn " + self.declaration.name.lexeme + ">"

