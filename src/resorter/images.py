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
            'exif_camera': {'func': cls.camera, 'help': r''},
            'exif_flash': {'func': cls.flash, 'help': r''},
            'exif_software': {'func': cls.software, 'help': r''},
            'exif_time': {'func': cls.time, 'help': r''},
            'exif_lon': {'func': cls.coo, 'help': r'GPS longitude'},
            'exif_lat': {'func': cls.coo, 'help': r'GPS latitude'},
            'exif_alt': {'func': cls.altitude, 'help': r'GPS altitude'},
            }

    @classmethod
    def open(cls, f):
        with open(f, 'rb') as fd:
            return exif.Image(fd)
    
    @staticmethod
    def get(f, s):
        image = Exif.cache(f)
        return image.get(s) if image.has_exif else None

    @staticmethod
    def coo(func, f, args):
        d,m,s = Exif.get(f, 'gps_'+func.lstrip('exif_'))
        return d + m/60 + s/3600

    @staticmethod
    def altitude(_, f, args):
        return Exif.get(f, 'gps_altitude')

    @staticmethod
    def camera(_, f, args):
        return Exif.get(f, 'camera') or 'UnknownCamera'

    @staticmethod
    def software(_, f, args):
        return Exif.get(f, 'software') or 'UnknownSoftware'

    @staticmethod
    def flash(_, f, args):
        return Exif.get(f, 'flash') or 'UnknownFlash'

    @staticmethod
    def time(_, f, args):
        date = Exif.get(f, 'datetime')
        if not date:
            return 'UnknownTime'
        date = datetime.datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
        return date.strftime('%d-%b-%Y.%H%M%S' if args is None else args)

if OK:
    modules.MODULES.append(Exif)
