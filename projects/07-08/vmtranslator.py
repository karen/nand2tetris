import os, sys, re

import commands as cmd
from util import *

def strip_comments(lines):
    return list(filter(lambda x: x, (COMMENT_RE.sub("", line) for line in lines)))

def lex(lines, input_filename):
    return [cmd.Command.create(line, input_filename) for line in lines]

def translate(commands):
    return (inst.to_asm() for inst in commands)

def main(files, directory=''):
    if not files:
        return

    all_output = []
    for filename in files:
        print("Translating {}...".format(filename))
        lines = open(filename, 'r').read().splitlines()
        fname = dir_file_without_ext(filename)[1]
        commands = [cmd.Bootstrap()] + lex(strip_comments(lines), fname)
        all_output.append(translate(commands))

    if directory:
        output_filename = get_output_name(directory=directory)
    else:
        parts = dir_file_without_ext(files[0])
        output_filename = get_output_name(file=parts)
    with open(output_filename, 'w') as f:
        for output in all_output:
            for line in output:
                f.write(str(line) + "\n")

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

        