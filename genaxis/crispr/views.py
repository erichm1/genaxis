from django.shortcuts import render
from rest_framework import viewsets
from .models import Species, Gene, CrisprEdit
from .serializers import SpeciesSerializer, GeneSerializer, CrisprEditSerializer


class SpeciesViewSet(viewsets.ModelViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer

class GeneViewSet(viewsets.ModelViewSet):
    queryset = Gene.objects.all()
    serializer_class = GeneSerializer

class CrisprEditViewSet(viewsets.ModelViewSet):
    queryset = CrisprEdit.objects.all()
    serializer_class = CrisprEditSerializer
