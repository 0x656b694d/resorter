import exif
import datetime
import resorter.modules as modules

class Exif(modules.Module):

    @classmethod
    def keys(cls):
        return {
            'exif-camera': cls.camera,
            'exif-flash': cls.flash,
            'exif-software': cls.software,
            'exif-time': cls.time
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

modules.MODULES.append(Exif)
