from django.contrib import admin

# Register your models here.
from .models import Institution, Formation, Candidature

# Register your models here.
admin.site.register(Institution)
admin.site.register(Formation)
admin.site.register(Candidature)
