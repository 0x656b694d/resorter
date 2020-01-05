import re
import sys
import os
import argparse
import logging
import traceback

import resorter.actions as actions
import resorter.filters as filters
import resorter.modules as modules

VERSION='0.1.0'

class ModuleFilter(filters.Filter):
    def __init__(self, e):
        self.module, self.value_expr = e.rsplit('=', 1)
        self.value_expr = re.compile(self.value_expr)
        self.func = parse_module(self.module)
        self.name = self.module + ' filter'

    def onEntry(self, f):
        value = compute_module(self.func, f)
        logging.debug('value=%s', value)
        return self.value_expr.fullmatch(value)

GROUP_RE = re.compile(r'(\{[^}]+\})')
PART_RE = re.compile(r'([\w-]+)(\[[^\]]+\])?')

def parse_module(part):
    value = []
    for m in PART_RE.split(part.strip('{}')):
        if m == '' or m == '.':
            key = None
            continue
        if key:
            value.append({'func': modules.KEYS[key], 'key': key, 'args': m.strip('[]') if m is not None else None})
            key = None
        else:
            key = m
    logging.debug('parsed module %s', value)
    return value

def parse(expression):
    expr_list = expression.split(os.sep)
    result = []
    for e in expr_list:
        for part in GROUP_RE.split(e):
            logging.debug('found part %s', part)
            result.append(parse_module(part) if part.startswith('{') else part)
    return result

def compute_module(module, f):
    value = f
    for m in module:
        key, func, args = m['key'], m['func'], m['args']
        logging.debug('applying %s on %s with %s', key, value, args)
        value = func(key, value, args)
    return value

def compute(modules, f):
    result = []
    for module in modules:
        logging.debug('computing %s', module)
        if isinstance(module, str):
            result.append(module)
        elif isinstance(module, list):
            result.append(compute_module(module, f))
    return '' if not len(result) else os.path.join(*result)

def process(files, expression, ask):
    modules = parse(expression)
    for f in files:
        try:
            logging.debug('resorting %s', f.path)
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
