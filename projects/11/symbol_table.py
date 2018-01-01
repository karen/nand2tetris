from collections import namedtuple
from util import BI_TYPES, IdentifierKind

class SymbolTable:
    Entry = namedtuple('Entry', ['type', 'kind', 'id'])
    def __init__(self):
        self.class_table = {}
        self.subroutine_table = {}
        self.curr_scope = self.class_table

    def start_subroutine(self):
        self.subroutine_table = {}
        self.curr_scope = self.subroutine_table

    def define(self, name, taipu, kind):
        self.curr_scope[name] = SymbolTable.Entry(taipu, kind, self.var_count(kind))

    def get(self, name):
        if name in self.curr_scope:
            return self.curr_scope[name]
        elif name in self.class_table:
            return self.class_table[name]
        else:
            return SymbolTable.Entry(None, None, None)

    def var_count(self, kind):
        scope = self.class_table if kind in [IdentifierKind.STATIC, IdentifierKind.FIELD] else self.subroutine_table
        count = 0
        for key in scope:
            if scope[key].kind == kind:
                count += 1
        return count

    def kind_of(self, name):
        return self.get(name).kind

    def type_of(self, name):
        return self.get(name).type

    def index_of(self, name):
        return self.get(name).id

    def qualify(self, caller, method):
        t = self.type_of(caller)
        calling_class = t if t is not None else caller
        return '{}.{}'.format(calling_class, method)

    def is_object(self, name):
        t = self.type_of(name)
        return t is not None and t not in BI_TYPES

    def __repr__(self):
        return 'Class Table: {}\nCurr Scope: {}\n'.format(self.class_table, self.curr_scope)
