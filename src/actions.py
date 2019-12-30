import shutil
import csv

def action_copy(source, dst, args):
    pass

def action_move(source, dst, args):
    pass

def action_print(source, dst, args):
    print('"{0}" "{1}"'.format(source.replace('"', '\\"'), dst.replace('"', '\\"')))

def action_dry(source, dst, args):
    print('{0} "{1}" "{2}"'.format(args.action, source.replace('"', '\\"'), dst.replace('"', '\\"')))

ACTIONS = {
    'copy': action_copy,
    'move': action_move,
    'print': action_print,
    'dry': action_dry
}
