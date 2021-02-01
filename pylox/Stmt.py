# coding=utf-8

from typing import Optional, List
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
	def __init__(self, statements: Optional[List[Stmt]]):
		self.statements = statements

	def accept(self, visitor):
		return visitor.visitBlockStmt(self)


class Expression(Stmt):
	def __init__(self, expression: Optional[Expr.Expr]):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitExpressionStmt(self)


class Function(Stmt):
	def __init__(self, name: Optional[Token.Token], params: Optional[List[Token.Token]], body: Optional[List[Stmt]]):
		self.name = name
		self.params = params
		self.body = body

	def accept(self, visitor):
		return visitor.visitFunctionStmt(self)


class Class(Stmt):
	def __init__(self, name: Optional[Token.Token], superclass: Optional[Expr.Variable], methods: Optional[List[Function]]):
		self.name = name
		self.superclass = superclass
		self.methods = methods

	def accept(self, visitor):
		return visitor.visitClassStmt(self)


class If(Stmt):
	def __init__(self, condition: Optional[Expr.Expr], thenBranch: Optional[Stmt], elseBranch: Optional[Stmt]):
		self.condition = condition
		self.thenBranch = thenBranch
		self.elseBranch = elseBranch

	def accept(self, visitor):
		return visitor.visitIfStmt(self)


class Print(Stmt):
	def __init__(self, expression: Optional[Expr.Expr]):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitPrintStmt(self)


class Return(Stmt):
	def __init__(self, keyword: Optional[Token.Token], value: Optional[Expr.Expr]):
		self.keyword = keyword
		self.value = value

	def accept(self, visitor):
		return visitor.visitReturnStmt(self)


class Var(Stmt):
	def __init__(self, name: Optional[Token.Token], initializer: Optional[Expr.Expr]):
		self.name = name
		self.initializer = initializer

	def accept(self, visitor):
		return visitor.visitVarStmt(self)


class While(Stmt):
	def __init__(self, condition: Optional[Expr.Expr], body: Optional[Stmt]):
		self.condition = condition
		self.body = body

	def accept(self, visitor):
		return visitor.visitWhileStmt(self)


class Visitor(object):
	def visitBlockStmt(self, stmt: Optional[Block]):
		raise NotImplementedError

	def visitExpressionStmt(self, stmt: Optional[Expression]):
		raise NotImplementedError

	def visitFunctionStmt(self, stmt: Optional[Function]):
		raise NotImplementedError

	def visitClassStmt(self, stmt: Optional[Class]):
		raise NotImplementedError

	def visitIfStmt(self, stmt: Optional[If]):
		raise NotImplementedError

	def visitPrintStmt(self, stmt: Optional[Print]):
		raise NotImplementedError

	def visitReturnStmt(self, stmt: Optional[Return]):
		raise NotImplementedError

	def visitVarStmt(self, stmt: Optional[Var]):
		raise NotImplementedError

	def visitWhileStmt(self, stmt: Optional[While]):
		raise NotImplementedError

