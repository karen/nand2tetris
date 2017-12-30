import re
from enum import Enum

COMMENT_RE = re.compile("\/\/[^\n]*$|\/\*.*?\*\/", re.MULTILINE | re.DOTALL)

class TokenType(Enum):
    KEYWORD = ('class|constructor|function|method|field|static|var|int'
               '|char|boolean|void|true|false|null|this|let|do|if|else'
               '|while|return')
    SYMBOL = '[' + re.escape('{}()[].,;+-*/&|<>=-') + ']'
    IDENTIFIER = '[A-Za-z_][\w\d_]*'
    INT_CONST = '\d+'
    STR_CONST = '"[^\\n]*"'
