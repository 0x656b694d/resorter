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

def process(files, expression, ask):
    expression = utils.split(expression, os.sep, modules.FUNCTIONS)
    for source in files:
        try:
            logging.debug(f'resorting {source!r}')
            value = ''.join(str(m.calc(source)) if isinstance(m, utils.Expression) else str(m) for m in expression)
            yield (source.path, value)
        except Exception as e:
            logging.error(f'Exception: {e}')
            traceback.print_tb(sys.exc_info()[2])
            if ask(f'Could not compute destination for {source.path}: {e}',
                {'Quit':'qQ', 'Ignore':'iI'}, 'i') in 'qQ': return False
    return True

def get_filters(i, n, o):

    def add(ff, d):
        return [filters.ExpressionFilter(f, modules.FUNCTIONS) if f.startswith('{') else filters.RegexFilter(f) for f in ff] if ff else [d]

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


