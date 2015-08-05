from django.test import TestCase

from ..decorators import cached_property
from ..decorators.cached_property import (read_only_cached_property,
                                          read_write_cached_property)

from .base import AssertNotRaisesMixin


class CachedPropertyTestCase(AssertNotRaisesMixin, TestCase):

    def test_magic(self):

        def function():
            f = lambda *args, **kwargs: None
            f.__name__ = 'name'
            return f

        # cannot resolve property name
        self.assertRaises(AssertionError, cached_property)

        empty = cached_property(name='empty')
        self.assertIsInstance(empty, read_only_cached_property)
        self.assertNotIsInstance(empty, read_write_cached_property)

        read_only = cached_property(function())
        self.assertIsInstance(read_only, read_only_cached_property)
        self.assertNotIsInstance(read_only, read_write_cached_property)

        read_write = read_only.setter(function())
        self.assertIsInstance(read_write, read_write_cached_property)

        read_write = read_only.deleter(function())
        self.assertIsInstance(read_write, read_write_cached_property)

        props = [
            cached_property(fset=function()),
            cached_property(fdel=function()),
            cached_property(fset=function(), fdel=function()),
            cached_property(fget=function(), fset=function()),
            cached_property(fget=function(), fdel=function()),
            cached_property(fget=function(), fset=function(), fdel=function()),
        ]
        for read_write in props:
            self.assertIsInstance(read_write, read_write_cached_property)

    def test_caching(self):

        class Class(object):
            data = None

            @cached_property
            def prop(self):
                return self.data

        obj = Class()

        # setting `data` does not creating cached value
        obj.data = 1
        self.assertFalse(Class.prop.is_cached(obj))

        # accessing `prop` creates cached value
        self.assertEqual(obj.prop, 1)
        self.assertTrue(Class.prop.is_cached(obj))

        # modifying `data` does not changes cached value
        obj.data = 2
        self.assertTrue(Class.prop.is_cached(obj))
        self.assertEqual(obj.prop, 1)

        # deleting `data` does not changes cached value
        del obj.data
        self.assertTrue(Class.prop.is_cached(obj))
        self.assertEqual(obj.prop, 1)

    def test_invalidating(self):

        class Class(object):
            data = None

            @cached_property
            def prop(self):
                return self.data

            @prop.invalidator
            def modify(self, value):
                self.data = value

            @prop.invalidator
            def just_invalidate(self):
                pass

        obj = Class()

        # invalidation does not raises when cached value not set
        self.assertNotRaises(obj.modify, 1)
        self.assertEqual(obj.data, 1)
        self.assertFalse(Class.prop.is_cached(obj))

        # calling invalidation methods invalidates cache
        obj.prop
        obj.just_invalidate()
        self.assertFalse(Class.prop.is_cached(obj))
        obj.prop
        obj.modify(2)
        self.assertFalse(Class.prop.is_cached(obj))

    def test_setter(self):
        class Class(object):
            data = None

            @cached_property
            def prop(self):
                return self.data

            @prop.setter
            def prop(self, value):
                self.data = value

        obj = Class()

        obj.data = 1
        self.assertEqual(obj.prop, 1)
        obj.prop = 2
        self.assertEqual(obj.prop, 2)

    def test_deleter(self):
        class Class(object):
            data = None

            @cached_property
            def prop(self):
                return self.data

            @prop.deleter
            def prop(self):
                del self.data

        obj = Class()

        obj.data = 1
        self.assertEqual(obj.prop, 1)
        del obj.prop
        self.assertFalse(Class.prop.is_cached(obj))
        self.assertEqual(obj.prop, None)