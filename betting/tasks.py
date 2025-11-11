from django.utils import timezone
from datetime import timedelta
import random
from .models import Race, Horse

def auto_settle_races():
    """
    Автоматический расчет завершенных забегов
    """
    # Находим забеги, которые ДОЛЖНЫ БЫЛИ начаться и еще не завершены
    races_to_settle = Race.objects.filter(
        status='scheduled',
        start_time__lte=timezone.now()  # ← Ищем забеги, которые уже должны были начаться
    )
    
    results = []
    
    for race in races_to_settle:
        # Проверяем, прошло ли достаточно времени с начала забега
        time_since_start = timezone.now() - race.start_time
        if time_since_start >= timedelta(minutes=2):  # Забег длится 2 минуты
            # Автоматически выбираем победителя
            horses_in_race = Horse.objects.filter(race=race)
            if horses_in_race.exists():
                # Более реалистичный выбор победителя
                horses_list = list(horses_in_race)
                weights = [1.0 / float(horse.odds) for horse in horses_list]
                
                winner = random.choices(horses_list, weights=weights, k=1)[0]
                race.winner = winner
                race.status = 'finished'
                race.save()
                
                # Рассчитываем выигрыши
                race.settle_bets()
                
                results.append(f'Забег "{race.name}" завершен. Победитель: {winner.name}')
            else:
                # Если нет лошадей, отменяем забег
                race.status = 'cancelled'
                race.save()
                results.append(f'Забег "{race.name}" отменен (нет лошадей)')
    
    return results