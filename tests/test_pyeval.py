
import unittest
from pythonpy.pyeval import pyeval

class TestPyEval(unittest.TestCase):
    
    def test_empty(self):
        self.assertEqual(pyeval([]), '')
    
    def test_numbers(self):
        self.assertEqual(pyeval(['3 * 4.5']), '13.5\n')
    
    def test_range(self):
        self.assertEqual(pyeval(['range(3)']), '0\n1\n2\n')
    
    def test_statements(self):
        self.assertEqual(pyeval(['-c', 'a=5', '-C', 'print(a)']), '5\n')
    
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
            assert pyeval([command])


if __name__ == '__main__':
    unittest.main()
