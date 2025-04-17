// CAROUSEL
// document.addEventListener('DOMContentLoaded', function () {
//     const track = document.querySelector('.carousel-track');
//     const dots = document.querySelectorAll('.carousel-dot');
//     const pauseBtn = document.getElementById('pauseBtn');
//     const playBtn = document.getElementById('playBtn');

//     // Pause/play functionality
//     pauseBtn.addEventListener('click', function () {
//         track.style.animationPlayState = 'paused';
//     });

//     playBtn.addEventListener('click', function () {
//         track.style.animationPlayState = 'running';
//     });

//     // Update dot indicators based on scroll position
//     function updateDots() {
//         const scrollPosition = Math.abs(parseInt(track.style.transform?.replace('translateX(', '').replace('%)', '') || 0));
//         const activeIndex = Math.floor(scrollPosition / (33.333 + 0.666)) % 4; // 4 original cards

//         dots.forEach((dot, index) => {
//             dot.classList.toggle('active', index === activeIndex);
//         });
//     }
// });

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


/*Speaker Modal */
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('speakerModal');
    const modalImg = document.getElementById('modalSpeakerImage');
    const modalName = document.getElementById('modalSpeakerName');
    const modalTitle = document.getElementById('modalSpeakerTitle');
    const modalBio = document.getElementById('modalSpeakerBio');
    const closeBtn = document.querySelector('.close-modal');

    // Handle "About" button clicks
    document.querySelectorAll('.about-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent anchor default behavior
            const speakerItem = this.closest('[data-reveal-item]');

            // Extract data from original structure
            modalImg.src = speakerItem.querySelector('img').src;
            modalImg.alt = speakerItem.querySelector('h3').textContent;
            modalName.textContent = speakerItem.querySelector('h3').textContent;
            modalTitle.textContent = speakerItem.querySelector('.is-speakers').textContent;
            modalBio.innerHTML = speakerItem.querySelector('.speaker-bio').innerHTML;

            // Show modal
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        });
    });

    // Close modal when clicking (X) or outside
    closeBtn.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    function closeModal() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Re-enable scrolling
    }

    // Simple JavaScript for the slideshow
    let currentSlide = 0;
    const slideshow = document.getElementById('venueSlideshow');
    const slides = slideshow.getElementsByTagName('img');
    const slideCount = slides.length;

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slideCount;
        slideshow.style.transform = `translateX(-${currentSlide * 100}%)`;
    }

    // Change slide every 5 seconds
    setInterval(nextSlide, 2000);


    // Event schedule toggle
    function toggleEventSchedule(element) {
        const content = element.nextElementSibling;
        if (content.classList.contains('expanded')) {
            content.style.maxHeight = '0';
            content.classList.remove('expanded');
        } else {
            content.style.maxHeight = content.scrollHeight + 'px';
            content.classList.add('expanded');
        }
    }
});