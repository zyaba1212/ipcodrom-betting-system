// =============================================
// 🏇 ОБНОВЛЕННЫЙ ФАЙЛ betting.js
// =============================================

// 🔧 ОСНОВНЫЕ ФУНКЦИИ ДЛЯ СТАВОК

// Функция для открытия модального окна ставки
function openBetModal(raceId) {
    const selectedHorse = document.querySelector('.horse-card.selected');
    if (!selectedHorse) {
        showMessage('Пожалуйста, выберите лошадь для ставки', 'error');
        return;
    }

    const horseId = selectedHorse.dataset.horseId;
    const horseName = selectedHorse.dataset.horseName;
    const odds = selectedHorse.dataset.odds;

    document.getElementById('modal-race-id').value = raceId;
    document.getElementById('modal-horse-id').value = horseId;
    document.getElementById('selected-horse-info').innerHTML = `
        <h3>${horseName}</h3>
        <p>Коэффициент: <strong>${odds}</strong></p>
    `;

    calculatePotentialWin();
    document.getElementById('betModal').style.display = 'block';
}

// Функция закрытия модального окна
function closeModal() {
    document.getElementById('betModal').style.display = 'none';
}

// Функция выбора лошади
function selectHorse(element, raceId) {
    const raceCard = element.closest('.race-card');
    raceCard.querySelectorAll('.horse-card').forEach(card => {
        card.classList.remove('selected');
    });

    element.classList.add('selected');

    const betButton = raceCard.querySelector('.btn-bet');
    if (betButton) {
        betButton.textContent = `Ставка на ${element.dataset.horseName}`;
        betButton.onclick = () => openBetModal(raceId);
    }
}

// Функция расчета потенциального выигрыша
function calculatePotentialWin() {
    const amountInput = document.getElementById('bet-amount');
    const selectedHorse = document.querySelector('.horse-card.selected');
    const potentialWinElem = document.getElementById('potential-win');

    if (amountInput && selectedHorse && potentialWinElem) {
        const amount = parseFloat(amountInput.value) || 0;
        const odds = parseFloat(selectedHorse.dataset.odds);
        const potentialWin = amount * odds;
        potentialWinElem.textContent = potentialWin.toFixed(2) + ' ₽';
    }
}

// Функция размещения ставки
function placeBet() {
    const raceId = document.getElementById('modal-race-id').value;
    const horseId = document.getElementById('modal-horse-id').value;
    const amount = document.getElementById('bet-amount').value;

    if (!horseId) {
        alert('Пожалуйста, выберите лошадь');
        return;
    }

    const submitBtn = document.querySelector('#betForm button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<div class="loading"></div> Размещение...';
    submitBtn.disabled = true;

    fetch('/bet/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            race_id: raceId,
            horse_id: horseId,
            amount: parseFloat(amount)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const balanceElem = document.querySelector('.user-balance');
            if (balanceElem) {
                balanceElem.textContent = data.new_balance.toFixed(2) + ' ₽';
            }

            showMessage('Ставка успешно размещена!', 'success');
            closeModal();

            setTimeout(() => {
                window.location.href = '/betting/dashboard/';
            }, 1500);
        } else {
            showMessage('Ошибка: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showMessage('Ошибка сети: ' + error, 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// Функция получения CSRF токена
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Функция показа сообщений
function showMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.textContent = text;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            messageDiv.remove();
        }, 300);
    }, 3000);
}

// =============================================
// 🎨 УЛУЧШЕННЫЕ HOVER-ЭФФЕКТЫ
// =============================================

function enhanceHoverEffects() {
    console.log('🎯 Активация улучшенных hover-эффектов...');

    const interactiveElements = document.querySelectorAll(
        '.btn, .nav-link, .card-button, .btn-race, .dashboard-card, .feature, .race-card, .horse-card, .payment-option, .bet-item'
    );

    console.log(`📊 Найдено ${interactiveElements.length} интерактивных элементов`);

    interactiveElements.forEach((element) => {
        element.style.transition = 'all 0.3s ease';

        element.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';

            if (this.classList.contains('btn') || this.classList.contains('card-button') || this.classList.contains('btn-race')) {
                this.style.boxShadow = '0 8px 20px rgba(0,0,0,0.15)';
            }
        });

        element.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';

            if (this.classList.contains('dashboard-card') || this.classList.contains('feature') || this.classList.contains('race-card')) {
                this.style.boxShadow = '0 3px 10px rgba(0,0,0,0.1)';
            }
            if (this.classList.contains('bet-item')) {
                this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            }
        });

        element.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(0)';
            this.style.transition = 'all 0.1s ease';
        });

        element.addEventListener('mouseup', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });

    const navLinks = document.querySelectorAll('.nav-link, .nav-link-btn');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(255,255,255,0.15)';
        });

        link.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    const heroButtons = document.querySelectorAll('.cta-buttons .btn');
    heroButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.02)';
            this.style.boxShadow = '0 10px 25px rgba(0,0,0,0.2)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
    });

    console.log('✅ Улучшенные hover-эффекты активированы!');
}

