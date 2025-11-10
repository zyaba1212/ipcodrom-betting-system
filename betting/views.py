from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Race, RaceParticipant, Bet

def home(request):
    """Главная страница со списком забегов"""
    races = Race.objects.all().order_by('-scheduled_time')
    return render(request, 'betting/home.html', {'races': races})

def race_detail(request, race_id):
    """Детальная страница забега"""
    race = Race.objects.get(id=race_id)
    participants = RaceParticipant.objects.filter(race=race)
    return render(request, 'betting/race_detail.html', {
        'race': race,
        'participants': participants
    })

@login_required
def place_bet(request, participant_id):
    """Размещение ставки"""
    participant = RaceParticipant.objects.get(id=participant_id)
    
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            bet_type = request.POST.get('bet_type')
            
            # Создание ставки
            bet = Bet(
                user=request.user,
                race_participant=participant,
                bet_type=bet_type,
                amount=amount
            )
            bet.save()  # Автоматически рассчитается potential_win
            
            messages.success(request, f'Ставка на {participant.horse.name} на сумму {amount} руб. размещена!')
            return redirect('race_detail', race_id=participant.race_id)
            
        except Exception as e:
            messages.error(request, f'Ошибка при размещении ставки: {str(e)}')
    
    return render(request, 'betting/place_bet.html', {
        'participant': participant
    })

@login_required
def bet_history(request):
    """История ставок пользователя"""
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'betting/bet_history.html', {'bets': bets})

def login_view(request):
    """Страница входа"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'betting/login.html', {'form': form})

def register(request):
    """Страница регистрации"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'betting/register.html', {'form': form})

def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('home')