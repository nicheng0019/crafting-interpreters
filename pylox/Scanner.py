from TokenType import TokenType
from Token import Token
import Pylox


class Scanner(object):
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.one_char_tokens_dict = {"(": TokenType.LEFT_PAREN, ")": TokenType.RIGHT_PAREN,
                                     '{': TokenType.LEFT_BRACE, '}': TokenType.RIGHT_BRACE,
                                     ',': TokenType.COMMA, '.': TokenType.DOT,
                                     '-': TokenType.MINUS, '+': TokenType.PLUS,
                                     ';': TokenType.SEMICOLON, '*': TokenType.STAR}

        self.two_char_tokens_dict = {"!": (TokenType.BANG_EQUAL, TokenType.BANG),
                                     "=": (TokenType.EQUAL_EQUAL, TokenType.EQUAL),
                                     "<": (TokenType.LESS_EQUAL, TokenType.LESS),
                                     ">": (TokenType.GREATER_EQUAL, TokenType.GREATER)}

        self.keywords_dict = {"and": TokenType.AND,
                                "class": TokenType.CLASS,
                                "else": TokenType.ELSE,
                                "false": TokenType.FALSE,
                                "for": TokenType.FOR,
                                "fun": TokenType.FUN,
                                "if": TokenType.IF,
                                "nil": TokenType.NIL,
                                "or": TokenType.OR,
                                "print": TokenType.PRINT,
                                "return": TokenType.RETURN,
                                "super": TokenType.SUPER,
                                "this": TokenType.THIS,
                                "true": TokenType.TRUE,
                                "var": TokenType.VAR,
                                "while": TokenType.WHILE}

    def scanTokens(self):
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()

        self.tokens.append(Token(TokenType.EOF, "", "", self.line))
        return self.tokens

    def scanToken(self):
        c = self.advance()
        if c in self.one_char_tokens_dict.keys():
            self.addToken(self.one_char_tokens_dict[c])

        elif c in self.two_char_tokens_dict.keys():
            self.addToken(self.two_char_tokens_dict[c][0] if self.match("=") else self.two_char_tokens_dict[c][1])

        elif c is "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.isAtEnd():
                    self.advance()
            else:
                self.addToken(TokenType.SLASH)

        elif c is " " or c is "\r" or c is "\t":
            return

        elif c is "\n":
            self.line += 1

        elif c is '"':
            self.string()

        # elif c is 'o':
        #     if self.peek() == 'r':
        #         self.addToken(TokenType.OR)

        else:
            if self.isDigit(c):
                self.number()
            elif self.isAlpha(c):
                self.identifier()
            else:
                Pylox.Lox.error(self.line, "Unexpected character.")
            return

    def addToken(self, tokentype, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(tokentype, text, literal, self.line))

    def isAtEnd(self):
        return self.current >= len(self.source)

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def match(self, expected):
        if self.isAtEnd():
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self):
        if self.isAtEnd():
            return "\0"

        return self.source[self.current]

    def string(self):
        while self.peek() != '"' and not self.isAtEnd():
            if self.peek() == "\n":
                self.line += 1

            self.advance()

        if self.isAtEnd():
            Pylox.Lox.error(self.line, "Unterminated string.")
            return

        self.advance()

        value = self.source[self.start + 1:self.current - 1]
        self.addToken(TokenType.STRING, value)

    def isDigit(self, c):
        return '0' <= c <= '9'

    def number(self):
        while self.isDigit(self.peek()):
            self.advance()

        if self.peek() == "." and self.isDigit(self.peekNext()):
            self.advance()

            while self.isDigit(self.peek()):
                self.advance()

        self.addToken(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def peekNext(self):
        if (self.current + 1) >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    def isAlpha(self, c):
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_'

    def isAlphaNumeric(self, c):
        return self.isAlpha(c) or self.isDigit(c)

    def identifier(self):
        while self.isAlphaNumeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        type = self.keywords_dict.get(text, None)
        if type is None:
            type = TokenType.IDENTIFIER

        self.addToken(type)

