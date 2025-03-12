
from rest_framework import serializers
from .models import Institution, Formation, Candidature
from django.contrib.auth.models import User


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


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
