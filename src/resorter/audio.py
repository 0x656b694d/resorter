import stagger

import resorter.modules as modules

class Id3(modules.Module):

    @classmethod
    def keys(cls):
        return {
            'id3-composer': cls.tag,
            'id3-title': cls.tag,
            'id3-album': cls.tag,
            'id3-artist': cls.tag,
            'id3-genre': cls.tag,
            'id3-disc': cls.tag,
            'id3-track': cls.tag
        }
    
    @classmethod
    def open(cls, f):
        return stagger.read_tag(f.path)
    
    @staticmethod
    def tag(key, f, args):
        id3 = Id3.cache(f)
        return id3.__getattribute__(key.lstrip('id3-'))

modules.MODULES.append(Id3)
