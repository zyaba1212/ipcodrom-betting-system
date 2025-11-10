from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Bet, Race, Horse

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['race', 'horse', 'amount']
        widgets = {
            'race': forms.Select(attrs={'class': 'form-control'}),
            'horse': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '10', 'step': '10'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        initial_race = kwargs.pop('race', None)
        super().__init__(*args, **kwargs)
        
        if initial_race:
            self.fields['race'].initial = initial_race
            self.fields['race'].disabled = True
            self.fields['horse'].queryset = Horse.objects.filter(
                race__id=initial_race.id
            )
        else:
            self.fields['race'].queryset = Race.objects.filter(
                status='scheduled'
            )
        
        if self.user and self.user.profile:
            self.fields['amount'].widget.attrs.update({
                'max': str(self.user.profile.balance)
            })