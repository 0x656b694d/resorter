import time

class Module(object):
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
            'replace': cls.replace
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
    def cap(s, args):
        return Text.change(args, s, str.capitalize)
    @staticmethod
    def low(s, args):
        return Text.change(args, s, str.lower)
    @staticmethod
    def up(s, args):
        return Text.change(args, s, str.upper)
    @staticmethod
    def replace(s, args):
        a = args.split(',', 1)
        return s.replace(a[0], a[1])

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
    def name(f, args):
        return Module.section(f.name, args)
    @staticmethod
    def path(f, args):
        return Module.section(f.path, args)
    @staticmethod
    def ext(f, args):
        e = f.name.rsplit('.', 1)
        e = e[1] if len(e) == 2 else ''
        return Module.section(e, args)
    @staticmethod
    def nam(f, args):
        e = f.name.rsplit('.', 1)
        return Module.section(e[0], args)

    @staticmethod
    def size(f, args):
        s = int(f.stat().st_size)
        if args is None: pass
        elif args in 'kK': s = s / 1024
        elif args in 'mM': s = s / 1024 / 1024
        elif args in 'gG': s = s / 1024 / 1024 / 1024
        elif args in 'tT': s = s / 1024 / 1024 / 1024 / 1024
        elif args in 'pP': s = s / 1024 / 1024 / 1024 / 1024 / 1024
        return int(s)

    @staticmethod
    def atime(f, args):
        t = time.localtime(f.stat().st_atime)
        return time.strftime('%d-%b-%Y.%H%M%S' if args is None else args)
    @staticmethod
    def mtime(f, args):
        t = time.localtime(f.stat().st_mtime)
        return time.strftime('%d-%b-%Y.%H%M%S' if args is None else args)
    @staticmethod
    def ctime(f, args):
        t = time.localtime(f.stat().st_ctime)
        return time.strftime('%d-%b-%Y.%H%M%S' if args is None else args)

MODULES=[Text, FileInfo]
KEYS={}

def update(args):
    for m in MODULES:
        if args.verbose:
            print('modules: {0} ({1})'.format(m.__name__, ', '.join(m.keys())))
        KEYS.update(m.keys())

