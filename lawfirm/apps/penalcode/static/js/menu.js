document.addEventListener('DOMContentLoaded', function () {
    const cards = document.querySelectorAll('.penal-modules-grid .module-card');
    cards.forEach(card => {
        card.addEventListener('click', function (event) {
            const targetUrl = card.getAttribute('href');
            if (targetUrl && targetUrl !== '#') {
                window.location.href = targetUrl;
            }
        });
    });
});