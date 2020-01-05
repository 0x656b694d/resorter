import os
import time
import logging
import codecs

class Module(object):

    CACHE = { 'name': None, 'data': None }

    @classmethod
    def open(cls, f):
        return None

    @classmethod
    def cache(cls, f):
        if f != cls.CACHE['name']:
            cls.CACHE = { 'name': f, 'data': cls.open(f) }
        return cls.CACHE['data']

    @staticmethod
    def range(args):
        if args is None:
            return None
        a,b = None,None
        r = args.split(':')
        if len(r[0]): a = int(r[0])
        if len(r) > 1 and len(r[1]): b = int(r[1])
        return (a,b)

    @staticmethod
    def section(s, args):
        if args is None: return s
        a,b = Module.range(args)
        return s[a:b]

class Text(Module):
    @classmethod
    def keys(cls):
        return {
            'cap': cls.cap,
            'low': cls.low,
            'up': cls.up,
            'replace': cls.replace,
            'decode': cls.decode
        }
    
    @staticmethod
    def change(args, s, f):
        if args is None: return f(s)
        a,b = Module.range(args)
        result = f(s[a:b])
        if a is not None: result = s[:a] + result
        if b is not None: result = result + s[b:]
        return result

    @staticmethod
    def cap(_, s, args):
        return Text.change(args, s, str.capitalize)
    @staticmethod
    def low(_, s, args):
        return Text.change(args, s, str.lower)
    @staticmethod
    def up(_, s, args):
        return Text.change(args, s, str.upper)
    @staticmethod
    def replace(_, s, args):
        a = args.split(',', 1)
        return s.replace(a[0], a[1])
    @staticmethod
    def decode(_, s, args):
        return codecs.decode(s, args)

class Counter(Module):
    count = None
    step = 1

    @classmethod
    def keys(cls):
        return {
            'counter': cls.counter
        }

    @staticmethod
    def counter(_, f, args):
        print(Counter.count)
        if Counter.count is None:
            args = args.split(',', 1)
            Counter.count = 0
            if len(args) == 2:
                Counter.count, Counter.step = [int(i) for i in args]
            else:
                Counter.count = int(args[0])
        logging.debug('counting %s by %s', Counter.count, Counter.step)
        Counter.count += Counter.step
        return str(Counter.count)

class FileInfo(Module):

    @classmethod
    def keys(cls):
        return {
            'name': cls.name,
            'path': cls.path,
            'ext': cls.ext,
            'nam': cls.nam,
            'size': cls.size,
            'atime': cls.atime,
            'ctime': cls.ctime,
            'mtime': cls.mtime
        }

    @staticmethod
    def name(_, f, args):
        return Module.section(os.path.basename(f.path), args)
    @staticmethod
    def path(_, f, args):
        return Module.section(os.path.dirname(f.path), args)
    @staticmethod
    def ext(_, f, args):
        _, ext = os.path.splitext(f.path)
        return Module.section(ext, args)
    @staticmethod
    def nam(_, f, args):
        root, _ = os.path.splitext(f.path)
        return Module.section(root, args)

    @staticmethod
    def size(_, f, args):
        if isinstance(f, str): raise RuntimeError('method not supported')
        s = int(f.stat().st_size)
        if args is None: pass
        elif args in 'kK': s = s / 1024
        elif args in 'mM': s = s / 1024 / 1024
        elif args in 'gG': s = s / 1024 / 1024 / 1024
        elif args in 'tT': s = s / 1024 / 1024 / 1024 / 1024
        elif args in 'pP': s = s / 1024 / 1024 / 1024 / 1024 / 1024
        return int(s)

    @staticmethod
    def atime(_, f, args):
        if isinstance(f, str): raise RuntimeError('method not supported')
        t = time.localtime(f.stat().st_atime)
        return time.strftime('%d-%b-%Y.%H%M%S' if args is None else args, t)
    @staticmethod
    def mtime(_, f, args):
        if isinstance(f, str): raise RuntimeError('method not supported')
        t = time.localtime(f.stat().st_mtime)
        return time.strftime('%d-%b-%Y.%H%M%S' if args is None else args, t)
    @staticmethod
    def ctime(_, f, args):
        if isinstance(f, str): raise RuntimeError('method not supported')
        t = time.localtime(f.stat().st_ctime)
        return time.strftime('%d-%b-%Y.%H%M%S' if args is None else args, t)

MODULES=[Text, Counter, FileInfo]
KEYS={}

def update():
    logging.debug('registering modules')
    for m in MODULES:
        logging.debug('... {0} ({1})'.format(m.__name__, ', '.join(m.keys())))
        KEYS.update(m.keys())

