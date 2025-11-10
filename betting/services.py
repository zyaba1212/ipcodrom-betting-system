from django.utils import timezone
from .models import Race, Bet, Profile
from django.db import transaction
import random

def calculate_race_results(race_id):
    """
    Автоматически рассчитывает результаты забега и распределяет выигрыши
    """
    try:
        race = Race.objects.get(id=race_id)
        
        if race.status != 'scheduled':
            return False, "Забег уже завершен или отменен"
        
        # Выбираем случайного победителя из лошадей забега
        horses = list(race.horses.all())
        if not horses:
            return False, "В забеге нет лошадей"
        
        winning_horse = random.choice(horses)
        
        # Обновляем статус забега
        race.status = 'finished'
        race.save()
        
        # Обрабатываем все ставки на этот забег
        with transaction.atomic():
            active_bets = Bet.objects.filter(race=race, status='active')
            
            for bet in active_bets:
                if bet.horse == winning_horse:
                    # Ставка выиграла - начисляем выигрыш
                    bet.status = 'won'
                    bet.settled_at = timezone.now()
                    bet.save()
                    
                    # Начисляем выигрыш на счет пользователя
                    user_profile = bet.user.profile
                    user_profile.balance += bet.potential_win
                    user_profile.save()
                    
                else:
                    # Ставка проиграла
                    bet.status = 'lost'
                    bet.settled_at = timezone.now()
                    bet.save()
        
        return True, f"Забег завершен! Победитель: {winning_horse.name}"
        
    except Race.DoesNotExist:
        return False, "Забег не найден"

def get_race_statistics(race_id):
    """
    Возвращает статистику по забегу
    """
    race = Race.objects.get(id=race_id)
    bets = Bet.objects.filter(race=race)
    
    stats = {
        'total_bets': bets.count(),
        'total_amount': sum(bet.amount for bet in bets),
        'active_bets': bets.filter(status='active').count(),
        'won_bets': bets.filter(status='won').count(),
        'lost_bets': bets.filter(status='lost').count(),
    }
    
    # Статистика по лошадям
    horse_stats = {}
    for horse in race.horses.all():
        horse_bets = bets.filter(horse=horse)
        horse_stats[horse.name] = {
            'bets_count': horse_bets.count(),
            'total_amount': sum(bet.amount for bet in horse_bets),
            'odds': horse.odds,
        }
    
    stats['horse_stats'] = horse_stats
    return stats