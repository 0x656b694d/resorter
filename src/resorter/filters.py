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

class RegexFilter(Filter):

    def __init__(self, e):
        self.regex = re.compile(e)
        self.name = 'RegexFilter'

    def onStr(self, f):
        return self.regex.fullmatch(f) is not None

class ExpressionFilter(Filter):
    def __init__(self, e, keywords):
        self.polish, value = utils.split(e, '', keywords)
        op = ''
        for ch in value:
            if ch in '=<>~':
                op += ch
            else: break
        self.op = op
        self.value = value[len(op):]
        if op == '~':
            self.value = re.compile(self.value)

        self.name = 'ExpressionFilter'

    def onEntry(self, source):
        value = self.polish.calc(source)
        logging.debug('value %s', value)
        if self.op == '~':
            return self.value.fullmatch(value)
        value = type(self.value)(value)
        if self.op in '==':
            return value == self.value
        if self.op == '>=':
            return value >= self.value
        if self.op == '<=':
            return value <= self.value
        if self.op == '>':
            return value > self.value
        if self.op == '<':
            return value < self.value

