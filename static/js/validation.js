document.addEventListener("DOMContentLoaded", function() {
    // Get all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');

    // Registration form validation
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        // Real-time validation for registration form fields
        setupRealTimeValidation('name', validateName);
        setupRealTimeValidation('email', validateEmail);
        setupRealTimeValidation('phone', validatePhone);
        setupRealTimeValidation('terms', validateTerms);
        
        // Submit validation
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
        // Real-time validation for accommodation form fields
        setupRealTimeValidation('room', validateRoom);
        setupRealTimeValidation('nights', validateNights);
        
        // Submit validation
        accommodationForm.addEventListener('submit', function(event) {
            if (!validateAccommodationForm()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            accommodationForm.classList.add('was-validated');
        });
    }

    // Payment form validation
    const paymentForm = document.querySelector('#credit-card-form form');
    if (paymentForm) {
        // Real-time validation for payment form fields
        setupRealTimeValidation('cardNumber', validateCardNumber);
        setupRealTimeValidation('cardExpiry', validateCardExpiry);
        setupRealTimeValidation('cardCVC', validateCardCVC);
        setupRealTimeValidation('cardName', validateCardName);
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

// Setup real-time validation for a field
function setupRealTimeValidation(fieldId, validationFunction) {
    const field = document.getElementById(fieldId);
    if (field) {
        // For radio and checkbox inputs
        if (field.type === 'radio' || field.type === 'checkbox') {
            field.addEventListener('change', function() {
                validationFunction(field);
            });
        } 
        // For select elements
        else if (field.tagName === 'SELECT') {
            field.addEventListener('change', function() {
                validationFunction(field);
            });
        } 
        // For text inputs
        else {
            // Validate after a slight delay to avoid validating during typing
            let typingTimer;
            field.addEventListener('input', function() {
                clearTimeout(typingTimer);
                typingTimer = setTimeout(function() {
                    validationFunction(field);
                }, 500); // Delay in milliseconds
            });
            
            // Also validate on blur (when user leaves the field)
            field.addEventListener('blur', function() {
                validationFunction(field);
            });
        }
    }
}

// Validate name field
function validateName(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    if (value === '') {
        isValid = false;
        message = 'Please enter your full name';
    } else if (value.length < 3) {
        isValid = false;
        message = 'Name is too short';
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Looks good!' : message, isValid);
    return isValid;
}

// Validate email field
function validateEmail(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    let isValid = true;
    let message = '';
    
    if (value === '') {
        isValid = false;
        message = 'Please enter your email address';
    } else if (!emailPattern.test(value)) {
        isValid = false;
        message = 'Please enter a valid email address';
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Looks good!' : message, isValid);
    return isValid;
}

// Validate phone field
function validatePhone(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    const phonePattern = /^[0-9+\-\s()]+$/;
    let isValid = true;
    let message = '';
    
    if (value === '') {
        isValid = false;
        message = 'Please enter your phone number';
    } else if (!phonePattern.test(value)) {
        isValid = false;
        message = 'Please enter a valid phone number';
    } else if (value.length < 7) {
        isValid = false;
        message = 'Phone number is too short';
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Looks good!' : message, isValid);
    return isValid;
}

// Validate terms checkbox
function validateTerms(field) {
    if (!field) return false;
    
    const isValid = field.checked;
    const message = 'You must agree to the terms and conditions';
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Agreed!' : message, isValid);
    return isValid;
}

// Validate room field
function validateRoom(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    const isValid = value !== '';
    const message = 'Please select a room type';
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Good choice!' : message, isValid);
    return isValid;
}

// Validate nights field
function validateNights(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    if (value === '') {
        isValid = false;
        message = 'Please enter the number of nights';
    } else if (isNaN(value) || parseInt(value) <= 0) {
        isValid = false;
        message = 'Please enter a valid number of nights';
    } else if (parseInt(value) > 10) {
        isValid = false;
        message = 'Maximum 10 nights allowed';
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Looks good!' : message, isValid);
    return isValid;
}

// Credit card number validation
function validateCardNumber(field) {
    if (!field) return false;
    
    const value = field.value.trim().replace(/\D/g, ''); // Remove non-digits
    let isValid = true;
    let message = '';
    
    if (value === '') {
        isValid = false;
        message = 'Please enter your card number';
    } else if (value.length < 13 || value.length > 19) {
        isValid = false;
        message = 'Card number should be between 13 and 19 digits';
    } else if (!luhnCheck(value)) {
        isValid = false;
        message = 'Invalid card number';
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Valid card number!' : message, isValid);
    return isValid;
}

// Credit card expiry validation
function validateCardExpiry(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    const expiryPattern = /^(0[1-9]|1[0-2])\/([0-9]{2})$/;
    let isValid = true;
    let message = '';
    
    if (value === '') {
        isValid = false;
        message = 'Please enter the expiry date';
    } else if (!expiryPattern.test(value)) {
        isValid = false;
        message = 'Format should be MM/YY';
    } else {
        // Check if card is expired
        const [month, year] = value.split('/');
        const expiryDate = new Date(2000 + parseInt(year), parseInt(month) - 1, 1);
        const today = new Date();
        
        if (expiryDate < today) {
            isValid = false;
            message = 'Card is expired';
        }
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Valid expiry date!' : message, isValid);
    return isValid;
}

// Credit card CVC validation
function validateCardCVC(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    const cvcPattern = /^[0-9]{3,4}$/;
    let isValid = true;
    let message = '';
    
    if (value === '') {
        isValid = false;
        message = 'Please enter the CVC';
    } else if (!cvcPattern.test(value)) {
        isValid = false;
        message = 'CVC should be 3 or 4 digits';
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Valid CVC!' : message, isValid);
    return isValid;
}

// Card name validation
function validateCardName(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    if (value === '') {
        isValid = false;
        message = 'Please enter the name on your card';
    } else if (value.length < 3) {
        isValid = false;
        message = 'Name is too short';
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Looks good!' : message, isValid);
    return isValid;
}

// Luhn algorithm (mod 10) to validate credit card numbers
function luhnCheck(cardNumber) {
    if (!cardNumber) return false;
    
    // Remove all non-digit characters
    cardNumber = cardNumber.replace(/\D/g, '');
    
    let sum = 0;
    let shouldDouble = false;
    
    // Loop through values starting from the rightmost digit
    for (let i = cardNumber.length - 1; i >= 0; i--) {
        let digit = parseInt(cardNumber.charAt(i));
        
        if (shouldDouble) {
            digit *= 2;
            if (digit > 9) digit -= 9;
        }
        
        sum += digit;
        shouldDouble = !shouldDouble;
    }
    
    return (sum % 10) === 0;
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
