from django.contrib import admin
from .models import Horse, Jockey, Race, RaceParticipant, Bet

@admin.register(Horse)
class HorseAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'age', 'rating']
    list_filter = ['color', 'age']
    search_fields = ['name']

@admin.register(Jockey)
class JockeyAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'license_number']
    search_fields = ['first_name', 'last_name']

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheduled_time', 'status', 'distance', 'prize_pool']
    list_filter = ['status', 'scheduled_time']
    search_fields = ['title']

@admin.register(RaceParticipant)
class RaceParticipantAdmin(admin.ModelAdmin):
    list_display = ['race', 'horse', 'jockey', 'lane_number', 'win_odds']
    list_filter = ['race']

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['user', 'race_participant', 'bet_type', 'amount', 'potential_win', 'status']
    list_filter = ['bet_type', 'status', 'created_at']