// =============================================
// ✨ АНИМАЦИИ ПОЯВЛЕНИЯ
// =============================================

function addAppearAnimations() {
    const animatedElements = document.querySelectorAll('.dashboard-card, .feature, .race-card, .stat');

    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';

        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100 + index * 100);
    });
}

// =============================================
// 📝 УЛУЧШЕНИЕ ФОРМ
// =============================================

function enhanceFormInteractivity() {
    const formInputs = document.querySelectorAll('.form-input, input[type="number"], input[type="text"], input[type="email"], input[type="password"]');

    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.borderColor = '#3498db';
            this.style.boxShadow = '0 0 0 3px rgba(52, 152, 219, 0.1)';
            this.parentElement.style.transform = 'translateY(-2px)';
        });

        input.addEventListener('blur', function() {
            this.style.borderColor = '#e9ecef';
            this.style.boxShadow = '';
            this.parentElement.style.transform = 'translateY(0)';
        });
    });
}

// =============================================
// 🔐 ФУНКЦИИ ДЛЯ ФОРМ АУТЕНТИФИКАЦИИ
// =============================================

// Функция переключения видимости пароля
function togglePasswordVisibility(targetId) {
    const input = document.getElementById(targetId);
    const toggle = input.parentElement.querySelector('.password-toggle');
    
    if (input.type === 'password') {
        input.type = 'text';
        toggle.textContent = '🔒';
        toggle.setAttribute('aria-label', 'Скрыть пароль');
    } else {
        input.type = 'password';
        toggle.textContent = '👁️';
        toggle.setAttribute('aria-label', 'Показать пароль');
    }
}

// Функция проверки силы пароля
function checkPasswordStrength(password) {
    let strength = 0;
    const requirements = {
        length: password.length >= 8,
        upper: /[A-Z]/.test(password),
        lower: /[a-z]/.test(password),
        number: /[0-9]/.test(password)
    };

    Object.keys(requirements).forEach(key => {
        const element = document.getElementById(`req${key.charAt(0).toUpperCase() + key.slice(1)}`);
        if (element) {
            element.classList.toggle('met', requirements[key]);
            element.innerHTML = (requirements[key] ? '✓' : '✗') + element.textContent.slice(1);
        }
    });

    if (requirements.length) strength++;
    if (requirements.upper) strength++;
    if (requirements.lower) strength++;
    if (requirements.number) strength++;

    const strengthBar = document.getElementById('passwordStrength');
    const strengthText = document.getElementById('passwordText');
    
    if (strengthBar && strengthText) {
        strengthBar.className = 'strength-fill';
        
        switch(strength) {
            case 0:
            case 1:
                strengthBar.classList.add('strength-weak');
                strengthText.textContent = 'Слабый пароль';
                strengthText.style.color = '#e74c3c';
                break;
            case 2:
                strengthBar.classList.add('strength-fair');
                strengthText.textContent = 'Средний пароль';
                strengthText.style.color = '#f39c12';
                break;
            case 3:
                strengthBar.classList.add('strength-good');
                strengthText.textContent = 'Хороший пароль';
                strengthText.style.color = '#3498db';
                break;
            case 4:
                strengthBar.classList.add('strength-strong');
                strengthText.textContent = 'Сильный пароль';
                strengthText.style.color = '#27ae60';
                break;
        }
    }
}

// Функция проверки совпадения паролей
function checkPasswordMatch() {
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');
    const matchElement = document.getElementById('passwordMatch');
    
    if (!password1 || !password2 || !matchElement) return;
    
    if (!password2.value) {
        matchElement.textContent = '';
        return;
    }
    
    if (password1.value === password2.value) {
        matchElement.textContent = '✓ Пароли совпадают';
        matchElement.style.color = '#27ae60';
    } else {
        matchElement.textContent = '✗ Пароли не совпадают';
        matchElement.style.color = '#e74c3c';
    }
}

