try:
    from pymediainfo import MediaInfo
    OK = True
except:
    OK = False

import logging
import datetime
import resorter.modules as modules

class Media(modules.Module):

    @classmethod
    def functions(cls):
        return {
            'track': {'func': cls.track,
                'help': r'MediaInfo (https://mediaarea.net/en/MediaInfo) track data',
                'args': ['track id or type', 'property'], 'example': 'track["Video","format"]', 'source': 'demo.avi', 'output': 'MPEG-4 Visual'},
            } if MediaInfo.can_parse() else {}

    @classmethod
    def open(cls, f):
        return MediaInfo.parse(f)
    
    @staticmethod
    def track(_, args):
        media = Media.cache(args[0])
        logging.debug('found media %s', media)
        t = args[1:]
        if len(t) == 1:
            prop = t[0]
            n = None
        else:
            n, prop = t
        for t in media.tracks:
            if t.track_id != n and t.track_type != n:
                continue
            return t.to_data().get(prop, None)
        return None

if OK:
    modules.MODULES.append(Media)
