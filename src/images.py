import exif
import modules

class Exif(modules.Module):

    F = (None, None)

    @classmethod
    def keys(cls):
        return {
            'exif-camera': cls.camera,
            'exif-flash': cls.flash,
            'exif-software': cls.software,
            'exif-time': cls.time
            }

    @staticmethod
    def cache(f):
        if f != Exif.F[0]:
            with open(f, 'rb') as fd:
                Exif.F = (f, exif.Image(fd))
        return Exif.F[1]

    @staticmethod
    def get(f, s):
        image = Exif.cache(f)
        return Exif.F[1].get(s) if Exif.F[1].has_exif else None

    @staticmethod
    def camera(f, args):
        return Exif.get(f, 'camera') or 'UnknownCamera'

    @staticmethod
    def software(f, args):
        return Exif.get(f, 'software') or 'UnknownSoftware'

    @staticmethod
    def flash(f, args):
        return Exif.get(f, 'flash') or 'UnknownFlash'

    @staticmethod
    def time(f, args):
        return Exif.get(f, 'datetime') or 'UnknownTime'
modules.MODULES.append(Exif)
