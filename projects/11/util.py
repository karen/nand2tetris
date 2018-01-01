import re
from enum import Enum

COMMENT_RE = re.compile("\/\/[^\n]*$|\/\*.*?\*\/", re.MULTILINE | re.DOTALL)

EXP_SYMBOLS = list("+-*/&|<>=")
UNARY_OPS = list("-~")
KEYWORD_CONSTANTS = ['true', 'false', 'null', 'this']
STMT_KEYWORDS = ['let', 'if', 'while', 'do', 'return']
FXN_KEYWORDS = ['constructor', 'function', 'method']
CLASS_VAR_KEYWORDS = ['static', 'field']
BI_TYPES = ['void', 'int', 'char', 'boolean']

class TokenType(Enum):
    KEYWORD = ('class|constructor|function|method|field|static|var|int'
               '|char|boolean|void|true|false|null|this|let|do|if|else'
               '|while|return')
    SYMBOL = '[' + re.escape('{}()[].,;+-*/&|<>=-~') + ']'
    IDENTIFIER = '[A-Za-z_][\w\d_]*'
    INT_CONST = '\d+'
    STR_CONST = '"[^\\n]*"'

    def __str__(self):
        if self == TokenType.INT_CONST:
            return 'integerConstant'
        elif self == TokenType.STR_CONST:
            return 'stringConstant'
        else:
            return self.name.lower()

class IdentifierKind(Enum):
    STATIC = 0
    FIELD = 1
    ARGUMENT = 2
    VAR = 3

kind_to_reg = {IdentifierKind.STATIC: 'static', IdentifierKind.FIELD: 'this',
               IdentifierKind.ARGUMENT: 'argument', IdentifierKind.VAR: 'local'}
keyword_to_kind = {'static': IdentifierKind.STATIC, 'field': IdentifierKind.FIELD}

def labeler():
    counter = 0
    label = "LABEL"
    while True:
        counter += 1
        yield label + str(counter)
