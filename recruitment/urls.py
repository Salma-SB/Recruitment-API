from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from api.views import (register_candidat, register_recruteur,
    CandidatViewSet, RecruteurViewSet, OffreEmploiViewSet, CandidatureViewSet)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'candidats', CandidatViewSet)
router.register(r'recruteurs', RecruteurViewSet)
router.register(r'offres-emploi', OffreEmploiViewSet)
router.register(r'candidatures', CandidatureViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/candidat/', register_candidat, name='register_candidat'),
    path('api/auth/register/recruteur/', register_recruteur, name='register_recruteur'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
