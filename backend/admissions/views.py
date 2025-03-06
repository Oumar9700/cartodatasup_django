from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Institution, Formation, Candidature
from .serializers import InstitutionSerializer, FormationSerializer, CandidatureSerializer

class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer

class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer

class CandidatureViewSet(viewsets.ModelViewSet):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
