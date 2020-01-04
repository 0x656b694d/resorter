import shutil
import os
import logging

def action_copy(source, dst, dry=False):
    if dry:
        if not os.path.exists(source):
            raise Exception('Source file not found: {0}'.format(source))
        elif not os.access(dst, os.R_OK):
            raise Exception('Couldn\'t read the source file: {0}'.format(source))
        if not os.access(dst, os.W_OK):
            raise Exception('Couldn\'t write the destination file: {0}'.format(dst))
    else:
        pass

def action_move(source, dst, dry=False):
    if dry:
        if not os.path.exists(source):
            raise Exception('Source file not found: {0}'.format(source))
        elif not os.access(src, os.R_OK):
            raise Exception('Couldn\'t read the source file: {0}'.format(source))
        if not os.access(dst, os.W_OK):
            raise Exception('Couldn\'t write the destination file: {0}'.format(dst))
    else:
        pass

def action_print(source, dst, dry=False):
    print('"{0}" "{1}"'.format(source.replace('"', '\\"'), dst.replace('"', '\\"')))

def action_check(source, dst, dry=False):
    if source != dst:
        print('"{0}" <> "{1}"'.format(source, dst))


ACTIONS = {
        'copy':  {'func': action_copy,  'help':'copy input file to the computed location'},
        'move':  {'func': action_move,  'help':'move file file to the computed location'},
        'print': {'func': action_print, 'help':'print source and destination paths'},
        'check': {'func': action_check, 'help':'check if the source and destination paths are equal'}
        }
