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

    #pagination to none
    pagination_class = None
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Récupérer les paramètres de filtre depuis la requête
        annee = self.request.query_params.get('annee')
        region = self.request.query_params.get('region')
        academy = self.request.query_params.get('academy')
        departement = self.request.query_params.get('departement')
        commune = self.request.query_params.get('commune')
        status_institution = self.request.query_params.get('status_institution')
        etablissement = self.request.query_params.get('etablissement')
        formation_selectivity = self.request.query_params.get('formation_selectivity')
        formation = self.request.query_params.get('formation')

        #une formation recherchée par saisie
        formation_searched = self.request.query_params.get('formation_searched')


        # Appliquer les filtres
        if annee:
            queryset = queryset.filter(candidatures__session_year=annee)
        if region:
            queryset = queryset.filter(institution__region=region)
        if academy:
            queryset = queryset.filter(institution__academy=academy)
        if departement:
            queryset = queryset.filter(institution__department_name=departement)
        if commune:
            queryset = queryset.filter(institution__commune=commune)
        if status_institution:
            queryset = queryset.filter(institution__status=status_institution)
        if etablissement:
            queryset = queryset.filter(institution__name__icontains=etablissement)
        if formation_selectivity:
            if formation_selectivity == "true":
                formation_selectivity = True
            elif formation_selectivity == "false":  
                formation_selectivity = False
            queryset = queryset.filter(is_selective=formation_selectivity)
        if formation:
            queryset = queryset.filter(detailed_category__icontains=formation)
        
        if formation_searched:
            queryset = queryset.filter(detailed_category__icontains=formation_searched)

        #order by capacity desc
        queryset = queryset.order_by('-capacity')

        return queryset

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
        institutions = institutions.filter(name__icontains=etablissement)
    if formation_selectivity:
        if formation_selectivity == "true":
            formation_selectivity = True
        elif formation_selectivity == "false":  
            formation_selectivity = False
        institutions = institutions.filter(formations__is_selective=formation_selectivity)
    if formation:
        institutions = institutions.filter(formations__detailed_category__icontains=formation)

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
class FormationsStatsView(APIView):
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

        #une formation recherchée par saisie
        formation_searched = request.query_params.get('formation_searched')

        tri = request.query_params.get('tri', 'ratio')  # default: sort by ratio
        order = request.query_params.get('order', 'desc')  # default: sort by desc
        sign = '-'
        if(order and order == "desc"):
            sign = '-'
        if(order and order == "asc"):
            sign = ''

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
            filters &= Q(detailed_category__icontains=formation)

        if formation_searched:
            filters &= Q(detailed_category__icontains=formation_searched)

        formations = Formation.objects.filter(filters).annotate(
            total_candidats=Sum('candidatures__total_candidates'),
            admitted_total=Sum('candidatures__admitted_total'),
            ratio=ExpressionWrapper(
                F('capacity') * 1.0 / F('candidatures__total_candidates'),
                output_field=FloatField()
            ),
            #filling_rate
            filling_rate  = ExpressionWrapper(
                F('candidatures__admitted_total') * 1.0 / F('capacity'),
                output_field=FloatField()
            ),   
            #admission_rate
            admission_rate  = ExpressionWrapper(
                F('candidatures__admitted_total') * 1.0 / F('candidatures__total_candidates'),
                output_field=FloatField()
            ),   
        ).order_by(f'{sign}{tri}' if tri in ['ratio', 'capacity', 'total_candidats', 'filling_rate', 'admission_rate'] else '-ratio')

        data = [
            {
                'formation_name': f.detailed_category,
                'capacity': f.capacity,
                'total_candidates': f.total_candidats,
                'admitted_total': f.admitted_total,
                'ratio': f.ratio ,
                'filling_rate': round((f.filling_rate or 0) * 100.0, 2),
                'admission_rate': round((f.admission_rate or 0) * 100.0, 2),
            }
            for f in formations
        ]

        return Response(data)


