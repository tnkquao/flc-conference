// CAROUSEL
document.addEventListener('DOMContentLoaded', function () {
    const track = document.querySelector('.carousel-track');
    const dots = document.querySelectorAll('.carousel-dot');
    const pauseBtn = document.getElementById('pauseBtn');
    const playBtn = document.getElementById('playBtn');

    // Pause/play functionality
    pauseBtn.addEventListener('click', function () {
        track.style.animationPlayState = 'paused';
    });

    playBtn.addEventListener('click', function () {
        track.style.animationPlayState = 'running';
    });

    // Update dot indicators based on scroll position
    function updateDots() {
        const scrollPosition = Math.abs(parseInt(track.style.transform?.replace('translateX(', '').replace('%)', '') || 0));
        const activeIndex = Math.floor(scrollPosition / (33.333 + 0.666)) % 4; // 4 original cards

        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === activeIndex);
        });
    }
});

// COUNTDOWN TIMER
function updateCountdown() {
    const conferenceDate = new Date("2025-07-29T00:00:00");

    const now = new Date();
    const diff = conferenceDate - now;

    if (diff <= 0) {
        document.querySelector('.countdown-banner').innerHTML =
            '<span class="register-text">Conference Started - Join Now!</span>';
        return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    document.getElementById('countdown-days').textContent = days.toString().padStart(2, '0');
    document.getElementById('countdown-hours').textContent = hours.toString().padStart(2, '0');
    document.getElementById('countdown-minutes').textContent = minutes.toString().padStart(2, '0');
}

// Update immediately and then every minute
updateCountdown();
setInterval(updateCountdown, 60000);

/* PROMO VIDEO */
function openModal() {
    let modal = document.getElementById("videoModal");
    let video = document.getElementById("popupVideo");

    modal.style.display = "flex";
    video.play();
}

function closeModal() {
    let modal = document.getElementById("videoModal");
    let video = document.getElementById("popupVideo");

    video.pause();
    video.currentTime = 0;
    modal.style.display = "none";
}

window.onclick = function (event) {
    let modal = document.getElementById("videoModal");
    if (event.target === modal) {
        closeModal();
    }
};