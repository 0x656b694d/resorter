try:
    import exif
    OK = True
except:
    OK = False

import datetime
import resorter.modules as modules

class Exif(modules.Module):

    @classmethod
    def functions(cls):
        return {
            'exif_make': {'func': cls.camera, 'help': r''},
            'exif_model': {'func': cls.camera, 'help': r''},
            'exif_flash': {'func': cls.flash, 'help': r''},
            'exif_software': {'func': cls.software, 'help': r''},
            'exif_time': {'func': cls.time, 'help': r''},
            'exif_lon': {'func': cls.coo, 'help': r'GPS longitude'},
            'exif_lat': {'func': cls.coo, 'help': r'GPS latitude'},
            'exif_alt': {'func': cls.altitude, 'help': r'GPS altitude'},
            }

    @classmethod
    def open(cls, f):
        try:
            with open(f, 'rb') as fd:
                return exif.Image(fd)
        except:
            return None
    
    @staticmethod
    def get(f, s):
        image = Exif.cache(f)
        return image.get(s) if image and image.has_exif else None

    @staticmethod
    def coo(func, args):
        e = Exif.get(args[0], 'gps_'+func.lstrip('exif_'))
        if not e: return 'NoGPS'
        d,m,s = e
        return d + m/60 + s/3600

    @staticmethod
    def altitude(_, args):
        return Exif.get(args[0], 'gps_altitude')

    @staticmethod
    def camera(key, args):
        key = key[len('exif_'):]
        value = Exif.get(args[0], key)
        return value.strip() if value else 'Unknown'+key.capitalize()

    @staticmethod
    def software(_, args):
        return Exif.get(args[0], 'software') or 'UnknownSoftware'

    @staticmethod
    def flash(_, args):
        return Exif.get(args[0], 'flash') or 'UnknownFlash'

    @staticmethod
    def time(_, args):
        date = Exif.get(args[0], 'datetime')
        if not date:
            return 'UnknownTime'
        date = datetime.datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
        if args:
            return date.strftime(args[0])
        return date.strftime('%d-%b-%Y.%H%M%S')

if OK:
    modules.MODULES.append(Exif)
