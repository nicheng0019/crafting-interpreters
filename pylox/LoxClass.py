# coding=utf-8

from LoxFunction import LoxCallable
from typing import List
from RuntimeError import PyloxRuntimeError


class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = dict()

    def __repr__(self):
        return self.klass.name + " instance"

    def get(self, name):
        if name in self.fields.keys():
            return self.fields.keys[name.lexeme]

        method = self.klass.findMethod(name.lexeme)
        if method:
            return method.bind(self)

        raise PyloxRuntimeError(name, "Undefined property '" + name.lexeme + "'.")

    def set(self, name, value):
        self.fields[name.lexeme] = value


class LoxClass(LoxCallable):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def __repr__(self):
        return self.name

    def __call__(self, interpreter, arguments: List[object]):
        instance = LoxInstance(self)
        initializer = self.findMethod("init")

        if initializer:
            initializer.bind(instance)(interpreter, arguments)

        return instance

    def arity(self):
        initializer = self.findMethod("init")
        if not initializer:
            return 0

        return initializer.arity()

    def findMethod(self, name):
        if name in self.methods.keys():
            return self.methods[name]

        if self.superclass:
            return self.superclass.findMethod(name)

