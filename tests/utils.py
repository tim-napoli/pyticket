"""This module contains utility functions to write tests."""
import os
import shutil
import tempfile


def repeat(count):
    """Decorator that will repeat the given test method class.

    :param count: times the decorated test method must be executed.

    >>> class MyClassTest(unittest.TestCase):
    >>>     # This function will be executed 100 times.
    >>>     @repeat(100)
    >>>     def test_thing_using_random(self):
    >>>         x = random.randrange(10)
    >>>         y = random.randrange(10)
    >>>         self.assertEqual(add_function(x, y), x + y)
    """
    def repeated(function):
        def wrapped(self, *args, **kwargs):
            for i in range(1, count):
                if i != 1:
                    self.setUp()
                function(self, *args, **kwargs)
                if i != count - 1:
                    self.tearDown()
        return wrapped
    return repeated


def read_file_content(path):
    """Returns the content of the file at ```path```.

    :param path: the path of the file to read.
    :return: the content of the file.
    """
    with open(path, "r") as f:
        return f.read()


def get_test_root_dir():
    if "PYTICKET_TEST_TMP_DIR" in os.environ:
        dirname = os.environ["PYTICKET_TEST_TMP_DIR"] + "/pyticket-test"
        if os.path.isdir(dirname):
            shutil.rmtree(dirname)
        os.mkdir(dirname)
        return dirname
    else:
        return tempfile.mkdtemp("pyticket")
