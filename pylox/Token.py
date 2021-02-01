# coding=utf-8

class Token(object):
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        if not self.literal:
            return str(self.type) + " " + self.lexeme + " " + str(self.literal)
        else:
            return str(self.type) + " " + self.lexeme + " "


