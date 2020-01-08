import shutil
import os

def action_copy(source, dst, dry=False):
    if dry:
        if not os.path.exists(source):
            raise Exception('Source file not found: {0}'.format(source))
        if not os.access(source, os.R_OK):
            raise Exception('Couldn\'t read the source file: {0}'.format(source))
        path = os.path.dirname(os.path.abspath(dst))
        if not os.access(path, os.W_OK):
            raise Exception('Couldn\'t write the destination folder: {0}'.format(path))
    else:
        pass

def action_move(source, dst, dry=False):
    if dry:
        if not os.path.exists(source):
            raise Exception('Source file not found: {0}'.format(source))
        if not os.access(source, os.R_OK):
            raise Exception('Couldn\'t read the source file: {0}'.format(source))
        path = os.path.dirname(os.path.abspath(dst))
        if not os.access(path, os.W_OK):
            raise Exception('Couldn\'t write the destination folder: {0}'.format(path))
    else:
        pass

def action_check(source, dst, dry=False):
    if source != dst:
        print('"{0}" <> "{1}"'.format(source, dst))


ACTIONS = {
        'copy':  {'func': action_copy,  'help':'copy input file to the computed location'},
        'move':  {'func': action_move,  'help':'move file file to the computed location'},
        'check': {'func': action_check, 'help':'check if the source and destination paths are equal'}
        }
