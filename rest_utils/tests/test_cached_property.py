from django.test import TestCase

from ..decorators import cached_property

from .base import AssertNotRaisesMixin


class CachedPropertyTestCase(AssertNotRaisesMixin, TestCase):

    @classmethod
    def setUpClass(cls):

        class Class(object):

            data = None

            read_only = cached_property(
                fget=lambda this: this.data,
                name='read_only',
            )

            write_only = cached_property(
                fset=lambda this, value: setattr(this, 'data', value),
                name='write_only',
            )

            del_only = cached_property(
                fdel=lambda this: delattr(this, 'data'),
                name='del_only',
            )

            read_write = cached_property(
                fget=lambda this: this.data,
                fset=lambda this, value: setattr(this, 'data', value),
                name='read_write',
            )

            read_del = cached_property(
                fget=lambda this: this.data,
                fdel=lambda this: delattr(this, 'data'),
                name='read_del',
            )

            write_del = cached_property(
                fset=lambda this, value: setattr(this, 'data', value),
                fdel=lambda this: delattr(this, 'data'),
                name='write_del',
            )

            prop = cached_property(
                fget=lambda this: this.data,
                fset=lambda this, value: setattr(this, 'data', value),
                fdel=lambda this: delattr(this, 'data'),
                name='prop',
            )

        cls.Class = Class

    def setUp(self):
        self.obj = self.Class()

    def tearDown(self):
        del self.obj

    def test_access(self):
        """
        This test checks that @cached_property
        cannot be read if no fget is specified,
        cannot be assigned if no fset is specified
         and cannot be deleted if no fdel is specified.
        """
        getter = lambda attr: (lambda: getattr(self.obj, attr))
        setter = lambda attr: (lambda value: setattr(self.obj, attr, value))
        deleter = lambda attr: (lambda: delattr(self.obj, attr))

        self.assertNotRaises(getter('read_only'))
        self.assertRaises(AttributeError, setter('read_only'), 1)
        self.assertRaises(AttributeError, deleter('read_only'))

        self.assertRaises(AttributeError, getter('write_only'))
        self.assertNotRaises(setter('write_only'), 1)
        self.assertRaises(AttributeError, deleter('write_only'))

        self.assertRaises(AttributeError, getter('del_only'))
        self.assertRaises(AttributeError, setter('del_only'), 1)
        self.assertNotRaises(deleter('del_only'))

        self.assertNotRaises(getter('read_write'))
        self.assertNotRaises(setter('read_write'), 1)
        self.assertRaises(AttributeError, deleter('read_write'))

        self.assertNotRaises(getter('read_del'))
        self.assertRaises(AttributeError, setter('read_del'), 1)
        self.assertNotRaises(deleter('read_del'))

        self.assertRaises(AttributeError, getter('write_del'))
        self.assertNotRaises(setter('write_del'), 1)
        self.assertNotRaises(deleter('write_del'))

        self.assertNotRaises(getter('prop'))
        self.assertNotRaises(setter('prop'), 1)
        self.assertNotRaises(deleter('prop'))

    def test_caching(self, Class=None):

        if not Class:
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

    def test_caching_with_read_write(self):

        class Class(object):
            data = None

            @cached_property
            def prop(self):
                return self.data

            @prop.setter
            def prop(self, value):
                self.data = value

        self.test_caching(Class)

    def test_caching_with_read_del(self):

        class Class(object):
            data = None

            @cached_property
            def prop(self):
                return self.data

            @prop.deleter
            def prop(self):
                del self.data

        self.test_caching(Class)

    def test_caching_with_full_ops(self):

        class Class(object):
            data = None

            @cached_property
            def prop(self):
                return self.data

            @prop.setter
            def prop(self, value):
                self.data = value

            @prop.deleter
            def prop(self):
                del self.data

        self.test_caching(Class)

    def test_invalidation(self):

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