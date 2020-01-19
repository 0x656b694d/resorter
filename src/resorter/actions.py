import shutil
import os
import shlex
import csv
import sys
import logging

class Action(object):
    def __init__(self, expressions, dry=False):
        self.dry = dry
    def act(self, source, dst):
        pass
    def finalize(self):
        pass

def flat(args, none=None):
    result = []
    for d in args:
        if d is None:
            if none is not None:
                result.append(none)
        elif isinstance(d, list):
            result.extend(d)
        else:
            result.append(d)
    return result

class Copy(Action):

    def act(self, source, dst):
        row = ' '.join(flat(dst, '?'))
        if self.dry:
            if not os.path.exists(source):
                raise RuntimeError(f'Source file not found: {source}')
            if not os.access(source, os.R_OK):
                raise RuntimeError(f'Couldn\'t read the source file: {source}')
            path = os.path.dirname(os.path.abspath(row))
            if not os.access(path, os.W_OK):
                raise RuntimeError(f'Couldn\'t write the destination folder: {path}')
        else:
            pass

class Move(Action):
    def act(self, source, dst):
        row = ' '.join(flat(dst, '?'))

        if self.dry:
            if not os.path.exists(source):
                raise RuntimeError(f'Source file not found: {source}')
            if not os.access(source, os.R_OK | os.W_OK):
                raise RuntimeError(f'Couldn\'t read or write the source file: {source}')
            path = os.path.dirname(os.path.abspath(row))
            if not os.access(path, os.W_OK):
                raise RuntimeError(f'Couldn\'t write the destination folder: {path}')
        else:
            pass

class Filter(Action):
    def act(self, source, dst):
        print(shlex.quote(source))

class Print(Action):
    def act(self, source, dst):
        row = ' '.join(flat(dst, '?'))
        if source != row:
            print(shlex.quote(source), shlex.quote(row), sep=' ')

class Csv(Action):
    def __init__(self, expressions, dry=False):
        self.writer = csv.writer(sys.stdout)
        self.writer.writerow(['file name']+[e.expr for e in expressions])
    def act(self, source, dst):
        row = [source] + flat(dst, '')
        for d in dst:
            if isinstance(d, list):
                row.extend(d)
            else:
                row.append(d)
        logging.debug(f'{row}')
        self.writer.writerow(row)

ACTIONS = {
        'copy':  {'class': Copy,  'help':'copy input file to the computed location'},
        'move':  {'class': Move,  'help':'move file file to the computed location'},
        'filter': {'class': Filter, 'help':'print the source paths only'},
        'print': {'class': Print, 'help':'print the source and the destination paths if they differ'},
        'csv': {'class': Csv, 'help':'output source and destination in the CSV format'},
        }
