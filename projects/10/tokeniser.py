from util import *

class Tokeniser:
    def __init__(self, f):
        self.in_name, self.out_name = f
        self.tokens = []
        self._tokenise()

    def has_next(self):
        """Returns true if the iteration has more elements
        """
        return self.tokens != []

    def next(self):
        """Returns the next element in the iteration
        """
        return self.tokens.pop()

    def peek(self):
        """Peek at the next element in the iteration
        """
        return self.tokens[-1]

    def _tokenise(self):
        file = open(self.in_name, 'r').read()
        code = filter(lambda x: x, self._strip_comments(file))
        pattern = '|'.join(token.value for token in TokenType)
        self.tokens = [self._classify(token) for token_list in
                            (re.findall(pattern, line) for line in code)
                                for token in token_list][::-1]

    def _strip_comments(self, file):
        return COMMENT_RE.sub("", file).splitlines()

    def _classify(self, token):
        if re.match(TokenType.KEYWORD.value, token) is not None:
            return (TokenType.KEYWORD, token)
        elif re.match(TokenType.SYMBOL.value, token) is not None:
            return (TokenType.SYMBOL, token)
        elif re.match(TokenType.IDENTIFIER.value, token) is not None:
            return (TokenType.IDENTIFIER, token)
        elif re.match(TokenType.INT_CONST.value, token) is not None:
            return (TokenType.INT_CONST, token)
        elif re.match(TokenType.STR_CONST.value, token) is not None:
            return (TokenType.STR_CONST, token)
