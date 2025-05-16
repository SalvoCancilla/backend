from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet, MulinelloViewSet, CannaViewSet, EscaViewSet,
    CategoriaViewSet, BrandViewSet
)

# Configurazione del router DRF per le API
router = DefaultRouter()
router.register('prodotti', ProductViewSet, basename='prodotto')
router.register('mulinelli', MulinelloViewSet, basename='mulinello')
router.register('canne', CannaViewSet, basename='canna')
router.register('esche', EscaViewSet, basename='esca')
router.register('categorie', CategoriaViewSet, basename='categoria')
router.register('brands', BrandViewSet, basename='brand')

# Pattern URL per l'app prodotti
urlpatterns = [
    path('api/', include(router.urls)),
]
