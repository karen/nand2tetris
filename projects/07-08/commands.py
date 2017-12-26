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
            return Label(m.groups())
        m = Goto.regexp.search(inst)
        if m is not None:
            return Goto(m.groups())
        m = IfGoto.regexp.search(inst)
        if m is not None:
            return IfGoto(m.groups())
        m = FunctionDef.regexp.search(inst)
        if m is not None:
            return FunctionDef(m.groups(), filename)
        if inst == Return.cmd_name:
            return Return()
        elif inst == Add.cmd_name:
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
        super().__init__()
        target, self.offset = groups
        self.source = MemorySegment.to_enum(target)
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
class Neg(UnaryCommand):
    cmd_name = "neg"
    def _assemble(self):
        return self.assemble("-M")

class Not(UnaryCommand):
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
    def __init__(self, groups):
        super().__init__()
        self.label = groups[0]

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
                    .goto(self.label)

class IfGoto(BranchCommand):
    cmd_name = "if-goto"
    regexp = re.compile("if-goto\s([\w\.]+)")

    def _assemble(self):
        return InstructionSeq("{} {}".format(self.cmd_name, self.label)) \
                    .dec_sp() \
                    .stack_to_register("D") \
                    .a_instruction(self.label) \
                    .c_instruction(comp="D", jump="JNE")

class FunctionDef(Command):
    cmd_name = "function"
    regexp = re.compile("function\s([\w\.]+)\s([\d\.]+)")

    def __init__(self, groups, filename):
        super().__init__()
        self.name, self.nargs = groups
        self._filename = filename

    def _assemble(self):
        insts = InstructionSeq("{} {} {}".format(self.cmd_name, self.name, self.nargs)) \
                    .label(self.name)
        for i in range(int(self.nargs)):
            insts = insts.const_to_stack(0).inc_sp()
        return insts

class Return(Command):
    cmd_name = "return"

    def _assemble(self):
        return InstructionSeq(self.cmd_name) \
                    .a_instruction(MemorySegment.LCL) \
                    .c_instruction(dest="D", comp="M") \
                    .a_instruction(R_ENDFRAME) \
                    .store_from("D") \
                    .a_instruction(5) \
                    .c_instruction(dest="A", comp="D-A") \
                    .c_instruction(dest="D", comp="M") \
                    .a_instruction(R_RETADDR) \
                    .store_from("D") \
                    .dec_sp() \
                    .stack_to_mem_seg(MemorySegment.ARG, 0) \
                    .a_instruction(MemorySegment.ARG) \
                    .c_instruction(dest="D", comp="M+1") \
                    .a_instruction("SP") \
                    .store_from("D") \
                    .dereference_endframe(MemorySegment.THAT) \
                    .dereference_endframe(MemorySegment.THIS) \
                    .dereference_endframe(MemorySegment.ARG) \
                    .dereference_endframe(MemorySegment.LCL) \
                    .a_instruction(R_RETADDR) \
                    .c_instruction(dest="A", comp="M")
