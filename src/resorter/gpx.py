import resorter.actions as actions
import resorter.utils as utils
import resorter.modules as modules


class Gpx(actions.Action):
    def __init__(self, dry=False):
        self.dry = dry
        self.trk_expr = utils.Expression(
            r'exif_lat.str/exif_lon.str/'
            r'if(exif_time<>"NoTime",exif_time["%Y-%m-%dT%H:%M:%SZ"],ctime["%Y-%m-%dT%H:%M:%SZ"])'
            r'/exif_alt.str'
            , modules.FUNCTIONS)
        print(r'<?xml version="1.0" encoding="UTF-8" standalone="no" ?>')
        print(r'<gpx xmlns="http://www.topografix.com/GPX/1/1" '
              r'version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
              r'creator="resorter" '
              r'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">')
        print(r'<time></time>')
        print(r'<metadata><name>Name</name></name></metadata>')
        print(r'<trk>')
        self.state = 0
    def act(self, source, dst):
        if not self.state:
            print(r'<trkseg>')
        lat, lon, tim, alt = self.trk_expr.calc(source).split('/')
        print(f'<trkpt lat="{lat}" lon="{lon}">'
              f'  <time>{tim}</time>'
              f'  <ele>{alt}</ele></trkpt>')
        self.state = 1

    def finalize(self):
        if self.state: print(r'</trkseg>')
        print(r'</trk>')
        print(r'</gpx>')

actions.ACTIONS.update({'gpx': {'class': Gpx, 'help':'export gpx track'}})
