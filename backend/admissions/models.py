from django.db import models

# Create your models here.
class Institution(models.Model):
    uai_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    department_code = models.CharField(max_length=5)
    department_name = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    academy = models.CharField(max_length=100)
    commune = models.CharField(max_length=100)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Formation(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="formations")
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    detailed_category = models.CharField(max_length=255)
    is_selective = models.BooleanField(default=False)
    gps_coordinates = models.CharField(max_length=50, null=True, blank=True)
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.institution.name}"


class Candidature(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="candidatures")
    session_year = models.IntegerField()
    
    total_candidates = models.IntegerField()
    female_candidates = models.IntegerField()
    boursier_candidates = models.IntegerField()
    
    neo_bac_general = models.IntegerField()
    neo_bac_techno = models.IntegerField()
    neo_bac_pro = models.IntegerField()
    
    admitted_total = models.IntegerField()
    admitted_females = models.IntegerField()
    admitted_boursiers = models.IntegerField()
    
    admitted_neo_bac_general = models.IntegerField()
    admitted_neo_bac_techno = models.IntegerField()
    admitted_neo_bac_pro = models.IntegerField()

    #Ajout de détails sur les mentions obtenues par les admis
    mention_tb = models.IntegerField(default=0)
    mention_b = models.IntegerField(default=0)
    mention_ab = models.IntegerField(default=0)
    mention_none = models.IntegerField(default=0)

    #Ajout de champs pour la mobilité des étudiants
    same_academy_admissions = models.IntegerField(default=0)
    different_academy_admissions = models.IntegerField(default=0)

    #Ajout de champs pour suivre le timing des admissions
    admitted_before_bac = models.IntegerField(default=0)
    admitted_after_procedure_start = models.IntegerField(default=0)
    admitted_after_procedure_end = models.IntegerField(default=0)

    def admission_rate(self):
        return (self.admitted_total / self.total_candidates) * 100 if self.total_candidates else 0

    def __str__(self):
        return f"{self.formation.name} - {self.session_year}"


    
