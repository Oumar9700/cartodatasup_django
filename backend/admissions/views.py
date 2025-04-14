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

from django.db.models import Sum, F, FloatField, ExpressionWrapper
from rest_framework.permissions import IsAuthenticated

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

def get_filter_options(request):

    # Récupération des filtres depuis la query string
    annee = request.GET.get('annee')
    region = request.GET.get('region')
    academy = request.GET.get('academy')
    departement = request.GET.get('departement')
    commune = request.GET.get('commune')
    status_institution = request.GET.get('status_institution')
    etablissement = request.GET.get('etablissement')
    formation_selectivity = request.GET.get('formation_selectivity')
    formation = request.GET.get('formation')

    institutions = Institution.objects.all()
    candidatures = Candidature.objects.all()

    if annee:
        institutions = institutions.filter(formations__candidatures__session_year=annee)
    if region:
        institutions = institutions.filter(region=region)
    if academy:
        institutions = institutions.filter(academy=academy)
    if departement:
        institutions = institutions.filter(department_name=departement)
    if commune:
        institutions = institutions.filter(commune=commune)
    if status_institution:
        institutions = institutions.filter(status=status_institution)
    if etablissement:
        institutions = institutions.filter(name=etablissement)
    if formation_selectivity:
        if formation_selectivity == "true":
            formation_selectivity = True
        elif formation_selectivity == "false":  
            formation_selectivity = False
        institutions = institutions.filter(formations__is_selective=formation_selectivity)
    if formation:
        institutions = institutions.filter(formations__name=formation)
        
    # Agrégation par statut
    # institutions = institutions.values('status').annotate(
    #     nombre_formations=Count('formations', distinct=True), 
    
    data = {
        "annees": list(candidatures.values_list('session_year', flat=True).distinct().order_by('session_year')),
        "academies": list(institutions.values_list('academy', flat=True).distinct().order_by('academy')),
        "departements": list(institutions.values_list('department_name', flat=True).distinct().order_by('department_name')),
        "communes": list(institutions.values_list('commune', flat=True).distinct().order_by('commune')),
        "regions": list(institutions.values_list('region', flat=True).distinct().order_by('region')),
        "status_institutions": list(institutions.values_list('status', flat=True).distinct().order_by('status')),
        "etablissements": list(institutions.values_list('name', flat=True).distinct().order_by('name')),
        "formation_selectivities": list(institutions.values_list('formations__is_selective', flat=True).distinct().order_by('formations__is_selective')),
        "formations": list(institutions.values_list('formations__name', flat=True).distinct().order_by('formations__name')),
    }
    return JsonResponse(data)


# Indicateur: stats par statut d'établissement
@api_view(['GET'])
def stats_par_statut_etablissement(request):
    # Récupération des filtres depuis la query string
    annee = request.GET.get('annee')
    region = request.GET.get('region')
    academy = request.GET.get('academy')
    departement = request.GET.get('departement')
    commune = request.GET.get('commune')
    status_institution = request.GET.get('status_institution')
    etablissement = request.GET.get('etablissement')
    formation_selectivity = request.GET.get('formation_selectivity')
    formation = request.GET.get('formation')

    # Filtrage des institutions si filtre présent
    institutions = Institution.objects.all()

    if annee:
        institutions = institutions.filter(formations__candidatures__session_year=annee)
    if region:
        institutions = institutions.filter(region=region)
    if academy:
        institutions = institutions.filter(academy=academy)
    if departement:
        institutions = institutions.filter(department_name=departement)
    if commune:
        institutions = institutions.filter(commune=commune)
    if status_institution:
        institutions = institutions.filter(status=status_institution)
    if etablissement:
        institutions = institutions.filter(name=etablissement)
    if formation_selectivity:
        if formation_selectivity == "true":
            formation_selectivity = True
        elif formation_selectivity == "false":  
            formation_selectivity = False
        institutions = institutions.filter(formations__is_selective=formation_selectivity)
    if formation:
        institutions = institutions.filter(formations__name=formation)

    # Agrégation par statut
    data = institutions.values('status').annotate(
        nombre_formations=Count('formations', distinct=True),

        #number of formations selective with True
        nombre_formations_selectives=Count('formations', filter=Q(formations__is_selective=True), distinct=True),
        nombre_formations_non_selectives=Count('formations', filter=Q(formations__is_selective=False), distinct=True),

        total_candidatures=Sum('formations__candidatures__total_candidates'),
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


# Indicateur: ratio capacité candidats
class RatioCapaciteCandidatsView(APIView):

    def get(self, request):

        annee = request.query_params.get('annee')
        region = request.query_params.get('region')
        academy = request.query_params.get('academy')
        departement = request.query_params.get('departement')
        commune = request.query_params.get('commune')
        status_institution = request.query_params.get('status_institution')
        etablissement = request.query_params.get('etablissement')
        formation_selectivity = request.query_params.get('formation_selectivity')
        formation = request.query_params.get('formation')

        tri = request.query_params.get('tri', 'ratio')  # default: sort by ratio

        filters = Q()
        if annee:
            filters &= Q(candidatures__session_year=annee)
        if region:
            filters &= Q(institution__region=region)
        if academy:
            filters &= Q(institution__academy=academy)
        if departement:
            filters &= Q(institution__department_name=departement)
        if commune:
            filters &= Q(institution__commune=commune)
        if status_institution:
            filters &= Q(institution__status=status_institution)
        if etablissement:
            filters &= Q(institution__name__icontains=etablissement)
        if formation_selectivity:
            if formation_selectivity.lower() == 'true':
                filters &= Q(is_selective=True)
            elif formation_selectivity.lower() == 'false':
                filters &= Q(is_selective=False)
        if formation:
            filters &= Q(name__icontains=formation)

        formations = Formation.objects.filter(filters).annotate(
            total_candidats=Sum('candidatures__total_candidates'),
            ratio=ExpressionWrapper(
                F('capacity') * 1.0 / F('candidatures__total_candidates'),
                output_field=FloatField()
            )
        ).order_by(f'-{tri}' if tri in ['ratio', 'capacite', 'total_candidats'] else '-ratio')

        data = [
            {
                'formation_name': f.name,
                'capacity': f.capacity,
                'total_candidates': f.total_candidats,
                'ratio': round(f.ratio, 2) if f.ratio else None,
            }
            for f in formations
        ]

        return Response(data)

