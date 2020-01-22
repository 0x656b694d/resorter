import shutil
import os
import shlex
import csv
import sys
import logging
from zipfile import ZipFile

import resorter.modules

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

class Zip(Action):
    def __init__(self, expressions, dry=False):
        if len(expressions) < 2:
            raise RuntimeError('zip action requires two expressions: for computing the zip file name and the path in the archive.'
                               ' Ex.: ... zip archive.zip docs/name')
        self.files = {}
        self.dry = dry

    def act(self, source, dst):
        f = self.files.get(dst[0], None)
        if f is None:
            print(dst[0])
            if self.dry:
                f = dst[0]
            else:
                f = ZipFile(dst[0], 'w')
                logging.info(f'new zip file {dst[0]}')
            self.files[dst[0]] = f
        name = '/'.join(flat(dst[1:], '?')) if len(dst>1) else os.pathsource.lstrip(os.sep)
        if self.dry:
            print(f'{source} -> {dst[0]}:{name}')
        else:
            logging.debug(f'Archiving {source} to {dst[0]}:{name}')
            f.write(source, arcname=name)
    
    def finalize(self):
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
        self.dry = dry
        if not dry:
            self.writer = csv.writer(sys.stdout)
            self.writer.writerow(['file name']+[e.expr for e in expressions])
    def act(self, source, dst):
        if not self.dry:
            self.writer.writerow([source] + flat(dst, ''))

class Fix(Action):
    def __init__(self, expressions, dry=False):
        resorter.modules.Set.allowed = not dry

ACTIONS = {
        'copy':  {'class': Copy,  'help':'copy input file to the computed location'},
        'move':  {'class': Move,  'help':'move file file to the computed location'},
        'filter': {'class': Filter, 'help':'print the source paths only'},
        'print': {'class': Print, 'help':'print the source and the destination paths if they differ'},
        'csv': {'class': Csv, 'help':'output source and destination in the CSV format'},
        'zip': {'class': Zip, 'help':'archive source to a zip file. First expression computes the zip file name, second - the path inside archive'},
        'fix': {'class': Fix, 'help':'allow file modifications'},
        }
