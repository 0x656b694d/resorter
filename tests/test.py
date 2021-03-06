import unittest
import os
import logging

import resorter.utils
from resorter.modules import modules

def ask_test(msg, opts, default=None):
    return default

class TestPolish(unittest.TestCase):
    def test_arithmetics(self):
            
        exprs = [
                ('2+3', [ ['NUMBER', 2], ['NUMBER', 3], ['OP', '+']]),
                ('2+3*4', [ ['NUMBER', 2], ['NUMBER', 3], ['NUMBER', 4], ['OP', '*'], ['OP', '+']]),
                ('(2+3)*4', [ ['NUMBER', 2], ['NUMBER', 3], ['OP', '+'],  ['NUMBER', 4], ['OP', '*']]),
                ('7-(2+3)*4', [ ['NUMBER', 7], ['NUMBER', 2], ['NUMBER', 3], ['OP', '+'],  ['NUMBER', 4], ['OP', '*'], ['OP', '-']]),
                ('-1', [ ['NUMBER', 1], ['OP', '--'] ]),
                ('2*(-1)', [ ['NUMBER', 2], ['NUMBER', 1], ['OP', '--'], ['OP', '*']]),
                ('2|5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '|']]),
                ('2&5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '&']]),
                ('2>5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '>']]),
                ('2<5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '<']]),
                ('2=5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '=']]),
                ('2==5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '==']]),
                ('2!=5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '!=']]),
                ('2<>5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '<>']]),
                ('2>=5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '>=']]),
                ('2<=5', [ ['NUMBER', 2], ['NUMBER', 5], ['OP', '<=']]),
                ('(func.fanc==15)||(68>fanc)', [ ['ID', 'func'], ['ID', 'fanc'], ['OP', '.'], ['NUMBER', 15], ['OP', '=='], ['NUMBER', 68], ['ID', 'fanc'], ['OP', '>'], ['OP', '||']]),
            ]
        for expr, expected in exprs:
            tokens = resorter.utils.tokenize(expr, [])
            polish = resorter.utils.polish(tokens)
            self.assertEqual(polish, expected)

    def test_func(self):
        exprs = [
                ('func', [ ['FUNC', resorter.utils.Func('func')] ]),
                ('func+2', [
                    ['FUNC', resorter.utils.Func('func')],
                    ['NUMBER', 2],
                    ['OP', '+'],
                    ]),
                ('func[3]+2', [
                    ['NUMBER', 3],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('func')],
                    ['NUMBER', 2],
                    ['OP', '+'],
                    ]),
                ('func[(3-4)]+2', [
                    ['NUMBER', 3],
                    ['NUMBER', 4],
                    ['OP', '-'],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('func')],
                    ['NUMBER', 2],
                    ['OP', '+'],
                    ]),
                ('func+func', [
                    ['FUNC', resorter.utils.Func('func')],
                    ['FUNC', resorter.utils.Func('func')],
                    ['OP', '+'],
                    ]),
                ('func.fonc', [
                    ['FUNC', resorter.utils.Func('func')],
                    ['FUNC', resorter.utils.Func('fonc')],
                    ['OP', '.'],
                    ]),
                ('func[2+3].fonc', [
                    ['NUMBER', 2],
                    ['NUMBER', 3],
                    ['OP', '+'],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('func')],
                    ['FUNC', resorter.utils.Func('fonc')],
                    ['OP', '.'],
                    ]),
                ('func.fonc[2+3]', [
                    ['FUNC', resorter.utils.Func('func')],
                    ['NUMBER', 2],
                    ['NUMBER', 3],
                    ['OP', '+'],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('fonc')],
                    ['OP', '.'],
                    ]),
                ('func[2+3].fonc[2+3]', [
                    ['NUMBER', 2],
                    ['NUMBER', 3],
                    ['OP', '+'],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('func')],
                    ['NUMBER', 2],
                    ['NUMBER', 3],
                    ['OP', '+'],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('fonc')],
                    ['OP', '.'],
                    ]),
                ('func[2+3]*fonc[2+3]', [
                    ['NUMBER', 2],
                    ['NUMBER', 3],
                    ['OP', '+'],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('func')],
                    ['NUMBER', 2],
                    ['NUMBER', 3],
                    ['OP', '+'],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('fonc')],
                    ['OP', '*'],
                    ]),
                ('func[2+3/fonc(4-5,6*7)]', [
                    ['NUMBER', 2],
                    ['NUMBER', 3],
                    ['NUMBER', 4],
                    ['NUMBER', 5],
                    ['OP', '-'],
                    ['NUMBER', 6],
                    ['NUMBER', 7],
                    ['OP', '*'],
                    ['OP', ','],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('fonc')],
                    ['OP', '/'],
                    ['OP', '+'],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('func')],
                    ]),
                ('func(2+fanc.fonc[4-5,6*7])', [
                    ['NUMBER', 2],
                    ['FUNC', resorter.utils.Func('fanc')],
                    ['NUMBER', 4],
                    ['NUMBER', 5],
                    ['OP', '-'],
                    ['NUMBER', 6],
                    ['NUMBER', 7],
                    ['OP', '*'],
                    ['OP', ','],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('fonc')],
                    ['OP', '.'],
                    ['OP', '+'],
                    ['ARGS', None],
                    ['FUNC', resorter.utils.Func('func')],
                    ]),
            ]
        for expr, expected in exprs:
            tokens = resorter.utils.tokenize(expr, ['func','fonc','fanc'])
            polish = resorter.utils.polish(tokens)
            self.assertEqual(expected, polish)

