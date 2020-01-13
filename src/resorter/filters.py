import re
import logging
import resorter.utils as utils

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

class ExpressionFilter(Filter):
    def __init__(self, e, keywords):
        self.expr = utils.Expression(e, keywords)
        self.name = 'ExpressionFilter'

    def onEntry(self, source):
        logging.debug(f'{source}')
        return self.expr.calc(source)

