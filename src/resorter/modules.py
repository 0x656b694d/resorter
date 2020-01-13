import os
import re
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
        a,b=0,-1
        if args is None:
            return (a,b)
        if len(args) > 0:
            if args[0]:
                a = int(args[0])
            b = a + 1
        if len(args) > 1 and args[1]:
            b = int(args[1])

        return (a,b)

    @staticmethod
    def section(s, args):
        if args is None: return s
        a,b = Module.range(args)
        return s[a:b]

class Num(Module):
    @classmethod
    def functions(cls):
        return {
            'round': {'func': cls.round_func, 'help': r'round a number. Argument: [precision]. Example: {size[k].round[1]}'},
            'num': {'func': cls.number, 'help': r'convert string to an number'},
        }
    @staticmethod
    def round_func(_, n, args):
        n = float(n)
        return round(n, *args) if args else round(n)
    @staticmethod
    def number(_, source, args):
        n = (float if '.' in source else int)(source)
        return round(n, *args) if args else n

class Conditions(Module):
    @classmethod
    def functions(cls):
        return {
                'if': {'func': cls.eef, 'help': r'if-else condition. Arguments: [condition, true value, false value]. Example: {if(size>1000,"big","small")}'},
                'any': {'func': cls.aany, 'help': r'true if any of arguments is true. Arguments: [conditions*]'},
                'all': {'func': cls.aall, 'help': r'true if all of arguments are true. Arguments: [conditions*]'},
                'in': {'func': cls.een, 'help': r'check agains a list of options. Arguments: [options]. Example: {if(exif_make.in("Canon","Nikon"),"Known", "Unknown")}'},
                'not': {'func': cls.noot, 'help': r'negation. Arguments: [condition]. Example: {if(not(exif_make.in("Canon","Nikon")),"Known", "Unknown")}'},
        }

    @staticmethod
    def eef(_, s, args):
        if not args or len(args) not in [1,2,3]:
            raise RuntimeError('function arguments mismatch: ' + Conditions.functions['if'].help)
        if isinstance(s, bool):
            return args[0] if s else args[1] if len(args) == 2 else ''
        return args[1] if args[0] else args[2] if len(args) == 3 else ''
    @staticmethod
    def aany(_, s, args):
        return any(args or s)
    @staticmethod
    def aall(_, s, args):
        return all(args or s)
    @staticmethod
    def een(_, s, args):
        return s in args
    @staticmethod
    def noot(_, s, args):
        return not (args[0] if args else s)

class Text(Module):
    @classmethod
    def functions(cls):
        return {
            'cap': {'func': cls.cap, 'help': r'capitalize. Example: {name.cap}'},
            'low': {'func': cls.low, 'help': r'lower case. Example: {name.low}'},
            'up': {'func': cls.up, 'help': r'upper case. Example: {name.up}'},
            'title': {'func': cls.title, 'help': r'title case. Example: {name.title}'},
            'replace': {'func': cls.replace, 'help': r"replace characters. Two arguments: [from,to]. Example: {name.replace[' ','_']}"},
            'decode': {'func': cls.decode, 'help': r'decode to current locale. Argument: [source encoding]. Example: {name.decode[cp1251]}'},
            'sub': {'func': cls.sub, 'help': r'substring. Argument: [from,to]. Example: {name.sub[0,4]}'},
            'index': {'func': cls.index, 'help': r'position of a substring. Argument: [substring]. Example: {name.sub[0,name.index[_]]}'},
        }
    
    @staticmethod
    def change(args, s, func):
        logging.debug(f'changing text in {s} at {args!r}')
        if args is None: return func(s)
        a,b = Module.range(args)
        result = func(s[a:b])
        if a is not None: result = s[:a] + result
        if b is not None: result = result + s[b:]
        return result

    @staticmethod
    def sub(_, s, args):
        return Module.section(s, args)
    @staticmethod
    def index(_, s, args):
        if not args: raise RuntimeError('missing index function parameter')
        result = -1
        for arg in args:
            result = s.find(str(arg))
            if result != -1:
                break
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
    def title(_, s, args):
        return Text.change(args, s, str.title)
    @staticmethod
    def replace(_, s, args):
        return s.replace(*args)
    @staticmethod
    def decode(_, s, args):
        return codecs.decode(s, *args)

