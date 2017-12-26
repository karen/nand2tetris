import os, re

from enum import Enum

COMMENT_RE = re.compile("\s*//.*$")
R_ENDFRAME = "R13"
R_RETADDR = "R14"
R_TEMP = "R15"

def generate_label(label):
    counter = -1
    while True:
        counter += 1
        yield label + str(counter)

def dir_file_without_ext(user_input):
    directory, file_and_ext = os.path.split(user_input)
    file, _ = os.path.splitext(file_and_ext)
    return (directory, file)

def get_output_name(file=None, directory=None):
    if file is not None:
        return os.path.join(*file) + ".asm"
    else:
        base = os.path.basename(directory)
        return os.path.join(directory, base) + ".asm"

def retrieve_all_vm_files(dir):
    vm_files = []
    for file in os.listdir(dir):
        if file.endswith(".vm"):
            vm_files.append(os.path.join(dir, file))
    return vm_files

class MemorySegment(Enum):
    LCL = 1
    ARG = 2
    THIS = 3
    THAT = 4
    TEMP = 5
    CONSTANT = 6
    STATIC = 7
    POINTER = 8

    @classmethod
    def to_enum(cls, key):
        return {'local': cls.LCL,
                'argument': cls.ARG,
                'this': cls.THIS, 'that': cls.THAT,
                'constant': cls.CONSTANT,
                'static': cls.STATIC,
                'temp': cls.TEMP,
                'pointer': cls.POINTER}[key]

    def is_ptr(self):
        return self == MemorySegment.LCL or self == MemorySegment.ARG or self == MemorySegment.THIS or self == MemorySegment.THAT

    def __str__(self):
        return self.name if self != MemorySegment.TEMP else str(self.value)