# Indicateur: repartition des admis
class RepartitionAdmisView(APIView):
    permission_classes = [IsAuthenticated]

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

        #une formation recherchée par saisie
        formation_searched = request.query_params.get('formation_searched')


        filters = Q()
        if annee:
            filters &= Q(session_year=annee)
        if region:
            filters &= Q(formation__institution__region=region)
        if academy:
            filters &= Q(formation__institution__academy=academy)
        if departement:
            filters &= Q(formation__institution__department_name=departement)
        if commune:
            filters &= Q(formation__institution__commune=commune)
        if status_institution:
            filters &= Q(formation__institution__status=status_institution)
        if etablissement:
            filters &= Q(formation__institution__name__icontains=etablissement)
        if formation_selectivity:
            if formation_selectivity.lower() == 'true':
                filters &= Q(formation__is_selective=True)
            elif formation_selectivity.lower() == 'false':
                filters &= Q(formation__is_selective=False)
        if formation:
            filters &= Q(formation__detailed_category__icontains=formation)
        
        if formation_searched:
            filters &= Q(formation__detailed_category__icontains=formation_searched)


        result = Candidature.objects.filter(filters).aggregate(
            #type de bac
            admitted_neo_bac_general=Sum("admitted_neo_bac_general"),
            admitted_neo_bac_techno=Sum("admitted_neo_bac_techno"),
            admitted_neo_bac_pro=Sum("admitted_neo_bac_pro"),
            admitted_others_candidates=Sum("admitted_others_candidates"),

            #mentions
            mention_tb=Sum("mention_tb"),
            mention_b=Sum("mention_b"),
            mention_ab=Sum("mention_ab"),
            mention_none=Sum("mention_none"),

            #mobilite
            same_academy_admissions=Sum("same_academy_admissions"),
            different_academy_admissions=Sum("different_academy_admissions"), 

            #boursiers
            boursiers=Sum("admitted_boursiers"),
            total_admitted=Sum("admitted_total"),
            admitted_females=Sum("admitted_females"),
            total_candidates=Sum("total_candidates"),

            #delais admission
            before_bac=Sum("admitted_before_bac"),
            after_procedure_start=Sum("admitted_after_procedure_start"),
            after_procedure_end=Sum("admitted_after_procedure_end"),
        )

        return Response(result)

class RepartitionGeographiqueFormationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        #une filiere de formation en particulier recherchée par saisie
        formation_searched = request.query_params.get('formation_searched')

        #Affichage des formation par commune, département, région ...
        group_by = request.query_params.get("repartition_geo_sector", "region")  # ou 'academie', 'departement', 'commune'
        
        #Filtrer l'affichage a tel departement, région, académie spécifique ...
        annee = request.query_params.get('annee')
        region = request.query_params.get('region')
        academy = request.query_params.get('academy')
        departement = request.query_params.get('departement')

        #Recuperer d'abord toutes les formations
        formations = Formation.objects.select_related("institution")

        #si une recherche de formation en particulier, filtrer les formations suivant cette filiere de formation voulue
        if formation_searched:
            formations = formations.filter(detailed_category__icontains=formation_searched)
        

        #ensuite je traite les regroupement - affichage par region ou academie ou ...
        if group_by not in ["region", "academy", "department_name", "commune"]:
            return Response({"error": "Paramètre group_by invalide"}, status=400)
        
        # Si je veux un affichage par region et y a deja, 
        # une annee deja choisi dans les filtres
        if group_by == "region" and annee:
            formations = formations.filter(candidatures__session_year=annee)

        # Si je veux un affichage par academie et y a deja, 
        # une, region ou une annee deja choisi dans les filtres
        if group_by == "academy" and region:
            formations = formations.filter(institution__region=region)
        if group_by == "academy" and annee:
            formations = formations.filter(candidatures__session_year=annee)
        

        # Si je veux un affichage par departement et y a deja une academy, 
        # une region ou une annee deja choisi dans les filtres
        if group_by == "department_name" and academy:
            formations = formations.filter(institution__academy=academy)
        if group_by == "department_name" and region:
            formations = formations.filter(institution__region=region)
        if group_by == "department_name" and annee:
            formations = formations.filter(candidatures__session_year=annee)
        

        # Si je veux un affichage par commune et y a deja une region, 
        # une academie ou un departement ou une annees deja choisi dans les filtres
        if group_by == "commune" and departement:
            formations = formations.filter(institution__department_name=departement)
        if group_by == "commune" and academy:
            formations = formations.filter(institution__academy=academy)
        if group_by == "commune" and region:
            formations = formations.filter(institution__region=region)
        if group_by == "commune" and annee:
            formations = formations.filter(candidatures__session_year=annee)
        

        results = (
            formations
            .values(f"institution__{group_by}")
            .annotate(nombre_formations=Count("id"))
            .order_by(f"institution__{group_by}")
        )

        data = [
            {
                "lieu": r[f"institution__{group_by}"],
                "nombre_formations": r["nombre_formations"],
            }
            for r in results
        ]

        return Response(data)