import re

from instruction_seq import InstructionSeq
from util import *

class Command():
    def __init__(self):
        self.asm = []

    @staticmethod
    def create(inst, filename):
        m = Push.regexp.search(inst)
        if m is not None:
            return Push(m.groups(), filename)
        m = Pop.regexp.search(inst)
        if m is not None:
            return Pop(m.groups(), filename)
        m = Label.regexp.search(inst)
        if m is not None:
            return Label(m.groups(), filename)
        m = Goto.regexp.search(inst)
        if m is not None:
            return Goto(m.groups(), filename)
        m = IfGoto.regexp.search(inst)
        if m is not None:
            return IfGoto(m.groups(), filename)
        if inst == Add.cmd_name:
            return Add()
        elif inst == Sub.cmd_name:
            return Sub()
        elif inst == Neg.cmd_name:
            return Neg()
        elif inst == Eq.cmd_name:
            return Eq()
        elif inst == Lt.cmd_name:
            return Lt()
        elif inst == Gt.cmd_name:
            return Gt()
        elif inst == And.cmd_name:
            return And()
        elif inst == Or.cmd_name:
            return Or()
        elif inst == Not.cmd_name:
            return Not()
        else:
            raise ValueError("Unknown instruction: {}".format(inst))

    def to_asm(self):
        if not self.asm:
            self.asm = self._assemble()
        return self.asm

class StackCommand(Command):
    def __init__(self, groups, filename):
        target, self.offset = groups
        self.source = MemorySegment.to_enum(target)
        self.asm = None
        self._filename = filename

    def __repr__(self):
        return "{} {} {}".format(self._cmd_name, self.source, self.offset)

class Push(StackCommand):
    cmd_name = "push"
    regexp = re.compile("push\s([\w\.]+)\s([\w]+)")
    def _assemble(self):
        insts = InstructionSeq("{} {} {}".format(self.cmd_name, self.source, self.offset))
        if self.source == MemorySegment.CONSTANT:
            insts = insts.const_to_stack(self.offset)
        elif self.source in [MemorySegment.LCL, MemorySegment.ARG,
            MemorySegment.THIS, MemorySegment.THAT, MemorySegment.TEMP]:
            insts = insts.mem_seg_to_stack(self.source, self.offset)
        elif self.source == MemorySegment.STATIC:
            insts = insts.static_to_stack(self._filename, self.offset)
        elif self.source == MemorySegment.POINTER:
            insts = insts.pointer_to_stack(self.offset)
        return insts.inc_sp()

class Pop(StackCommand):
    cmd_name = "pop"
    regexp = re.compile("pop\s([\w\.]+)\s([\w]+)")
    def _assemble(self):
        insts = InstructionSeq("{} {} {}".format(self.cmd_name, self.source, self.offset))
        insts = insts.dec_sp()
        if self.source in [MemorySegment.LCL, MemorySegment.ARG,
            MemorySegment.THIS, MemorySegment.THAT, MemorySegment.TEMP]:
            insts = insts.stack_to_mem_seg(self.source, self.offset)
        elif self.source == MemorySegment.STATIC:
            insts = insts.stack_to_static(self._filename, self.offset)
        elif self.source == MemorySegment.POINTER:
            insts = insts.stack_to_pointer(self.offset)
        elif self.source == MemorySegment.CONSTANT:
            raise ValueError("pop constant _ is an invalid instruction")
        return insts

class BinaryCommand(Command):
    def assemble(self, comp):
        return InstructionSeq(self.cmd_name).binary_op(comp)

class Add(BinaryCommand):
    cmd_name = "add"
    def _assemble(self):
        return self.assemble("D+M")

class Sub(BinaryCommand):
    cmd_name = "sub"
    def _assemble(self):
        return self.assemble("M-D")

class And(BinaryCommand):
    cmd_name = "and"
    def _assemble(self):
        return self.assemble("D&M")

class Or(BinaryCommand):
    cmd_name = "or"
    def _assemble(self):
        return self.assemble("D|M")

class UnaryCommand(Command):
    def assemble(self, comp):
        return InstructionSeq(self.cmd_name).dec_sp() \
                    .dereference("SP") \
                    .c_instruction(dest="M", comp=comp) \
                    .inc_sp()
class Neg(Command):
    cmd_name = "neg"
    def _assemble(self):
        return self.assemble("-M")

class Not(Command):
    cmd_name = "not"
    def _assemble(self):
        return self.assemble("!M")

class ComparisonCommand(Command):
    label = generate_label("CMP")

    def assemble(self, kind):
        cmp_label = next(ComparisonCommand.label)
        jmp_label = next(ComparisonCommand.label)
        return InstructionSeq(self.cmd_name).dec_sp() \
                    .stack_to_register("D") \
                    .dec_sp() \
                    .stack_to_register("A") \
                    .c_instruction(dest="D", comp="A-D") \
                    .a_instruction(cmp_label) \
                    .c_instruction(comp="D", jump=kind) \
                    .push(False) \
                    .a_instruction(jmp_label) \
                    .c_instruction(comp="0", jump="JMP") \
                    .label(cmp_label) \
                    .push(True) \
                    .label(jmp_label) \

class Eq(ComparisonCommand):
    cmd_name = "eq"
    def _assemble(self):
        return self.assemble("JEQ")

class Lt(ComparisonCommand):
    cmd_name = "lt"
    def _assemble(self):
        return self.assemble("JLT")

class Gt(ComparisonCommand):
    cmd_name = "gt"
    def _assemble(self):
        return self.assemble("JGT")

class BranchCommand(Command):
    def __init__(self, groups, filename):
        self.label = groups[0]
        self.asm = None

class Label(BranchCommand):
    cmd_name = "label"
    regexp = re.compile("label\s([\w\.]+)")

    def _assemble(self):
        return InstructionSeq("{} {}".format(self.cmd_name, self.label)) \
                    .label(self.label)

class Goto(BranchCommand):
    cmd_name = "goto"
    regexp = re.compile("^goto\s([\w\.]+)")

    def _assemble(self):
        return InstructionSeq("{} {}".format(self.cmd_name, self.label)) \
                    .a_instruction(self.label) \
                    .c_instruction(comp="0", jump="JMP")

class IfGoto(BranchCommand):
    cmd_name = "if-goto"
    regexp = re.compile("if-goto\s([\w\.]+)")

    def _assemble(self):
        return InstructionSeq("{} {}".format(self.cmd_name, self.label)) \
                    .dec_sp() \
                    .stack_to_register("D") \
                    .a_instruction(self.label) \
                    .c_instruction(comp="D", jump="JNE")
