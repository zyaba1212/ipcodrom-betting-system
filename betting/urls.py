from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('race/<int:race_id>/', views.race_detail, name='race_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('bet/<int:participant_id>/', views.place_bet, name='place_bet'),
    path('test/', views.test_view, name='test'),
    path('history/', views.bet_history, name='bet_history'),
]