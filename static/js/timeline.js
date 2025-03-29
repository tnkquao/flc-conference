/**
 * Interactive Event Timeline with Animated Milestone Markers
 * First Love Church Conference
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeTimeline();
});

// Conference start and end dates
const conferenceStartDate = new Date('2025-07-20');
const conferenceEndDate = new Date('2025-07-25');

// For testing/preview purposes - uncomment to simulate the conference is active
// const mockToday = new Date('2025-07-22'); // Simulates day 3 of the conference
// const originalNow = Date.now;
// Date.now = function() { return mockToday.getTime(); };

/**
 * Initialize the interactive timeline
 */
function initializeTimeline() {
    // Add click event listeners to milestone markers
    const markers = document.querySelectorAll('.milestone-marker');
    const items = document.querySelectorAll('.timeline-item');
    
    // Animate timeline items on load
    setTimeout(() => {
        items.forEach((item, index) => {
            setTimeout(() => {
                item.classList.remove('timeline-hidden');
                item.classList.add('timeline-visible');
            }, index * 200);
        });
    }, 500);

    // Add marker click functionality
    markers.forEach(marker => {
        marker.addEventListener('click', function() {
            const parent = this.closest('.timeline-item');
            const details = parent.querySelector('.milestone-details');
            
            if (details.classList.contains('active')) {
                details.classList.remove('active');
            } else {
                // Close all other open details first
                document.querySelectorAll('.milestone-details.active').forEach(el => {
                    el.classList.remove('active');
                });
                
                // Open this one
                details.classList.add('active');
            }
        });
    });
    
    // Initialize timeline progress
    updateProgressBar();
    
    // Set initial marker states
    setMarkerStates();
}

/**
 * Update the progress bar based on current date
 */
function updateProgressBar() {
    const today = new Date();
    const progressBar = document.querySelector('.timeline-progress');
    const daysCounter = document.querySelector('.days-counter');
    
    // Calculate days between start and end
    const totalDays = (conferenceEndDate - conferenceStartDate) / (1000 * 60 * 60 * 24);
    
    // Calculate days until conference starts
    const daysUntilStart = Math.ceil((conferenceStartDate - today) / (1000 * 60 * 60 * 24));
    
    // Calculate days from start to today
    const daysPassed = Math.max(0, Math.min(totalDays, Math.ceil((today - conferenceStartDate) / (1000 * 60 * 60 * 24))));
    
    // Calculate progress percentage
    let progressPercentage = 0;
    let counterText = '';
    
    if (today < conferenceStartDate) {
        // Conference hasn't started yet
        progressPercentage = 0;
        counterText = `${daysUntilStart} day${daysUntilStart !== 1 ? 's' : ''} until conference starts`;
    } else if (today > conferenceEndDate) {
        // Conference has ended
        progressPercentage = 100;
        counterText = 'Conference has ended';
    } else {
        // Conference is in progress
        progressPercentage = (daysPassed / totalDays) * 100;
        const daysRemaining = totalDays - daysPassed;
        counterText = `Conference in progress: Day ${daysPassed + 1} of ${totalDays + 1}`;
    }
    
    // Update the DOM
    progressBar.style.width = `${progressPercentage}%`;
    daysCounter.textContent = counterText;
}

/**
 * Set the visual state of the milestone markers based on the current date
 */
function setMarkerStates() {
    const today = new Date();
    const timelineItems = document.querySelectorAll('.timeline-item');
    
    timelineItems.forEach((item, index) => {
        const dateText = item.querySelector('.timeline-date').innerText;
        const marker = item.querySelector('.milestone-marker');
        
        // Parse the date from the format "JUL\n20"
        const month = dateText.split('\n')[0];
        const day = dateText.split('\n')[1];
        
        // Create a Date object for this milestone
        const milestoneDate = new Date(`2025-${getMonthNumber(month)}-${day}`);
        
        // Compare with today's date
        if (today >= milestoneDate) {
            // Past or current day
            marker.style.backgroundColor = '#e11d20';
            marker.style.transform = 'scale(1.2)';
        } else {
            // Future day
            marker.style.backgroundColor = '#aaa';
        }
    });
}

/**
 * Convert month abbreviation to month number
 */
function getMonthNumber(monthAbbr) {
    const months = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08', 
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    };
    
    return months[monthAbbr] || '01';
}