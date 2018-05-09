from rest_framework.routers import DefaultRouter

from .views import BillingViewSet, PhoneCallViewSet

router = DefaultRouter()
router.register(r'phonecalls', PhoneCallViewSet, base_name='phonecall')
router.register(r'billing', BillingViewSet, base_name='billing')
urlpatterns = router.urls
