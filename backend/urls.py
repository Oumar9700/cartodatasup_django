"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

#Authentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

#for Api
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from admissions.views import InstitutionViewSet, FormationViewSet, CandidatureViewSet, import_data

from admissions.views import RegisterView, LoginView, LogoutView, FormationParStatutView, FormationsStatsView, RepartitionAdmisView, RepartitionGeographiqueFormationsView
from admissions.views import stats_par_statut_etablissement, get_filter_options
# from admissions.views import AFormationParStatutView

router = DefaultRouter()
router.register(r'institutions', InstitutionViewSet)
router.register(r'formations', FormationViewSet)
router.register(r'candidatures', CandidatureViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),

    #Urls for authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),

    path('api/filters/', get_filter_options, name='get_filter_options'),

    path('api/public-vs-private/', stats_par_statut_etablissement),
    path('api/formations/stats/', FormationsStatsView.as_view(), name='formations-stats'),
    path('api/admissions/repartition/', RepartitionAdmisView.as_view(), name='repartition-admis'),
    path('api/repartition-geographique-formations/', RepartitionGeographiqueFormationsView.as_view(), name='repartition_geographique_formations'),

    path('api/import-data/',import_data, name='import_data'),

    # path('api/formations/status/', FormationParStatutView.as_view(), name='formations-par-statut'),
    # path('api/stats-etablissement/', AFormationParStatutView.as_view()),

    path('api/', include(router.urls)),
]

