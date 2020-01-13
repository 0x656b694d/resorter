#!/usr/bin/env python3

import argparse
import os
import logging
import sys

import resorter.resorter
import resorter.utils
import resorter.actions
import resorter.modules

import resorter.images
import resorter.audio
import resorter.media

def parse_args():
    examples = """
    Example: %(prog)s -f photos -a copy -e {exif_camera}/{name}
    """
    parser = argparse.ArgumentParser(description='File organizer', prog='resorter', fromfile_prefix_chars='@', epilog=examples)
    actions = resorter.actions.ACTIONS

    parser.add_argument('-a', '--action', dest='action', default='copy', required=False,
                        help='action to be executed over input files ({0})'.format(', '.join(actions.keys())))
    parser.add_argument('-e', '--expression', dest='expr', default='./{name}', required=False,
                        help='specify the expression to format the destination or a @file name')

    parser.add_argument('-f', '--from', dest='input', nargs='?', default=sys.stdin,
                        help='read file names from a directory, a file. Default: stdin')

    parser.add_argument('-if', '--ifilter', metavar='EXPR', dest='ifilter', action='append',
                        help=r'expression for the input files to be included')
    parser.add_argument('-nif', '--nifilter', metavar='EXPR', dest='nifilter', action='append',
                        help=r'expression for the input files to be excluded')
    parser.add_argument('-of', '--ofilter', metavar='EXPR', dest='ofilter', action='append',
                        help=r'expression for the output files to be excluded')

    parser.add_argument('-s', '--silent', dest='silent', action='store_const',
                        const=True, default=False,
                        help='be silent')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='be verbose')
    parser.add_argument('-g', '--debug', dest='debug', action='store_const',
                        const=True, default=False,
                        help='print debug messages')

    parser.add_argument('-c', '--ask', dest='ask', action='store_const',
                        const=True, default=False,
                        help='ask confirmation on each file')
    parser.add_argument('-p', '--stop', dest='stop', action='store_const',
                        const=True, default=False,
                        help='stop on first failure')
    parser.add_argument('-i', '--ignore', dest='ignore', action='store_const',
                        const=True, default=False,
                        help='ignore failures')
    parser.add_argument('-r', '--recursive', dest='recursive', action='store_const',
                        const=True, default=False,
                        help='scan directories recursively')

    parser.add_argument('--dry-run', dest='dry_run', action='store_const',
                        const=True, default=False,
                        help='don\'t perform actions, only print')

    parser.add_argument('--version', action='version', version='%(prog)s '+resorter.resorter.VERSION)
    parser.add_argument('--list-functions', dest='list_functions', action='store_const',
                        const=True, default=False,
                        help='list available functions to use in EXPR')

    return parser.parse_args()

def ask_cli(msg, opts, default=None):
    while True:
        answer = input('{0} {1}? [{2}] '.format(msg, '/'.join(opts.keys()), '/'.join([v[0] for v in opts.values()]) ))
        if default is not None and len(answer) == 0:
            return default
        if len(answer) == 0: continue
        for o in opts:
            if answer in opts[o]:
                logging.debug('answer: %s (%s)', answer, o)
                return answer

def main():

    args = parse_args()

    loglevel = logging.CRITICAL if args.silent else logging.WARNING
    if args.verbose:
        loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG
    logging.basicConfig(
        format='%(levelname)s:%(module)s.%(funcName)s: %(message)s', level=loglevel)
    
    resorter.modules.update()

    if args.list_functions:
        resorter.modules.list_functions()
        return

    filters = resorter.resorter.get_filters(args.ifilter, args.nifilter, args.ofilter)
    
    if isinstance(args.input, str) and not os.path.isdir(args.input):
        files = resorter.utils.read_filenames(open(args.input, 'r'), args.recursive)
    else:
        files = resorter.utils.read_filenames(args.input, args.recursive)

    expression = args.expr
    if expression.startswith('@'):
        with open(expression.lstrip('@'), 'r') as f:
            expression = ''.join(f.readlines())

    pairs = resorter.resorter.resort(files, filters, expression, ask_cli)
    
    action = resorter.actions.ACTIONS[args.action]['func']
    for s, d in pairs:
        try:
            logging.debug(f'%srunning {args.action} over {s} to {d}', 'dry ' if args.dry_run else '')
            if args.ask:
                options = {'Confirm': 'cCyY', 'Ignore': 'iInN', 'Quit': 'qQxX'}
                answer = ask_cli('{0}: {1} -> {2}\n'.format(args.action, s, d), options , 'c')
                if answer in options['Ignore']:
                    continue
                elif answer in options['Quit']:
                    break
            elif not args.silent:
                print('... {0}{1} {2} -> {3}'.format('dry ' if args.dry_run else '', args.action, s, d))
            action(s, d, args.dry_run)
        except Exception as e:
            if args.ignore:
                logging.debug('Ignoring exception: %s', e)
            else:
                logging.error('Exception: %s', e)
                if args.stop:
                    break
                if ask_cli(f'Could not {args.action} from {s} to {d}: {e!r}',
                    {'Quit': 'qQ', 'Ignore': 'iI'}, 'i') in 'qQ':
                    break
    return 0

try:
    exit(main())
except KeyboardInterrupt:
    logging.warning('Keyboard interrupt')
    exit(-1)

