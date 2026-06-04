from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Candidat, Recruteur, OffreEmploi, Candidature, MatchingResult


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'telephone', 'photo', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


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
