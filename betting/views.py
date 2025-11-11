from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from .models import UserProfile, Race, Horse, Bet
from decimal import Decimal
from .models import UserProfile, Race, Horse, Bet, Transaction 

def home(request):
    # Автоматически рассчитываем завершенные забеги
    from .tasks import auto_settle_races
    try:
        settlement_results = auto_settle_races()
        if settlement_results:
            messages.info(request, 'Некоторые забеги были автоматически завершены')
    except Exception as e:
        # Игнорируем ошибки в автоматическом расчете
        pass

    # Проверяем, есть ли запланированные забеги
    scheduled_races = Race.objects.filter(status='scheduled')
    if not scheduled_races.exists():
        from .parsers import RaceDataParser
        try:
            RaceDataParser.update_races_from_real_sources()
            messages.info(request, 'Данные о забегах обновлены!')
        except Exception as e:
            messages.warning(request, 'Не удалось обновить данные о забегах')

    context = {}
    if request.user.is_authenticated:
        try:
            user_profile = request.user.betting_profile
            context['user_profile'] = user_profile
            
            # Мотивационная статистика пользователя
            user_bets = Bet.objects.filter(user=request.user)
            total_bets = user_bets.count()
            won_bets = user_bets.filter(is_winner=True).count()
            active_bets = user_bets.filter(is_settled=False).count()
            total_won = user_bets.filter(is_winner=True).aggregate(Sum('potential_win'))['potential_win__sum'] or 0
            total_wagered = user_bets.aggregate(Sum('amount'))['amount__sum'] or 0
            
            # Рассчитываем мотивационные показатели
            if total_bets > 0:
                win_rate = (won_bets / total_bets) * 100
            else:
                win_rate = 0
            
            # Определяем уровень игрока
            if total_bets == 0:
                player_level = "Новичок"
                level_description = "Сделайте первую ставку чтобы начать!"
            elif win_rate >= 50:
                player_level = "Эксперт"
                level_description = "Отличные результаты! Продолжайте в том же духе!"
            elif win_rate >= 30:
                player_level = "Опытный"
                level_description = "Хорошая игра! Вы на верном пути!"
            elif win_rate >= 15:
                player_level = "Любитель" 
                level_description = "Неплохо! Удача на вашей стороне!"
            else:
                player_level = "Новичок"
                level_description = "Практика ведет к совершенству!"
            
            # Следующая цель
            if total_bets < 5:
                next_goal = "Сделать 5 ставок"
            elif won_bets == 0:
                next_goal = "Одержать первую победу"
            elif total_won < 1000:
                next_goal = "Выиграть 1000 ₽"
            elif win_rate < 20:
                next_goal = "Достичь 20% побед"
            else:
                next_goal = "Увеличить баланс на 50%"
            
            context.update({
                'total_bets': total_bets,
                'won_bets': won_bets,
                'active_bets': active_bets,
                'total_won': total_won,
                'total_wagered': total_wagered,
                'win_rate': round(win_rate, 1),
                'player_level': player_level,
                'level_description': level_description,
                'next_goal': next_goal,
            })
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)
            context['user_profile'] = user_profile

    # Ближайшие забеги
    upcoming_races = Race.objects.filter(
        status='scheduled',
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]
    
    # Недавно завершенные забеги
    recent_races = Race.objects.filter(
        status='finished'
    ).order_by('-start_time')[:3]

    context.update({
        'upcoming_races': upcoming_races,
        'recent_races': recent_races
    })

    return render(request, 'betting/home.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not all([username, email, password1]):
            messages.error(request, 'Все поля обязательны')
            return render(request, 'betting/register.html')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'betting/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Имя пользователя занято')
            return render(request, 'betting/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email уже зарегистрирован')
            return render(request, 'betting/register.html')

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user = authenticate(username=username, password=password1)
            if user:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('betting:home')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')

    return render(request, 'betting/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('betting:home')
        else:
            messages.error(request, 'Неверные данные')
    return render(request, 'betting/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('betting:home')

def terms(request):
    return render(request, 'betting/terms.html')

@login_required
def place_bet(request):
    races = Race.objects.filter(status='scheduled').order_by('start_time')
    user_profile = request.user.betting_profile

    context = {
        'races': races,
        'user_profile': user_profile
    }
    return render(request, 'betting/place_bet.html', context)

@login_required
def place_bet_race(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    horses = Horse.objects.filter(race=race)
    user_profile = request.user.betting_profile

    if request.method == 'POST':
        horse_id = request.POST.get('horse_id')
        amount = request.POST.get('amount')
        bet_type = request.POST.get('bet_type', 'win')

        try:
            horse = Horse.objects.get(id=horse_id)
            amount = Decimal(amount)

            # Корректируем коэффициенты в зависимости от типа ставки
            base_odds = horse.odds
            if bet_type == 'place':
                adjusted_odds = base_odds * Decimal('0.6')
                bet_type_display = 'место'
            elif bet_type == 'show':
                adjusted_odds = base_odds * Decimal('0.4')
                bet_type_display = 'показ'
            else:
                adjusted_odds = base_odds
                bet_type_display = 'победу'

            if amount < Decimal('10'):
                messages.error(request, 'Минимальная сумма ставки - 10 ₽')
            elif amount > user_profile.balance:
                messages.error(request, 'Недостаточно средств')
            else:
                # Создаем ставку
                bet = Bet.objects.create(
                    user=request.user,
                    race=race,
                    horse=horse,
                    bet_type=bet_type,
                    amount=amount,
                    odds=adjusted_odds
                )
                # Списываем средства
                user_profile.balance -= amount
                user_profile.save()
                
                # Записываем транзакцию ставки
                Transaction.objects.create(
                    user=request.user,
                    transaction_type='bet',
                    amount=amount,
                    description=f'Ставка на {bet_type_display} - {horse.name}'
                )

                messages.success(request, f'Ставка на {bet_type_display} ({horse.name}) принята! Сумма: {amount} ₽, Коэффициент: {adjusted_odds}')
                return redirect('betting:home')

        except (Horse.DoesNotExist, ValueError) as e:
            messages.error(request, 'Ошибка при размещении ставки')

    context = {
        'race': race,
        'horses': horses,
        'user_profile': user_profile
    }
    return render(request, 'betting/place_bet_race.html', context)

@login_required
def bet_history(request):
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    user_profile = request.user.betting_profile
    
    context = {
        'bets': bets,
        'user_profile': user_profile
    }
    return render(request, 'betting/bet_history.html', context)

@login_required
def deposit(request):
    try:
        user_profile = request.user.betting_profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = Decimal(amount)
            if amount >= 10:
                # Пополняем баланс
                user_profile.balance += amount
                user_profile.save()
                
                # Записываем транзакцию
                Transaction.objects.create(
                    user=request.user,
                    transaction_type='deposit',
                    amount=amount,
                    description=f'Пополнение счета'
                )
                
                messages.success(request, f'Баланс пополнен на {amount} ₽')
                return redirect('betting:home')
            else:
                messages.error(request, 'Минимальная сумма пополнения - 10 ₽')
        except (ValueError, TypeError):
            messages.error(request, 'Введите корректную сумму')

    return render(request, 'betting/deposit.html', {'user_profile': user_profile})

@login_required
def withdraw(request):
    try:
        user_profile = request.user.betting_profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        method = request.POST.get('method')
        details = request.POST.get('details')

        try:
            amount = Decimal(amount)
            if amount >= 100:
                if amount <= user_profile.balance:
                    # Списываем средства
                    user_profile.balance -= amount
                    user_profile.save()
                    
                    # Записываем транзакцию
                    Transaction.objects.create(
                        user=request.user,
                        transaction_type='withdraw',
                        amount=amount,
                        description=f'Вывод средств ({method})'
                    )
                    
                    messages.success(request, f'Запрос на вывод {amount} ₽ отправлен')
                    return redirect('betting:home')
                else:
                    messages.error(request, 'Недостаточно средств')
            else:
                messages.error(request, 'Минимальная сумма вывода - 100 ₽')
        except (ValueError, TypeError):
            messages.error(request, 'Введите корректную сумму')

    return render(request, 'betting/withdraw.html', {'user_profile': user_profile})

@login_required
def user_stats(request):
    user_profile = request.user.betting_profile
    user_bets = Bet.objects.filter(user=request.user)
    
    # Общая статистика
    total_bets = user_bets.count()
    active_bets = user_bets.filter(is_settled=False).count()
    won_bets = user_bets.filter(is_winner=True).count()
    lost_bets = user_bets.filter(is_settled=True, is_winner=False).count()
    
    # Финансовая статистика
    total_wagered = user_bets.aggregate(Sum('amount'))['amount__sum'] or 0
    total_won = user_bets.filter(is_winner=True).aggregate(Sum('potential_win'))['potential_win__sum'] or 0
    net_profit = total_won - total_wagered
    
    # Статистика по типам ставок (ИСПРАВЛЕНО: убираем models.)
    bet_types = user_bets.values('bet_type').annotate(
        count=Count('id'),
        won=Count('id', filter=Q(is_winner=True))  # Убрали models.
    )
    
    context = {
        'user_profile': user_profile,
        'total_bets': total_bets,
        'active_bets': active_bets,
        'won_bets': won_bets,
        'lost_bets': lost_bets,
        'total_wagered': total_wagered,
        'total_won': total_won,
        'net_profit': net_profit,
        'bet_types': bet_types,
    }
    return render(request, 'betting/user_stats.html', context)

@login_required
def user_profile(request):
    user_profile = request.user.betting_profile
    user_bets = Bet.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'user_profile': user_profile,
        'recent_bets': user_bets
    }
    return render(request, 'betting/user_profile.html', context)

@login_required
def transaction_history(request):
    """История транзакций пользователя"""
    transactions = Transaction.objects.filter(user=request.user)
    user_profile = request.user.betting_profile
    
    # Статистика по типам транзакций
    deposit_total = transactions.filter(transaction_type='deposit').aggregate(Sum('amount'))['amount__sum'] or 0
    withdraw_total = transactions.filter(transaction_type='withdraw').aggregate(Sum('amount'))['amount__sum'] or 0
    win_total = transactions.filter(transaction_type='win').aggregate(Sum('amount'))['amount__sum'] or 0
    bet_total = transactions.filter(transaction_type='bet').aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'transactions': transactions,
        'user_profile': user_profile,
        'deposit_total': deposit_total,
        'withdraw_total': withdraw_total,
        'win_total': win_total,
        'bet_total': bet_total,
    }
    return render(request, 'betting/transaction_history.html', context)