class Counter(Module):
    count = None
    step = 1

    @classmethod
    def functions(cls):
        return {
            'counter': {'func': cls.counter, 'help': r'counting number. Arguments: [start,step]. Example: {nam}_{counter[100,10]}{ext}'}
        }

    @staticmethod
    def counter(_, f, args):
        print(Counter.count)
        if Counter.count is None:
            Counter.count = 0
            if len(args) > 0:
                Counter.count = args[0]
            if len(args) > 1:
                Counter.step = args[1]
        logging.debug('counting %s by %s', Counter.count, Counter.step)
        Counter.count += Counter.step
        return Counter.count

class FileInfo(Module):

    @classmethod
    def functions(cls):
        return {
            'name': {'func': cls.name, 'help': 'file name with extension, without path'},
            'path': {'func': cls.path, 'help': 'file path without file name'},
            'abspath': {'func': cls.abspath, 'help': 'absolute file path without file name'},
            'ext': {'func': cls.ext, 'help': 'file extension with leading dot'},
            'nam': {'func': cls.nam, 'help': 'file name without extension'},
            'size': {'func': cls.size, 'help': r'file size in bytes. Argument: [metric prefix k/m/g/t/p]. Example: {size[m]}'},
            'atime': {'func': cls.atime, 'help': r"file last access time. Argument: [python time format string]. Example: {atime['%Y']}"},
            'ctime': {'func': cls.ctime, 'help': r"file creation time. Argument: [python time format string]. Example: {ctime['%Y']}"},
            'mtime': {'func': cls.mtime, 'help': r"file last modification time. Argument: [python time format string]. Example: {mtime['%Y']}"},
        }

    @staticmethod
    def name(_, f, args):
        if not isinstance(f, str): f = f.path
        return Module.section(os.path.basename(f), args)
    @staticmethod
    def abspath(_, f, args):
        if not isinstance(f, str): f = f.path
        return Module.section(os.path.abspath(os.path.dirname(f)), args)
    @staticmethod
    def path(_, f, args):
        if not isinstance(f, str): f = f.path
        return Module.section(os.path.dirname(f), args)
    @staticmethod
    def ext(_, f, args):
        if not isinstance(f, str): f = f.path
        _, ext = os.path.splitext(f)
        return Module.section(ext, args)
    @staticmethod
    def nam(_, f, args):
        if not isinstance(f, str): f = f.path
        root, _ = os.path.splitext(os.path.basename(f))
        return Module.section(root, args)

    @staticmethod
    def size(_, f, args):
        if isinstance(f, str):
            s = os.stat(f).st_size
        else:
            s = f.stat().st_size
        if args is None:
            return s
        args = args[0]
        if args in 'kK': s = s / 1024
        elif args in 'mM': s = s / 1024 / 1024
        elif args in 'gG': s = s / 1024 / 1024 / 1024
        elif args in 'tT': s = s / 1024 / 1024 / 1024 / 1024
        elif args in 'pP': s = s / 1024 / 1024 / 1024 / 1024 / 1024
        return s

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


MODULES=[Text, Num, Counter, FileInfo, Conditions]
FUNCTIONS={}

def update():
    logging.debug('registering modules')
    for m in MODULES:
        logging.debug('... {0} ({1})'.format(m.__name__, ', '.join(m.functions())))
        FUNCTIONS.update(m.functions())

def list_functions():
    for m in MODULES:
        print('Module {0}:'.format(m.__name__))
        for k,v in m.functions().items():
            print('\t{0} - {1}'.format(k, v['help']))
        print()

