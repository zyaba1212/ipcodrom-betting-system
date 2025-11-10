from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('bet/', views.place_bet, name='place_bet'),
    path('bet/<int:race_id>/', views.place_bet, name='place_bet_race'),
    path('history/', views.bet_history, name='bet_history'),
    path('race/<int:race_id>/', views.race_detail, name='race_detail'),
    path('deposit/', views.deposit_funds, name='deposit'),
    
    # Админские URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('complete-race/<int:race_id>/', views.complete_race, name='complete_race'),
    path('race-statistics/<int:race_id>/', views.race_statistics, name='race_statistics'),
]