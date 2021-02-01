# coding=utf-8

from typing import Optional, List
import Token


class Expr(object):
	def accept(self, visitor):
		raise NotImplementedError

	def __setattr__(self, attr, value):
		if hasattr(self, attr):
			raise Exception("Attempting to alter read-only value")

		self.__dict__[attr] = value


class Assign(Expr):
	def __init__(self, name: Optional[Token.Token], value: Optional[Expr]):
		self.name = name
		self.value = value

	def accept(self, visitor):
		return visitor.visitAssignExpr(self)


class Binary(Expr):
	def __init__(self, left: Optional[Expr], operator: Optional[Token.Token], right: Optional[Expr]):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visitBinaryExpr(self)


class Call(Expr):
	def __init__(self, callee: Optional[Expr], paren: Optional[Token.Token], arguments: Optional[List[Expr]]):
		self.callee = callee
		self.paren = paren
		self.arguments = arguments

	def accept(self, visitor):
		return visitor.visitCallExpr(self)


class Get(Expr):
	def __init__(self, object: Optional[Expr], name: Optional[Token.Token]):
		self.object = object
		self.name = name

	def accept(self, visitor):
		return visitor.visitGetExpr(self)


class Grouping(Expr):
	def __init__(self, expression: Optional[Expr]):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitGroupingExpr(self)


class Literal(Expr):
	def __init__(self, value: Optional[object]):
		self.value = value

	def accept(self, visitor):
		return visitor.visitLiteralExpr(self)


class Logical(Expr):
	def __init__(self, left: Optional[Expr], operator: Optional[Token.Token], right: Optional[Expr]):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visitLogicalExpr(self)


class Set(Expr):
	def __init__(self, object: Optional[Expr], name: Optional[Token.Token], value: Optional[Expr]):
		self.object = object
		self.name = name
		self.value = value

	def accept(self, visitor):
		return visitor.visitSetExpr(self)


class Super(Expr):
	def __init__(self, keyword: Optional[Token.Token], method: Optional[Token.Token]):
		self.keyword = keyword
		self.method = method

	def accept(self, visitor):
		return visitor.visitSuperExpr(self)


class This(Expr):
	def __init__(self, keyword: Optional[Token.Token]):
		self.keyword = keyword

	def accept(self, visitor):
		return visitor.visitThisExpr(self)


class Unary(Expr):
	def __init__(self, operator: Optional[Token.Token], right: Optional[Expr]):
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visitUnaryExpr(self)


class Variable(Expr):
	def __init__(self, name: Optional[Token.Token]):
		self.name = name

	def accept(self, visitor):
		return visitor.visitVariableExpr(self)


class Visitor(object):
	def visitAssignExpr(self, expr: Optional[Assign]):
		raise NotImplementedError

	def visitBinaryExpr(self, expr: Optional[Binary]):
		raise NotImplementedError

	def visitCallExpr(self, expr: Optional[Call]):
		raise NotImplementedError

	def visitGetExpr(self, expr: Optional[Get]):
		raise NotImplementedError

	def visitGroupingExpr(self, expr: Optional[Grouping]):
		raise NotImplementedError

	def visitLiteralExpr(self, expr: Optional[Literal]):
		raise NotImplementedError

	def visitLogicalExpr(self, expr: Optional[Logical]):
		raise NotImplementedError

	def visitSetExpr(self, expr: Optional[Set]):
		raise NotImplementedError

	def visitSuperExpr(self, expr: Optional[Super]):
		raise NotImplementedError

	def visitThisExpr(self, expr: Optional[This]):
		raise NotImplementedError

	def visitUnaryExpr(self, expr: Optional[Unary]):
		raise NotImplementedError

	def visitVariableExpr(self, expr: Optional[Variable]):
		raise NotImplementedError

