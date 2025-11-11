from django.core.management.base import BaseCommand
from betting.parsers import RaceDataParser

class Command(BaseCommand):
    help = 'Создание тестовых данных для системы ставок'

    def handle(self, *args, **options):
        self.stdout.write('Создание реалистичных тестовых данных...')
        
        # Используем парсер для создания реалистичных данных
        RaceDataParser.update_races_from_real_sources()
        
        self.stdout.write(
            self.style.SUCCESS('Реалистичные тестовые данные успешно созданы!')
        )