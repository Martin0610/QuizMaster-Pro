// QuizMaster Pro - Minimalist, High-Performance JS

document.addEventListener('DOMContentLoaded', function() {
    initThemeToggle();
    initAlertAutoDismiss();
});

// Theme toggle
function initThemeToggle() {
    const savedTheme = localStorage.getItem('qm_theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }

    const toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.setAttribute('aria-label', 'Toggle theme');
    toggleBtn.className = 'btn btn-secondary btn-sm';
    toggleBtn.style.position = 'fixed';
    toggleBtn.style.bottom = '1rem';
    toggleBtn.style.right = '1rem';
    toggleBtn.style.zIndex = '999';
    toggleBtn.style.boxShadow = 'var(--shadow-md)';
    toggleBtn.innerHTML = document.body.classList.contains('dark-theme') ? '☀️ Light' : '🌙 Dark';

    toggleBtn.addEventListener('click', function() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        toggleBtn.innerHTML = isDark ? '☀️ Light' : '🌙 Dark';
        localStorage.setItem('qm_theme', isDark ? 'dark' : 'light');
    });

    document.body.appendChild(toggleBtn);
}

// Auto dismiss flash alerts
function initAlertAutoDismiss() {
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.2s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 200);
        }, 4000);
    });
}

// Notifications
function showNotification(message, type = 'info') {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '1.25rem';
        container.style.right = '1.25rem';
        container.style.zIndex = '1000';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '0.5rem';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type}`;
    toast.style.margin = '0';
    toast.style.boxShadow = 'var(--shadow-md)';
    toast.style.minWidth = '240px';

    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `<strong>${icon}</strong> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 200);
    }, 3000);
}

// Sound effects (lightweight Web Audio - created only on explicit interaction)
let audioCtx = null;
function getAudioContext() {
    if (!audioCtx && (window.AudioContext || window.webkitAudioContext)) {
        const AudioClass = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioClass();
    }
    return audioCtx;
}

function playBeep(freq, duration) {
    try {
        const ctx = getAudioContext();
        if (!ctx || ctx.state === 'suspended') {
            if (ctx) ctx.resume();
        }
        if (!ctx) return;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.05, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + duration);
    } catch (e) {
        // Silently ignore audio playback errors
    }
}

// Animate numbers
function animateStats() {
    document.querySelectorAll('.stat-number').forEach(el => {
        const raw = el.textContent.trim();
        const target = parseInt(raw, 10);
        if (isNaN(target)) return;
        let count = 0;
        const step = Math.max(1, Math.floor(target / 20));
        const timer = setInterval(() => {
            count += step;
            if (count >= target) {
                el.textContent = raw.includes('+') ? `${target}+` : target;
                clearInterval(timer);
            } else {
                el.textContent = count;
            }
        }, 25);
    });
}

// Start quiz helper
function startQuiz(quizId) {
    window.location.href = `/quiz/${quizId}`;
}

// Export for global templates
window.QuizMaster = {
    showNotification,
    startQuiz,
    animateStats,
    playSuccessSound: () => playBeep(587.33, 0.15),
    playErrorSound: () => playBeep(220, 0.2),
    playAchievementSound: () => {
        playBeep(523.25, 0.1);
        setTimeout(() => playBeep(659.25, 0.15), 100);
    }
};