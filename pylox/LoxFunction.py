# coding=utf-8

from Interpreter import Interpreter
from typing import List


class LoxCallable:
    def __init__(self):
        pass

    def __call__(self, interpreter: Interpreter, arguments: List[object]):
        pass

    @property
    def arity(self):
        return 0