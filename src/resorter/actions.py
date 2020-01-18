import shutil
import os
import shlex

class Action(object):
    def __init__(self, dry=False):
        self.dry = dry
    def act(self, source, dst):
        pass
    def finalize(self):
        pass

class Copy(Action):

    def act(self, source, dst):
        if self.dry:
            if not os.path.exists(source):
                raise RuntimeError(f'Source file not found: {source}')
            if not os.access(source, os.R_OK):
                raise RuntimeError(f'Couldn\'t read the source file: {source}')
            path = os.path.dirname(os.path.abspath(dst))
            if not os.access(path, os.W_OK):
                raise RuntimeError(f'Couldn\'t write the destination folder: {path}')
        else:
            pass

class Move(Action):
    def act(self, source, dst):

        if self.dry:
            if not os.path.exists(source):
                raise RuntimeError(f'Source file not found: {source}')
            if not os.access(source, os.R_OK | os.W_OK):
                raise RuntimeError(f'Couldn\'t read or write the source file: {source}')
            path = os.path.dirname(os.path.abspath(dst))
            if not os.access(path, os.W_OK):
                raise RuntimeError(f'Couldn\'t write the destination folder: {path}')
        else:
            pass

class Filter(Action):
    def act(self, source, dst):
        print(shlex.quote(source))

class Print(Action):
    def act(self, source, dst):
        if source != dst:
            print(shlex.quote(source), shlex.quote(dst), sep=' ')

ACTIONS = {
        'copy':  {'class': Copy,  'help':'copy input file to the computed location'},
        'move':  {'class': Move,  'help':'move file file to the computed location'},
        'filter': {'class': Filter, 'help':'print the source paths only'},
        'print': {'class': Print, 'help':'print the source and the destination paths if they differ'}
        }
