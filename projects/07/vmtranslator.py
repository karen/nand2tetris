import sys, re

import commands as cmd
from util import COMMENT_RE

def strip_comments(lines):
    return list(filter(lambda x: x, (COMMENT_RE.sub("", line) for line in lines)))

def lex(lines, input_filename):
    return [cmd.Command.create(line, input_filename) for line in lines]

def translate(commands):
    return (inst.to_asm() for inst in commands)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError ("Usage: vmtranslator ./path/to/file.vm ./path/to/out.asm")
    else:
        input_filename, output_filename = sys.argv[1], sys.argv[2]
        lines = open(input_filename, 'r').read().splitlines()
        output = translate(lex(strip_comments(lines), input_filename))
        with open(output_filename, 'w') as f:
            for line in output:
                f.write(str(line) + "\n")