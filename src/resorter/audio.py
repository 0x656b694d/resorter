import stagger

import resorter.modules as modules

class Id3(modules.Module):

    @classmethod
    def keys(cls):
        return {
            'id3-composer': {'func': cls.tag, 'help': r'composer'},
            'id3-title': {'func': cls.tag, 'help': r'title'},
            'id3-album': {'func': cls.tag, 'help': r'album'},
            'id3-artist': {'func': cls.tag, 'help': r'artist'},
            'id3-genre': {'func': cls.tag, 'help': r'genre'},
            'id3-disc': {'func': cls.tag, 'help': r'disc'},
            'id3-track': {'func': cls.tag, 'help': r'track'},
        }
    
    @classmethod
    def open(cls, f):
        return stagger.read_tag(f.path)
    
    @staticmethod
    def tag(key, f, args):
        id3 = Id3.cache(f)
        return id3.__getattribute__(key.lstrip('id3-'))

modules.MODULES.append(Id3)
