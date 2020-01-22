try:
    from PIL import Image
    OK = True
except:
    OK = False

import datetime
import logging
from resorter.modules.modules import MODULES, Module

EXIF_TAGS = {
  'make': 271,
  'model': 272,
  'software': 305,
  'lat': 0x8825,
  'lon': 0x8825,
  'alt': 0x8825,
  'speed': 0x8825,
  'time': 0x0132,
  'flash': 0x9209,
  'redeye': 0x9209,
  'distance': 0x9206,
  'gpstime': 0x8825,
  'orientation': 0x112,
}

FLASH = {
# 0x01 - fired/not fired
# 0x40 - red eye reduction
# 0x06 - return 5 - not detected 6 - detected
# 0x18 - 0x10 Off 0x18 Auto
    0x0 : 'No Flash', # 0000
    0x1 : 'Fired',    # 0001
    0x5 : 'Fired, Return not detected', # 0101
    0x7 : 'Fired, Return detected',     # 0111
    0x8 : 'On, Did not fire',           # 1000
    0x9 : 'On, Fired',                  # 1001
    0xd : 'On, Return not detected',    # 1100
    0xf : 'On, Return detected',        # 1111
    0x10: 'Off, Did not fire',          # 1 0000
    0x14: 'Off, Did not fire, Return not detected',
    0x18: 'Auto, Did not fire',
    0x19: 'Auto, Fired',                # 1 1001
    0x1d: 'Auto, Fired, Return not detected',
    0x1f: 'Auto, Fired, Return detected',
    0x20: 'No flash function',
    0x30: 'Off, No flash function',
    0x41: 'Fired, Red-eye reduction',   # 0100 0001
    0x45: 'Fired, Red-eye reduction, Return not detected',
    0x47: 'Fired, Red-eye reduction, Return detected',
    0x49: 'On, Red-eye reduction',
    0x4d: 'On, Red-eye reduction, Return not detected',
    0x4f: 'On, Red-eye reduction, Return detected',
    0x50: 'Off, Red-eye reduction',
    0x58: 'Auto, Did not fire, Red-eye reduction', # 0111 1000
    0x59: 'Auto, Fired, Red-eye reduction',
    0x5d: 'Auto, Fired, Red-eye reduction, Return not detected',
    0x5f: 'Auto, Fired, Red-eye reduction, Return detected',
}

def tags(cls):
    return dict(zip(['exif_'+k for k in EXIF_TAGS.keys()], [{'func': cls.exif, 'set': cls.setexif, 'help': 'EXIF '+k} for k in EXIF_TAGS.keys()]))

class ImageData(Module):
    ready = False

    @classmethod
    def functions(cls):
        if not cls.ready:
            cls.f = {
                'image_width': {'func': cls.width, 'help': r'pixel width'},
                'image_height': {'func': cls.height, 'help': r'pixel height'},
                'exif': {'func': cls.exif, 'help': r'True if the file has exif data'},
            }
            cls.f.update(tags(cls))
            cls.ready = True
        return cls.f

    @classmethod
    def open(cls, f):
        try:
            return Image.open(f)
        except Exception as e:
            logging.warning(e)
            return None

    @staticmethod
    def width(_, args):
        return ImageData.cache(args[0]).size[0]

    @staticmethod
    def height(_, args):
        return ImageData.cache(args[0]).size[1]

    @staticmethod
    def exif(key, args):
        i = ImageData.cache(args[0])
        if key=='exif':
            return True if i else False
        if i is None:
            return None
        key = key[5:]
        value = None
        if i:
            t = EXIF_TAGS.get(key, None)
            if t is not None:
                v = i.getexif().get(t, None)
                if v is not None:
                    value = ImageData.parse_exif(key, v, args)
        return value

    @staticmethod
    def setexif(key, args):
        i = ImageData.cache(args[0])
        if key=='exif':
            return True if i else False
        if i is None:
            return None
        key = key[5:]
        value = None
        if i:
            t = EXIF_TAGS.get(key, None)
            if t is not None:
                value = ImageData.write_exif(key, args)
        return value

    @staticmethod
    def parse_exif(key, value, args):
        if key == 'lat':
            ref = value.get(1, 'N') # N/S
            coo = value.get(2, None)
            if coo is None: return coo
            d,m,s = coo
            decimal = round((d[0]/d[1])+(m[0]/m[1])/60.0+(s[0]/s[1])/3600.0, 6)
            return decimal if ref == 'N' else -decimal
        elif key == 'lon':
            ref = value.get(3, 'E') # E/W
            coo = value.get(4, None)
            if coo is None: return coo
            d,m,s = coo
            decimal = round((d[0]/d[1])+(m[0]/m[1])/60.0+(s[0]/s[1])/3600.0, 6)
            return decimal if ref == 'E' else -decimal
        elif key == 'alt':
            logging.debug(value)
            ref = value.get(5, 0) # 1 - below sea level
            a = value.get(6, None)  #meters
            if a is None: return None
            a = round(a[0]/a[1], 2)
            return -a if ref else e
        elif key == 'speed':
            ref = value.get(12, 'K') # K/M/N
            s = value.get(13, None)
            if s is None: return s
            return ref + str(s)
        elif key == 'flash':
            return 'Yes' if value & 0x01 else 'No'
        elif key == 'redeye':
            return 'On' if value & 0x40 else 'Off'
        elif key == 'distance':
            return 'Inf' if value == 0xffffffff else 'Unknown' if value == 0 else value
        elif key == 'gpstime':
            d = value.get(29, None)
            if not d: return None
            h, m, s = value.get(7, ([0,0])*3)
            h = h[0]/h[1]
            m = m[0]/m[1]
            s = s[0]/s[1]
            y,mon,d = d.split(':')
            date = datetime.datetime(*(int(x) for x in [y, mon, d, h, m, s]))
            return date.strftime(args[1]) if len(args) == 2 else date
        elif key == 'time':
            date = datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
            return date.strftime(args[1]) if len(args) == 2 else date
        elif key == 'orientation':
            return value
        if isinstance(value, str): return value.strip()
        return value

if OK:
    MODULES.append(ImageData)
