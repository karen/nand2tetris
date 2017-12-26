import re

from enum import Enum

COMMENT_RE = re.compile("\s*//.*$")

def generate_label(label):
    counter = -1
    while True:
        counter += 1
        yield label + str(counter)

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
