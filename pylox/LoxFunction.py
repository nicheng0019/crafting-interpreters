# coding=utf-8

from typing import List
import Stmt
import Environment
from Return import Return


class LoxCallable:
    def __init__(self):
        pass

    def __call__(self, interpreter, arguments: List[object]):
        return None

    @property
    def arity(self):
        return 0


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment.Environment, isInitializer):
        super(LoxCallable, self).__init__()
        self.closure = closure
        self.declaration = declaration
        self.isInitializer = isInitializer

    def __call__(self, interpreter, arguments: List[object]):
        environment = Environment.Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as returnValue:
            if self.isInitializer:
                return self.closure.getAt(0, "this")
            return returnValue.value

        if self.isInitializer:
            return self.closure.getAt(0, "this")

        return None

    @property
    def arity(self):
        return len(self.declaration.params)

    def __repr__(self):
        return "<fn " + self.declaration.name.lexeme + ">"

    def bind(self, instance):
        environment = Environment.Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.isInitializer)


