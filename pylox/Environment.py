# coding=utf-8


from RuntimeError import PyloxRuntimeError

class Environment:
    def __init__(self, enclosing=None):
        self.values = dict()
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values.keys():
            return self.values[name]

        if self.enclosing:
            return self.enclosing.get(name)

        raise PyloxRuntimeError(name, "Undefined variable '" + name.lexeme + "'.")

    def assign(self, name, value):
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return

        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise PyloxRuntimeError(name, "Undefined variable '" + name.lexeme + "'.")

