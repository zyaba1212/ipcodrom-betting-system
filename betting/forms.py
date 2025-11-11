from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Bet, Race, Horse

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Имя пользователя'
    }))
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Пароль'
    }))
    
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Подтвердите пароль'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class BetForm(forms.ModelForm):
    horse = forms.ModelChoiceField(
        queryset=Horse.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    amount = forms.DecimalField(
        min_value=10,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Сумма ставки',
            'min': '10',
            'step': '0.01'
        })
    )
    
    bet_type = forms.ChoiceField(
        choices=Bet.BET_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Bet
        fields = ['horse', 'bet_type', 'amount']

    def __init__(self, *args, **kwargs):
        self.race = kwargs.pop('race', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.race:
            self.fields['horse'].queryset = Horse.objects.filter(race=self.race)
        
        if self.user and hasattr(self.user, 'betting_profile'):
            user_balance = self.user.betting_profile.balance
            self.fields['amount'].widget.attrs['max'] = str(user_balance)

class DepositForm(forms.Form):
    amount = forms.DecimalField(
        min_value=10,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Сумма пополнения',
            'min': '10',
            'step': '0.01'
        })
    )

class WithdrawForm(forms.Form):
    amount = forms.DecimalField(
        min_value=100,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Сумма вывода',
            'min': '100',
            'step': '0.01'
        })
    )
    
    method = forms.ChoiceField(
        choices=[
            ('bank_card', 'Банковская карта'),
            ('electronic', 'Электронный кошелек'),
            ('bank_transfer', 'Банковский перевод')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    details = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Реквизиты'
        })
    )