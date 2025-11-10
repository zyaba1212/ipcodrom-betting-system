from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Race, RaceParticipant, Bet

def home(request):
    races = Race.objects.all().order_by('scheduled_time')
    return render(request, 'betting/home.html', {'races': races})

def race_detail(request, race_id):
    race = Race.objects.get(id=race_id)
    participants = RaceParticipant.objects.filter(race=race)
    return render(request, 'betting/race_detail.html', {
        'race': race,
        'participants': participants
    })

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'betting/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'betting/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')

@login_required
def place_bet(request, participant_id):
    participant = RaceParticipant.objects.get(id=participant_id)
    
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            bet_type = request.POST.get('bet_type')
            
            # Создаем ставку
            bet = Bet(
                user=request.user,
                race_participant=participant,
                bet_type=bet_type,
                amount=amount
            )
            bet.save()  # Автоматически рассчитается potential_win
            
            messages.success(request, f'Ставка на {participant.horse.name} на сумму {amount} руб. размещена!')
            return redirect('race_detail', race_id=participant.race.id)
            
        except Exception as e:
            messages.error(request, f'Ошибка при размещении ставки: {str(e)}')
    
    return render(request, 'betting/place_bet.html', {
        'participant': participant
    })

@login_required
def bet_history(request):
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'betting/bet_history.html', {'bets': bets})

def test_view(request):
    from django.http import HttpResponse
    return HttpResponse("Тест работает!")