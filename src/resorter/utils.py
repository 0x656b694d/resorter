import logging
import re
import os

class PathEntry(object): # DirEntry alike
    def __init__(self, f):
        self.path = f
        self.stat = None
    def stat(self):
        if self.stat is None:
            self.stat = os.stat(self.path)
        return self.stat

def read_filenames(source, recursive):
    if isinstance(source, str): # dir
        logging.info(f'scanning directory {source}')
        with os.scandir(source) as it:
            for entry in it:
                if not entry.is_dir():
                    logging.info(f'found {entry.path}')
                    yield entry
                elif recursive:
                    logging.debug(f'entering directory {entry.path}')
                    yield from read_filenames(entry.path, recursive)
                else:
                    logging.info(f'skipping {entry.path}')
    else:
        for line in source:
            line = line.rstrip('\r\n')
            if len(line) == 0: continue
            logging.info(f'found {line}')
            if os.path.isdir(line):
                yield from read_filenames(line, recursive)
            else:
                yield PathEntry(line)

def tokenize(expr, keywords):
    logging.debug(expr)

    token_spec = [
            ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
            ('STRING',   r"'[^']*'"),      # 'Strings'
            ('STRING2',  r'"[^"]*"'),      # "Strings"
            ('ID',       r'[A-Za-z_]+'),   # Identifiers
            ('OP',       r'[+\-*/\^.,%]|\|\||&&|\||&|==?|<=|>=|<>|[<>]|!=|~='), # Arithmetic operators
            ('BRACKETS', r'[\(\)\[\]{}]'),   # Brackets
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
            raise RuntimeError(f'unexpected {value!r} while parsing {expr}')
        yield (kind, value)

class Func(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f'Func({self.name})'

    def __eq__(self, f):
        return self.name == f.name
    def __hash__(self):
        return self.name.__hash__()

LOGIC = ['||', '&&']
COMP = ['=', '>', '<', '==', '>=', '<=', '!=', '<>', '~=']
OPS = [','] + LOGIC + COMP + ['+','-','|','--','^','/','*','&','%','.']
BRACKETS = { '[': ']', '(': ')', '{': '}'}

def polish(tokens):
        result = []
        ops_q = []
        logging.debug('Polishing')
        def pops(op):
            if isinstance(op, Func):
                return ['FUNC', op]
            elif op == 'ARGS':
                return [op, None]
            else:
                return ['OP', op]
        prev = (None, None)
        for kind, value in tokens:
            logging.debug(f'found token {kind}: {value}')
            logging.debug(f'ops queue: {ops_q!r}')
            if kind == 'OP':
                if value == '-' and (prev[0] in [None, 'OP'] or prev[1] in BRACKETS.keys()):
                    logging.debug(f'unary minus because {prev}')
                    value = '--'
                while len(ops_q):
                    top = ops_q[-1]
                    if isinstance(top, Func):
                        result.append(['FUNC', ops_q.pop()])
                    elif top == 'ARGS':
                        result.append([ops_q.pop(), None])
                    elif top in OPS and OPS.index(top) >= OPS.index(value):
                        result.append(['OP', ops_q.pop()])
                    else:
                        break
                ops_q.append(value)
            elif kind == 'FUNC':
                ops_q.append(Func(value))
            elif kind == 'BRACKETS':
                if value in BRACKETS.keys():
                    if len(ops_q) and isinstance(ops_q[-1], Func):
                        ops_q.append('ARGS')
                    ops_q.append(value)
                if value in BRACKETS.values():
                    while len(ops_q):
                        v = ops_q.pop()
                        if v in BRACKETS.keys():
                            if BRACKETS[v] == value:
                                break
                            else:
                                raise RuntimeError(f'Bracket {v!r} mismatch')
                        result.append(pops(v))
            else:
                result.append([kind, value])
            prev = (kind, value)
        ops_q.reverse()
        for op in ops_q:
            result.append(pops(op))
        logging.debug(f'Polish notation: {result!r}')
        return result

class Expression(object):
    def __init__(self, expr, keywords):
        self.keywords = keywords
        tokens = tokenize(expr, keywords.keys())
        self.polish = polish(tokens)
        # Translate ID to module function
        for kv in self.polish:
            kind, value = kv
            if kind == 'FUNC':
                kv[1] = (value.name, keywords[value.name]['func'])
                logging.debug(f'found FUNC {value.name}: {kv[1]!r}')

    def calc(self, source):
        logging.debug(f'running expression calculation on {source}')
        result = []
        class Args(): pass

        def callf(farg, source):
            if not isinstance(farg, list):
                return farg
            f, args = farg
            name, func = f
            v = func(name, source, args)
            logging.debug(f'{name}({args!r}) returned {v}')
            return v

        for kind, value in self.polish:
            logging.debug(f'... {kind} {value}')
            if kind == 'OP' and value == '--':
                a = result.pop()
                if type(a) not in [int, float]:
                    a = str(a)
                    a = (float if '.' in a else int)(a)
                result.append(-a)
            elif kind == 'OP' and len(result) < 2:
                result.append(value)
            elif kind == 'OP':
                b = result.pop()
                a = result.pop()
                if value == ',':
                    if isinstance(a, list):
                        a.append(b)
                        result.append(a)
                    else:
                        result.append([a,b])
                elif value == '.':
                    logging.debug(f'computing {a!r}.{b!r}')
                    v = callf(a, source)
                    v = callf(b, v)
                    result.append(v)
                elif value in LOGIC:
                    a = callf(a, source)
                    b = callf(b, source)
                    if value == '||':
                        result.append(a or b)
                    if value == '&&':
                        result.append(a and b)
                elif value in COMP:
                    a = callf(a, source)
                    b = callf(b, source)
                    if value == '<':
                        result.append(a < b)
                    elif value == '>':
                        result.append(a > b)
                    elif value in ('=', '=='):
                        result.append(a == b)
                    elif value in ('!=', '<>'):
                        result.append(a != b)
                    elif value == '>=':
                        result.append(a >= b)
                    elif value == '<=':
                        result.append(a <= b)
                    elif value == '~=':
                        a = str(a)
                        b = str(a)
                        result.append(True if re.fullmatch(b, a) else False)

                elif value in '/\\':
                    a = callf(a, source)
                    b = callf(b, source)
                    if type(a) == type(b) and type(a) == str:
                        result.append(a+os.sep+b)
                    else:
                        if type(a) not in [int, float]:
                            a = str(a)
                            a = (float if '.' in a else int)(a)
                        if type(b) not in [int, float]:
                            b = str(b)
                            b = (float if '.' in b else int)(b)
                        result.append(a / b)
                elif value == '+':
                    a = callf(a, source)
                    b = callf(b, source)
                    if type(a) != type(b):
                        if type(a) not in [int, float]:
                            a = str(a)
                            a = (float if '.' in a else int)(a)
                        if type(b) not in [int, float]:
                            b = str(b)
                            b = (float if '.' in b else int)(b)

                    result.append(a + b)
                else: # numeric
                    a = callf(a, source)
                    b = callf(b, source)

                    if type(a) not in [int, float]:
                        a = str(a)
                        a = (float if '.' in a else int)(a)
                    if type(b) not in [int, float]:
                        b = str(b)
                        b = (float if '.' in b else int)(b)
                    elif value == '-':
                        result.append(a-b)
                    elif value == '*':
                        result.append(a*b)
                    elif value == '%':
                        result.append(a%b)
                    elif value == '^':
                        result.append(a**b)
                    elif value == '|':
                        result.append(a | b)
                    elif value == '&':
                        result.append(a & b)

            elif kind == 'ARGS':
                result.append(Args())
            elif kind == 'FUNC':
                args = None
                if len(result) and isinstance(result[-1], Args):
                    result.pop()
                    args = result.pop()
                    if not isinstance(args, list):
                        args = [ args ]
                result.append([value, args])
            else:
                logging.debug(f'adding {value}')
                result.append(value)
            logging.debug(f'result: {result!r}')
        
        result = callf(result.pop(), source)

        logging.debug(f'computed {result!r}')
        return result

