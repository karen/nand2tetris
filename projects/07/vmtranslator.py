import os, sys, re

import commands as cmd
from util import COMMENT_RE

def strip_comments(lines):
    return list(filter(lambda x: x, (COMMENT_RE.sub("", line) for line in lines)))

def lex(lines, input_filename):
    return [cmd.Command.create(line, input_filename) for line in lines]

def translate(commands):
    return (inst.to_asm() for inst in commands)

def main(files, dir=None):
    if not files:
        return

    output = []
    for filename in files:
        print("Translating {}...".format(filename))
        lines = open(filename, 'r').read().splitlines()
        filename = get_basename(filename)
        output.append(translate(lex(strip_comments(lines), filename)))

    output_filename = dir + ".asm" if dir else get_basename(files[0])
    with open(output_filename, 'w') as f:
        for line in output:
            f.write(str(line) + "\n")

def get_basename(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def retrieve_all_vm_files(dir):
    vm_files = []
    for file in os.listdir(dir):
        if file.endswith(".vm"):
            vm_files.append(os.path.join(dir, file))
    return vm_files

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError ("Usage: vmtranslator ./path/to/file.vm")
    else:
        input_filename = sys.argv[1]
        files_to_translate = []
        if os.path.isdir(input_filename):
            files_to_translate = retrieve_all_vm_files(input_filename)
            main(files_to_translate, input_filename)
        else:
            files_to_translate = [input_filename]
            main(files_to_translate)

        