# coding=utf-8

from typing import List
import Expr
import Token


class Stmt(object):
	def accept(self, visitor):
		raise NotImplementedError

	def __setattr__(self, attr, value):
		if hasattr(self, attr):
			raise Exception("Attempting to alter read-only value")

		self.__dict__[attr] = value


class Block(Stmt):
	def __init__(self, statements: List[Stmt]):
		self.statements = statements

	def accept(self, visitor):
		return visitor.visitBlockStmt(self)


class Expression(Stmt):
	def __init__(self, expression: Expr.Expr):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitExpressionStmt(self)


class Function(Stmt):
	def __init__(self, name: Token.Token, params: List[Token.Token], body: List[Stmt]):
		self.name = name
		self.params = params
		self.body = body

	def accept(self, visitor):
		return visitor.visitFunctionStmt(self)


class Class(Stmt):
	def __init__(self, name: Token.Token, superclass: Expr.Variable, methods: List[Function]):
		self.name = name
		self.superclass = superclass
		self.methods = methods

	def accept(self, visitor):
		return visitor.visitClassStmt(self)


class If(Stmt):
	def __init__(self, condition: Expr.Expr, thenBranch: Stmt, elseBranch: Stmt):
		self.condition = condition
		self.thenBranch = thenBranch
		self.elseBranch = elseBranch

	def accept(self, visitor):
		return visitor.visitIfStmt(self)


class Print(Stmt):
	def __init__(self, expression: Expr.Expr):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitPrintStmt(self)


class Return(Stmt):
	def __init__(self, keyword: Token.Token, value: Expr.Expr):
		self.keyword = keyword
		self.value = value

	def accept(self, visitor):
		return visitor.visitReturnStmt(self)


class Var(Stmt):
	def __init__(self, name: Token.Token, initializer: Expr.Expr):
		self.name = name
		self.initializer = initializer

	def accept(self, visitor):
		return visitor.visitVarStmt(self)


class While(Stmt):
	def __init__(self, condition: Expr.Expr, body: Stmt):
		self.condition = condition
		self.body = body

	def accept(self, visitor):
		return visitor.visitWhileStmt(self)


class Visitor(object):
	def visitBlockStmt(self, stmt: Block):
		raise NotImplementedError

	def visitExpressionStmt(self, stmt: Expression):
		raise NotImplementedError

	def visitFunctionStmt(self, stmt: Function):
		raise NotImplementedError

	def visitClassStmt(self, stmt: Class):
		raise NotImplementedError

	def visitIfStmt(self, stmt: If):
		raise NotImplementedError

	def visitPrintStmt(self, stmt: Print):
		raise NotImplementedError

	def visitReturnStmt(self, stmt: Return):
		raise NotImplementedError

	def visitVarStmt(self, stmt: Var):
		raise NotImplementedError

	def visitWhileStmt(self, stmt: While):
		raise NotImplementedError