// Функция показа индикатора загрузки
function showLoadingState(button) {
    const btnText = button.querySelector('.btn-text');
    const btnLoading = button.querySelector('.btn-loading');
    
    if (btnText && btnLoading) {
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';
        button.disabled = true;
    }
}

// Функция скрытия индикатора загрузки
function hideLoadingState(button) {
    const btnText = button.querySelector('.btn-text');
    const btnLoading = button.querySelector('.btn-loading');
    
    if (btnText && btnLoading) {
        btnText.style.display = 'flex';
        btnLoading.style.display = 'none';
        button.disabled = false;
    }
}

// Инициализация форм аутентификации
function initAuthForms() {
    console.log('🔐 Инициализация форм аутентификации...');

    // Обработчики для переключения видимости пароля
    document.querySelectorAll('.password-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            togglePasswordVisibility(targetId);
        });
    });

    // Обработчики для формы регистрации
    const password1Input = document.getElementById('password1');
    const password2Input = document.getElementById('password2');
    const registerForm = document.getElementById('registerForm');
    const registerSubmitBtn = document.getElementById('registerSubmitBtn');

    if (password1Input) {
        password1Input.addEventListener('input', function() {
            checkPasswordStrength(this.value);
            checkPasswordMatch();
        });
    }

    if (password2Input) {
        password2Input.addEventListener('input', checkPasswordMatch);
    }

    if (registerForm && registerSubmitBtn) {
        registerForm.addEventListener('submit', function(e) {
            showLoadingState(registerSubmitBtn);
            
            setTimeout(() => {
                if (registerSubmitBtn.disabled) {
                    hideLoadingState(registerSubmitBtn);
                }
            }, 5000);
        });
    }

    // Обработчики для формы входа
    const loginForm = document.getElementById('loginForm');
    const loginSubmitBtn = document.getElementById('loginSubmitBtn');

    if (loginForm && loginSubmitBtn) {
        loginForm.addEventListener('submit', function(e) {
            showLoadingState(loginSubmitBtn);
            
            setTimeout(() => {
                if (loginSubmitBtn.disabled) {
                    hideLoadingState(loginSubmitBtn);
                }
            }, 5000);
        });
    }

    // Автофокус на первое поле формы
    const firstInput = document.querySelector('.auth-form .form-input');
    if (firstInput) {
        firstInput.focus();
    }

    console.log('✅ Формы аутентификации инициализированы');
}

// =============================================
// 📄 ФУНКЦИИ ДЛЯ РАЗНЫХ СТРАНИЦ
// =============================================

// Функции для страницы place_bet.html
function selectRace(raceId) {
    document.getElementById('race').value = raceId;
    updateHorses(raceId);
}

function updateHorses(raceId) {
    const horseSelect = document.getElementById('horse');
    if (!horseSelect) return;

    horseSelect.innerHTML = '<option value="">-- Выберите лошадь --</option>';

    // Заглушка - в реальном приложении здесь будет AJAX запрос
    const horses = [
        {id: 1, name: 'Молния', odds: 2.50},
        {id: 2, name: 'Стрела', odds: 3.00},
        {id: 3, name: 'Ветер', odds: 4.50},
        {id: 4, name: 'Звезда', odds: 2.80},
        {id: 5, name: 'Буря', odds: 5.00}
    ];

    horses.forEach(horse => {
        const option = document.createElement('option');
        option.value = horse.id;
        option.textContent = `${horse.name} (Коэффициент: ${horse.odds})`;
        option.dataset.odds = horse.odds;
        horseSelect.appendChild(option);
    });
}

function updatePotentialWin() {
    const amount = parseFloat(document.getElementById('amount').value) || 0;
    const horseSelect = document.getElementById('horse');
    const selectedOption = horseSelect.options[horseSelect.selectedIndex];
    const odds = parseFloat(selectedOption.dataset.odds) || 0;

    const potentialWin = amount * odds;
    const potentialWinElem = document.getElementById('potentialWin');
    if (potentialWinElem) {
        potentialWinElem.textContent = potentialWin.toFixed(2) + ' ₽';
    }
}

