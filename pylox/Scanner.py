from TokenType import *
from Token import *
from Pylox import *


class Scanner(object):
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line= 1
        self.token_dict = {"(": TokenType.LEFT_PAREN, ")": TokenType.RIGHT_PAREN,
                           '{': TokenType.LEFT_BRACE, '}': TokenType.RIGHT_BRACE,
                            ',': TokenType.COMMA, '.': TokenType.DOT,
                            '-': TokenType.MINUS, '+': TokenType.PLUS,
                            ';': TokenType.SEMICOLON, '*': TokenType.STAR}

    def scanTokens(self):
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()

        self.tokens.append(Token(TokenType.EOF, "", "", self.line))
        return self.tokens

    def scanToken(self):
        c = self.advance()
        if c not in self.token_dict.keys():
            Lox.error(self.line, "Unexpected character.")
            return

        self.addToken(self.token_dict[c])

    def addToken(self, tokentype):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(tokentype, text, "", self.line))

    def isAtEnd(self):
        return self.current >= len(self.source)

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

