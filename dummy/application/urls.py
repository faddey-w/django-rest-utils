__author__ = 'faddey'

from rest_utils.routers import NestingRouter, RecursiveRouter

from .views import PrimaryViewSet, NestedViewSet

router = RecursiveRouter()

router.register('data', PrimaryViewSet, 'root')

urlpatterns = router.urls
