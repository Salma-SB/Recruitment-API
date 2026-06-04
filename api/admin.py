from django.contrib import admin
from .models import User, Candidat, Recruteur, OffreEmploi, Candidature, MatchingResult


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role',)
    search_fields = ('email', 'first_name', 'last_name')


@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(Recruteur)
class RecruteurAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'entreprise', 'secteur')
    search_fields = ('user__email', 'entreprise')


@admin.register(OffreEmploi)
class OffreEmploiAdmin(admin.ModelAdmin):
    list_display = ('titre', 'recruteur', 'type_contrat', 'localisation', 'statut', 'date_limite')
    list_filter = ('statut', 'type_contrat')
    search_fields = ('titre', 'description')


@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'offre_emploi', 'statut', 'date_candidature')
    list_filter = ('statut',)


@admin.register(MatchingResult)
class MatchingResultAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'offre_emploi', 'score', 'created_at')
    ordering = ('-score',)
