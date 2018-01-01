from symbol_table import SymbolTable
from tokeniser import Tokeniser
from vmcodewriter import VMCodeWriter
from util import *
from html import escape

class Parser:
    def __init__(self, f):
        self.in_name, self.out_name = f
        self.output = []
        self.tokeniser = Tokeniser(f)
        self.st_handler = None
        self.writer = VMCodeWriter(f)
        self.local_state = {'labeler': labeler()}
        self.parse()
        self.writer.close()
    
    def parse(self):
        if self.tokeniser.has_next():
            self.compileClass()
        return self.out_name, self.output 

    def compileClass(self):
        self.expect(TokenType.KEYWORD, 'class')
        klass = self.expect(TokenType.IDENTIFIER)
        self.st_handler = SymbolTable(klass)
        self.local_state['class'] = klass
        self.expect(TokenType.SYMBOL, '{')
        while self.peek(TokenType.KEYWORD, CLASS_VAR_KEYWORDS):
            entry = self.compileClassVarDec()
        while self.peek(TokenType.KEYWORD, FXN_KEYWORDS):
            self.st_handler.start_subroutine()
            self.compileSubroutine()
        self.expect(TokenType.SYMBOL, '}')
        del self.local_state['class']

    def compileClassVarDec(self):
        kind = keyword_to_kind[self.expect(TokenType.KEYWORD)]
        taipu = self.compileType()
        name = self.expect(TokenType.IDENTIFIER)
        self.st_handler.define(name, taipu, kind)
        varlist = self.tryCompileVarList(taipu=taipu, kind=kind)
        self.expect(TokenType.SYMBOL, ";")

    def compileType(self):
        ttype, token = self.tokeniser.peek()
        if ttype == TokenType.KEYWORD and token in BI_TYPES:
            return self.expect(TokenType.KEYWORD, token)
        elif ttype == TokenType.IDENTIFIER:
            return self.expect(TokenType.IDENTIFIER)
        else:
            raise SyntaxError("Expected type in {} or identifier, got: {} of type {}".format(BI_TYPES, token, ttype))
        
    def tryCompileVarList(self, exp_type=False, taipu=None, kind=None):
        varlist = []
        while self.peek(TokenType.SYMBOL, ","):
            self.expect(TokenType.SYMBOL, ",")
            if exp_type:
                taipu = self.compileType()
            name = self.expect(TokenType.IDENTIFIER)
            varlist.append((name, taipu, kind))
        for entry in varlist:
            self.st_handler.define(*entry)
        return len(varlist)

    def compileSubroutine(self):
        fxn_kind = self.expect(TokenType.KEYWORD, FXN_KEYWORDS)
        self.compileType()
        fxn_name = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.SYMBOL, "(")
        self.compileParameterList()
        self.expect(TokenType.SYMBOL, ")")
        self.compileSubroutineBody(fxn_name, fxn_kind)

    def compileParameterList(self):
        nvars = 0
        if not self.peek(TokenType.SYMBOL, ")"):
            kind = IdentifierKind.ARGUMENT
            taipu = self.compileType()
            name = self.expect(TokenType.IDENTIFIER)
            self.st_handler.define(name, taipu, kind)
            nvars += 1
            nvars += self.tryCompileVarList(exp_type=True, kind=kind)
        return nvars

    def compileSubroutineBody(self, fxn_name, fxn_kind):
        self.expect(TokenType.SYMBOL, "{")
        while self.peek(TokenType.KEYWORD, "var"):
            self.compileVarDec()
        nlocs = self.st_handler.var_count(IdentifierKind.VAR)
        self.writer.fun_dec(fxn_name, nlocs)
        self.compileFxnKind(fxn_kind)
        self.compileStatements()
        self.expect(TokenType.SYMBOL, "}")

    def compileFxnKind(self, kind):
        if kind == 'constructor':
            num_fields = self.st_handler.var_count(IdentifierKind.FIELD)
            self.writer.alloc(num_fields)
            self.writer.pop_this_ptr()
        elif kind == 'method':
            self.st_handler.define('this', self.local_state['class'], IdentifierKind.ARGUMENT)
            self.writer.push_variable('this', self.st_handler)
            self.writer.pop_this_ptr()

    def compileVarDec(self):
        nvars = 1
        self.expect(TokenType.KEYWORD, "var")
        kind = IdentifierKind.VAR
        taipu = self.compileType()
        name = self.expect(TokenType.IDENTIFIER)
        self.st_handler.define(name, taipu, kind)
        nvars += self.tryCompileVarList(taipu=taipu, kind=kind)
        self.expect(TokenType.SYMBOL, ";")
        return nvars

    def compileStatements(self):
        while self.peek(TokenType.KEYWORD, STMT_KEYWORDS):
            self.compileStatement()

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
        self.expect(TokenType.KEYWORD, "let")
        var = self.expect(TokenType.IDENTIFIER)
        arr_to_arr = False
        if self.peek(TokenType.SYMBOL, "["):
            arr_to_arr = True
            self.writer.push_variable(var, self.st_handler)
            self.expect(TokenType.SYMBOL, "[")
            self.compileExpression()
            self.expect(TokenType.SYMBOL, "]")
            self.writer.binary_op("+")
        self.expect(TokenType.SYMBOL, "=")
        if self.peek(TokenType.SYMBOL, "["):
            arr_to_arr &= True
        else:
            arr_to_arr &= False
        self.compileExpression()
        self.expect(TokenType.SYMBOL, ";")
        if arr_to_arr:
            self.writer.pop('temp', 0)
            self.writer.pop_that_ptr()
            self.writer.push('temp', 0)
            self.writer.pop_that()
        else:
            self.writer.pop_variable(var, self.st_handler)

    def compileIf(self):
        self.expect(TokenType.KEYWORD, "if")
        endif = next(self.local_state['labeler'])
        self.compileCond(endif)
        if self.peek(TokenType.KEYWORD, "else"):
            self.expect(TokenType.KEYWORD, "else")
            self.expectBracedStatements()
        self.writer.label(endif)

    def expectGroupedExpression(self):
        self.expect(TokenType.SYMBOL, "(")
        self.compileExpression()
        self.expect(TokenType.SYMBOL, ")")

    def expectBracedStatements(self):
        self.expect(TokenType.SYMBOL, "{")
        self.compileStatements()
        self.expect(TokenType.SYMBOL, "}")

    def compileWhile(self):
        self.expect(TokenType.KEYWORD, "while")
        loop = next(self.local_state['labeler'])
        self.writer.label(loop)
        self.compileCond(loop)

    def compileCond(self, ret):
        self.expectGroupedExpression()
        self.writer.unary_op('~')
        not_cond = next(self.local_state['labeler'])
        self.writer.ifgoto(not_cond)
        self.expectBracedStatements()
        self.writer.goto(ret)
        self.writer.label(not_cond)

    def compileDo(self):
        self.expect(TokenType.KEYWORD, "do")
        caller = self.expect(TokenType.IDENTIFIER)
        self.compileSubroutineCall(caller)
        self.writer.pop("temp", "0")
        self.expect(TokenType.SYMBOL, ";")

    def compileReturn(self):
        self.expect(TokenType.KEYWORD, "return")
        if not self.peek(TokenType.SYMBOL, ";"):
            self.compileExpression()
        else:
            self.writer.int_const(0)
        self.writer.ret()
        self.expect(TokenType.SYMBOL, ";")

    def compileExpression(self):
        self.compileTerm()
        while self.peek(TokenType.SYMBOL, EXP_SYMBOLS):
            op = self.compileOp()
            self.compileTerm()
            self.writer.binary_op(op)

    def compileOp(self):
        return self.expect(TokenType.SYMBOL)

    def compileTerm(self):
        if self.peek(TokenType.INT_CONST):
            int = self.expect(TokenType.INT_CONST)
            self.writer.int_const(int)
        elif self.peek(TokenType.STR_CONST):
            str = self.compileStrConst()
            self.writer.str_const(str)
        elif self.peek(TokenType.KEYWORD, KEYWORD_CONSTANTS):
            kw = self.expect(TokenType.KEYWORD, KEYWORD_CONSTANTS)
            self.writer.kw_const(kw)
        elif self.peek(TokenType.SYMBOL, UNARY_OPS):
            self.compileUnaryOp()
        elif self.peek(TokenType.SYMBOL, "("):
            self.expectGroupedExpression()
        elif self.tokeniser.has_next():
            t1, token1 = self.tokeniser.next()
            if self.tokeniser.has_next():
                t2, token2 = self.tokeniser.peek()
                if self.peek(TokenType.SYMBOL, "["):
                    self.compileArrayAccess(token1)
                elif self.peek(TokenType.SYMBOL, ["(", "."]):
                    self.compileSubroutineCall(token1)
                else:
                    self.writer.push_variable(token1, self.st_handler)

    def compileStrConst(self):
        ttype, token = self.tokeniser.next()
        return token[1:-1]

    def compileUnaryOp(self):
        op = self.expect(TokenType.SYMBOL, ["-", "~"])
        self.compileTerm()
        self.writer.unary_op(op)

    def compileArrayAccess(self, arr):
        self.writer.push_variable(arr, self.st_handler)
        self.expect(TokenType.SYMBOL, "[")
        self.compileExpression()
        self.expect(TokenType.SYMBOL, "]")
        self.writer.binary_op("+")
        self.writer.pop_that_ptr()
        self.writer.push_that()

    def compileSubroutineCall(self, caller):
        if self.peek(TokenType.SYMBOL, "("):
            method = caller
            self.writer.push_this_ptr()
            nargs = self.expectExpressionList() + 1
        elif self.peek(TokenType.SYMBOL, "."):
            method, nargs = self.compileMethodCall(caller)
        qualified_name = self.st_handler.qualify(caller, method)
        self.writer.call(qualified_name, nargs)

    def compileMethodCall(self, caller):
        if self.st_handler.is_object(caller):
            self.writer.push_variable(caller, self.st_handler)
        self.expect(TokenType.SYMBOL, ".")
        method = self.expect(TokenType.IDENTIFIER)
        nargs = self.expectExpressionList()
        return method, nargs
        
    def expectExpressionList(self):
        self.expect(TokenType.SYMBOL, "(")
        nexps = self.compileExpressionList()
        self.expect(TokenType.SYMBOL, ")")
        return nexps

    def compileExpressionList(self):
        nexps = 0
        if not self.peek(TokenType.SYMBOL, ")"):
            self.compileExpression()
            nexps += 1
            while self.peek(TokenType.SYMBOL, ","):
                self.expect(TokenType.SYMBOL, ",")
                self.compileExpression()
                nexps += 1
        return nexps

    def peek(self, e_type, e_token=None):
        if not self.tokeniser.has_next():
            return False
        a_type, a_token = self.tokeniser.peek()
        return self.token_match(e_type, e_token, a_type, a_token)

    def expect(self, e_type, e_token=None):
        a_type, a_token = self.tokeniser.next()
        if self.token_match(e_type, e_token, a_type, a_token):
            return a_token
        else:
            raise SyntaxError("Expected {} of type {}, got {} of type {}".format(e_token, e_type, a_token, a_type))
        
    def token_match(self, e_type, e_token, a_type, a_token):
        return (e_type == a_type or (type(e_type) == list and a_type in e_type)) and \
                    (e_token is None or e_token == a_token or (type(e_token) == list and a_token in e_token))
