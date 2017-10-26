"""This module contains utility functions to write tests."""

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
