class Token(object):
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        return str(self.type) + " " + self.lexeme + " " + self.literal


