from util import MemorySegment

class InstructionSeq():
    def __init__(self, command=""):
        self.insts = ["// " + command]

    def a_instruction(self, val):
        self.insts.append('@' + str(val))
        return self

    def c_instruction(self, comp, dest=None, jump=None):
        if dest is not None and jump is None:
            self.insts.append(dest + "=" + comp)
        elif dest is None and jump is not None:
            self.insts.append(comp + ";" + jump)
        else:
            raise ValueError("One of (dest|jump) must be given, not both or none\n dest={}, jump={}".format(dest, jump))
        return self

    def dec_sp(self):
        return self.a_instruction("SP").c_instruction(comp="M-1", dest="M")

    def inc_sp(self):
        return self.a_instruction("SP").c_instruction(comp="M+1", dest="M")

    def dereference(self, ptr):
        """Dereference the given pointer so M is equal to *ptr
        @ptr
        A=M
        """
        self.a_instruction(ptr)
        self.c_instruction(dest="A", comp="M")
        return self

    def store_from(self, reg):
        """Stores the value from the "D" or "A" register
        """
        self.c_instruction(dest="M", comp=reg)
        return self

    def const_to_stack(self, val):
        """Push a constant value on the stack
        @val
        D=A
        *SP = D
        """
        self.a_instruction(val)
        self.c_instruction(dest="D", comp="A")
        self.dereference("SP")
        self.store_from("D")
        return self

    def mem_seg_to_stack(self, source, offset):
        """Push a value from the given memory segment to the stack
        @source
        D=A
        @offset
        A=A+D
        D=M
        *SP=D
        """
        self._offset_address(source, offset, type(source) == MemorySegment and source.is_ptr())
        self.c_instruction(dest="A", comp="D")
        self.c_instruction(dest="D", comp="M")
        self.dereference("SP")
        self.store_from("D")
        return self

    def static_to_stack(self, filename, offset):
        """Push a static variable to the stack
        @Filename.offset
        D=M
        *SP=D
        """
        self.a_instruction(filename + "." + offset)
        self.c_instruction(dest="D", comp="M")
        self.dereference("SP")
        self.store_from("D")
        return self

    def pointer_to_stack(self, offset):
        """Push the value at THIS/THAT into the stack
        @THIS
        D=M
        *SP=D

        @THAT
        D=M
        *SP=D
        """
        source = MemorySegment.THIS if offset == "0" else MemorySegment.THAT
        self.a_instruction(source)
        self.c_instruction(dest="D", comp="M")
        self.dereference("SP")
        self.store_from("D")
        return self

    def stack_to_mem_seg(self, source, offset):
        """Pop the value from the stack and store it in the memory segment
        Assumes that the stack pointer has already been decremented
        @source
        D=A
        @offset
        D=A+D
        @R15 (Store the address temporarily in R15)
        M=D
        D=*SP
        *R15=D
        """
        self._offset_address(source, offset, type(source) == MemorySegment and source.is_ptr())
        self.a_instruction("R15")
        self.store_from("D")
        self.stack_to_register("D")
        self.dereference("R15")
        self.store_from("D")
        return self

    def _offset_address(self, base, offset, ptr=False):
        """Computes the address base+offset and stores in the D register
        """
        comp = "M" if ptr else "A"
        self.a_instruction(base)
        self.c_instruction(dest="D", comp=comp)
        self.a_instruction(offset)
        self.c_instruction(dest="D", comp="D+A")
        return self

    def stack_to_static(self, filename, offset):
        """Pop the value from the stack and store it in the static segment
        D=*SP
        @Filename.offset
        M=D
        """
        self.stack_to_register("D")
        self.a_instruction(filename + "." + offset)
        self.store_from("D")
        return self

    def stack_to_pointer(self, offset):
        """Pop the value from the stack and store it in the pointer segment
        @THIS
        M=*SP

        @THAT
        M=*SP
        """
        target = MemorySegment.THIS if offset == "0" else MemorySegment.THAT
        self.stack_to_register("D")
        self.a_instruction(target)
        self.store_from("D")
        return self

    def stack_to_register(self, reg):
        """Peek into the stack. Places the value in the specified register.
        """
        self.dereference("SP")
        self.c_instruction(dest=reg, comp="M")
        return self

    def binary_op(self, comp):
        """For a binary operation a `op` b:
        SP--
        D=b
        SP--
        *SP=a `op` b
        SP++
        """
        self.dec_sp()
        self.stack_to_register("D")
        self.dec_sp()
        self.dereference("SP")
        self.c_instruction(dest="M", comp=comp)
        self.inc_sp()
        return self

    def push(self, bool):
        """Pushes a boolean value onto the stack.
        True == -1
        False == 0
        """
        self.dereference("SP")
        comp = -1 if bool else 0
        self.c_instruction(dest="M", comp=str(comp))
        self.inc_sp()
        return self

    def label(self, label):
        """Pushes a label into the instruction sequence
        """
        self.insts.append("(" + label + ")")
        return self

    def __str__(self):
        return "\n".join(self.insts)
