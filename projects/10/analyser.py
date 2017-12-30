import sys, os
from parser import Parser

class JackAnalyser:
    @staticmethod
    def analyse(files_to_parse):
        return [Parser(f).parse() for f in files_to_parse]

    @staticmethod
    def write(files_to_write):
        for fname, output in files_to_write:
            directory, file = os.path.split(fname)
            directory += '/out'
            if not os.path.exists(directory):
                os.makedirs(directory)
            fname = os.path.join(directory, file)
            with open(fname, 'w') as f:
                for line in output:
                    f.write(line + '\n')

def get_files_to_parse(file):
    output = []
    if os.path.isdir(file):
        directory = file
        print("Parsing directory: {}".format(directory))
        for f in os.listdir(directory):
            if f.endswith(".jack"):
                filename = os.path.join(directory, f)
                output.append((filename, filename.replace('.jack', '.xml')))
    else:
        print("Parsing file: {}".format(file))
        output.append((file, file.replace('.jack', '.xml')))
    return output

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: jackanalyser [/path/to/file.jack|/path/to/dir]")
    else:
        file = sys.argv[1]
        files = get_files_to_parse(file)
        analysed = JackAnalyser.analyse(files)
        JackAnalyser.write(analysed)
