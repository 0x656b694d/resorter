import re

class Filter(object):
    def onStr(self, _):
        return True

    def onEntry(self, f):
        return self.onStr(f.path)

    def __call__(self, f):
        return (self.onStr if isinstance(f, str) else self.onEntry)(f)

class RegexFilter(Filter):

    def __init__(self, e):
        self.regex = re.compile(e)

    def onStr(self, f):
        return self.regex.fullmatch(f) is not None

