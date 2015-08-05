from django.test import TestCase

from mock import Mock

from rest_utils.decorators import raise_on_false

from .base import AssertNotRaisesMixin


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