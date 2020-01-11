import re
import sys
import os
import argparse
import logging
import traceback

import resorter.actions as actions
import resorter.filters as filters
import resorter.modules as modules
import resorter.utils as utils

VERSION='0.1.0'

class ModuleFilter(filters.Filter):
    def __init__(self, e):

        expr = split(e, '')
        self.module = expr[0]
        op = ''
        for ch in expr[1]:
            if ch in '=<>~':
                op += ch
            else: break
        self.op = op
        if op == '~':
            self.value = re.compile(expr[1][len(op):])
        else:
            self.value = expr[1][len(op):]

        self.func = parse_module(self.module)
        self.name = self.module + ' filter'

    def onEntry(self, f):
        value = compute_module(self.func, f)
        logging.debug('value %s', value)
        if self.op == '~':
            return self.value.fullmatch(value)
        value = type(self.value)(value)
        if self.op in '==':
            return value == self.value
        if self.op == '>=':
            return value >= self.value
        if self.op == '<=':
            return value <= self.value
        if self.op == '>':
            return value > self.value
        if self.op == '<':
            return value < self.value


GROUP_RE = re.compile(r'(\{[^}]+\})')
PART_RE = re.compile(r'([\w-]+)(\[[^\]]+\])?')

def parse_module(part):
    value = []
    for m in PART_RE.split(part.strip('{}')):
        if m == '' or m == '.':
            func = None
            continue
        if func:
            value.append({'func': modules.FUNCTIONS[func]['func'], 'func': func, 'args': m.strip('[]') if m is not None else None})
            func = None
        else:
            func = m
    logging.debug('parsed module %s', value)
    return value

class Expression(object):
    def __init__(self, expr):
        tokens = utils.tokenize(expr.strip('{}'), modules.FUNCTIONS)
        polish = utils.polish(tokens)
        # Translate ID to module function
        for kv in polish:
            kind, value = kv
            if kind == 'FUNC':
                kv[1] = (value.name, modules.FUNCTIONS[value.name]['func'])

        self.polish = polish

    def calc(self, source):
        result = []
        class Dot(): pass
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
            if kind == 'OP':
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
                else:
                    a = callf(a, source)
                    b = callf(b, source)
 
                    if type(a) not in [int, float]:
                        a = str(a)
                        a = (float if '.' in a else int)(a)
                    if type(b) not in [int, float]:
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

def split(s, sep):
    result = []
    word = []
    open_brackets = r'{[('
    close_brackets = r'}])'
    brackets = []
    for ch in s:
        if ch in sep and not len(brackets):
            if len(word):
                result.append(''.join(word))
                word = []
            result.append(ch)
            continue
        if ch in open_brackets:
            brackets.append(ch)
            if ch == '{' and len(word):
                result.append(''.join(word))
                word = []
            word.append(ch)
        elif ch in close_brackets:
            b = brackets.pop()
            if open_brackets.find(b) != close_brackets.find(ch):
                raise Exception(f'Unmatched bracket {ch} in {s}')
            word.append(ch)
            if ch == '}':
                result.append(Expression(''.join(word)))
                word = []
        else:
            word.append(ch)
    if len(word):
        result.append(''.join(word))
    if len(brackets):
        raise RuntimeError(f'Unmatched brackets {brackets!r} in {s}')
    return result

def compute(modules, f):
    result = []
    for module in modules:
        if isinstance(module, Expression):
            result.append(module.calc(f))
        else:
            result.append(module)
    return ''.join(str(r) for r in result)

def process(files, expression, ask):
    modules = split(expression, os.sep)
    for f in files:
        try:
            logging.debug(f'resorting {f!r}')
            yield (f.path, compute(modules, f))
        except Exception as e:
            logging.warning('Exception: %s', e)
            traceback.print_tb(sys.exc_info()[2])
            if ask('Could not compute destination for {0}: {1}'.format(f.path, e),
                {'Quit':'qQ', 'Ignore':'iI'}, 'i') in 'qQ': return False
    return True

def get_filters(i, n, o):

    def add(ff, d):
        return [ModuleFilter(f) if f.startswith('{') else filters.RegexFilter(f) for f in ff] if ff else [d]

    return (add(i, filters.TrueFilter()), add(n, filters.FalseFilter()), add(o, filters.TrueFilter()))

def resort(files, filters, expression, ask):

    ifilters, nifilters, ofilters = filters

    logging.debug('ifilters %s', ','.join([f.name for f in ifilters]))
    logging.debug('nifilters %s', ''.join([f.name for f in nifilters]))
    logging.debug('ofilters %s', ''.join([f.name for f in ofilters]))

    files = filter(
        lambda f: any((i(f) for i in ifilters))
            and all((not i(f) for i in nifilters)),
        files
    )

    pairs = process(files, expression, ask)
    pairs = filter(
        lambda p: any((o(p[1]) for o in ofilters)),
        pairs
    )

    return pairs


