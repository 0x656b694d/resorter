#!/usr/bin/env python3

import argparse
import os
import logging
import sys
import traceback

import resorter.utils
import resorter.actions
import resorter.modules

import resorter.images
import resorter.audio
import resorter.media

VERSION='0.1.0'

def parse_args():
    examples = """
    Example: %(prog)s -f photos copy exif_make/name
    """
    parser = argparse.ArgumentParser(description='File organizer', prog='resorter', fromfile_prefix_chars='@', epilog=examples)
    actions = resorter.actions.ACTIONS

    parser.add_argument('ACTION', default='filter', nargs='?',
                        help='action to be executed over input files ({0})'.format(', '.join(actions.keys())))
    parser.add_argument('EXPRESSION',  default='./name', nargs='?',
                        help='specify the expression to format the destination or a @file name. Default: ./name')

    parser.add_argument('-f', '--from', dest='input', nargs='?', default='.', #sys.stdin,
                        help='read file names from a directory, a file. Default: stdin')
    parser.add_argument('-r', '--recursive', dest='recursive', action='store_const',
                        const=True, default=False,
                        help='scan directories recursively')

    parser.add_argument('-if', '--include', metavar='EXPR', dest='include',
                        help=r'expression for the input files to be included')

    parser.add_argument('-s', '--silent', dest='silent', action='store_const',
                        const=True, default=False,
                        help='be silent')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='be verbose')
    parser.add_argument('-g', '--debug', dest='debug', action='store_const',
                        const=True, default=False,
                        help='print debug messages')

    parser.add_argument('-a', '--ask', dest='ask', action='store_const',
                        const=True, default=False,
                        help='ask confirmation on each file')
    parser.add_argument('-p', '--stop', dest='stop', action='store_const',
                        const=True, default=False,
                        help='stop on first failure')
    parser.add_argument('-i', '--ignore', dest='ignore', action='store_const',
                        const=True, default=False,
                        help='ignore failures')

    parser.add_argument('--dry-run', dest='dry_run', action='store_const',
                        const=True, default=False,
                        help='don\'t perform actions, only print')

    parser.add_argument('--version', action='version', version='%(prog)s '+VERSION)
    parser.add_argument('--list-functions', dest='list_functions', action='store_const',
                        const=True, default=False,
                        help='list available functions to use in EXPR')

    return parser.parse_intermixed_args()

def ask_cli(msg, opts, default=None):
    answer = None

    question = '{0} {1}? [{2}] '.format(msg, '/'.join(opts.keys()), '/'.join(['*'+v[0] if v[0] == default else v[0] for v in opts.values()]) )
    while not [ k for k, v in opts.items() if answer and answer in v ]:
        answer = input(question)
        if default and not answer:
            answer = default
            print(answer)
            break
    logging.debug(f'answer: {answer}')
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

    logging.debug(f'action "{args.ACTION}"')
    logging.debug(f'expr "{args.EXPRESSION}"')
    logging.debug(f'filter "{args.include}"')

    expression = args.EXPRESSION
    if expression.startswith('@'):
        with open(expression.lstrip('@'), 'r') as f:
            expression = ''.join(f.readlines())

    files = resorter.utils.read_filenames(sys.stdin if args.input == '-' else args.input, args.recursive)
    if args.include:
        filter_expr = resorter.utils.Expression(args.include, resorter.modules.FUNCTIONS)
        files = filter(filter_expr.calc, files)
    
    action = resorter.actions.ACTIONS[args.ACTION]['func']
    expression = resorter.utils.Expression(expression, resorter.modules.FUNCTIONS)

    ask = ask_cli if args.ask else None

    for source in files:
        try:
            s = source.path
            d = str(expression.calc(source))
            question = ('dry ' if args.dry_run else '') + f'{args.ACTION}: {s} -> {d}\n'
            logging.debug(question)
            if ask:
                options = {'Confirm': 'cCyY', 'Ignore': 'iInN', 'Quit': 'qQxX'}
                answer = ask(question, options , 'c')
                if answer in options['Ignore']:
                    continue
                elif answer in options['Quit']:
                    break
            action(s, d, args.dry_run)
        except Exception as e:
            logging.error(f'Exception: {e}')
            if loglevel == logging.DEBUG:
                traceback.print_tb(sys.exc_info()[2])
            if args.ignore:
                args.silent or print(e, file=sys.stderr)
            elif args.stop or ask_cli(f'Could not {args.ACTION} {s}: {e!r}',
                    {'Quit': 'qQ', 'Ignore': 'iI'}, 'i') in 'qQ':
                break
    return 0

try:
    exit(main())
except KeyboardInterrupt:
    logging.warning('Keyboard interrupt')
    exit(-1)


