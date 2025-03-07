import csv
import os
from django.core.management.base import BaseCommand
from admissions.models import Institution, Formation, Candidature

class Command(BaseCommand):
    help = "Importe les données des établissements, formations et candidatures depuis un fichier CSV"

    def handle(self, *args, **kwargs):
        file_path = os.path.join("data", "fr-esr-parcoursup_2023.csv")  # 📌 Modifier si besoin

        # Vérification de l'existence du fichier CSV
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"❌ Le fichier {file_path} est introuvable."))
            return

        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')  # ⚠️ Utilisation de ';' comme séparateur

            for row in reader:
                try:
                    # 🔹 Création ou mise à jour de l'établissement
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

                    # 🔹 Création ou mise à jour de la formation
                    formation, _ = Formation.objects.get_or_create(
                        institution=institution,
                        name=row["Filière de formation"],
                        category=row["Filière de formation très agrégée"],
                        detailed_category=row["Filière de formation détaillée"],
                        is_selective=row["Sélectivité"] == "formation sélective",
                        gps_coordinates=row["Coordonnées GPS de la formation"],
                        capacity=int(row["Capacité de l’établissement par formation"] or 0)
                    )

                    # 🔹 Création de la candidature
                    Candidature.objects.create(
                        formation=formation,
                        session_year=int(row["Session"]),

                        total_candidates=int(row["Effectif total des candidats pour une formation"] or 0),
                        female_candidates=int(row["Dont effectif des candidates pour une formation"] or 0),
                        boursier_candidates=int(row["Dont effectif des candidats boursiers néo bacheliers généraux en phase principale"] or 0) +
                                           int(row["Dont effectif des candidats boursiers néo bacheliers technologiques en phase principale"] or 0) +
                                           int(row["Dont effectif des candidats boursiers néo bacheliers professionnels en phase principale"] or 0),

                        neo_bac_general=int(row["Effectif des candidats néo bacheliers généraux en phase principale"] or 0),
                        neo_bac_techno=int(row["Effectif des candidats néo bacheliers technologiques en phase principale"] or 0),
                        neo_bac_pro=int(row["Effectif des candidats néo bacheliers professionnels en phase principale"] or 0),

                        admitted_total=int(row["Effectif total des candidats ayant accepté la proposition de l’établissement (admis)"] or 0),
                        admitted_females=int(row["Dont effectif des candidates admises"] or 0),
                        admitted_boursiers=int(row["Dont effectif des admis boursiers néo bacheliers"] or 0),

                        admitted_neo_bac_general=int(row["Effectif des admis néo bacheliers généraux"] or 0),
                        admitted_neo_bac_techno=int(row["Effectif des admis néo bacheliers technologiques"] or 0),
                        admitted_neo_bac_pro=int(row["Effectif des admis néo bacheliers professionnels"] or 0),

                        mention_tb=int(row["Dont effectif des admis néo bacheliers avec mention Très Bien au bac"] or 0),
                        mention_b=int(row["Dont effectif des admis néo bacheliers avec mention Bien au bac"] or 0),
                        mention_ab=int(row["Dont effectif des admis néo bacheliers avec mention Assez Bien au bac"] or 0),
                        mention_none=int(row["Dont effectif des admis néo bacheliers sans mention au bac"] or 0),

                        same_academy_admissions=int(row["Dont effectif des admis issus de la même académie"] or 0),
                        different_academy_admissions=int(row["Effectif total des candidats ayant accepté la proposition de l’établissement (admis)"] or 0) -
                                                      int(row["Dont effectif des admis issus de la même académie"] or 0),

                        admitted_before_bac=int ( float (row["Dont effectif des admis ayant reçu leur proposition d’admission avant le baccalauréat"]) or 0),
                        admitted_after_procedure_start=int ( float (row["Dont effectif des admis ayant reçu leur proposition d’admission à l'ouverture de la procédure principale"]) or 0),
                        admitted_after_procedure_end=int ( float (row["Dont effectif des admis ayant reçu leur proposition d’admission avant la fin de la procédure principale"]) or 0),
                    )

                    self.stdout.write(self.style.SUCCESS(f"✅ Importé : {formation.name} ({row['Session']})"))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ Erreur avec {row['Établissement']} - {str(e)}"))

        self.stdout.write(self.style.SUCCESS("🎉 Importation terminée !"))
