
from rest_framework import serializers
from .models import Institution, Formation, Candidature

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'

class FormationSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer()

    class Meta:
        model = Formation
        fields = '__all__'

class CandidatureSerializer(serializers.ModelSerializer):
    formation = FormationSerializer()
    admission_rate = serializers.SerializerMethodField()

    class Meta:
        model = Candidature
        fields = '__all__'

    def get_admission_rate(self, obj):
        return obj.admission_rate()
