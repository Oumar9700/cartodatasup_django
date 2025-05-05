import os
import sys

# Indique le chemin du projet Django
sys.path.insert(0, os.path.dirname(__file__))

# Réglage de la variable d'environnement
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
