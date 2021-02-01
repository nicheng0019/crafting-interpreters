# coding=utf-8
import os
import sys


def GenerateAst(outputDir):
    stmtlist = [
        "Block      : List[Stmt] statements",
        "Expression : Expr.Expr expression",
        "Function   : Token.Token name, List[Token.Token] params," + " List[Stmt] body",
        "Class      : Token.Token name, Expr.Variable superclass," + " List[Function] methods",
        "If         : Expr.Expr condition, Stmt thenBranch," + " Stmt elseBranch",
        "Print      : Expr.Expr expression",
        "Return     : Token.Token keyword, Expr.Expr value",
        "Var        : Token.Token name, Expr.Expr initializer",
        "While      : Expr.Expr condition, Stmt body"]

    exprlist = ["Assign   : Token.Token name, Expr value",
                "Binary   : Expr left, Token.Token operator, Expr right",
                "Call     : Expr callee, Token.Token paren, List[Expr] arguments",
                "Get      : Expr object, Token.Token name",
                "Grouping : Expr expression",
                "Literal  : object value",
                "Logical  : Expr left, Token.Token operator, Expr right",
                "Set      : Expr object, Token.Token name, Expr value",
                "Super    : Token.Token keyword, Token.Token method",
                "This     : Token.Token keyword",
                "Unary    : Token.Token operator, Expr right",
                "Variable : Token.Token name"]

    def definetype(writer, baseName, className, fieldList):
        writer.write('class ' + className + '(' + baseName + '):\n')
        writer.write('\tdef __init__(self')
        fields = []
        for f in fieldList:
            f = f.strip()
            ty, na = f.split(" ")
            fields.append([ty, na])

        for f in fields:
            ty, na = f
            writer.write(', ' + na + ': Optional[' + ty + ']')

        writer.write('):\n')
        for f in fields:
            ty, na = f
            writer.write('\t\tself.' + na + ' = ' + na + '\n')

        writer.write("\n")

        writer.write('\tdef accept(self, visitor):\n')
        writer.write('\t\treturn visitor.visit' + className + baseName + '(self)\n\n\n')

    def defineAst(outputDir, baseName, types):
        with open(os.path.join(outputDir, baseName + ".py"), "w") as fpy:
            fpy.write("# coding=utf-8\n\n")
            fpy.write('from typing import Optional, List\n')
            if baseName == 'Stmt':
                fpy.write("import Expr\n")
            fpy.write('import Token\n\n\n')

            fpy.write('class ' + baseName + '(object):\n')
            fpy.write('\tdef accept(self, visitor):\n')
            fpy.write('\t\traise NotImplementedError\n\n')

            fpy.write('\tdef __setattr__(self, attr, value):\n')
            fpy.write('\t\tif hasattr(self, attr):\n')
            fpy.write('\t\t\traise Exception("Attempting to alter read-only value")\n\n')

            fpy.write('\t\tself.__dict__[attr] = value\n\n\n')

            classNames = []
            for t in types:
                className, fields = t.split(":", maxsplit=1)
                className = className.strip()
                classNames.append(className)
                fields = fields.strip()
                fieldList = fields.split(",")

                definetype(fpy, baseName, className, fieldList)

            fpy.write('class Visitor(object):\n')

            for cn in classNames:
                fpy.write('\tdef visit' + cn + baseName + '(self, ' + baseName.lower() + ': Optional[' +
                          cn + ']):' + '\n')
                fpy.write('\t\traise NotImplementedError\n\n')

            fpy.close()

    defineAst(outputDir, "Stmt", stmtlist)
    defineAst(outputDir, "Expr", exprlist)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: generate_ast <output directory>")
        exit()

    GenerateAst(sys.argv[1])
