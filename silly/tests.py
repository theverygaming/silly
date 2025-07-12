import unittest
from . import globalvars, modload


class TransactionCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = globalvars.registry.get_environment(autocommit=False)

    @classmethod
    def tearDownClass(cls):
        cls.env.close()
        cls.env = None
        super().tearDownClass()


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for module in modload.loaded_modules:
        path = modload.find_module(module) / "tests"
        if not path.is_dir():
            continue
        tests = loader.discover(start_dir=str(path), pattern="test_*.py", top_level_dir=None)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result
