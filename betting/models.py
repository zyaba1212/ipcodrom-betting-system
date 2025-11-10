from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Race(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланирован'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название забега")
    scheduled_time = models.DateTimeField(verbose_name="Время проведения")
    distance = models.IntegerField(verbose_name="Дистанция (метры)")
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Призовой фонд")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Статус")
    
    def __str__(self):
        return self.title
        
    def formatted_time(self):
        """Красивое отображение даты и времени"""
        return self.scheduled_time.strftime("%d.%m.%Y в %H:%M")

class Horse(models.Model):
    name = models.CharField(max_length=100, verbose_name="Кличка лошади")
    breed = models.CharField(max_length=100, verbose_name="Порода", default='Unknown')  # Добавьте default
    age = models.IntegerField(verbose_name="Возраст")
    
    def __str__(self):
        return self.name

class Jockey(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    license_number = models.CharField(max_length=50, verbose_name="Номер лицензии")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class RaceParticipant(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, verbose_name="Забег")
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE, verbose_name="Лошадь")
    jockey = models.ForeignKey(Jockey, on_delete=models.CASCADE, verbose_name="Жокей")
    lane_number = models.IntegerField(verbose_name="Номер дорожки")
    win_odds = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Коэффициент на победу")
    
    def __str__(self):
        return f"{self.horse.name} (Дорожка {self.lane_number})"

class Bet(models.Model):
    BET_TYPES = [
        ('win', 'На победу'),
        ('place', 'На показ'),
        ('show', 'На третье место'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('won', 'Выиграла'),
        ('lost', 'Проиграла'),
        ('cancelled', 'Отменена'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    race_participant = models.ForeignKey(RaceParticipant, on_delete=models.CASCADE, verbose_name="Участник забега")
    bet_type = models.CharField(max_length=10, choices=BET_TYPES, verbose_name="Тип ставки")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма ставки")
    potential_win = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Потенциальный выигрыш")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус ставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def save(self, *args, **kwargs):
        # Расчет потенциального выигрыша
        from decimal import Decimal
        if self.bet_type == 'win':
            self.potential_win = Decimal(float(self.amount) * float(self.race_participant.win_odds))
        elif self.bet_type == 'place':
            self.potential_win = Decimal(float(self.amount) * 1.8)  # Упрощенный коэффициент
        elif self.bet_type == 'show':
            self.potential_win = Decimal(float(self.amount) * 1.5)  # Упрощенный коэффициент
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Ставка {self.user.username} на {self.race_participant.horse.name} - {self.amount} руб."