try:
    import stagger
    OK = True
except:
    OK = False

import resorter.modules as modules

class Id3(modules.Module):

    @classmethod
    def functions(cls):
        return {
            'id3_composer': {'func': cls.tag, 'help': r'composer'},
            'id3_title': {'func': cls.tag, 'help': r'title'},
            'id3_album': {'func': cls.tag, 'help': r'album'},
            'id3_artist': {'func': cls.tag, 'help': r'artist'},
            'id3_genre': {'func': cls.tag, 'help': r'genre'},
            'id3_disc': {'func': cls.tag, 'help': r'disc'},
            'id3_track': {'func': cls.tag, 'help': r'track'},
        }
    
    @classmethod
    def open(cls, source):
        return stagger.read_tag(source.path)
    
    @staticmethod
    def tag(func, source, args):
        id3 = Id3.cache(source)
        return id3.__getattribute__(func.lstrip('id3_'))

if OK:
    modules.MODULES.append(Id3)
