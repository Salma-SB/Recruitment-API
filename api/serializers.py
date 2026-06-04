from rest_framework import serializers
from .models import User, Candidat, Recruteur, OffreEmploi, Candidature, MatchingResult


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.username = validated_data['email']
        user.set_password(password)
        user.save()
        return user


class CandidatSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Candidat
        fields = '__all__'


class RecruteurSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Recruteur
        fields = '__all__'


class OffreEmploiSerializer(serializers.ModelSerializer):
    recruteur = RecruteurSerializer(read_only=True)

    class Meta:
        model = OffreEmploi
        fields = '__all__'


class CandidatureSerializer(serializers.ModelSerializer):
    candidat = CandidatSerializer(read_only=True)
    offre_emploi = OffreEmploiSerializer(read_only=True)

    class Meta:
        model = Candidature
        fields = '__all__'
        read_only_fields = ['statut', 'date_candidature']


class MatchingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingResult
        fields = '__all__'
