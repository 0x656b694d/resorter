import unittest
import os
import logging

import resorter.resorter
import resorter.utils
import resorter.filters
import resorter.modules

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

class TestFilterMethods(unittest.TestCase):

    def test_empty_filters(self):
        filters = resorter.resorter.get_filters(None, None, None)
        i,n,o = filters
        self.assertEqual(i[0].name, 'True')
        self.assertEqual(n[0].name, 'False')
        self.assertEqual(o[0].name, 'True')

    def test_input_filter(self):
        filters = resorter.resorter.get_filters(['name=="abc"'], ['path==name'], None)
        i, n, o = filters
        self.assertEqual(i[0].name, 'ExpressionFilter')
        self.assertEqual(n[0].name, 'ExpressionFilter')
        self.assertEqual(o[0].name, 'True')

        self.assertFalse(i[0](resorter.utils.PathEntry("abcd")))
        self.assertTrue(i[0](resorter.utils.PathEntry("abc")))

        self.assertFalse(n[0](resorter.utils.PathEntry("path/abc")))
        self.assertTrue(n[0](resorter.utils.PathEntry("abc/abc")))

class TestExpressions(unittest.TestCase):
    def test_abs_name(self):
        filters = resorter.resorter.get_filters(None, None, None)
        name = '/abs/path/name.ext'
        expressions = [
                (r'{name}', 'name.ext'),
                (r'{path}', '/abs/path'),
                (r'{ext}', '.ext'),
                (r'{nam}', 'name'),
                (r'{abspath}', '/abs/path'),
                ]
        files = (resorter.utils.read_filenames([name], False))
        for expr,expected in expressions:
            for source,dest in resorter.resorter.resort(files, filters, expr, ask_test):
                self.assertEqual(source, name)
                self.assertEqual(expected, dest)
    
    def test_hidden_name(self):
        filters = resorter.resorter.get_filters(None, None, None)
        name = 'rel/path/.name'
        expressions = [
                (r'{path}', 'rel/path'),
                (r'{name}', '.name'),
                (r'{ext}', ''),
                (r'{nam}', '.name'),
                (r'{abspath}', os.path.abspath(os.path.curdir) + '/rel/path'),
                ]
        files = list(resorter.utils.read_filenames([name], False))
        for expr,expected in expressions:
            for source,dest in resorter.resorter.resort(files, filters, expr, ask_test):
                self.assertEqual(source, name)
                self.assertEqual(expected, dest)

    def test_text(self):
        filters = resorter.resorter.get_filters(None, None, None)
        name = 'some_PATH string'
        expressions = [
                (r'{name}', name),
                (r'{name.up}', 'SOME_PATH STRING'),
                (r'{name.low}', 'some_path string'),
                (r'{name.cap}', 'Some_path string'),
                (r'{name.title}', 'Some_Path String'),
                (r'{name.sub[1,4]}', 'ome'),
                (r'{name.sub[4]}', '_'),
                (r'{name.replace[" ","_"]}', 'some_PATH_string'),
                (r'{name.replace["PATH","xxx"]}', 'some_xxx string'),
                (r'{name.index["PATH"]}', '5'),
                ]
        files = list(resorter.utils.read_filenames([name], False))
        for expr,expected in expressions:
            for source,dest in resorter.resorter.resort(files, filters, expr, ask_test):
                self.assertEqual(source, name)
                self.assertEqual(expected, dest)

    def test_num(self):
        filters = resorter.resorter.get_filters(None, None, None)
        name = 'path/some_42.65_'
        expressions = [
                (r'{name.index[4]}', '5'),
                (r'{name.sub[name.index[4]]}', '4'),
                (r'{name.sub[5,10].round}', '43'),
                (r'{name.sub[5,10].round[2]}', '42.65'),
                (r'{name.sub[5,10]-1.5}', '41.15'),
                (r'{name.sub[5,10]+1.5}', '44.15'),
                (r'{(name[5,10].round-1)%4}', '2'),
                (r'{(name[5,10].round-1)/6}', '7.0'),
                (r'{(name[5,10].round-1)/6^2}', '49.0'),
                (r'{name[0,4]+path}', 'somepath'),
                (r'{name[5,7].num+name[8,10]}', '107'),
                (r'{2^3}', '8'),
                (r'{-2^3}', '-8'),
                ]
        files = list(resorter.utils.read_filenames([name], False))
        for expr,expected in expressions:
            for source,dest in resorter.resorter.resort(files, filters, expr, ask_test):
                self.assertEqual(source, name)
                self.assertEqual(expected, dest)

    def test_conditions(self):
        filters = resorter.resorter.get_filters(None, None, None)
        name = 'Hello'
        expressions = [
                (r'{name.in("Goodbye","Hello","Hi")}', 'True'),
                (r'{name.in("Goodbye","Hi")}', 'False'),
                (r'{all("Goodbye",name=="Hello")}', 'True'),
                (r'{any("Goodbye",name=="xx")}', 'True'),
                (r'{not(name=="xx")}', 'True'),
                (r'{if(name=="Hello", 12, 14)}', '12'),
                (r'{if(name~="H.l+o", 12, 14)}', '12'),
                (r'{if(name=="Hlo", 12, 14)}', '14'),
                ]
        files = list(resorter.utils.read_filenames([name], False))
        for expr,expected in expressions:
            for source,dest in resorter.resorter.resort(files, filters, expr, ask_test):
                self.assertEqual(source, name)
                self.assertEqual(expected, dest)

    def test_comp(self):
        filters = resorter.resorter.get_filters(None, None, None)
        expressions = [
                (r'{2=3}', 'False'),
                (r'{2=2}', 'True'),
                (r'{2<>2}', 'False'),
                (r'{2!=4}', 'True'),
                (r'{2>=2}', 'True'),
                (r'{2>=1}', 'True'),
                (r'{2<=2}', 'True'),
                (r'{2<=3}', 'True'),
                (r'{2>1}', 'True'),
                (r'{2<1}', 'False'),
                ]
        files = list(resorter.utils.read_filenames(['name'], False))
        for expr,expected in expressions:
            for source,dest in resorter.resorter.resort(files, filters, expr, ask_test):
                self.assertEqual(expected, dest)

if __name__=='__main__':
    loglevel = logging.DEBUG
    logging.basicConfig(
        format='%(levelname)s:%(module)s.%(funcName)s: %(message)s', level=loglevel)
    unittest.main()

resorter.modules.update()
