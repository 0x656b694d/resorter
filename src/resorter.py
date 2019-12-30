#!/usr/bin/env python3

import re
import os
import argparse
import actions
import modules
import images

def true(f):
    return True

class Filter(object):
    pass

class RegexFilter(Filter):

    def __init__(self, e):
        self.e = re.compile(e)

    def __call__(self, f):
        return self.e.fullmatch(f if isinstance(f, str) else f.path) is not None

class ModuleFilter(Filter):

    def __init__(self, e):
        self.e = e.rsplit('=', 1)

    def __call__(self, f):
        return compute(f, self.e[0]) == self.e[1]

def get_files(source, args):
    """return list of files"""
    if args.verbose:
        print('get_files: scanning '+source)
    with os.scandir(source) as it:
        for entry in it:
            if args.verbose:
                print('get_files: found '+entry.path)
            if not entry.is_dir():
                yield entry
            elif args.recursive:
                if args.verbose:
                    print('get_files: entering directory '+entry.path)
                yield from get_files(entry.path, args)

GROUP=re.compile(r'(\{[^}]+\})')
PART=re.compile(r'([\w-]+)(\[[^\]]+\])?')

def compute(f, e):

    key = None
    value = f
    for m in PART.split(e.strip('{}')):
        if m == '' or m == '.':
            key = None
            continue
        if key:
            value = modules.KEYS[key](value, m.strip('[]') if m is not None else None)
            key = None
        else:
            key = m
    return value

def resort(files, args):
    path = args.expression.split(os.sep)
    for f in files:
        if args.verbose:
            print('resort: {0}'.format(f.path))
        output = []
        if args.output is not None:
            output.append(args.output)
        first = args.output is None or args.output.endswith(os.sep)
        for e in path:
            if not first: output.append(os.sep)
            first = False
            for part in GROUP.split(e):
                output.append(str(compute(f, part)) if part.startswith('{') else part)
        yield (f.path, ''.join(output))

def main():
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
                    help='input file filter regular expression or module output')
    parser.add_argument('-of', '--ofilter', metavar='expr', dest='ofilter', action='append',
                    help='output file filter regular expression')

    parser.add_argument('-v', '--verbose', dest='verbose', action='store_const',
                    const=True, default=False,
                    help='be verbose')

    parser.add_argument('-r', '--recursive', dest='recursive', action='store_const',
                    const=True, default=False,
                    help='scan directories recursively')

    parser.add_argument('--dry-run', dest='dry_run', action='store_const',
                    const=True, default=False,
                    help='don\'t perform actions, only print')

    args = parser.parse_args()

    if args.verbose:
        print("Search location: " + args.source)
    
    modules.update(args)

    ifilters = [true]
    ofilters = [true]

    if args.ifilter:
        ifilters = []
        for ifs in args.ifilter:
            if ifs.startswith('{'):
                ifilters.append(ModuleFilter(ifs))
            else:
                ifilters.append(RegexFilter(ifs))

    if args.ofilter:
        ofilters = []
        for ofs in args.ofilter:
            ofilters.append(filters.RegexFilter(ofs))

    files = filter(
        lambda f: any((ifilt(f) for ifilt in ifilters)),
        get_files(args.source, args)
    )
    
    pairs = filter(
        lambda p: any((ofilt(p[1]) for ofilt in ofilters)),
        resort(files, args)
    )

    if not args.dry_run:
        action = actions.ACTIONS[args.action]
        for s,d in pairs:
            action(s, d, args)

if __name__ == "__main__":
    main()

