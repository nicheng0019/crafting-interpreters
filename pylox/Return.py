# coding=utf-8


class Return(RuntimeError):
    def __init__(self, value):
        super(RuntimeError, self).__init__()
        self.value = value


