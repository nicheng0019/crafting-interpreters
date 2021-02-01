# coding=utf-8

import sys
import Scanner


class Lox(object):
    hadError = False
    exit_status = {64: "EX_USAGE ", 65: "EX_DATAERR",
                    66: "EX_NOINPUT", 70: "EX_SOFTWARE"}

    @classmethod
    def main(cls, argv):
        if len(argv) > 2:
            print("Usage: python Pylox.py [script]")
            cls.exit(64)
        elif len(argv) == 2:
            cls.runFile(argv[1])
        else:
            cls.runPrompt()

    @classmethod
    def runFile(cls, path):
        print("run file", path)
        with open(path) as file:
            bytes = file.read()

        #print(type(bytes))
        cls.run(bytes)

        if cls.hadError:
            cls.exit(65)

    @classmethod
    def runPrompt(cls):
        while True:
            print("> ", end="")
            line = input()

            if not line:
                break

            cls.run(line)

            cls.hadError = False

    @classmethod
    def run(cls, source):
        scanner = Scanner.Scanner(source)
        tokens = scanner.scanTokens()

        for token in tokens:
            print("run token: ", token, "##token end")

    @classmethod
    def error(cls, line, message):
        cls.report(line, "", message)

    @classmethod
    def report(cls, line, where, message):
        print("[line {:d}] Error{:s}: {:s}".format(line, where, message))
        cls.hadError = True

    @classmethod
    def exit(cls, iret):
        sys.exit(cls.exit_status[iret])


if __name__ == "__main__":
    Lox.main(sys.argv)
