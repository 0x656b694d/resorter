import os
import re
from datetime import datetime
import logging
import codecs
import pathlib
import subprocess
import resorter.utils

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
                'round': {'func': cls.round, 'help': r'round a number', 'args': ['precision'], 'example': '(len(path)/len(name)).round[1]'},
                'num': {'func': cls.number, 'help': r'convert string to an number', 'args': ['precision'], 'example': 'name[4,6].num', 'source': 'doc_12.jpg'},
                }
    @staticmethod
    def number(_, args):
        if len(args) > 1: return round(_, args)
        n = args[0]
        n = (float if '.' in n else int)(n) if isinstance(n, str) else n
        return n

    @staticmethod
    def round(_, args):
        n = args[0]
        n = (float if '.' in n else int)(n) if isinstance(n, str) else n
        p = int(args[1]) if len(args) > 1 else 0
        return round(n, p) if p else round(n)

class Conditions(Module):
    @classmethod
    def functions(cls):
        return {
                'if': {'func': cls.eef, 'help': r'if-else condition', 'args': ['condition', 'true value', 'false value'], 'example': 'if(len(name)>8,"long","short")'},
                'any': {'func': cls.aany, 'help': r'true if any of arguments is true', 'args': ['condition', '...']},
                'all': {'func': cls.aall, 'help': r'true if all of arguments are true', 'args': ['condition', '...']},
                'in': {'func': cls.een, 'help': r'check agains a list of options', 'args': ['option', '...'], 'example': 'ext.in(".ext",".xls")'},
                'not': {'func': cls.noot, 'help': r'negation', 'args': ['condition'], 'example': 'not(ext==".jpg")'},
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

class List(Module):
    @classmethod
    def functions(cls):
        return {
            'join': {'func': cls.join, 'help': r'join list', 'args': ['separator'], 'example': '(nam,ext).join("-")'},
            'split': {'func': cls.split, 'help': r'split string', 'args': ['separator'], 'example': 'path.split["/"]'},
            }
    @staticmethod
    def join(_, args):
        sep = args[1] if len(args) == 2 else '-'
        return sep.join(str(a) for a in args[0])
    @staticmethod
    def split(_, args):
        sep = args[1] if len(args) == 2 else os.sep
        return args[0].split(sep)

class Text(Module):
    @classmethod
    def functions(cls):
        return {
            'cap': {'func': cls.cap, 'help': r'capitalize', 'example': 'name.cap'},
            'low': {'func': cls.low, 'help': r'lower case', 'example': 'name.low'},
            'up': {'func': cls.up, 'help': r'upper case', 'example': 'name.up'},
            'title': {'func': cls.title, 'help': r'title case', 'example': 'name.title'},
            'replace': {'func': cls.replace, 'help': r'replace substrings', 'args': ['from','to'], 'example': "name.replace['am','ik']"},
            'sub': {'func': cls.sub, 'help': r'substring', 'argument': ['from', 'to'], 'example': 'name.sub[0,4]'},
            'index': {'func': cls.index, 'help': r'position of a substring', 'argument': ['substring'], 'example': 'name.sub[0,name.index["e"]]'},
            'len': {'func': cls.length, 'help': r'length of a substring', 'example': 'name[5,len(name)]'},
            'str': {'func': cls.string, 'help': r'convert to string', 'example': 'len(name).str'},
        }

    @staticmethod
    def string(_, args):
        return str(args[0])

    @staticmethod
    def sub(_, args):
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
            'counter': {'func': cls.counter, 'help': r'counting number', 'args': ['start', 'step'], 'example': 'nam+"_"+counter[100,10].str+ext'}
        }

    @staticmethod
    def counter(_, args):
        if Counter.count is None:
            Counter.count = 0
            if len(args) > 1:
                Counter.count = args[1]
            if len(args) > 2:
                Counter.step = args[2]
        else:
            Counter.count += Counter.step
        return Counter.count

