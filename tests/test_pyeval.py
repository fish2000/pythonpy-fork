
import unittest
from pythonpy.pyeval import pyeval

class TestPyEval(unittest.TestCase):
    
    def pyeval(self, args, result):
        return self.assertEqual(pyeval(args)[0], result)
    
    def test_empty(self):
        self.pyeval([], '')
    
    def test_numbers(self):
        self.pyeval(['3 * 4.5'], '13.5\n')
    
    def test_range(self):
        self.pyeval(['range(3)'], '0\n1\n2\n')
    
    def test_bytes(self):
        self.pyeval(['b"Yo dogg"'], "b'Yo dogg'\n")
    
    def test_statements(self):
        self.pyeval(['-c', 'a=5', '-C', 'print(a)'], '5\n')
    
    def test_imports(self):
        module_commands = [
            "math.ceil(2.5)",
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
            "np.array([0, 2, 4, 6, 8], dtype='uint8')"
        ]
        for command in module_commands:
            assert pyeval([command])[0]

if __name__ == '__main__':
    unittest.main()
