import logging
import os

def get_from_dir(source, recursive):
    """return list of input files as DirEntries"""
    logging.debug('scanning %s', source)
    with os.scandir(source) as it:
        for entry in it:
            logging.debug('found %s', entry.path)
            if not entry.is_dir():
                yield entry
            elif recursive:
                logging.debug('entering directory %s', entry.path)
                yield from get_from_dir(entry.path, recursive)

class PathEntry(object): # DirEntry alike
    def __init__(self, f):
        self.path = f
    def stat(self):
        return os.stat(self.path)

def get_from_file(f, recursive):
    logging.debug('reading file names from %s', f)
    for line in f.readlines():
        line = line.rstrip('\r\n')
        if len(line) == 0: continue
        logging.debug('found %s', line)
        if os.path.isdir(line):
            yield from get_from_dir(line, recursive)
        else:
            yield PathEntry(line)
