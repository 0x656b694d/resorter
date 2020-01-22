import os
from datetime import datetime
import logging
import pathlib
from resorter.modules.modules import MODULES, Module

class FileInfo(Module):

    @classmethod
    def functions(cls):
        return {
                'name': {'func': cls.name, 'set': cls.setname, 'help': 'file name with extension, without path', 'example': 'name'},
                'path': {'func': cls.path, 'help': 'file path without file name', 'args': ['last parent index'], 'example': 'path[2]', 'source': 'a/b/c/name.ext'},
                'parent': {'func': cls.path, 'help': 'file path without file name', 'args': ['parent index'], 'example': 'parent[1]'},
                'abspath': {'func': cls.abspath, 'help': 'absolute file path without file name', 'example': 'abspath'},
                'ext': {'func': cls.ext, 'set': cls.setext, 'help': 'file extension with leading dot', 'example': 'ext'},
                'nam': {'func': cls.nam, 'set': cls.setnam, 'help': 'file name without extension', 'example': 'nam'},
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
    def setname(_, args):
        newname = os.path.join(os.path.dirname(args[0]), args[1])
        logging.debug(f'rename {args[0]} to {newname}')
        os.rename(args[0], newname)
        return newname

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
    def setext(_, args):
        root, _ = os.path.splitext(args[0])
        newname = root + args[1]
        logging.debug(f'rename {args[0]} to {newname}')
        os.rename(args[0], newname)
        return newname

    @staticmethod
    def nam(_, args):
        root, _ = os.path.splitext(os.path.basename(args[0]))
        return Module.slice(root, Module.range(args[1:]))
    @staticmethod
    def setnam(_, args):
        path, name = os.path.split(args[0])
        _, ext = os.path.splitext(name)
        newname = os.path.join(path, args[1] + ext)
        logging.debug(f'rename {args[0]} to {newname}')
        os.rename(args[0], newname)
        return newname

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

MODULES.append(FileInfo)
