from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.balance}₽"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Horse(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=50)
    age = models.IntegerField()
    owner = models.CharField(max_length=100)
    odds = models.DecimalField(max_digits=5, decimal_places=2)
    min_bet = models.DecimalField(max_digits=8, decimal_places=2, default=10.00)

    def __str__(self):
        return f"{self.name} ({self.odds})"

class Race(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланирован'),
        ('ongoing', 'В процессе'),
        ('finished', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    name = models.CharField(max_length=200)
    date_time = models.DateTimeField()
    distance = models.IntegerField(help_text="Дистанция в метрах")
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    horses = models.ManyToManyField(Horse, through='RaceParticipant')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class RaceParticipant(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE)
    position = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['race', 'horse']

class Bet(models.Model):
    BET_STATUS = [
        ('active', 'Активна'),
        ('won', 'Выиграна'),
        ('lost', 'Проиграна'),
        ('cancelled', 'Отменена'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    potential_win = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BET_STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Автоматически рассчитываем потенциальный выигрыш
        self.potential_win = self.amount * self.horse.odds
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.amount}₽ на {self.horse.name}"

class Bonus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)