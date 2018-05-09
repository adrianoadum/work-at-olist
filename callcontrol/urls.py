from rest_framework.routers import DefaultRouter

from .views import PhoneCallViewSet

router = DefaultRouter()
router.register(r'phonecalls', PhoneCallViewSet, base_name='phonecall')
urlpatterns = router.urls
