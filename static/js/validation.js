document.addEventListener("DOMContentLoaded", function() {
    // Get all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');

    // Registration form validation
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(event) {
            if (!validateRegistrationForm()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            registrationForm.classList.add('was-validated');
        });
    }

    // Accommodation form validation
    const accommodationForm = document.getElementById('accommodationForm');
    if (accommodationForm) {
        accommodationForm.addEventListener('submit', function(event) {
            if (!validateAccommodationForm()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            accommodationForm.classList.add('was-validated');
        });
    }

    // Generic form validation for all forms with needs-validation class
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
});

// Validate registration form
function validateRegistrationForm() {
    let isValid = true;
    
    // Name validation
    const nameField = document.getElementById('name');
    if (nameField && nameField.value.trim() === '') {
        nameField.setCustomValidity('Please enter your full name');
        isValid = false;
    } else if (nameField) {
        nameField.setCustomValidity('');
    }
    
    // Email validation
    const emailField = document.getElementById('email');
    if (emailField) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (emailField.value.trim() === '') {
            emailField.setCustomValidity('Please enter your email address');
            isValid = false;
        } else if (!emailPattern.test(emailField.value)) {
            emailField.setCustomValidity('Please enter a valid email address');
            isValid = false;
        } else {
            emailField.setCustomValidity('');
        }
    }
    
    // Phone validation
    const phoneField = document.getElementById('phone');
    if (phoneField) {
        const phonePattern = /^[0-9+\-\s()]+$/;
        if (phoneField.value.trim() === '') {
            phoneField.setCustomValidity('Please enter your phone number');
            isValid = false;
        } else if (!phonePattern.test(phoneField.value)) {
            phoneField.setCustomValidity('Please enter a valid phone number');
            isValid = false;
        } else {
            phoneField.setCustomValidity('');
        }
    }
    
    return isValid;
}

// Validate accommodation form
function validateAccommodationForm() {
    let isValid = true;
    
    // Room validation
    const roomField = document.getElementById('room');
    if (roomField && roomField.value.trim() === '') {
        roomField.setCustomValidity('Please select a room type');
        isValid = false;
    } else if (roomField) {
        roomField.setCustomValidity('');
    }
    
    // Nights validation
    const nightsField = document.getElementById('nights');
    if (nightsField) {
        if (nightsField.value.trim() === '') {
            nightsField.setCustomValidity('Please enter the number of nights');
            isValid = false;
        } else if (isNaN(nightsField.value) || parseInt(nightsField.value) <= 0) {
            nightsField.setCustomValidity('Please enter a valid number of nights');
            isValid = false;
        } else {
            nightsField.setCustomValidity('');
        }
    }
    
    return isValid;
}

// Show feedback to user
function showFeedback(element, message, isValid) {
    // Find or create feedback element
    let feedback = element.nextElementSibling;
    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
        feedback = document.createElement('div');
        feedback.className = isValid ? 'valid-feedback' : 'invalid-feedback';
        element.parentNode.insertBefore(feedback, element.nextSibling);
    }
    
    feedback.textContent = message;
    element.classList.toggle('is-valid', isValid);
    element.classList.toggle('is-invalid', !isValid);
}

// Update total cost in accommodation form
function updateTotal() {
    const roomSelect = document.getElementById('room');
    const nightsInput = document.getElementById('nights');
    const totalElement = document.getElementById('totalCost');
    
    if (roomSelect && nightsInput && totalElement) {
        const roomPrices = {
            'single': 50,
            'double': 80,
            'shared': 30
        };
        
        const roomType = roomSelect.value;
        const nights = parseInt(nightsInput.value) || 0;
        const roomPrice = roomPrices[roomType] || 0;
        const totalCost = roomPrice * nights;
        
        totalElement.textContent = `$${totalCost}`;
    }
}

// Add event listeners for total cost calculation
document.addEventListener("DOMContentLoaded", function() {
    const roomSelect = document.getElementById('room');
    const nightsInput = document.getElementById('nights');
    
    if (roomSelect) {
        roomSelect.addEventListener('change', updateTotal);
    }
    
    if (nightsInput) {
        nightsInput.addEventListener('input', updateTotal);
    }
    
    // Initial calculation
    updateTotal();
});
