from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('race/<int:race_id>/', views.race_detail, name='race_detail'),
    path('place_bet/<int:participant_id>/', views.place_bet, name='place_bet'),
    path('bet_history/', views.bet_history, name='bet_history'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]