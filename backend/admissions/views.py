from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Institution, Formation, Candidature
from .serializers import InstitutionSerializer, FormationSerializer, CandidatureSerializer, RegisterSerializer

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout

from django.db.models import Count, Sum, Q
from rest_framework.decorators import api_view
from django.http import JsonResponse

class FormationParStatutView(APIView):
    def get(self, request):
        data = (
            Formation.objects
            .values('institution__status')
            .annotate(nombre=Count('id'))
        )
        # Formatage clair
        result = {
            entry['institution__status']: entry['nombre']
            for entry in data
        }
        return Response(result)

class AFormationParStatutView(APIView):
    def get(self, request):
        commune = request.GET.get('commune')
        academie = request.GET.get('academie')

        institutions = Institution.objects.all()
        if commune:
            institutions = institutions.filter(commune=commune)
        if academie:
            institutions = institutions.filter(academy=academie)

        data = institutions.values('status').annotate(
            nombre_formations=Count('formations', distinct=True),
            total_candidatures=Sum('formations__candidatures__total_candidates'),
            total_femmes=Sum('formations__candidatures__female_candidates')
        )
        return Response(data)

#Get all formations, institutions and candidatures
class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer

class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer

class CandidatureViewSet(viewsets.ModelViewSet):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
#Get all formations, institutions and candidatures


# Authentication
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)

            return Response({
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        # ajoute d'autres champs si besoin
                    },
                    "token": str(refresh.access_token),
                    "refreshToken": str(refresh)
                }
            })

        return Response(
            {"error": "Identifiants invalides"},
            status=status.HTTP_401_UNAUTHORIZED
        )

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Ajout du token dans la blacklist
            logout(request)  # Déconnexion du user Django
            return Response({"message": "Déconnexion réussie"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# Authentication




@api_view(['GET'])
def stats_par_statut_etablissement(request):
    # Récupération des filtres depuis la query string
    commune = request.GET.get('commune')
    academie = request.GET.get('academie')

    # Filtrage des institutions si filtre présent
    institutions = Institution.objects.all()
    if commune:
        institutions = institutions.filter(commune=commune)
    if academie:
        institutions = institutions.filter(academy=academie)

    # Agrégation par statut
    data = institutions.values('status').annotate(
        nombre_formations=Count('formations', distinct=True),

        #number of formations selective with True
        nombre_formations_selectives=Count('formations', filter=Q(formations__is_selective=True), distinct=True),
        nombre_formations_non_selectives=Count('formations', filter=Q(formations__is_selective=False), distinct=True),

        total_candidatures=Count('formations__candidatures__total_candidates'),
        total_females=Sum('formations__candidatures__female_candidates'),
        
        total_admis=Sum('formations__candidatures__admitted_total'),
        total_boursiers=Sum('formations__candidatures__boursier_candidates'),

        total_neo_bac_general=Sum('formations__candidatures__neo_bac_general'),
        neo_bac_techno=Sum('formations__candidatures__neo_bac_techno'),
        neo_bac_pro=Sum('formations__candidatures__neo_bac_pro'),

        admitted_females=Sum('formations__candidatures__admitted_females'),
        admitted_boursiers=Sum('formations__candidatures__admitted_boursiers'),

        admitted_neo_bac_general=Sum('formations__candidatures__admitted_neo_bac_general'),
        admitted_neo_bac_pro=Sum('formations__candidatures__admitted_neo_bac_pro'),
        admitted_neo_bac_techno=Sum('formations__candidatures__admitted_neo_bac_techno'),

        mention_ab=Sum('formations__candidatures__mention_ab'),
        mention_none=Sum('formations__candidatures__mention_none'),


    )

    return Response(data)


def get_filter_options(request):

    # Récupération des filtres depuis la query string
    annee = request.GET.get('annee')
    academy = request.GET.get('academy')
    departement = request.GET.get('departement')
    region = request.GET.get('region')
    etablissement = request.GET.get('etablissement')

    institutions = Institution.objects.all()
    candidatures = Candidature.objects.all()

    if annee:
        institutions = institutions.filter(formations__candidatures__session_year=annee)
    if academy:
        institutions = institutions.filter(academy=academy)
    if departement:
        institutions = institutions.filter(department_name=departement)
    if region:
        institutions = institutions.filter(region=region)
    if etablissement:
        institutions = institutions.filter(name=etablissement)
    # Agrégation par statut
    # institutions = institutions.values('status').annotate(
    #     nombre_formations=Count('formations', distinct=True), 
    
    data = {
        "annees": list(candidatures.values_list('session_year', flat=True).distinct().order_by('session_year')),
        "academies": list(institutions.values_list('academy', flat=True).distinct().order_by('academy')),
        "departements": list(institutions.values_list('department_name', flat=True).distinct().order_by('department_name')),
        "communes": list(institutions.values_list('commune', flat=True).distinct().order_by('commune')),
        "regions": list(institutions.values_list('region', flat=True).distinct().order_by('region')),
        "etablissements": list(institutions.values_list('name', flat=True).distinct().order_by('name')),
    }
    return JsonResponse(data)