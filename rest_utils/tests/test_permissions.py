from unittest import skip
from mock import Mock

from django.http import Http404
from django.test import TestCase

from rest_utils.permissions import (DenyCreateOnPutPermission,
                                    NotAuthenticatedPermission)


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