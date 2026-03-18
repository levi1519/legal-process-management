// ── Password show/hide toggles ──
document.querySelectorAll('.pw-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
        const targetId = btn.dataset.target;
        const input = document.getElementById(targetId);
        if (!input) return;
        const isHidden = input.type === 'password';
        input.type = isHidden ? 'text' : 'password';
        const icon = btn.querySelector('i');
        icon.className = isHidden ? 'bi bi-eye-slash' : 'bi bi-eye';
    });
});

// ── Password strength indicator ──
const pwInput = document.getElementById('id_new_password1');
const fillEl = document.getElementById('pwStrengthFill');
const textEl = document.getElementById('pwStrengthText');

const levels = [
    { min: 0, max: 1, pct: '15%', color: 'var(--danger)', label: 'Muy débil' },
    { min: 2, max: 2, pct: '35%', color: 'var(--warning)', label: 'Débil' },
    { min: 3, max: 3, pct: '65%', color: 'var(--gold)', label: 'Aceptable' },
    { min: 4, max: 4, pct: '85%', color: 'var(--success)', label: 'Fuerte' },
    { min: 5, max: 99, pct: '100%', color: 'var(--success)', label: 'Muy fuerte' },
];

function scorePassword(pw) {
    let score = 0;
    if (pw.length >= 8) score++;
    if (pw.length >= 12) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    return score;
}

pwInput?.addEventListener('input', () => {
    const pw = pwInput.value;
    const score = pw.length === 0 ? -1 : scorePassword(pw);

    if (score === -1) {
        fillEl.style.width = '0';
        fillEl.style.background = '';
        textEl.textContent = '';
        return;
    }

    const lvl = levels.find(l => score >= l.min && score <= l.max) || levels[0];
    fillEl.style.width = lvl.pct;
    fillEl.style.background = lvl.color;
    textEl.textContent = `Seguridad: ${lvl.label}`;
    textEl.style.color = lvl.color;
});