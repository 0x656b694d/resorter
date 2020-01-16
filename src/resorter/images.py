try:
    import exifread
    OK = True
except:
    OK = False

import datetime
import resorter.modules as modules

exif_tags = {
        'software': 'EXIF Software',
        'time': 'EXIF DateTime',
        'width': 'EXIF ImageWidth',
        'height': 'EXIF ImageLength',
        'flash': 'EXIF Flash',

        'make': 'Image Make',
        'model': 'Image Model',

        'lon': 'GPS GPSLongitude',
        'lat': 'GPS GPSLatitude',
        'alt': 'GPS GPSAltitude',
        }

class Exif(modules.Module):

    @classmethod
    def functions(cls):
        return {
            'exif_make': {'func': cls.generic, 'help': r'the camera maker'},
            'exif_model': {'func': cls.generic, 'help': r'the camera model'},
            'exif_flash': {'func': cls.generic, 'help': r'flash info'},
            'exif_software': {'func': cls.generic, 'help': r'editing software'},
            'exif_time': {'func': cls.time, 'help': r'image timestamp'},
            'exif_lon': {'func': cls.coo, 'help': r'GPS longitude'},
            'exif_lat': {'func': cls.coo, 'help': r'GPS latitude'},
            'exif_alt': {'func': cls.generic, 'help': r'GPS altitude'},
            'exif_width': {'func': cls.generic, 'help': r'pixel width'},
            'exif_height': {'func': cls.generic, 'help': r'pixel height'},
            }

    @classmethod
    def open(cls, f):
        try:
            with open(f, 'rb') as fd:
                return exifread.process_file(fd)
        except:
            return None
    
    @staticmethod
    def get(f, s):
        image = Exif.cache(f)
        if not image: return None
        value = image.get(s, None)
        return value

    @staticmethod
    def generic(key, args):
        return Exif.get(args[0], exif_tags[key[5:]]) or 'No'+key[5:].capitalize()

    @staticmethod
    def coo(key, args):
        e = Exif.get(args[0], exif_tags[key[5:]])
        if e is None:
            return 'No'+key[5:].capitalize()
        d,m,s = e
        return d + m/60 + s/3600

    @staticmethod
    def time(_, args):
        date = Exif.get(args[0], exif_tags[key[5:]])
        if date is None:
            return 'UnknownTime'
        date = datetime.datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
        if len(args)>1:
            return date.strftime(args[1])
        return date.strftime('%d-%b-%Y.%H%M%S')

if OK:
    modules.MODULES.append(Exif)
