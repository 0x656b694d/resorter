import shutil

def action_copy(source, dst, args):
    pass

def action_move(source, dst, args):
    pass

def action_csv(source, dst, args):
    print('"{0}", "{1}"'.format(source, dst))

ACTIONS = {
    'copy': action_copy,
    'move': action_move,
    'csv': action_csv
}
