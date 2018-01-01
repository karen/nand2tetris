import sys, os
from parser import Parser

class JackAnalyser:
    @staticmethod
    def analyse(files_to_parse):
        return [Parser(f).parse() for f in files_to_parse]

def get_files_to_parse(file):
    output = []

    if os.path.isdir(file):
        directory = file
        print("Parsing directory: {}".format(directory))
        for f in os.listdir(directory):
            if f.endswith(".jack"):
                i = os.path.join(directory, f)
                outdir = directory + '/out'
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                o = os.path.join(outdir, f)
                output.append((i, o.replace('.jack', '.vm')))
                print("Compiling {} into {}".format(i, o))
    else:
        print("Parsing file: {}".format(file))
        output.append((file, file.replace('.jack', '.vm')))
    return output

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: jackanalyser [/path/to/file.jack|/path/to/dir]")
    else:
        file = sys.argv[1]
        files = get_files_to_parse(file)
        analysed = JackAnalyser.analyse(files)
