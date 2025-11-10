from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Race, Horse, Bet, Profile
from .forms import UserRegistrationForm, BetForm
from .services import calculate_race_results, get_race_statistics
from .notifications import send_bet_notification

def home(request):
    races = Race.objects.filter(date_time__gte=timezone.now()).order_by('date_time')[:5]
    
    context = {
        'races': races,
    }
    
    if request.user.is_authenticated:
        active_bets = Bet.objects.filter(user=request.user, status='active')
        won_bets = Bet.objects.filter(user=request.user, status='won')
        
        context.update({
            'active_bets_count': active_bets.count(),
            'total_won': sum(bet.potential_win for bet in won_bets),
        })
    
    return render(request, 'betting/home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! На ваш счет начислено 1000₽.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'betting/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'betting/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')

@login_required
def place_bet(request, race_id=None):
    race = None
    if race_id:
        race = get_object_or_404(Race, id=race_id)
    
    if request.method == 'POST':
        form = BetForm(request.POST, user=request.user, race=race)
        if form.is_valid():
            bet = form.save(commit=False)
            bet.user = request.user
            
            if request.user.profile.balance >= bet.amount:
                request.user.profile.balance -= bet.amount
                request.user.profile.save()
                
                bet.save()
                send_bet_notification(request.user, bet, 'placed')  # Уведомление
                return redirect('home')
            else:
                messages.error(request, 'Недостаточно средств на счете!')
    else:
        form = BetForm(user=request.user, race=race)
    
    races = Race.objects.filter(status='scheduled', date_time__gte=timezone.now())
    return render(request, 'betting/place_bet.html', {
        'form': form,
        'races': races,
        'selected_race': race
    })

@login_required
def bet_history(request):
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'betting/bet_history.html', {'bets': bets})

@login_required
def race_detail(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    return render(request, 'betting/race_detail.html', {'race': race})

@login_required
def deposit_funds(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            if amount < 10:
                messages.error(request, 'Минимальная сумма пополнения - 10 рублей')
            else:
                from decimal import Decimal
                request.user.profile.balance += Decimal(str(amount))
                request.user.profile.save()
                messages.success(request, f'Счет успешно пополнен на {amount} рублей')
                return redirect('home')
        except (ValueError, TypeError):
            messages.error(request, 'Введите корректную сумму')
    
    return render(request, 'betting/deposit.html')

@login_required
def admin_dashboard(request):
    """Панель управления для администраторов"""
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещен")
        return redirect('home')
    
    races = Race.objects.all().order_by('-date_time')
    total_bets = Bet.objects.count()
    total_users = Profile.objects.count()
    
    context = {
        'races': races,
        'total_bets': total_bets,
        'total_users': total_users,
    }
    return render(request, 'betting/admin_dashboard.html', context)

@login_required
def complete_race(request, race_id):
    """Завершение забега и расчет результатов"""
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещен")
        return redirect('home')
    
    success, message = calculate_race_results(race_id)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('admin_dashboard')

@login_required
def race_statistics(request, race_id):
    """Статистика по забегу"""
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещен")
        return redirect('home')
    
    stats = get_race_statistics(race_id)
    race = Race.objects.get(id=race_id)
    
    context = {
        'race': race,
        'stats': stats,
    }
    return render(request, 'betting/race_statistics.html', context)

@login_required
def user_stats(request):
    """Статистика пользователя"""
    from django.db.models import Count, Sum, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Базовая статистика
    user_bets = Bet.objects.filter(user=request.user)
    total_bets = user_bets.count()
    won_bets = user_bets.filter(status='won').count()
    lost_bets = user_bets.filter(status='lost').count()
    
    # Финансовая статистика
    total_won = user_bets.filter(status='won').aggregate(Sum('potential_win'))['potential_win__sum'] or 0
    total_lost = user_bets.filter(status='lost').aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_won - total_lost
    
    # Процент побед
    win_percentage = round((won_bets / total_bets * 100) if total_bets > 0 else 0, 1)
    
    # Простая заглушка для monthly_stats (можно улучшить)
    monthly_stats = [
        {'month': 'Янв', 'win_percentage': 65},
        {'month': 'Фев', 'win_percentage': 45},
        {'month': 'Мар', 'win_percentage': 70},
        {'month': 'Апр', 'win_percentage': 55},
        {'month': 'Май', 'win_percentage': 80},
    ]
    
    context = {
        'total_bets': total_bets,
        'won_bets': won_bets,
        'lost_bets': lost_bets,
        'total_won': total_won,
        'total_lost': total_lost,
        'net_profit': net_profit,
        'win_percentage': win_percentage,
        'monthly_stats': monthly_stats,
    }
    
    return render(request, 'betting/user_stats.html', context)