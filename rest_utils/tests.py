# -*- coding: utf-8 -*-
from mock import Mock
from unittest import skip
import traceback

from django.http import Http404
# from django_nose import FastFixtureTestCase as TestCase
from django.test import TestCase

from .permissions import DenyCreateOnPutPermission, NotAuthenticatedPermission
from .decorators import raise_on_false, cached_property
from .decorators.cached_property import read_write_cached_property, read_only_cached_property


class AssertNotRaisesMixin(object):

    def assertNotRaises(self, callable_obj, *args, **kwargs):
        try:
            callable_obj(*args, **kwargs)
        except:
            msg = ("Function raises an exception unexpectedly\n"
                   "Original exception was:\n\n" + traceback.format_exc())
            self.fail(msg)


@skip
class PermissionsTest(TestCase):
    def test_deny_create_on_put_permission(self):
        permission = DenyCreateOnPutPermission()
        view = Mock()
        request = Mock()

        request.method = 'GET'
        self.assertTrue(permission.has_permission(request, view))

        request.method = 'PUT'
        self.assertTrue(permission.has_permission(request, view))

        request.method = 'PUT'
        view.get_object = Mock(side_effect=Http404)
        self.assertFalse(permission.has_permission(request, view))

    def test_not_authenticated_permission(self):
        permission = NotAuthenticatedPermission()

        view = Mock()
        request = Mock()

        request.user.is_authenticated = Mock(return_value=True)
        self.assertFalse(permission.has_permission(request, view))

        request.user.is_authenticated = Mock(return_value=False)
        self.assertTrue(permission.has_permission(request, view))


class RaiseOnFalseTest(AssertNotRaisesMixin, TestCase):

    def test_raising(self):
        return_false = Mock(return_value=False)
        return_true = Mock(return_value=True)

        raising_decorator = raise_on_false(default_raises=True)
        silent_decorator = raise_on_false(default_raises=False)

        raising = raising_decorator(return_false)
        # This function will always raise an exception
        # unless we'll silent it explicitly
        self.assertRaises(BaseException, raising)
        self.assertRaises(BaseException, raising, raise_exception=True)
        self.assertNotRaises(raising, raise_exception=False)

        silent = silent_decorator(return_false)
        # This function will raise an exception
        # only if we explicitly specify it
        self.assertNotRaises(silent)
        self.assertNotRaises(silent, raise_exception=False)
        self.assertRaises(BaseException, silent, raise_exception=True)

        never_raises = raising_decorator(return_true)
        # This function never raise exception because it returns True
        self.assertNotRaises(never_raises)
        self.assertNotRaises(never_raises, raise_exception=True)
        self.assertNotRaises(never_raises, raise_exception=False)

        never_raises = silent_decorator(return_true)
        # This function never raise exception because it returns True
        self.assertNotRaises(never_raises)
        self.assertNotRaises(never_raises, raise_exception=True)
        self.assertNotRaises(never_raises, raise_exception=False)

    def test_on_exception(self):
        reverse = lambda seq: seq[::-1]
        arg = 'argument'

        decorator = raise_on_false()
        f = decorator(Mock(return_value=False))

        handler = lambda sed: ([reverse(sed)], {})
        f.on_exception(handler)

        self.assertRaisesMessage(
            BaseException, reverse(arg),
            f, arg, raise_exception=True
        )


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

