import unittest
from subprocess import check_output

class TestPythonPy(unittest.TestCase):
    
    def checkOutput(self, string, result, **kwargs):
        return self.assertEqual(check_output(string, **kwargs), result)
    
    def test_list_stdin(self):
        self.checkOutput("""echo $'a,2\nb,1' | py -l 'sorted(l, key=lambda x: x.split(",")[1])'""", b'b,1\na,2\n', shell=True)
    
    def test_version(self):
        from pythonpy.__version__ import __version__
        import sys
        pyversion = sys.version.split(' ')[0]
        self.checkOutput(['py', '--version'], bytes(f'''Pythonpy {__version__}\nPython {pyversion}\n''', encoding='UTF-8'))
    
    def test_empty(self):
        self.checkOutput(['py'], b'')
    
    def test_numbers(self):
        self.checkOutput(['py', '3 * 4.5'], b'13.5\n')
    
    def test_range(self):
        self.checkOutput(['py', 'range(3)'], b'0\n1\n2\n')
    
    def test_split_input(self):
        self.checkOutput(["""echo a,b | py -x 'x[1]' --si ,"""], b'b\n', shell=True)
    
    def test_split_output(self):
        self.checkOutput(["""echo abc | py -x x --si '' --so ','"""], b'a,b,c\n', shell=True)
    
    def test_ignore_errors(self):
        self.checkOutput("""echo a | py -x --i 'None.None'""", b'', shell=True)
        self.checkOutput("""echo a | py -fx --i 'None.None'""", b'', shell=True)
    
    def test_statements(self):
        self.checkOutput("""py -c 'a=5' -C 'print(a)'""", b'5\n', shell=True)
        self.checkOutput("""echo 3 | py -c 'a=5' -x x -C 'print(a)'""", b'3\n5\n', shell=True)
    
    def test_imports(self):
        module_commands = ["math.ceil(2.5)",
                           "calendar.weekday(1955, 11, 5)",
                           "csv.list_dialects()",
                           "datetime.timedelta(hours=-5)",
                           "hashlib.sha224(b\"Nobody inspects the spammish repetition\").hexdigest()",
                           "glob.glob('*')",
                           "itertools.product(['a','b'], [1,2])",
                           "json.dumps([1,2,3,{'4': 5, '6': 7}], separators=(',',':'))",
                           "os.name",
                           "random.randint(0, 1000)",
                           "re.compile('[a-z]').findall('abcd')",
                           "shutil.get_archive_formats()",
                           "tempfile.gettempdir()",
                           "uuid.uuid1()",
                           "math",
                           "[math]",
                           "numpy.array([0, 2, 4, 6, 8], dtype='uint8')",
                           "np.array([0, 2, 4, 6, 8], dtype='uint8')",
                           ]
        for command in module_commands:
            check_output("py %r" % command, shell=True)


if __name__ == '__main__':
    unittest.main()
