import shutil
import os
import shlex

def action_copy(source, dst, dry=False):
    if dry:
        if not os.path.exists(source):
            raise RuntimeError(f'Source file not found: {source}')
        if not os.access(source, os.R_OK):
            raise RuntimeError(f'Couldn\'t read the source file: {source}')
        path = os.path.dirname(os.path.abspath(dst))
        if not os.access(path, os.W_OK):
            raise RuntimeError(f'Couldn\'t write the destination folder: {path}')
    else:
        pass

def action_move(source, dst, dry=False):
    if dry:
        if not os.path.exists(source):
            raise RuntimeError(f'Source file not found: {source}')
        if not os.access(source, os.R_OK | os.W_OK):
            raise RuntimeError(f'Couldn\'t read or write the source file: {source}')
        path = os.path.dirname(os.path.abspath(dst))
        if not os.access(path, os.W_OK):
            raise RuntimeError(f'Couldn\'t write the destination folder: {path}')
    else:
        pass

def action_filter(source, dst, dry=False):
    print(shlex.quote(source))

def action_print(source, dst, dry=False):
    if source != dst:
        print(shlex.quote(source), shlex.quote(dst), sep=' ')

ACTIONS = {
        'copy':  {'func': action_copy,  'help':'copy input file to the computed location'},
        'move':  {'func': action_move,  'help':'move file file to the computed location'},
        'filter': {'func': action_filter, 'help':'print the source paths only'},
        'print': {'func': action_print, 'help':'print the source and the destination paths if they differ'}
        }
