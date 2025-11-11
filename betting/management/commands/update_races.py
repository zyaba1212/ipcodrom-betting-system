from django.core.management.base import BaseCommand
from betting.parsers import RaceDataParser

class Command(BaseCommand):
    help = 'Обновление данных о забегах из реальных источников'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем обновление данных о забегах...')
        
        try:
            RaceDataParser.update_races_from_real_sources()
            self.stdout.write(
                self.style.SUCCESS('Данные о забегах успешно обновлены!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при обновлении данных: {str(e)}')
            )