from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    ROLE_CHOICES = [
        ('candidat', 'Candidat'),
        ('recruteur', 'Recruteur'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telephone = models.CharField(
        max_length=20, blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Numero invalide.')]
    )
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'role']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.role}"


class Candidat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    competences = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    cv = models.FileField(upload_to='cv/', blank=True, null=True)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Recruteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    entreprise = models.CharField(max_length=200)
    secteur = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class OffreEmploi(models.Model):
    TYPE_CHOICES = [
        ('stage', 'Stage'), ('CDD', 'CDD'),
        ('CDI', 'CDI'), ('freelance', 'Freelance'),
    ]
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'), ('ferme', 'Ferme'),
    ]

    recruteur = models.ForeignKey(Recruteur, on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    competences_requises = models.TextField()
    type_contrat = models.CharField(max_length=20, choices=TYPE_CHOICES)
    localisation = models.CharField(max_length=200)
    date_limite = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.titre


class Candidature(models.Model):
    STATUT_CHOICES = [
        ('en attente', 'En attente'),
        ('acceptée', 'Acceptée'),
        ('refusée', 'Refusée'),
    ]

    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='candidatures')
    offre_emploi = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE, related_name='candidatures')
    date_candidature = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en attente')

    class Meta:
        unique_together = ('candidat', 'offre_emploi')

    def __str__(self):
        return f"{self.candidat} - {self.offre_emploi}"


class MatchingResult(models.Model):
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE)
    offre_emploi = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE)
    score = models.FloatField()
    analyse = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"{self.candidat} - {self.offre_emploi} : {self.score}"