def process(files, expr, ask):
    expr = resorter.utils.Expression(expr, modules.FUNCTIONS)
    for source in files:
        yield (source, expr.calc(source))
    return True

def test_all(test, names, expressions):
    files = list(resorter.utils.read_filenames(names, False))
    for expr,expected in expressions:
        for source,dest in process(files, expr, ask_test):
            test.assertEqual(expected, dest)

class TestModule(modules.Module):
    tester = None
    called_get = False
    called_set = False

    @staticmethod
    def init(tester):
        TestModule.tester = tester
        TestModule.called_get = False
        TestModule.called_set = False

    @classmethod
    def functions(cls):
        return { 'test': { 'func': cls.get, 'set': cls.set, 'help': 'test' } }

    @staticmethod
    def get(key, args):
        TestModule.tester.assertEqual(key, 'test')
        TestModule.called_get = True
        return args[-1]

    @staticmethod
    def set(key, args):
        TestModule.tester.assertEqual(key, 'test')
        TestModule.called_set = True
        return args[-1]

modules.MODULES.append(TestModule)

class TestFunctions(unittest.TestCase):
    def test_simple(self):
        modules.Set.allowed = False
        TestModule.init(self)
        name = 'path/name.ext'
        expressions = [
            (r'test', name),
            (r'test("abc")', 'abc'),
            (r'test.set("xyz")', None),
            ]
        test_all(self, [name], expressions)
        self.assertTrue(TestModule.called_get)
        self.assertFalse(TestModule.called_set)
    
    def test_allowed(self):
        TestModule.init(self)
        name = 'path/name.ext'
        expressions = [
            (r'test', name),
            (r'test("abc")', 'abc'),
            (r'test.set("xyz")', 'xyz'),
            ]
        modules.Set.allowed = True
        test_all(self, [name], expressions)
        self.assertTrue(TestModule.called_get)
        self.assertTrue(TestModule.called_set)
        modules.Set.allowed = False

    def test_lazy(self):
        TestModule.init(self)
        name = 'path/name.ext'
        expressions = [
            (r'if(nam=="name",test.set("xyz"),none)', 'xyz'),
            ]
        modules.Set.allowed = True
        test_all(self, [name], expressions)
        self.assertFalse(TestModule.called_get)
        self.assertTrue(TestModule.called_set)

        TestModule.init(self)
        expressions = [
            (r'if(nam=="xxx",test.set("xyz"),none)', None),
            (r'if(nam=="name",none,test.set("xyz"))', None),
            ]
        test_all(self, [name], expressions)
        self.assertFalse(TestModule.called_get)
        self.assertFalse(TestModule.called_set)
        modules.Set.allowed = False


