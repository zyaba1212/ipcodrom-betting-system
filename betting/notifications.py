from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def send_bet_notification(user, bet, bet_type):
    """
    Отправляет уведомления о ставках
    """
    if bet_type == 'placed':
        message = f'Ваша ставка на {bet.horse.name} принята! Сумма: {bet.amount}₽, потенциальный выигрыш: {bet.potential_win}₽'
        messages.success(user, message)
        
        # Отправка email (если настроено)
        try:
            send_mail(
                'Ставка принята - Ипподром',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except:
            pass
            
    elif bet_type == 'won':
        message = f'🎉 Поздравляем! Ваша ставка на {bet.horse.name} выиграла! Выигрыш: {bet.potential_win}₽'
        messages.success(user, message)
        
    elif bet_type == 'lost':
        message = f'😔 Ставка на {bet.horse.name} не сыграла. Сумма ставки: {bet.amount}₽'
        messages.info(user, message)

def send_race_notification(race, notification_type):
    """
    Уведомления о забегах
    """
    if notification_type == 'completed':
        message = f'Забег "{race.name}" завершен! Результаты доступны в истории ставок.'
        # Здесь можно добавить массовую рассылку пользователям