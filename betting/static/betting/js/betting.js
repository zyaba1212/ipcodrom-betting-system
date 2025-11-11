// betting.js - Основные функции для системы ставок

document.addEventListener('DOMContentLoaded', function() {
    initializeBettingSystem();
    setupEventListeners();
    initializePlaceBetRace();
});

function initializeBettingSystem() {
    console.log('Система ставок инициализирована');
    
    // Обновляем время каждую минуту
    setInterval(updateRaceTimers, 60000);
    updateRaceTimers();
    
    // Инициализируем формы
    initializeForms();
}

function setupEventListeners() {
    // Обработчики для динамического обновления коэффициентов
    const horseSelects = document.querySelectorAll('select[name="horse_id"]');
    horseSelects.forEach(select => {
        select.addEventListener('change', updateBetDetails);
    });
    
    // Обработчики для суммы ставки
    const amountInputs = document.querySelectorAll('input[name="amount"]');
    amountInputs.forEach(input => {
        input.addEventListener('input', updateBetDetails);
    });
    
    // Подтверждение действий
    setupConfirmations();
}

function initializePlaceBetRace() {
    // Инициализация страницы размещения ставки на конкретный забег
    const betForm = document.querySelector('.bet-form');
    if (betForm) {
        setupHorseSelection();
        setupAmountInput();
    }
}

function setupHorseSelection() {
    const horseRadios = document.querySelectorAll('input[name="horse_id"]');
    const amountInput = document.getElementById('amount');
    const potentialWinElement = document.querySelector('.potential-win');
    
    horseRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updatePotentialWin();
        });
    });
    
    if (amountInput && potentialWinElement) {
        amountInput.addEventListener('input', updatePotentialWin);
    }
}

function setupAmountInput() {
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        // Устанавливаем максимальное значение равное балансу пользователя
        const balanceElement = document.querySelector('.user-balance');
        if (balanceElement) {
            const balance = parseFloat(balanceElement.textContent);
            amountInput.max = balance;
        }
        
        // Валидация при вводе
        amountInput.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            const min = parseFloat(this.min);
            const max = parseFloat(this.max);
            
            if (value < min) {
                this.value = min;
                showMessage(`Минимальная ставка: ${min} ₽`, 'error');
            } else if (value > max) {
                this.value = max;
                showMessage(`Максимальная ставка: ${max} ₽`, 'error');
            }
            
            updatePotentialWin();
        });
    }
}

function updatePotentialWin() {
    const selectedHorse = document.querySelector('input[name="horse_id"]:checked');
    const amountInput = document.getElementById('amount');
    const potentialWinElement = document.querySelector('.potential-win');
    
    if (selectedHorse && amountInput && potentialWinElement) {
        const odds = parseFloat(selectedHorse.dataset.odds);
        const amount = parseFloat(amountInput.value) || 0;
        const potentialWin = amount * odds;
        
        potentialWinElement.textContent = potentialWin.toFixed(2) + ' ₽';
        
        // Подсвечиваем если выигрыш существенный
        if (potentialWin > amount * 2) {
            potentialWinElement.style.color = '#27ae60';
            potentialWinElement.style.fontWeight = 'bold';
        } else {
            potentialWinElement.style.color = '';
            potentialWinElement.style.fontWeight = '';
        }
    }
}

function updateRaceTimers() {
    const raceTimers = document.querySelectorAll('.race-timer');
    
    raceTimers.forEach(timer => {
        const startTime = new Date(timer.dataset.startTime);
        const now = new Date();
        const diff = startTime - now;
        
        if (diff > 0) {
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            timer.textContent = `Через ${hours}ч ${minutes}м`;
        } else {
            timer.textContent = 'Начался';
            timer.classList.add('race-started');
        }
    });
}

function updateBetDetails() {
    const form = this.closest('form');
    if (!form) return;
    
    const horseSelect = form.querySelector('select[name="horse_id"]');
    const amountInput = form.querySelector('input[name="amount"]');
    const potentialWinElement = form.querySelector('.potential-win');
    
    if (horseSelect && amountInput && potentialWinElement) {
        const selectedOption = horseSelect.options[horseSelect.selectedIndex];
        const odds = parseFloat(selectedOption.dataset.odds || 1);
        const amount = parseFloat(amountInput.value) || 0;
        const potentialWin = amount * odds;
        
        potentialWinElement.textContent = potentialWin.toFixed(2) + ' ₽';
    }
}

function initializeForms() {
    // Валидация форм ставок
    const betForms = document.querySelectorAll('.bet-form');
    betForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const amountInput = this.querySelector('input[name="amount"]');
            const balanceElement = document.querySelector('.user-balance');
            const horseSelected = this.querySelector('input[name="horse_id"]:checked') || 
                                 this.querySelector('select[name="horse_id"] option:checked');
            
            if (!horseSelected) {
                e.preventDefault();
                showMessage('Выберите лошадь для ставки', 'error');
                return;
            }
            
            if (amountInput && balanceElement) {
                const amount = parseFloat(amountInput.value);
                const balance = parseFloat(balanceElement.textContent);
                
                if (amount < 10) {
                    e.preventDefault();
                    showMessage('Минимальная сумма ставки - 10 ₽', 'error');
                    return;
                }
                
                if (amount > balance) {
                    e.preventDefault();
                    showMessage('Недостаточно средств на балансе', 'error');
                    return;
                }
            }
        });
    });
    
    // Валидация форм пополнения/вывода
    const transactionForms = document.querySelectorAll('.transaction-form');
    transactionForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const amountInput = this.querySelector('input[name="amount"]');
            if (amountInput) {
                const amount = parseFloat(amountInput.value);
                const minAmount = parseFloat(amountInput.min) || 0;
                
                if (amount < minAmount) {
                    e.preventDefault();
                    showMessage(`Минимальная сумма - ${minAmount} ₽`, 'error');
                }
            }
        });
    });
}

function setupConfirmations() {
    // Подтверждение выхода
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    logoutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите выйти?')) {
                e.preventDefault();
            }
        });
    });
    
    // Подтверждение вывода средств
    const withdrawForms = document.querySelectorAll('form[action*="withdraw"]');
    withdrawForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const amountInput = this.querySelector('input[name="amount"]');
            if (amountInput) {
                const amount = parseFloat(amountInput.value);
                if (!confirm(`Подтвердите вывод ${amount} ₽`)) {
                    e.preventDefault();
                }
            }
        });
    });
}

function showMessage(text, type = 'info') {
    // Создаем элемент сообщения
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    
    // Добавляем в начало контента
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        const messagesContainer = mainContent.querySelector('.messages') || createMessagesContainer();
        messagesContainer.insertBefore(messageDiv, messagesContainer.firstChild);
        
        // Автоматически удаляем через 5 секунд
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(container, mainContent.firstChild);
    }
    return container;
}

// Вспомогательные функции
function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Экспортируем функции для использования в других скриптах
window.BettingSystem = {
    showMessage,
    formatCurrency,
    formatDate,
    updateBetDetails,
    updatePotentialWin
};