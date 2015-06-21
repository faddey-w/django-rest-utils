# -*- coding: utf-8 -*-
from mock import Mock
from unittest import skip

from django.http import Http404
# from django_nose import FastFixtureTestCase as TestCase
from django.test import TestCase

from .permissions import DenyCreateOnPutPermission, NotAuthenticatedPermission
from .decorators import raise_on_false


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


class RaiseOnFalseTest(TestCase):

    def assertNotRaises(self, callable_obj, *args, **kwargs):
        try:
            callable_obj(*args, **kwargs)
        except:
            self.fail("Function raises an exception unexpectedly")

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
