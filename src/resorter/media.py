import logging
from pymediainfo import MediaInfo
import datetime
import resorter.modules as modules

class Media(modules.Module):

    @classmethod
    def keys(cls):
        return {
            'track': cls.track,
            } if MediaInfo.can_parse() else {}

    @classmethod
    def open(cls, f):
        return MediaInfo.parse(f.path)
    
    @staticmethod
    def track(_, f, args):
        logging.debug('reading %s from %s', args, f)
        media = Media.cache(f)
        logging.debug('found media %s', media)
        t = args.split(',', 1)
        if len(t) == 1:
            prop = t[0]
            n = None
        else:
            n, prop = t
        unknown = "Unknown"+prop.capitalize()
        for t in media.tracks:
            if t.track_id != n and t.track_type != n:
                continue
            return t.to_data().get(prop, unknown)
        return unknown

modules.MODULES.append(Media)