class TestExpressions(unittest.TestCase):
    def test_abs_name(self):
        name = '/abs/path/name.ext'
        expressions = [
                (r'{name}', 'name.ext'),
                (r'{path}', '/abs/path'),
                (r'{ext}', '.ext'),
                (r'{nam}', 'name'),
                (r'{abspath}', '/abs/path'),
                ]
        test_all(self, [name], expressions)
    
    def test_hidden_name(self):
        name = 'rel/path/.name'
        expressions = [
                (r'{path}', 'rel/path'),
                (r'{name}', '.name'),
                (r'{ext}', ''),
                (r'{nam}', '.name'),
                (r'{abspath}', os.path.abspath(os.path.curdir) + '/rel/path'),
                ]
        test_all(self, [name], expressions)

    def test_list(self):
        name = 'some/path/filename.ext'
        expressions = [
                (r'path.split', ['some','path']),
                (r'path.split["e"]', ['som','/path']),
                (r'(path,ext).join["x"]', 'some/pathx.ext'),
                (r'(path,ext).join', 'some/path-.ext'),
                ]
        test_all(self, [name], expressions)

    def test_text(self):
        name = 'some_PATH string'
        expressions = [
                (r'name', name),
                (r'name.up', 'SOME_PATH STRING'),
                (r'name.low', 'some_path string'),
                (r'name.cap', 'Some_path string'),
                (r'name.title', 'Some_Path String'),
                (r'name.sub[1,4]', 'ome'),
                (r'name.sub[4]', '_'),
                (r'name.replace[" ","_"]', 'some_PATH_string'),
                (r'name.replace["PATH","xxx"]', 'some_xxx string'),
                (r'name.index["PATH"]', 5),
                (r'name.len', len(name)),
                (r'name[len(name)-6, len(name)]', 'string'),
                (r'name:len+xx', name+str(len(name))+'xx'),
                (r'/name', '/'+name),
                ]
        test_all(self, [name], expressions)

    def test_num(self):
        name = 'path/some_42.65_'
        expressions = [
                (r'{name.index[4]}', 5),
                (r'{name.sub[name.index[4]]}', '4'),
                (r'{name.sub[5,10].round}', 43),
                (r'{name.sub[5,10].round[2]}', 42.65),
                (r'{name.sub[5,10].num-1.5}', 41.15),
                (r'{name.sub[5,10].num+1.5}', 44.15),
                (r'{(name[5,10].round-1)%4}', 2),
                (r'{(name[5,10].round-1)/6}', 7.0),
                (r'{(name[5,10].round-1)/6^2}', 49.0),
                (r'{name[0,4]+path}', 'somepath'),
                (r'{name[0,4]/path}', 'some/path'),
                (r'{name[5,7].num+name[8,10].num}', 107),
                (r'{2^3}', 8),
                (r'{-2^3}', -8),
                ]
        test_all(self, [name], expressions)

    def test_conditions(self):
        name = 'Hello'
        expressions = [
                (r'name.in("Goodbye","Hello","Hi")', True),
                (r'name.in("Goodbye","Hi")', False),
                (r'all("Goodbye",name=="Hello")', True),
                (r'any("Goodbye",name=="xx")', True),
                (r'not(name=="xx")', True),
                (r'if(name=="Hello", 12, 14)', 12),
                (r'if(name~="H.l+o", 12, 14)', 12),
                (r'if(name=="Hlo", 12, 14)', 14),
                (r'if(name=="Hlo", 12)', name),
                (r'if(name=="Hello", 12)', 12),
                (r'if(name=="Hlo")', None),
                (r'if(name=="Hello")', name),
                (r'name.if(name=="Hello")', name),
                (r'name.if(name!="Hello")', None),
                (r'name.if(name=="Hello", 15)', 15),
                (r'name.if(name!="Hello", 15)', name),
                ]
        test_all(self, [name], expressions)

    def test_comp(self):
        expressions = [
                (r'2=3', False),
                (r'2=2', True),
                (r'2<>2', False),
                (r'2!=4', True),
                (r'2>=2', True),
                (r'2>=1', True),
                (r'2<=2', True),
                (r'2<=3', True),
                (r'2>1', True),
                (r'2<1', False),
                ]
        test_all(self, ['name'], expressions)

    def test_counter(self):
        expressions = [
                (r'name+counter[10,2]', [('a', 'a10'), ('b', 'b12')]),
                ]
        files = list(resorter.utils.read_filenames(['a','b'], False))
        for expr,expected in expressions:
            result = process(files, expr, ask_test)
            self.assertEqual(expected, list(result));


if __name__=='__main__':
    loglevel = logging.DEBUG
    logging.basicConfig(
        format='%(levelname)s:%(module)s.%(funcName)s: %(message)s', level=loglevel)
    unittest.main()

modules.update()
