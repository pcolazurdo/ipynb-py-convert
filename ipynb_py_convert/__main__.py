import json
import sys
from os import path
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile",
                        help="Input file. Can be a .py or .ipynb source file")
    parser.add_argument("outputfile",
                        help="Out file (will overwrite). Can be a .py or .ipynb source file")
    parser.add_argument("-v", "--verbosity", action="count",
                        help="increase output verbosity - not in use")
    parser.add_argument("-d", "--delimiter", default="\n\n\n",
                        help="Allows you to set a different delimiter where to cut the input file and create a new cell. Default is '\\n\\n\\n' following the flake8 E302 rule")
    args = parser.parse_args(sys.argv[1:])
    return (args.verbosity, args.inputfile, args.outputfile, args.delimiter)


header_comment = '# %%\n'


def nb2py(notebook):
    result = []
    cells = notebook['cells']

    for cell in cells:
        cell_type = cell['cell_type']

        if cell_type == 'markdown':
            result.append('%s"""\n%s\n"""'%
                          (header_comment, ''.join(cell['source'])))

        if cell_type == 'code':
            result.append("%s%s" % (header_comment, ''.join(cell['source'])))

    return '\n\n'.join(result)


def py2nb(py_str):
    # remove leading header comment
    if py_str.startswith(header_comment):
        py_str = py_str[len(header_comment):]

    cells = []
    # chunks = py_str.split('\n\n%s' % header_comment)
    chunks = py_str.split('\n\n\n')

    for chunk in chunks:
        cell_type = 'code'
        if chunk.startswith("'''"):
            chunk = chunk.strip("'\n")
            cell_type = 'markdown'
        elif chunk.startswith('"""'):
            chunk = chunk.strip('"\n')
            cell_type = 'markdown'

        cell = {
            'cell_type': cell_type,
            'metadata': {},
            'source': chunk.splitlines(True),
        }

        if cell_type == 'code':
            cell.update({'outputs': [], 'execution_count': None})

        cells.append(cell)

    notebook = {
        'cells': cells,
        'metadata': {
            'anaconda-cloud': {},
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3'},
            'language_info': {
                'codemirror_mode': {'name': 'ipython', 'version': 3},
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.6.1'}},
        'nbformat': 4,
        'nbformat_minor': 4
    }

    return notebook


def convert(in_file, out_file):
    _, in_ext = path.splitext(in_file)
    _, out_ext = path.splitext(out_file)

    if in_ext == '.ipynb' and out_ext == '.py':
        with open(in_file, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        py_str = nb2py(notebook)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(py_str)

    elif in_ext == '.py' and out_ext == '.ipynb':
        with open(in_file, 'r', encoding='utf-8') as f:
            py_str = f.read()
        notebook = py2nb(py_str)
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)

    else:
        raise(Exception('Extensions must be .ipynb and .py or vice versa'))


def main():
    print(parse_arguments())
    # if len(argv) < 3:
    #     print('Usage: ipynb-py-convert in.ipynb out.py')
    #     print('or:    ipynb-py-convert in.py out.ipynb')
    #     sys.exit(1)
    debug, in_file, out_file, delimiter = parse_arguments()

    convert(in_file=in_file, out_file=out_file)


if __name__ == '__main__':
    main()
