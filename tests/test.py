import unittest
import logging

import resorter.resorter
import resorter.utils
import resorter.filters

def ask_test(msg, opts, default=None):
    return default

class TestFilterMethods(unittest.TestCase):
    def test_regex(self):
        rf = resorter.filters.RegexFilter(r'abc.*')
        self.assertTrue(rf('abcd'))
        self.assertFalse(rf('bcd'))

class TestGetFiles(unittest.TestCase):
    def test_file(self):
        names = list(map(resorter.utils.PathEntry, [ 'name1', 'name2', 'name3' ]))
        output = 'dst'
        filters = resorter.resorter.get_filters(None, None, None)
        i,n,o = filters
        self.assertEqual(i[0].__name__, 'true')
        self.assertEqual(n[0].__name__, 'false')
        self.assertEqual(o[0].__name__, 'true')
        expression = '{path}'
        pairs = list(resorter.resorter.resort(names, filters, expression, output, ask_test))
        self.assertEqual(len(pairs), 3)
        for i,o in pairs:
            print(i,o)
        self.assertEqual(pairs[0][0].path, names[0].path)
        self.assertEqual(pairs[1][0].path, names[1].path)
        self.assertEqual(pairs[2][0].path, names[2].path)

        self.assertEqual(pairs[0][1].path, output+'/name1')


if __name__=='__main__':
    loglevel = logging.DEBUG
    logging.basicConfig(
        format='%(levelname)s:%(module)s.%(funcName)s: %(message)s', level=loglevel)
    unittest.main()
