from tokeniser import Tokeniser
from util import *
from html import escape

class Parser:
    def __init__(self, f):
        self.in_name, self.out_name = f
        self.output = []
        self.tokeniser = Tokeniser(f)
        self.depth = 0
        self.parse()
    
    def parse(self):
        if self.tokeniser.has_next():
            self.compileClass()
        return self.out_name, self.output 

    def compileClass(self):
        self.open_tag('class')
        self.expect(TokenType.KEYWORD, 'class')
        self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.SYMBOL, '{')
        while self.peek(TokenType.KEYWORD, ['static', 'field']):
            self.compileClassVarDec()
        while self.peek(TokenType.KEYWORD, ['function', 'constructor', 'method']):
            self.compileSubroutine()
        self.expect(TokenType.SYMBOL, '}')
        self.close_tag('class')

    def compileClassVarDec(self):
        self.open_tag('classVarDec')
        self.expect(TokenType.KEYWORD)
        self.compileType()
        self.expect(TokenType.IDENTIFIER)
        self.tryCompileVarList()
        self.expect(TokenType.SYMBOL, ";")
        self.close_tag('classVarDec')
        return self.tokeniser.peek() if self.tokeniser.has_next() else (None, None)

    def compileType(self):
        ttype, token = self.tokeniser.peek()
        type_list = ["void", "int", "char", "boolean"]
        if ttype == TokenType.KEYWORD and token in type_list:
            self.expect(TokenType.KEYWORD, token)
        elif ttype == TokenType.IDENTIFIER:
            self.expect(TokenType.IDENTIFIER)
        else:
            raise SyntaxError("Expected type in {} or identifier, got: {} of type {}".format(type_list, token, ttype))

    def tryCompileVarList(self, exp_type=False):
        while self.peek(TokenType.SYMBOL, ","):
            self.expect(TokenType.SYMBOL, ",")
            if exp_type:
                self.compileType()
            self.expect(TokenType.IDENTIFIER)

    def compileSubroutine(self):
        self.open_tag('subroutineDec')
        self.expect(TokenType.KEYWORD, ['constructor', 'function', 'method'])
        self.expect([TokenType.KEYWORD, TokenType.IDENTIFIER])
        self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.SYMBOL, "(")
        self.compileParameterList()
        self.expect(TokenType.SYMBOL, ")")
        self.compileSubroutineBody()
        self.close_tag('subroutineDec')
        return self.tokeniser.peek() if self.tokeniser.has_next() else (None, None)

    def compileParameterList(self):
        self.open_tag('parameterList')
        if not self.peek(TokenType.SYMBOL, ")"):    
            self.compileType()
            self.expect(TokenType.IDENTIFIER)
            self.tryCompileVarList(True)
        self.close_tag('parameterList')

    def compileSubroutineBody(self):
        self.open_tag('subroutineBody')
        self.expect(TokenType.SYMBOL, "{")
        while self.peek(TokenType.KEYWORD, "var"):
            self.compileVarDec()
        self.compileStatements()
        self.expect(TokenType.SYMBOL, "}")
        self.close_tag('subroutineBody')

    def compileVarDec(self):
        self.open_tag("varDec")
        self.expect(TokenType.KEYWORD, "var")
        self.compileType()
        self.expect(TokenType.IDENTIFIER)
        self.tryCompileVarList()
        self.expect(TokenType.SYMBOL, ";")
        self.close_tag("varDec")

    def compileStatements(self):
        self.open_tag("statements")
        while self.peek(TokenType.KEYWORD, ['let', 'if', 'while', 'do', 'return']):
            self.compileStatement()
        self.close_tag("statements")

    def compileStatement(self):
        if self.peek(TokenType.KEYWORD, "let"):
            self.compileLet()
        elif self.peek(TokenType.KEYWORD, "if"):
            self.compileIf()
        elif self.peek(TokenType.KEYWORD, "while"):
            self.compileWhile()
        elif self.peek(TokenType.KEYWORD, "do"):
            self.compileDo()
        elif self.peek(TokenType.KEYWORD, "return"):
            self.compileReturn()

    def compileLet(self):
        self.open_tag("letStatement")
        self.expect(TokenType.KEYWORD, "let")
        self.expect(TokenType.IDENTIFIER)
        if self.peek(TokenType.SYMBOL, "["):
            self.expect(TokenType.SYMBOL, "[")
            self.compileExpression()
            self.expect(TokenType.SYMBOL, "]")
        self.expect(TokenType.SYMBOL, "=")
        self.compileExpression()
        self.expect(TokenType.SYMBOL, ";")
        self.close_tag("letStatement")

    def compileIf(self):
        self.open_tag("ifStatement")
        self.expect(TokenType.KEYWORD, "if")
        self.expectGroupedExpression()
        self.expect(TokenType.SYMBOL, "{")
        self.compileStatements()
        self.expect(TokenType.SYMBOL, "}")
        if self.peek(TokenType.KEYWORD, "else"):
            self.expect(TokenType.KEYWORD, "else")
            self.expect(TokenType.SYMBOL, "{")
            self.compileStatements()
            self.expect(TokenType.SYMBOL, "}")
        self.close_tag("ifStatement")

    def expectGroupedExpression(self):
        self.expect(TokenType.SYMBOL, "(")
        self.compileExpression()
        self.expect(TokenType.SYMBOL, ")")

    def compileWhile(self):
        self.open_tag("whileStatement")
        self.expect(TokenType.KEYWORD, "while")
        self.expectGroupedExpression()
        self.expect(TokenType.SYMBOL, "{")
        self.compileStatements()
        self.expect(TokenType.SYMBOL, "}")
        self.close_tag("whileStatement")

    def compileDo(self):
        self.open_tag("doStatement")
        self.expect(TokenType.KEYWORD, "do")
        self.expect(TokenType.IDENTIFIER)
        self.compileSubroutineCall()
        self.expect(TokenType.SYMBOL, ";")
        self.close_tag("doStatement")

    def compileReturn(self):
        self.open_tag("returnStatement")
        self.expect(TokenType.KEYWORD, "return")
        if not self.peek(TokenType.SYMBOL, ";"):
            self.compileExpression()
        self.expect(TokenType.SYMBOL, ";")
        self.close_tag("returnStatement")

    def compileExpression(self):
        self.open_tag("expression")
        self.compileTerm()
        while self.peek(TokenType.SYMBOL, list("+-*/&|<>=")):
            self.compileOp()
            self.compileTerm()
        self.close_tag("expression")

    def compileOp(self):
        self.expect(TokenType.SYMBOL)

    def compileTerm(self):
        self.open_tag("term")
        if self.peek(TokenType.INT_CONST):
            self.expect(TokenType.INT_CONST)
        elif self.peek(TokenType.STR_CONST):
            self.compileStrConst()
        elif self.peek(TokenType.KEYWORD, ['true', 'false', 'null', 'this']):
            self.compileKeywordConstant()
        elif self.peek(TokenType.SYMBOL, ["-", "~"]):
            self.compileUnaryOp()
        elif self.peek(TokenType.SYMBOL, "("):
            self.expectGroupedExpression()
        elif self.tokeniser.has_next():
            t1, token1 = self.tokeniser.next()
            self.terminal_tag(t1, token1)
            if self.tokeniser.has_next():
                t2, token2 = self.tokeniser.peek()
                if self.peek(TokenType.SYMBOL, "["):
                    self.compileArrayAccess()
                elif self.peek(TokenType.SYMBOL, ["(", "."]):
                    self.compileSubroutineCall()
        self.close_tag("term")

    def compileStrConst(self):
        ttype, token = self.tokeniser.next()
        self.terminal_tag(TokenType.STR_CONST, token[1:-1])

    def compileKeywordConstant(self):
        self.expect(TokenType.KEYWORD, ['true', 'false', 'null', 'this'])

    def compileUnaryOp(self):
        self.expect(TokenType.SYMBOL, ["-", "~"])
        self.compileTerm()

    def compileArrayAccess(self):
        self.expect(TokenType.SYMBOL, "[")
        self.compileExpression()
        self.expect(TokenType.SYMBOL, "]")

    def compileSubroutineCall(self):
        if self.peek(TokenType.SYMBOL, "("):
            self.expectExpressionList()
        elif self.peek(TokenType.SYMBOL, "."):
            self.expect(TokenType.SYMBOL, ".")
            self.expect(TokenType.IDENTIFIER)
            self.expectExpressionList()

    def expectExpressionList(self):
        self.expect(TokenType.SYMBOL, "(")
        self.compileExpressionList()
        self.expect(TokenType.SYMBOL, ")")

    def compileExpressionList(self):
        self.open_tag("expressionList")
        if not self.peek(TokenType.SYMBOL, ")"):
            self.compileExpression()
            while self.peek(TokenType.SYMBOL, ","):
                self.expect(TokenType.SYMBOL, ",")
                self.compileExpression()
        self.close_tag("expressionList")

    def peek(self, e_type, e_token=None, expect=True):
        if not self.tokeniser.has_next():
            return False
        a_type, a_token = self.tokeniser.peek()
        return self.token_match(e_type, e_token, a_type, a_token)

    def expect(self, e_type, e_token=None):
        if not self.tokeniser.has_next():
            return None, None
        a_type, a_token = self.tokeniser.next()
        if self.token_match(e_type, e_token, a_type, a_token):
            self.terminal_tag(a_type, a_token)
            return self.tokeniser.peek() if self.tokeniser.has_next() else None, None
        else:
            raise SyntaxError("Expected {} of type {}, got {} of type {}".format(e_token, e_type, a_token, a_type))
        
    def token_match(self, e_type, e_token, a_type, a_token):
        return (e_type == a_type or (type(e_type) == list and a_type in e_type)) and \
                    (e_token is None or e_token == a_token or (type(e_token) == list and a_token in e_token))

    def open_tag(self, tag_name, value=''):
        self.output.append('{}<{}>{}'.format(' ' * self.depth, escape(tag_name), escape(value)))
        self.depth += 2

    def close_tag(self, tag_name, newline=True):
        self.depth -= 2
        tag = '</{}>'.format(escape(tag_name))
        if newline or not self.output:
            self.output.append(' ' * self.depth + tag)
        else:
            self.output[-1] += tag

    def terminal_tag(self, tag_name, value):
        self.depth += 2
        self.open_tag(str(tag_name), value=value)
        self.close_tag(str(tag_name), False)
        self.depth -= 2