class FileInfo(Module):

    @classmethod
    def functions(cls):
        return {
                'name': {'func': cls.name, 'help': 'file name with extension, without path', 'example': 'name'},
                'path': {'func': cls.path, 'help': 'file path without file name', 'args': ['last parent index'], 'example': 'path[2]', 'source': 'a/b/c/name.ext'},
                'parent': {'func': cls.path, 'help': 'file path without file name', 'args': ['parent index'], 'example': 'parent[1]'},
                'abspath': {'func': cls.abspath, 'help': 'absolute file path without file name', 'example': 'abspath'},
                'ext': {'func': cls.ext, 'help': 'file extension with leading dot', 'example': 'ext'},
                'nam': {'func': cls.nam, 'help': 'file name without extension', 'example': 'nam'},
                'size': {'func': cls.size, 'help': r'file size in bytes', 'args': ['metric prefix k/m/g/t/p'], 'example': 'size[m]', 'output': 42},
                'atime': {'func': cls.atime, 'help': r'file last access time', 'args': ['python time format string'], 'example': "atime['%Y']", 'output': '2019'},
                'ctime': {'func': cls.ctime, 'help': r'file creation time', 'args': ['python time format string'], 'example': "ctime['%Y']", 'output': '2019'},
                'mtime': {'func': cls.mtime, 'help': r'file last modification time', 'args': ['python time format string'], 'example': "mtime['%Y']", 'output': '2019'},
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
        if len(args)>1:
            p = os.sep.join(pathlib.PurePath(args[0]).parts[-args[1]-1:-1])
        else:
            p = os.path.dirname(args[0])
        return p
    @staticmethod
    def parent(_, args):
        if len(args)>1:
            p = pathlib.PurePath(args[0]).parts[-args[1]-1]
        else:
            p = os.path.basename(os.path.dirname(args[0]))
        return p
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
    def get_time(st_t, fmt):
        t = datetime.fromtimestamp(st_t)
        fmt = fmt[1] if len(fmt) == 2 else None
        return t.strftime(fmt) if fmt else t

    @staticmethod
    def atime(_, args):
        return FileInfo.get_time(FileInfo.cache(args[0]).st_atime, args)

    @staticmethod
    def mtime(_, args):
        return FileInfo.get_time(FileInfo.cache(args[0]).st_mtime, args)

    @staticmethod
    def ctime(_, args):
        return FileInfo.get_time(FileInfo.cache(args[0]).st_ctime, args)

class Custom(Module):
    
    funcs = {}

    @classmethod
    def functions(cls):
        return cls.funcs

    @staticmethod
    def call(key, args):
        script = Custom.funcs[key]['help']
        logging.debug(f'calling {key}: {script} {args}')
        p = subprocess.run([script]+[os.fsencode(a) for a in args], stdout=subprocess.PIPE, check=True)# python 3.8: capture_output=True)
        return p.stdout.decode().replace('\n', '').replace('\r', '')

MODULES=[Text, Num, List, Counter, FileInfo, Conditions, Custom]
FUNCTIONS={}

def example(f):
    source = f.get('source', 'some/path/name.ext')
    args = f.get('args', None)
    text = ''
    if args: text += f'. Arguments: {args}'
    ex = f.get('example', None)
    if ex:
        result = f.get('output', None) or resorter.utils.Expression(ex, FUNCTIONS).calc(source)
        text += f'. Example: {source} -> {ex} -> {result}'
    return text

def update():
    logging.debug('registering modules')
    for m in MODULES:
        logging.debug('... {0} ({1})'.format(m.__name__, ', '.join(m.functions())))
        FUNCTIONS.update(m.functions())

def append(scripts):
    for script in scripts:
        name, _ = os.path.splitext(os.path.basename(script))
        logging.debug(f'custom script {name}: {script}')
        Custom.funcs[name] = {'func': Custom.call, 'help': script}

def list_functions(verbose):
    for m in MODULES:
        if not m.functions():
            continue
        print(m.__name__)
        for k,v in m.functions().items():
            text = f'\t{k} - {v["help"]}'
            if verbose:
                text += example(v)
            print(text)
        print()

