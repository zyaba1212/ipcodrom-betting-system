from django.contrib import admin
from django.utils import timezone
from .models import UserProfile, Race, Horse, Bet
from .parsers import RaceDataParser

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at', 'updated_at']
    search_fields = ['user__username']
    list_filter = ['created_at']

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'status', 'winner', 'created_at']
    list_filter = ['status', 'start_time']
    search_fields = ['name']
    actions = ['mark_as_finished', 'cancel_race', 'update_races_data']
    
    # Ограничиваем выбор победителя только лошадьми этого забега
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "winner":
            # Получаем ID забега из URL
            race_id = request.resolver_match.kwargs.get('object_id')
            if race_id:
                kwargs["queryset"] = Horse.objects.filter(race_id=race_id)
            else:
                kwargs["queryset"] = Horse.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def mark_as_finished(self, request, queryset):
        for race in queryset:
            race.status = 'finished'
            race.save()
            # Автоматически рассчитываем выигрыши
            race.settle_bets()
        self.message_user(request, "Выбранные забеги завершены")
    mark_as_finished.short_description = "Завершить выбранные забеги"
    
    def cancel_race(self, request, queryset):
        updated = queryset.update(status='cancelled')
        # Возвращаем ставки при отмене забега
        for race in queryset:
            bets = Bet.objects.filter(race=race, is_settled=False)
            for bet in bets:
                user_profile = bet.user.betting_profile
                user_profile.balance += bet.amount
                user_profile.save()
                bet.is_settled = True
                bet.save()
        self.message_user(request, f"{updated} забегов отменено")
    cancel_race.short_description = "Отменить выбранные забеги"
    
    def update_races_data(self, request, queryset):
        try:
            RaceDataParser.update_races_from_real_sources()
            self.message_user(request, "Данные о забегах обновлены")
        except Exception as e:
            self.message_user(request, f"Ошибка при обновлении: {str(e)}")
    update_races_data.short_description = "Обновить данные о забегах"

@admin.register(Horse)
class HorseAdmin(admin.ModelAdmin):
    list_display = ['name', 'race', 'odds', 'color', 'jockey']
    list_filter = ['race']
    search_fields = ['name']
    list_editable = ['odds']

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['user', 'race', 'horse', 'bet_type', 'amount', 'odds', 'potential_win', 'is_winner', 'is_settled', 'created_at']
    list_filter = ['is_winner', 'is_settled', 'bet_type', 'race']
    search_fields = ['user__username', 'horse__name']
    readonly_fields = ['potential_win', 'created_at']
    actions = ['settle_bets']
    
    def settle_bets(self, request, queryset):
        for bet in queryset:
            if not bet.is_settled:
                bet.is_settled = True
                bet.settled_at = timezone.now()
                bet.save()
                if bet.is_winner:
                    user_profile = bet.user.betting_profile
                    user_profile.balance += bet.potential_win
                    user_profile.save()
        self.message_user(request, "Выбранные ставки рассчитаны")
    settle_bets.short_description = "Рассчитать выбранные ставки"