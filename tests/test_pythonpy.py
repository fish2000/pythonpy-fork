import unittest
from subprocess import check_output

class TestPythonPy(unittest.TestCase):
    
    def test_empty(self):
        self.assertEqual(check_output(['py']), b'')
    
    def test_numbers(self):
        self.assertEqual(check_output(['py', '3 * 4.5']), b'13.5\n')
    
    def test_range(self):
        self.assertEqual(check_output(['py', 'range(3)']), b'0\n1\n2\n')
    
    def test_split_input(self):
        self.assertEqual(check_output(["""echo a,b | py -x 'x[1]' --si ,"""], shell=True), b'b\n')
    
    def test_split_output(self):
        self.assertEqual(check_output(["""echo abc | py -x x --si '' --so ','"""], shell=True), b'a,b,c\n')
    
    def test_ignore_errors(self):
        self.assertEqual(check_output("""echo a | py -x --i 'None.None'""", shell=True), b'')
        self.assertEqual(check_output("""echo a | py -fx --i 'None.None'""", shell=True), b'')
    
    def test_statements(self):
        self.assertEqual(check_output("""py -c 'a=5' -C 'print(a)'""", shell=True), b'5\n')
        self.assertEqual(check_output("""echo 3 | py -c 'a=5' -x x -C 'print(a)'""", shell=True), b'3\n5\n')
    
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
                           ]
        for command in module_commands:
            check_output("py %r" % command, shell=True)


if __name__ == '__main__':
    unittest.main()
