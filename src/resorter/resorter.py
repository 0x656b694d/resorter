#!/usr/bin/env python3

import re
import os
import argparse
import logging

import actions
import filters
import modules
import images
import audio

def true(_):
    return True
def false(_):
    return False


class ModuleFilter(filters.Filter):
    def __init__(self, e):
        self.m, e = e.rsplit('=', 1)
        self.e = re.compile(e)

    def onEntry(self, f):
        logging.debug("%s, %s", self.e.pattern, self.m)
        return self.e.fullmatch(compute(f, self.m)) is not None

def get_files(source, args):
    """return list of files"""
    logging.debug('scanning %s', source)
    with os.scandir(source) as it:
        for entry in it:
            logging.debug('found %s', entry.path)
            if not entry.is_dir():
                yield entry
            elif args.recursive:
                logging.debug('entering directory %s', entry.path)
                yield from get_files(entry.path, args)

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

def resort(files, args):
    expr_list = args.expression.split(os.sep)
    for f in files:
        try:
            logging.debug('resorting %s', f.path)
            output = []
            for e in expr_list:
                value = []
                for part in GROUP.split(e):
                    value.append(str(compute(f, part))
                                if part.startswith('{') else part)
                output.append(''.join(value))
            yield (f.path, os.path.join(args.output or '', *output))
        except Exception as e:
            logging.warning('Exception: %s', e)
            if ask('Could not compute destination for {0}: {1}'.format(f.path, e),
                {'Quit':'qQ', 'Ignore':'iI'}, 'i') in 'qQ': return False
    return True


def parse_args():
    parser = argparse.ArgumentParser(description='File organizer')

    parser.add_argument('action', metavar='ACTION', choices=actions.ACTIONS.keys(),
                        help='specify the action to perform over files')
    parser.add_argument('source', metavar='SOURCE', type=str,
                        help='source location')
    parser.add_argument('expression', metavar='EXPR', type=str,
                        help='specify the expression to format the destination')

    parser.add_argument('-o', '--output', metavar='output', type=str,
                        help='destination base location')
    parser.add_argument('-if', '--ifilter', metavar='expr', dest='ifilter', action='append',
                        help=r'regular or {module} expression for the input files to be included')
    parser.add_argument('-nif', '--nifilter', metavar='expr', dest='nifilter', action='append',
                        help=r'regular or {module} expression for the input files to be excluded')
    parser.add_argument('-of', '--ofilter', metavar='expr', dest='ofilter', action='append',
                        help='output file filter regular expression')

    parser.add_argument('-s', '--silent', dest='silent', action='store_const',
                        const=True, default=False,
                        help='be silent')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='be verbose')
    parser.add_argument('-g', '--debug', dest='debug', action='store_const',
                        const=True, default=False,
                        help='print debug messages')

    parser.add_argument('-r', '--recursive', dest='recursive', action='store_const',
                        const=True, default=False,
                        help='scan directories recursively')

    parser.add_argument('--dry-run', dest='dry_run', action='store_const',
                        const=True, default=False,
                        help='don\'t perform actions, only print')

    return parser.parse_args()

def ask(msg, opts, default=None):
    while True:
        answer = input('{0} {1}? '.format(msg,'/'.join(opts.keys())))
        if default is not None and len(answer) == 0:
            return default
        if len(answer) == 0: continue
        for o in opts:
            if answer in opts[o]:
                logging.debug('answer: %s (%s)', answer, o)
                return answer
    

def main(args):
    loglevel = logging.CRITICAL if args.silent else logging.WARNING
    if args.verbose:
        loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG
    logging.basicConfig(
        format='%(levelname)s:%(module)s.%(funcName)s: %(message)s', level=loglevel)

    modules.update(args)

    ifilters = [true]
    nifilters = [false]
    ofilters = [true]

    if args.ifilter:
        ifilters = []
        for ifs in args.ifilter:
            if ifs.startswith('{'):
                ifilters.append(ModuleFilter(ifs))
            else:
                ifilters.append(filters.RegexFilter(ifs))

    if args.nifilter:
        nifilters = []
        for nifs in args.nifilter:
            if nifs.startswith('{'):
                nifilters.append(ModuleFilter(nifs))
            else:
                nifilters.append(filters.RegexFilter(nifs))

    if args.ofilter:
        ofilters = []
        for ofs in args.ofilter:
            if ofs.startswith('{'):
                logging.critical('output module filters are not supported')
                continue
            ofilters.append(filters.RegexFilter(ofs))

    files = filter(
        lambda f: any((i(f) for i in ifilters))
            and all((not i(f) for i in nifilters)),
        get_files(args.source, args)
    )

    pairs = filter(
        lambda p: any((o(p[1]) for o in ofilters)),
        resort(files, args)
    )

    action = actions.ACTIONS['dry' if args.dry_run else args.action]
    for s, d in pairs:
        try:
            action(s, d, args)
        except Exception as e:
            logging.warning('Exception: %s', e)
            if ask('Could not {0} from {1} to {2}: {3}'
                .format(args.action, s, d, e),
                {'Quit': 'qQ', 'Ignore': 'iI'}, 'i') in 'qQ': break


if __name__ == "__main__":
    try:
        main(parse_args())
    except KeyboardInterrupt as e:
        logging.warning('Keyboard interrupt')
