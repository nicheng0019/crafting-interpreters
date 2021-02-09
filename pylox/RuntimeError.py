#coding=utf-8


class PyloxRuntimeError(RuntimeError):
    def __init__(self, token, message):
        super(RuntimeError, self).__init__()

        self.token = token
        self.message = message