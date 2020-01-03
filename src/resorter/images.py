import exif
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
        return Exif.get(f, 'datetime') or 'UnknownTime'
modules.MODULES.append(Exif)
