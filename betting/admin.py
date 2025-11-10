from django.contrib import admin
from .models import Profile, Race, Horse, Bet

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at']
    search_fields = ['user__username']
    list_filter = ['created_at']

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_time', 'distance', 'prize_pool', 'status', 'horses_count']
    list_filter = ['status', 'date_time']
    search_fields = ['name']
    date_hierarchy = 'date_time'
    
    def horses_count(self, obj):
        return obj.horses.count()
    horses_count.short_description = 'Кол-во лошадей'

@admin.register(Horse)
class HorseAdmin(admin.ModelAdmin):
    list_display = ['name', 'breed', 'age', 'owner', 'odds', 'min_bet', 'races_count']
    list_filter = ['breed']
    search_fields = ['name', 'owner']
    list_editable = ['odds', 'min_bet']
    
    def races_count(self, obj):
        return obj.race_set.count()
    races_count.short_description = 'Участий в забегах'

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['user', 'race', 'horse', 'amount', 'potential_win', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'race']
    search_fields = ['user__username', 'horse__name']
    readonly_fields = ['potential_win', 'created_at']
    actions = ['mark_as_won', 'mark_as_lost']
    
    def mark_as_won(self, request, queryset):
        updated = queryset.update(status='won')
        self.message_user(request, f'{updated} ставок отмечены как выигранные')
    mark_as_won.short_description = "Отметить как выигранные"
    
    def mark_as_lost(self, request, queryset):
        updated = queryset.update(status='lost')
        self.message_user(request, f'{updated} ставок отмечены как проигранные')
    mark_as_lost.short_description = "Отметить как проигранные"