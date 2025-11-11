from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='betting_profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
    def get_transaction_history(self):
        """Получить историю транзакций пользователя"""
        return Transaction.objects.filter(user=self.user)
class Race(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланирован'),
        ('in_progress', 'В процессе'),
        ('finished', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey('Horse', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_races')

    def __str__(self):
        return self.name

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def settle_bets(self):
        """Рассчитать выигрыши по ставкам после завершения забега"""
        if self.status == 'finished' and self.winner:
            winning_bets = Bet.objects.filter(race=self, horse=self.winner, is_settled=False)
            for bet in winning_bets:
                bet.is_winner = True
                bet.is_settled = True
                bet.settled_at = timezone.now()
                bet.save()
                
                # Начисляем выигрыш
                user_profile = bet.user.betting_profile
                user_profile.balance += bet.potential_win
                user_profile.save()
                
                # Записываем транзакцию выигрыша
                Transaction.objects.create(
                    user=bet.user,
                    transaction_type='win',
                    amount=bet.potential_win,
                    description=f'Выигрыш по ставке - {bet.horse.name}'
                )
        
        # Также помечаем проигравшие ставки
        losing_bets = Bet.objects.filter(race=self, is_settled=False).exclude(horse=self.winner)
        for bet in losing_bets:
            bet.is_winner = False
            bet.is_settled = True
            bet.settled_at = timezone.now()
            bet.save()

class Horse(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='horses')
    name = models.CharField(max_length=100)
    odds = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    color = models.CharField(max_length=50, blank=True)
    jockey = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.odds})"

class Bet(models.Model):
    BET_TYPES = [
        ('win', 'Победа'),
        ('place', 'Место'),
        ('show', 'Показ'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE)
    bet_type = models.CharField(max_length=10, choices=BET_TYPES, default='win')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    odds = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    potential_win = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_winner = models.BooleanField(default=False)
    is_settled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Автоматически рассчитываем потенциальный выигрыш
        self.potential_win = self.amount * self.odds
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.horse.name} - {self.amount}₽"

# Сигналы для автоматического создания профиля
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Пополнение'),
        ('withdraw', 'Вывод'),
        ('bet', 'Ставка'),
        ('win', 'Выигрыш'),
        ('refund', 'Возврат'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.amount}₽"
    
    class Meta:
        ordering = ['-created_at']