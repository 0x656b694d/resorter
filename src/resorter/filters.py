import re

class Filter(object):
    def __init__(self):
        self.name = 'BaseFilter'

    def onStr(self, _):
        return True

    def onEntry(self, f):
        return self.onStr(f.path)

    def __call__(self, f):
        return (self.onStr if isinstance(f, str) else self.onEntry)(f)

class TrueFilter(Filter):
    def __init__(self):
        self.name = 'True'

class FalseFilter(Filter):
    def __init__(self):
        self.name = 'False'
    def onStr(self, _):
        return False

class RegexFilter(Filter):

    def __init__(self, e):
        self.regex = re.compile(e)
        self.name = 'RegexFilter'

    def onStr(self, f):
        return self.regex.fullmatch(f) is not None

