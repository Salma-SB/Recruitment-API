from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Candidat, Recruteur, OffreEmploi, Candidature


def create_candidat_user(email='candidat@test.com'):
    user = User.objects.create_user(
        username=email, email=email, password='testpass123',
        first_name='Jean', last_name='Dupont', role='candidat',
    )
    return user, Candidat.objects.create(user=user)


def create_recruteur_user(email='recruteur@test.com'):
    user = User.objects.create_user(
        username=email, email=email, password='testpass123',
        first_name='Marie', last_name='Martin', role='recruteur',
    )
    return user, Recruteur.objects.create(user=user, entreprise='Tech Corp')


def create_offre(recruteur):
    return OffreEmploi.objects.create(
        recruteur=recruteur,
        titre='Développeur Python',
        description='Poste de dev Python',
        competences_requises='Python, Django',
        type_contrat='CDI',
        localisation='Paris',
        date_limite=date(2026, 12, 31),
    )


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_inscription_candidat(self):
        r = self.client.post('/api/auth/register/candidat/', {
            'first_name': 'Test', 'last_name': 'User',
            'email': 'new@test.com', 'password': 'testpass123',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_inscription_recruteur(self):
        r = self.client.post('/api/auth/register/recruteur/', {
            'first_name': 'Alice', 'last_name': 'Martin',
            'email': 'rec@test.com', 'password': 'testpass123',
            'entreprise': 'Corp SA',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_login_retourne_token(self):
        create_candidat_user('login@test.com')
        r = self.client.post('/api/auth/login/',
            {'email': 'login@test.com', 'password': 'testpass123'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('access', r.data)

    def test_acces_sans_token_interdit(self):
        r = self.client.get('/api/candidats/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class OffreEmploiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.recruteur_user, self.recruteur = create_recruteur_user()
        self.client.force_authenticate(user=self.recruteur_user)

    def test_creation_offre(self):
        r = self.client.post('/api/offres-emploi/', {
            'titre': 'Dev Python', 'description': 'Description du poste',
            'competences_requises': 'Python', 'type_contrat': 'CDI',
            'localisation': 'Paris', 'date_limite': '2026-12-31',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_liste_offres(self):
        create_offre(self.recruteur)
        r = self.client.get('/api/offres-emploi/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(r.data['results']), 1)

    def test_suppression_ferme_statut(self):
        offre = create_offre(self.recruteur)
        self.client.delete(f'/api/offres-emploi/{offre.id}/')
        offre.refresh_from_db()
        self.assertEqual(offre.statut, 'ferme')


class CandidatureTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.candidat_user, self.candidat = create_candidat_user()
        _, self.recruteur = create_recruteur_user()
        self.offre = create_offre(self.recruteur)
        self.client.force_authenticate(user=self.candidat_user)

    def test_creation_candidature(self):
        r = self.client.post('/api/candidatures/', {'offre': self.offre.id}, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['statut'], 'en attente')

    def test_double_candidature_interdite(self):
        self.client.post('/api/candidatures/', {'offre': self.offre.id}, format='json')
        r = self.client.post('/api/candidatures/', {'offre': self.offre.id}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mes_candidatures(self):
        Candidature.objects.create(candidat=self.candidat, offre_emploi=self.offre)
        r = self.client.get('/api/candidatures/mes-candidatures/')
        self.assertEqual(len(r.data), 1)

    def test_changer_statut(self):
        c = Candidature.objects.create(candidat=self.candidat, offre_emploi=self.offre)
        r = self.client.patch(f'/api/candidatures/{c.id}/statut/',
            {'statut': 'acceptée'}, format='json')
        self.assertEqual(r.data['statut'], 'acceptée')

    def test_statut_invalide_rejete(self):
        c = Candidature.objects.create(candidat=self.candidat, offre_emploi=self.offre)
        r = self.client.patch(f'/api/candidatures/{c.id}/statut/',
            {'statut': 'approuvée'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
