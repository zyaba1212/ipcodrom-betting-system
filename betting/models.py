from django.db import models
from django.contrib.auth.models import User

class Horse(models.Model):
    name = models.CharField(max_length=100, verbose_name="Кличка")
    color = models.CharField(max_length=50, verbose_name="Масть") 
    age = models.IntegerField(verbose_name="Возраст")
    rating = models.IntegerField(default=1000, verbose_name="Рейтинг")
    
    def __str__(self):
        return f"{self.name} ({self.color})"

class Jockey(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    license_number = models.CharField(max_length=50, verbose_name="Номер лицензии")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Race(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланирован'),
        ('in_progress', 'В процессе'),
        ('finished', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название забега")
    scheduled_time = models.DateTimeField(verbose_name="Дата и время старта")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    distance = models.IntegerField(verbose_name="Дистанция (метры)")
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Призовой фонд")
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_time}"

class RaceParticipant(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, verbose_name="Забег")
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE, verbose_name="Лошадь")
    jockey = models.ForeignKey(Jockey, on_delete=models.CASCADE, verbose_name="Жокей")
    lane_number = models.IntegerField(verbose_name="Номер дорожки")
    win_odds = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="Коэффициент на победу")
    final_position = models.IntegerField(null=True, blank=True, verbose_name="Финальная позиция")
    
    class Meta:
        unique_together = ['race', 'lane_number']
    
    def __str__(self):
        return f"{self.horse.name} (Дорожка {self.lane_number}) в забеге '{self.race.title}'"

class Bet(models.Model):
    BET_TYPES = [
        ('win', 'На победу'),
        ('place', 'На попадание в призы (Топ-3)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    race_participant = models.ForeignKey(RaceParticipant, on_delete=models.CASCADE, verbose_name="Участник забега")
    bet_type = models.CharField(max_length=10, choices=BET_TYPES, verbose_name="Тип ставки")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма ставки")
    potential_win = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Потенциальный выигрыш")
    status = models.CharField(max_length=20, default='active', verbose_name="Статус ставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def save(self, *args, **kwargs):
        from decimal import Decimal
        if self.bet_type == 'win':
            self.potential_win = Decimal(float(self.amount) * float(self.race_participant.win_odds))
        elif self.bet_type == 'place':
            self.potential_win = Decimal(float(self.amount) * 1.5)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Ставка {self.user.username} на {self.race_participant.horse.name} - {self.amount} руб."