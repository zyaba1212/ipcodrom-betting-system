from django.urls import path
from . import views

app_name = 'betting'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('terms/', views.terms, name='terms'),
    path('place-bet/', views.place_bet, name='place_bet'),
    path('place-bet/<int:race_id>/', views.place_bet_race, name='place_bet_race'),
    path('bet-history/', views.bet_history, name='bet_history'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('stats/', views.user_stats, name='user_stats'),
    path('profile/', views.user_profile, name='user_profile'),
    path('transactions/', views.transaction_history, name='transaction_history'),
]