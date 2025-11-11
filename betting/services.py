from django.utils import timezone
from .models import Race, Bet, UserProfile
from django.db.models import Sum, Count
from django.contrib.auth.models import User

class BettingService:
    @staticmethod
    def calculate_potential_win(amount, odds):
        """Рассчитать потенциальный выигрыш"""
        return amount * odds
    
    @staticmethod
    def place_bet(user, race, horse, amount, bet_type='win'):
        """Разместить ставку"""
        try:
            user_profile = user.betting_profile
            
            # Проверяем достаточно ли средств
            if amount > user_profile.balance:
                return False, "Недостаточно средств"
            
            if amount < 10:
                return False, "Минимальная сумма ставки - 10 ₽"
            
            # Создаем ставку
            bet = Bet.objects.create(
                user=user,
                race=race,
                horse=horse,
                bet_type=bet_type,
                amount=amount,
                odds=horse.odds
            )
            
            # Списываем средства
            user_profile.balance -= amount
            user_profile.save()
            
            return True, "Ставка успешно размещена"
            
        except Exception as e:
            return False, f"Ошибка при размещении ставки: {str(e)}"
    
    @staticmethod
    def settle_race(race, winner_horse):
        """Рассчитать результаты забега"""
        try:
            race.winner = winner_horse
            race.status = 'finished'
            race.save()
            
            # Рассчитываем выигрыши
            winning_bets = Bet.objects.filter(
                race=race, 
                horse=winner_horse, 
                is_settled=False
            )
            
            for bet in winning_bets:
                bet.is_winner = True
                bet.is_settled = True
                bet.settled_at = timezone.now()
                bet.save()
                
                # Начисляем выигрыш
                user_profile = bet.user.betting_profile
                user_profile.balance += bet.potential_win
                user_profile.save()
            
            return True, f"Забег завершен. Победитель: {winner_horse.name}"
            
        except Exception as e:
            return False, f"Ошибка при расчете забега: {str(e)}"

class AnalyticsService:
    @staticmethod
    def get_user_stats(user):
        """Получить статистику пользователя"""
        user_bets = Bet.objects.filter(user=user)
        
        stats = {
            'total_bets': user_bets.count(),
            'active_bets': user_bets.filter(is_settled=False).count(),
            'won_bets': user_bets.filter(is_winner=True).count(),
            'lost_bets': user_bets.filter(is_settled=True, is_winner=False).count(),
            'total_wagered': user_bets.aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_won': user_bets.filter(is_winner=True).aggregate(Sum('potential_win'))['potential_win__sum'] or 0,
        }
        
        stats['net_profit'] = stats['total_won'] - stats['total_wagered']
        stats['win_rate'] = (stats['won_bets'] / stats['total_bets'] * 100) if stats['total_bets'] > 0 else 0
        
        return stats
    
    @staticmethod
    def get_race_stats(race):
        """Получить статистику по забегу"""
        race_bets = Bet.objects.filter(race=race)
        
        stats = {
            'total_bets': race_bets.count(),
            'total_amount': race_bets.aggregate(Sum('amount'))['amount__sum'] or 0,
            'bets_per_horse': race_bets.values('horse__name').annotate(
                count=Count('id'),
                total=Sum('amount')
            ),
        }
        
        return stats

class NotificationService:
    @staticmethod
    def send_bet_confirmation(user, bet):
        """Отправить подтверждение ставки"""
        # Здесь может быть логика отправки email или уведомлений
        message = f"Ваша ставка на {bet.horse.name} принята. Сумма: {bet.amount} ₽"
        return message
    
    @staticmethod
    def send_win_notification(user, bet):
        """Отправить уведомление о выигрыше"""
        message = f"Поздравляем! Ваша ставка на {bet.horse.name} выиграла! Выигрыш: {bet.potential_win} ₽"
        return message