// Функции для страницы bet_history.html
function toggleBetDetails(element) {
    element.classList.toggle('expanded');
}

// =============================================
// 🚀 ОСНОВНАЯ ИНИЦИАЛИЗАЦИЯ
// =============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🏇 Беттинг система загружена и инициализирована!');
    
    // Включаем улучшенные hover-эффекты
    enhanceHoverEffects();
    
    // Добавляем анимации появления
    addAppearAnimations();
    
    // Улучшаем интерактивность форм
    enhanceFormInteractivity();
    
    // Инициализируем формы аутентификации
    initAuthForms();

    // Обработчики для модальных окон
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    // Обработчики для форм ставок
    const betForm = document.getElementById('betForm');
    if (betForm) {
        betForm.addEventListener('submit', function(e) {
            e.preventDefault();
            placeBet();
        });
    }

    const amountInput = document.getElementById('bet-amount');
    if (amountInput) {
        amountInput.addEventListener('input', calculatePotentialWin);
    }

    const amountInputMain = document.getElementById('amount');
    if (amountInputMain) {
        amountInputMain.addEventListener('input', updatePotentialWin);
    }

    const horseSelect = document.getElementById('horse');
    if (horseSelect) {
        horseSelect.addEventListener('change', updatePotentialWin);
    }

    // Закрытие модального окна по ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });

    // Закрытие модального окна по клику вне его
    window.onclick = function(event) {
        const modal = document.getElementById('betModal');
        if (event.target === modal) {
            closeModal();
        }
    }

    console.log('🎉 Все системы инициализированы!');
});

// Добавляем CSS анимации в документ
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

console.log('🏇 Обновленный betting.js успешно загружен!');

// =============================================
// 🔐 ФУНКЦИИ ВОССТАНОВЛЕНИЯ ПАРОЛЯ
// =============================================

// Функция показа модального окна восстановления пароля
function showPasswordRecovery() {
    const modal = document.getElementById('passwordRecoveryModal');
    if (modal) {
        modal.style.display = 'block';
        
        // Автофокус на поле email
        const emailInput = document.getElementById('recovery-email');
        if (emailInput) {
            setTimeout(() => {
                emailInput.focus();
            }, 300);
        }
    }
}

// Функция закрытия модального окна восстановления пароля
function closePasswordRecovery() {
    const modal = document.getElementById('passwordRecoveryModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Функция отправки запроса на восстановление пароля
function handlePasswordRecovery(event) {
    if (event) {
        event.preventDefault();
    }
    
    const emailInput = document.getElementById('recovery-email');
    const submitBtn = event ? event.target.querySelector('button[type="submit"]') : null;
    
    if (!emailInput) return;
    
    const email = emailInput.value.trim();
    
    if (!email) {
        showMessage('Введите email адрес', 'error');
        return;
    }
    
    // Показываем индикатор загрузки
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<div class="loading-spinner"></div> Отправка...';
        submitBtn.disabled = true;
        
        // Имитация отправки запроса
        setTimeout(() => {
            showMessage(`Инструкции по восстановлению пароля отправлены на email: ${email}`, 'success');
            closePasswordRecovery();
            
            // Восстанавливаем кнопку
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            emailInput.value = '';
        }, 2000);
    }
}

// =============================================
// 🎯 ИНИЦИАЛИЗАЦИЯ ФОРМ ВОССТАНОВЛЕНИЯ ПАРОЛЯ
// =============================================

function initPasswordRecovery() {
    console.log('🔐 Инициализация функций восстановления пароля...');
    
    // Обработчик для формы восстановления пароля
    const recoveryForm = document.getElementById('recoveryForm');
    if (recoveryForm) {
        recoveryForm.addEventListener('submit', handlePasswordRecovery);
    }
    
    // Обработчик для ссылки "Забыли пароль?"
    const forgotPasswordLinks = document.querySelectorAll('.forgot-password');
    forgotPasswordLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            showPasswordRecovery();
        });
    });
    
    // Закрытие модального окна по клику вне его
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('passwordRecoveryModal');
        if (event.target === modal) {
            closePasswordRecovery();
        }
    });
    
    // Закрытие по ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePasswordRecovery();
        }
    });
    
    console.log('✅ Функции восстановления пароля инициализированы');
}

// Добавляем инициализацию в основной блок
document.addEventListener('DOMContentLoaded', function() {
    // ... существующий код ...
    initPasswordRecovery();
});