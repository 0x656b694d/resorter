import logging
import re
import os

def get_from_dir(source, recursive):
    """return list of input files as DirEntries"""
    logging.info(f'scanning {source}')
    with os.scandir(source) as it:
        for entry in it:
            if not entry.is_dir():
                logging.info(f'found {entry.path}')
                yield entry
            elif recursive:
                logging.debug(f'entering directory {entry.path}')
                yield from get_from_dir(entry.path, recursive)
            else:
                logging.info(f'skipping {entry.path}')

class PathEntry(object): # DirEntry alike
    def __init__(self, f):
        self.path = f
    def stat(self):
        return os.stat(self.path)

def get_from_file(f, recursive):
    logging.debug(f'reading file names from {f}')
    for line in f.readlines():
        line = line.rstrip('\r\n')
        if len(line) == 0: continue
        logging.debug(f'found {line}')
        if os.path.isdir(line):
            yield from get_from_dir(line, recursive)
        else:
            yield PathEntry(line)


def tokenize(expr, keywords):
    logging.debug(expr)

    token_spec = [
            ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
            ('STRING',   r"'[^']*'"),
            ('STRING2',  r'"[^"]*"'),
            ('ID',       r'[A-Za-z_]+'),   # Identifiers
            ('OP',       r'[+\-*/\^.,]'),  # Arithmetic operators
            ('BRACKETS', r'[\(\)\[\]]'),   # Brackets
            ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
            ('MISMATCH', r'.'),            # Any other character
        ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
    for mo in re.finditer(tok_regex, expr):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'STRING':
            value = value.strip("'")
        elif kind == 'STRING2':
            value = value.strip('"')
        elif kind == 'ID':
            if value in keywords:
                kind = 'FUNC'
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'unexpected {value!r}')
        yield (kind, value)

class Func(object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f'Func({self.name})'

def polish(tokens):
        ops = ['+','-','/','*',r'%','^','.',',']
        result = []
        ops_q = []
        brackets = { '[': ']', '(': ')' }
        logging.debug('Polishing')
        for kind, value in tokens:
            logging.debug(f'found token {kind}: {value}')
            logging.debug(f'ops queue: {ops_q!r}')
            if kind == 'OP' and value == '.':
                while len(ops_q):
                    top = ops_q[-1]
                    if isinstance(top, Func):
                        result.append(['FUNC', ops_q.pop()])
                    else:
                        break
                result.append([kind, value])
            elif kind == 'OP':
                while len(ops_q):
                    top = ops_q[-1]
                    if top in ops and ops.index(top) >= ops.index(value):
                        result.append(['OP', ops_q.pop()])
                    elif isinstance(top, Func):
                        result.append(['FUNC', ops_q.pop()])
                    else:
                        break
                ops_q.append(value)
            elif kind == 'FUNC':
                ops_q.append(Func(value))
            elif kind == 'BRACKETS':
                if value in brackets.keys():
                    ops_q.append(value)
                if value in brackets.values():
                    while len(ops_q):
                        v = ops_q.pop()
                        if v in brackets.keys():
                            if brackets[v] == value:
                                if value == ']':
                                    result.append(['ARGS', True])
                                break
                            else:
                                raise RuntimeError(f'Bracket {v!r} mismatch')
                        result.append(['FUNC' if isinstance(v, Func) else 'OP', v])
            else:
                result.append([kind, value])
        ops_q.reverse()
        for op in ops_q:
            result.append(['FUNC' if isinstance(op, Func) else 'OP', op])
        logging.debug(f'Polish notation: {result!r}')
        return result

