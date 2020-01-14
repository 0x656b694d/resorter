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
        a, b = 0, None
        if args is None:
            return (a, b)
        if len(args) > 0:
            if args[0]:
                a = int(args[0])
            b = a + 1
        if len(args) > 1 and args[1]:
            b = int(args[1])
        return (a, b)

    @staticmethod
    def slice(s, rng):
        if rng is None: return s
        a, b = rng
        return s[a:b]

class Num(Module):
    @classmethod
    def functions(cls):
        return {
            'round': {'func': cls.number, 'help': r'round a number. Argument: [precision]. Example: {size[k].round[1]}'},
            'num': {'func': cls.number, 'help': r'convert string to an number. Argument: [precision]'},
        }
    @staticmethod
    def number(_, args):
        n = (float if '.' in args[0] else int)(args[0])
        p = int(args[1]) if len(args) > 1 else 0
        return round(n, p) if p else round(n)

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
    def eef(_, args):
        if len(args) == 3:
            return args[1] if args[0] else args[2]
        return args[2] if args[1] else args[3]
    @staticmethod
    def aany(_, args):
        return any(args[1:])
    @staticmethod
    def aall(_, args):
        return all(args[1:])
    @staticmethod
    def een(_, args):
        return args[0] in args[1:]
    @staticmethod
    def noot(_, args):
        return not args[-1]

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
            'len': {'func': cls.length, 'help': r'length of a substring. Example: name[5,len(name)]'},
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
    def sub(_, args):
        logging.debug(f'{args}')
        return Module.slice(args[0], Module.range(args[1:]))
    @staticmethod
    def index(_, args):
        result = -1
        for arg in args[1:]:
            result = args[0].find(str(arg))
            if result != -1:
                break
        return result

    @staticmethod
    def cap(_, args):
        return args[0].capitalize()
    @staticmethod
    def low(_, args):
        return args[0].lower()
    @staticmethod
    def up(_, args):
        return args[0].upper()
    @staticmethod
    def title(_, args):
        return args[0].title()
    @staticmethod
    def replace(_, args):
        return args[0].replace(*args[1:])
    @staticmethod
    def decode(_, args):
        return codecs.decode(*args)

    @staticmethod
    def length(_, args):
        return len(args[0])

class Counter(Module):
    count = None
    step = 1

    @classmethod
    def functions(cls):
        return {
            'counter': {'func': cls.counter, 'help': r'counting number. Arguments: [start,step]. Example: {nam}_{counter[100,10]}{ext}'}
        }

    @staticmethod
    def counter(_, args):
        if Counter.count is None:
            Counter.count = 0
            if len(args) > 1:
                Counter.count = args[1]
            if len(args) > 2:
                Counter.step = args[2]
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

    @classmethod
    def open(cls, f):
        return os.stat(f)

    @staticmethod
    def name(_, args):
        return Module.slice(os.path.basename(args[0]), Module.range(args[1:]))
    @staticmethod
    def abspath(_, args):
        return Module.slice(os.path.abspath(os.path.dirname(args[0])), Module.range(args[1:]))
    @staticmethod
    def path(_, args):
        return Module.slice(os.path.dirname(args[0]), Module.range(args[1:]))
    @staticmethod
    def ext(_, args):
        _, ext = os.path.splitext(args[0])
        return Module.slice(ext, Module.range(args[1:]))
    @staticmethod
    def nam(_, args):
        root, _ = os.path.splitext(os.path.basename(args[0]))
        return Module.slice(root, Module.range(args[1:]))

    @staticmethod
    def size(_, args):
        s = FileInfo.cache(args[0]).st_size
        if len(args) == 1:
            return s
        args = args[1]
        if args in 'kK': s = s / 1024
        elif args in 'mM': s = s / 1024 / 1024
        elif args in 'gG': s = s / 1024 / 1024 / 1024
        elif args in 'tT': s = s / 1024 / 1024 / 1024 / 1024
        elif args in 'pP': s = s / 1024 / 1024 / 1024 / 1024 / 1024
        return s

    @staticmethod
    def atime(_, args):
        s = FileInfo.cache(args[0])
        t = time.localtime(s.st_atime)
        return time.strftime('%d-%b-%Y %H-%M-%S' if len(args)<2 else args[1], t)
    @staticmethod
    def mtime(_, args):
        s = FileInfo.cache(args[0])
        t = time.localtime(s.st_mtime)
        return time.strftime('%d-%b-%Y %H-%M-%S' if len(args)<2 else args[1], t)
    @staticmethod
    def ctime(_, args):
        s = FileInfo.cache(args[0])
        t = time.localtime(s.st_ctime)
        return time.strftime('%d-%b-%Y %H-%M-%S' if len(args)<2 else args[1], t)

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

