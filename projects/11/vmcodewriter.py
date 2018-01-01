import os
from util import IdentifierKind, kind_to_reg

class VMCodeWriter:
    def __init__(self, f):
        self.input_filename, self.output_filename = f
        self.namespace, _ = os.path.splitext(os.path.split(self.input_filename)[1])
        self.f = open(self.output_filename, 'w')

    def close(self):
        self.f.close()

    def write(self, fx='', arg1='', arg2=''):
        self.f.write("{} {} {}\n".format(fx, arg1, arg2))

    def fun_dec(self, fxn_name, nlocs):
        self.write("function", "{}.{}".format(self.namespace, fxn_name), nlocs)

    def call(self, fxn_name, nargs):
        self.write("call", fxn_name, nargs)

    def ret(self):
        self.write("return")

    def int_const(self, val):
        self.push(reg="constant", val=val)

    def str_const(self, str):
        self.int_const(len(str))
        self.call("String.new", 1)
        for c in str:
            self.int_const(ord(c))
            self.call("String.appendChar", 2)

    def kw_const(self, kw):
        if kw == 'true':
            self.int_const(1)
            self.write('neg')
        elif kw == 'this':
            self.push_this_ptr()
        else:
            self.int_const(0)

    def unary_op(self, op):
        if op == '-':
            self.write('neg')
        elif op == '~':
            self.write('not')

    def binary_op(self, op):
        op_table = {'+': 'add', '-': 'sub',\
                    '*': 'call Math.multiply 2', '/': 'call Math.divide 2',\
                    '<': 'lt', '>': 'gt', '=': 'eq',\
                    '&': 'and', '|': 'or'}
        self.write(op_table[op])

    def push(self, reg='', val=''):
        self.write("push", reg, val)

    def pop(self, reg='', val=''):
        self.write("pop", reg, val)

    def push_this_ptr(self):
        self.push('pointer', '0')

    def push_that_ptr(self):
        self.push('pointer', '1')

    def pop_this_ptr(self):
        self.pop('pointer', '0')

    def pop_that_ptr(self):
        self.pop('pointer', '1')

    def push_that(self):
        self.pop('that', '0')

    def label(self, l):
        self.write("label", l)

    def ifgoto(self, label):
        self.write("if-goto", label)

    def goto(self, label):
        self.write("goto", label)

    def alloc(self, num_fields):
        self.int_const(num_fields)
        self.call("Memory.alloc", 1)

    def pop_variable(self, var, st):
        entry = st.get(var)
        segment = kind_to_reg[entry.kind]
        index = entry.id
        self.pop(segment, index)

    def push_variable(self, var, st):
        entry = st.get(var)
        segment = kind_to_reg[entry.kind]
        index = entry.id
        self.push(segment, index)