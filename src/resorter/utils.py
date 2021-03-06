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
    if isinstance(source, str) or isinstance(source, bytes): # dir
        logging.info(f'scanning directory {source}')
        source = os.fsencode(source)
        with os.scandir(source) as it:
            for entry in it:
                if not entry.is_dir():
                    logging.info(f'found {entry.path}')
                    yield os.fsdecode(entry.path)
                elif recursive:
                    logging.debug(f'entering directory {entry.path}')
                    yield from read_filenames(entry.path, recursive)
                else:
                    logging.info(f'skipping {entry.path}')
    elif isinstance(source, list):
        logging.debug(f'reading lines from {source}')
        for line in source:
            line = line.rstrip('\r\n')
            if len(line) == 0: continue
            logging.info(f'found {line}')
            if os.path.isdir(line):
                yield from read_filenames(line, recursive)
            else:
                yield line

def unescape(s):
    return s.replace(r'\t', '\t').replace(r'\r', '\r').replace(r'\n', '\n').replace(r'\'', '\'').replace(r'\"', '"')

def tokenize(expr, keywords):
    logging.debug(expr)

    token_spec = [
            ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
            ('STRING',   r"'(?:[^'\\]|\\.)*'"), # 'Strings'
            ("STRING2",  r'"(?:[^"\\]|\\.)*"'), # "Strings"
            ('ID',       r'[A-Za-z_0-9]+'),   # Identifiers
            ('OP',       r'[:+\-*/\^.,%]|\|\||&&|\||&|==?|<=|>=|<>|[<>]|!=|~='), # Arithmetic operators
            ('BRACKETS', r'[\(\)\[\]{}]'),   # Brackets
            ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
            ('MISMATCH', r'.'),            # Any other character
        ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
    for mo in re.finditer(tok_regex, expr):
        kind = mo.lastgroup
        value = mo.group()
        logging.debug(f'{kind}: {value}')
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind.startswith('STRING'):
            value = unescape(value[1:-1])
        elif kind == 'ID' and value in keywords:
            kind = 'FUNC'
        elif kind == 'MISMATCH':
            raise RuntimeError(f'unexpected {value!r} while parsing {expr}')
        if kind != 'SKIP':
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
OPS = [','] + LOGIC + COMP + ['+','-','|','--','^','/','*','&','%',':','.']
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

class FuncError(Exception):
    def __init__(self, exc, funcb):
        self.exc = exc
        self.funcb = funcb

class FuncB(object):
    def __init__(self, name, f): #name, func, hlp):
        self.name = name
        self.func = f
        self.args = []

    def __repr__(self):
        return f'Function_{self.name}({self.args})'

    def call(self):
        if self.args[0] is None: return None
        try:
            v = self.func['func'](self.name, self.args)
            logging.debug(f'{self.name}({self.args!r}) returned {v}')
            return v
        except Exception as e:
            raise FuncError(e, self)

class Caller(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, name, args):
        return self.func(name, args)

class Expression(object):
    def __init__(self, expr, keywords):
        self.keywords = keywords
        self.expr = expr
        tokens = tokenize(expr, keywords.keys())
        self.polish = polish(tokens)
        # Translate ID to module function
        for kv in self.polish:
            kind, value = kv
            if kind == 'FUNC':
                f = keywords[value.name]
                kv[1] = FuncB(value.name, f)
                logging.debug(f'found FUNC {value.name}: {kv[1]!r}')

    def calc(self, source):
        logging.debug(f'running expression calculation on {source}')
        result = []
        class Args(): pass

        def callf(funcarg):
            if isinstance(funcarg, list):
                return [ f.call() if isinstance(funcarg, FuncB) else f for f in funcarg ]

            while isinstance(funcarg, FuncB):
                funcarg = funcarg.call()
            return funcarg

        for kind, value in self.polish:
            logging.debug(f'... {kind} {value}')
            if kind == 'OP' and value == '--':
                a = result.pop()
                if type(a) not in [int, float]:
                    a = str(a)
                    a = (float if '.' in a else int)(a)
                result.append(-a)
            elif kind == 'OP' and len(result) < 1:
                result.append(value)
            elif kind == 'OP' and len(result) < 2:
                b = callf(result.pop())
                result.append(value + b)
            elif kind == 'OP' and value == '.':
                b = result.pop()
                a = result.pop()
                logging.debug(f'appending left op to {b}')
                if isinstance(b, FuncB):
                    if isinstance(b.func['func'], Caller):
                        b.args[0] = a
                        result.append(b)
                    else:
                        b.args[0] = callf(a)
                        result.append(callf(b))
                else:
                    result.append(callf(a)+'.'+b)
            elif kind == 'OP' and value == '||':
                b = result.pop()
                a = result.pop()
                result.append(callf(a) or callf(b))
            elif kind == 'OP' and value == '&&':
                b = result.pop()
                a = result.pop()
                result.append(callf(a) and callf(b))
            elif kind == 'OP' and value == ',':
                b = result.pop()
                a = result.pop()
                if isinstance(a, FuncB) and not isinstance(a.func['func'], Caller):
                    a = callf(a)
                if isinstance(b, FuncB) and not isinstance(b.func['func'], Caller):
                    b = callf(b)
                if isinstance(a, list):
                    a.append(b)
                    result.append(a)
                else:
                    result.append([a,b])
            elif kind == 'OP':
                b = callf(result.pop())
                a = callf(result.pop())
                if value == ':':
                    result.append(str(a) + str(b))
                elif value in LOGIC or value in COMP:
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
                        b = str(b)
                        result.append(True if re.fullmatch(b, a) else False)
                elif type(a) in (int, float) and type(b) in (int, float): # numeric
                    if type(a) not in (int, float):
                        a = str(a)
                        a = (float if '.' in a else int)(a)
                    if type(b) not in (int, float):
                        b = str(b)
                        b = (float if '.' in b else int)(b)

                    if value == '+':
                        result.append(a+b)
                    elif value == '-':
                        result.append(a-b)
                    elif value == '*':
                        result.append(a*b)
                    elif value == '/':
                        result.append(a/b)
                    elif value == '%':
                        result.append(a%b)
                    elif value == '^':
                        result.append(a**b)
                    elif value == '|':
                        result.append(a | b)
                    elif value == '&':
                        result.append(a & b)
                else:
                    if not isinstance(a, str): a = str(a)
                    if not isinstance(b, str): b = str(b)
                    if value == '+':
                        result.append(a + b)
                    elif value in '/\\':
                        result.append(a + os.sep + b)
                    else:
                        result.append(a + value + b)

            elif kind == 'ARGS':
                result.append(Args())
            elif kind == 'FUNC':
                logging.debug(f'--- {value!r} -- {result}')
                args = [ source ]
                if len(result) and isinstance(result[-1], Args):
                    result.pop() # Args marker
                    a = callf(result.pop()) # arguments values
                    logging.debug(f'args on stack: {a}')
                    (args.extend if isinstance(a, list) else args.append)(a)
                value.args = args
                result.append(value)
            else:
                logging.debug(f'adding {value}')
                result.append(value)
            logging.debug(f'result: {result!r}')
        
        value = []
        while len(result):
            value.append(callf(result.pop()))
        if len(value) == 1:
            value = value[0]

        logging.debug(f'computed {value!r}')
        return value

