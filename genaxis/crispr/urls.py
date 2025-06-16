from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpeciesViewSet,GeneViewSet, CrisprEditViewSet

router = DefaultRouter()
router.register(r'species', SpeciesViewSet)
router.register(r'genes', GeneViewSet)
router.register(r'edits', CrisprEditViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
