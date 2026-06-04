import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.conf import settings
from openai import OpenAI
from drf_spectacular.utils import extend_schema

from .models import Candidat, Recruteur, OffreEmploi, Candidature, MatchingResult
from .serializers import (
    UserSerializer, CandidatSerializer, RecruteurSerializer,
    OffreEmploiSerializer, CandidatureSerializer, MatchingResultSerializer,
)


@extend_schema(
    request={'application/json': {'type': 'object',
        'properties': {'first_name': {'type': 'string'}, 'last_name': {'type': 'string'},
            'email': {'type': 'string'}, 'password': {'type': 'string'}},
        'required': ['first_name', 'last_name', 'email', 'password']}},
    responses={201: UserSerializer},
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_candidat(request):
    data = request.data.dict() if hasattr(request.data, 'dict') else dict(request.data)
    data['role'] = 'candidat'
    data['username'] = data.get('email', '')
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        Candidat.objects.create(user=user)
        return Response({'message': 'Compte candidat créé avec succès'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request={'application/json': {'type': 'object',
        'properties': {'first_name': {'type': 'string'}, 'last_name': {'type': 'string'},
            'email': {'type': 'string'}, 'password': {'type': 'string'},
            'entreprise': {'type': 'string'}, 'secteur': {'type': 'string'}},
        'required': ['first_name', 'last_name', 'email', 'password', 'entreprise']}},
    responses={201: UserSerializer},
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_recruteur(request):
    data = request.data.dict() if hasattr(request.data, 'dict') else dict(request.data)
    data['role'] = 'recruteur'
    data['username'] = data.get('email', '')
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        Recruteur.objects.create(
            user=user,
            entreprise=data.get('entreprise', ''),
            secteur=data.get('secteur', ''),
        )
        return Response({'message': 'Compte recruteur créé avec succès'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CandidatViewSet(viewsets.ModelViewSet):
    queryset = Candidat.objects.all()
    serializer_class = CandidatSerializer

    def update(self, request, pk=None, **kwargs):
        candidat = get_object_or_404(Candidat, pk=pk)
        serializer = CandidatSerializer(candidat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecruteurViewSet(viewsets.ModelViewSet):
    queryset = Recruteur.objects.all()
    serializer_class = RecruteurSerializer

    @action(detail=False, methods=['get'], url_path='candidats')
    def liste_candidats(self, request):
        competence = request.query_params.get('competence')
        disponible = request.query_params.get('disponible')
        candidats = Candidat.objects.all()
        if competence:
            candidats = candidats.filter(competences__icontains=competence)
        if disponible is not None:
            candidats = candidats.filter(disponible=disponible.lower() == 'true')
        serializer = CandidatSerializer(candidats, many=True)
        return Response(serializer.data)


class OffreEmploiViewSet(viewsets.ModelViewSet):
    queryset = OffreEmploi.objects.all()
    serializer_class = OffreEmploiSerializer

    def create(self, request):
        recruteur = get_object_or_404(Recruteur, user=request.user)
        serializer = OffreEmploiSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(recruteur=recruteur)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, **kwargs):
        offre = get_object_or_404(OffreEmploi, pk=pk)
        recruteur = get_object_or_404(Recruteur, user=request.user)
        if offre.recruteur != recruteur:
            return Response(
                {'message': "Vous n'êtes pas autorisé à modifier cette offre."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = OffreEmploiSerializer(offre, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        offre = get_object_or_404(OffreEmploi, pk=pk)
        recruteur = get_object_or_404(Recruteur, user=request.user)
        if offre.recruteur != recruteur:
            return Response(
                {'message': "Vous n'êtes pas autorisé à supprimer cette offre."},
                status=status.HTTP_403_FORBIDDEN,
            )
        offre.statut = 'ferme'
        offre.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='candidat-recommend')
    def recommend_candidat(self, request, pk=None):
        offre_emploi = get_object_or_404(OffreEmploi, pk=pk)
        candidats = Candidat.objects.filter(disponible=True)
        if not candidats.exists():
            return Response({'message': 'Aucun candidat disponible.'})
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        resultats = []
        for candidat in candidats:
            prompt = (
                f"Offre : {offre_emploi.titre}\n"
                f"Description : {offre_emploi.description}\n"
                f"Competences requises : {offre_emploi.competences_requises}\n\n"
                f"Candidat : {candidat.user.first_name} {candidat.user.last_name}\n"
                f"Competences : {candidat.competences}\n"
                f"Experience : {candidat.experience}\n\n"
                'Retourne uniquement un objet JSON avec "score" (0-100) et "analyse" (string courte).'
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                )
                result = json.loads(response.choices[0].message.content)
                matching_result = MatchingResult.objects.create(
                    candidat=candidat, offre_emploi=offre_emploi,
                    score=result['score'], analyse=result['analyse'],
                )
                resultats.append(matching_result)
            except Exception as e:
                return Response(
                    {'message': f'Erreur OpenAI : {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        resultats.sort(key=lambda x: x.score, reverse=True)
        return Response(MatchingResultSerializer(resultats, many=True).data)


class CandidatureViewSet(viewsets.ModelViewSet):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer

    def create(self, request):
        candidat = get_object_or_404(Candidat, user=request.user)
        offre_id = request.data.get('offre')
        offre = get_object_or_404(OffreEmploi, pk=offre_id)
        if Candidature.objects.filter(candidat=candidat, offre_emploi=offre).exists():
            return Response(
                {'message': 'Vous avez déjà postulé à cette offre'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        candidature = Candidature.objects.create(
            candidat=candidat, offre_emploi=offre, statut='en attente',
        )
        return Response(CandidatureSerializer(candidature).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='mes-candidatures')
    def mes_candidatures(self, request):
        candidat = get_object_or_404(Candidat, user=request.user)
        candidatures = Candidature.objects.filter(candidat=candidat)
        return Response(CandidatureSerializer(candidatures, many=True).data)

    @action(detail=True, methods=['patch'], url_path='statut')
    def changer_statut(self, request, pk=None):
        candidature = get_object_or_404(Candidature, pk=pk)
        nouveau_statut = request.data.get('statut')
        valeurs_valides = ['en attente', 'acceptée', 'refusée']
        if nouveau_statut not in valeurs_valides:
            return Response(
                {'message': f'Statut invalide. Valeurs acceptées : {valeurs_valides}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        candidature.statut = nouveau_statut
        candidature.save()
        return Response(CandidatureSerializer(candidature).data)
