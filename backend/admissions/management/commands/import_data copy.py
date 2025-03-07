import csv
from django.core.management.base import BaseCommand
from myapp.models import Institution, Formation, Candidature

class Command(BaseCommand):
    help = "Importe les données à partir d'un fichier CSV"

    def handle(self, *args, **kwargs):
        file_path = "data/parcoursup_data.csv"  # 📌 Modifier avec le bon chemin du fichier

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Création ou récupération de l'institution
                institution, _ = Institution.objects.get_or_create(
                    uai_code=row["Code UAI de l'établissement"],
                    defaults={
                        "name": row["Établissement"],
                        "department_code": row["Code départemental de l’établissement"],
                        "department_name": row["Département de l’établissement"],
                        "region": row["Région de l’établissement"],
                        "academy": row["Académie de l’établissement"],
                        "commune": row["Commune de l’établissement"],
                        "is_public": row["Statut de l’établissement de la filière de formation (public, privé…)"] == "Public"
                    }
                )

                # Création ou récupération de la formation
                formation, _ = Formation.objects.get_or_create(
                    institution=institution,
                    name=row["Filière de formation"],
                    category=row["Filière de formation très agrégée"],
                    detailed_category=row["Filière de formation détaillée"],
                    is_selective=row["Sélectivité"] == "formation sélective",
                    gps_coordinates=row["Coordonnées GPS de la formation"],
                    capacity=int(row["Capacité de l’établissement par formation"]) if row["Capacité de l’établissement par formation"] else 0
                )

                # Création de la candidature
                Candidature.objects.create(
                    formation=formation,
                    session_year=int(row["Session"]),
                    total_candidates=int(row["Effectif total des candidats pour une formation"]),
                    admitted_total=int(row["Effectif total des candidats ayant accepté la proposition de l’établissement (admis)"])
                )

        self.stdout.write(self.style.SUCCESS("Importation des données terminée avec succès !"))
