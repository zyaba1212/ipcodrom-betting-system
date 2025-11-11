from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from betting.models import Race, Horse

class Command(BaseCommand):
    help = 'Автоматический расчет завершенных забегов и определение победителей'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем автоматический расчет забегов...')
        
        # Находим забеги, которые уже должны были начаться
        races_to_settle = Race.objects.filter(
            status='scheduled',
            start_time__lte=timezone.now()  # Забеги, которые уже начались
        )
        
        settled_count = 0
        
        for race in races_to_settle:
            # Проверяем, прошло ли достаточно времени с начала забега
            time_since_start = timezone.now() - race.start_time
            if time_since_start >= timedelta(minutes=2):  # Забег длится 2 минуты
                self.stdout.write(f'Обрабатываем забег: {race.name}')
                
                # Автоматически выбираем победителя
                horses_in_race = Horse.objects.filter(race=race)
                if horses_in_race.exists():
                    horses_list = list(horses_in_race)
                    weights = [1.0 / float(horse.odds) for horse in horses_list]
                    
                    winner = random.choices(horses_list, weights=weights, k=1)[0]
                    race.winner = winner
                    race.status = 'finished'
                    race.save()
                    
                    # Рассчитываем выигрыши
                    race.settle_bets()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Забег "{race.name}" завершен. Победитель: {winner.name}')
                    )
                    settled_count += 1
                else:
                    race.status = 'cancelled'
                    race.save()
                    self.stdout.write(
                        self.style.WARNING(f'Забег "{race.name}" отменен (нет лошадей)')
                    )
        
        if settled_count == 0:
            self.stdout.write('Нет забегов для автоматического расчета')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Автоматически завершено {settled_count} забегов!')
            )