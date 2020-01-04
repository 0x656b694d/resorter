import re
import os
import argparse
import logging

import resorter.actions as actions
import resorter.filters as filters
import resorter.modules as modules

VERSION='0.1.0'

class ModuleFilter(filters.Filter):
    def __init__(self, e):
        self.module, self.value_expr = e.rsplit('=', 1)
        self.value_expr = re.compile(self.value_expr)
        self.name = self.module + ' filter'

    def onEntry(self, f):
        value = compute(f, self.module)
        return self.value_expr.fullmatch(value)

GROUP = re.compile(r'(\{[^}]+\})')
PART = re.compile(r'([\w-]+)(\[[^\]]+\])?')

def compute(f, e):
    logging.debug("%s on %s", e, f)
    key = None
    value = f
    for m in PART.split(e.strip('{}')):
        if m == '' or m == '.':
            key = None
            continue
        if key:
            module = modules.KEYS[key]
            logging.debug('applying %s on %s with %s', module.__name__, value, m)
            value = module(key, value,
                    m.strip('[]') if m is not None else None)
            key = None
        else:
            key = m
    return value

def process(files, expression, ask):
    expr_list = expression.split(os.sep)
    for f in files:
        try:
            logging.debug('resorting %s', f.path)
            result = []
            for e in expr_list:
                value = []
                for part in GROUP.split(e):
                    value.append(str(compute(f, part))
                                if part.startswith('{') else part)
                result.append(''.join(value))
            yield (f.path, os.path.join(*result))
        except Exception as e:
            logging.warning('Exception: %s', e)
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
