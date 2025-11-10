from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def time_until(dt):
    """Показывает время до события"""
    now = timezone.now()
    if dt > now:
        diff = dt - now
        if diff.days > 0:
            return f"через {diff.days} дн."
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"через {hours} ч."
        else:
            minutes = diff.seconds // 60
            return f"через {minutes} мин."
    return "начался"

@register.filter
def format_odds(odds):
    """Форматирует коэффициенты"""
    return f"{odds:.2f}"

@register.simple_tag
def get_random_tip():
    """Случайные советы для ставок"""
    tips = [
        "💡 Изучите историю лошади перед ставкой",
        "💡 Обращайте внимание на погодные условия",
        "💡 Молодые лошади часто показывают неожиданные результаты",
        "💡 Высокие коэффициенты = высокий риск",
        "💡 Диверсифицируйте ставки на разные забеги"
    ]
    import random
    return random.choice(tips)