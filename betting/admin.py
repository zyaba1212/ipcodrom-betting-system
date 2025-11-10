from django.contrib import admin
from .models import Race, Horse, Jockey, RaceParticipant, Bet

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheduled_time', 'distance', 'prize_pool', 'status']
    list_filter = ['status', 'scheduled_time']
    search_fields = ['title']

@admin.register(Horse)
class HorseAdmin(admin.ModelAdmin):
    list_display = ['name', 'breed', 'age']
    list_filter = ['breed']
    search_fields = ['name']

@admin.register(Jockey)
class JockeyAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'license_number']
    search_fields = ['first_name', 'last_name']

@admin.register(RaceParticipant)
class RaceParticipantAdmin(admin.ModelAdmin):
    list_display = ['race', 'horse', 'jockey', 'lane_number', 'win_odds']
    list_filter = ['race']
    search_fields = ['horse__name', 'jockey__first_name', 'jockey__last_name']

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['user', 'race_participant', 'bet_type', 'amount', 'potential_win', 'status', 'created_at']
    list_filter = ['bet_type', 'status', 'created_at']
    search_fields = ['user__username', 'race_participant__horse__name']