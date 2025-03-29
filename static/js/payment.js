document.addEventListener("DOMContentLoaded", function() {
    setupPaymentOptions();
    setupPaypalButton();
});

// Show feedback to user (this duplicates the function in validation.js for modularity)
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

// Setup payment option selection
function setupPaymentOptions() {
    const paymentOptions = document.querySelectorAll('.payment-option');
    
    paymentOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options
            paymentOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to clicked option
            this.classList.add('selected');
            
            // Update the payment method input
            const methodInput = document.getElementById('paymentMethod');
            if (methodInput) {
                methodInput.value = this.dataset.method;
            }
            
            // Show/hide payment forms based on selection
            const paypalForm = document.getElementById('paypal-button-container');
            const creditCardForm = document.getElementById('credit-card-form');
            
            if (this.dataset.method === 'paypal' && paypalForm) {
                paypalForm.style.display = 'block';
                if (creditCardForm) creditCardForm.style.display = 'none';
            } else if (this.dataset.method === 'credit-card' && creditCardForm) {
                creditCardForm.style.display = 'block';
                if (paypalForm) paypalForm.style.display = 'none';
            }
        });
    });
    
    // Select default payment option
    if (paymentOptions.length > 0) {
        paymentOptions[0].click();
    }
}

// Setup PayPal button
function setupPaypalButton() {
    const paypalButtonContainer = document.getElementById('paypal-button-container');
    
    if (paypalButtonContainer) {
        // Check if we're on the payment page
        const totalAmountElement = document.getElementById('totalAmount');
        if (!totalAmountElement) return;
        
        const totalAmount = parseFloat(totalAmountElement.textContent.replace('$', '')) || 0;
        
        // For testing purposes, we'll just add a button that simulates payment completion
        // In a real application, you would use the PayPal SDK
        const payButton = document.createElement('button');
        payButton.className = 'btn btn-primary btn-lg w-100 mt-3';
        payButton.textContent = 'Complete Payment with PayPal';
        payButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Simulate payment processing
            this.disabled = true;
            this.textContent = 'Processing...';
            
            // Create a hidden form to submit payment data
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/payment/process';
            
            // Add payment ID
            const paymentIdInput = document.createElement('input');
            paymentIdInput.type = 'hidden';
            paymentIdInput.name = 'payment_id';
            paymentIdInput.value = 'PAY-' + Math.random().toString(36).substr(2, 9);
            form.appendChild(paymentIdInput);
            
            // Add payment details
            const paymentDetailsInput = document.createElement('input');
            paymentDetailsInput.type = 'hidden';
            paymentDetailsInput.name = 'payment_details';
            paymentDetailsInput.value = JSON.stringify({
                amount: totalAmount,
                currency: 'USD',
                method: 'paypal'
            });
            form.appendChild(paymentDetailsInput);
            
            // Submit the form
            document.body.appendChild(form);
            form.submit();
        });
        
        paypalButtonContainer.appendChild(payButton);
    }
}

// Credit card validation functions
function validateCreditCard() {
    let isValid = true;
    
    isValid = validateCardNumber(document.getElementById('cardNumber')) && isValid;
    isValid = validateCardName(document.getElementById('cardName')) && isValid;
    isValid = validateCardExpiry(document.getElementById('cardExpiry')) && isValid;
    isValid = validateCardCVC(document.getElementById('cardCVC')) && isValid;
    
    return isValid;
}

// Validate card number with real-time feedback
function validateCardNumber(field) {
    if (!field) return false;
    
    const value = field.value.replace(/\s/g, '');
    let isValid = true;
    let message = '';
    let cardType = '';
    
    // Determine card type based on first digits
    if (/^4/.test(value)) {
        cardType = 'Visa';
    } else if (/^5[1-5]/.test(value)) {
        cardType = 'MasterCard';
    } else if (/^3[47]/.test(value)) {
        cardType = 'American Express';
    } else if (/^6(?:011|5)/.test(value)) {
        cardType = 'Discover';
    }
    
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
    
    // Show card type for better user experience
    if (isValid && cardType) {
        message = `Valid ${cardType} card`;
    } else if (isValid) {
        message = 'Valid card number';
    }
    
    // Update card icons if needed
    const cardIcons = field.parentNode.querySelector('.input-group-text');
    if (cardIcons && cardType) {
        // Highlight the detected card type
        Array.from(cardIcons.children).forEach(icon => {
            if ((cardType === 'Visa' && icon.classList.contains('fa-cc-visa')) ||
                (cardType === 'MasterCard' && icon.classList.contains('fa-cc-mastercard')) ||
                (cardType === 'American Express' && icon.classList.contains('fa-cc-amex'))) {
                icon.classList.add('text-primary');
            } else {
                icon.classList.remove('text-primary');
            }
        });
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, message, isValid);
    return isValid;
}

// Validate card name with real-time feedback
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
    } else if (!/^[a-zA-Z\s]+$/.test(value)) {
        isValid = false;
        message = 'Name should contain only letters and spaces';
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Valid name' : message, isValid);
    return isValid;
}

// Validate card expiry with real-time feedback
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
        const parts = value.split('/');
        const month = parseInt(parts[0], 10);
        const year = parseInt('20' + parts[1], 10);
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth() + 1;
        
        if (year < currentYear || (year === currentYear && month < currentMonth)) {
            isValid = false;
            message = 'Card has expired';
        } else if (year > currentYear + 10) {
            isValid = false;
            message = 'Expiry date too far in the future';
        }
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Valid expiry date' : message, isValid);
    return isValid;
}

// Validate card CVC with real-time feedback
function validateCardCVC(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    const cvcPattern = /^[0-9]{3,4}$/;
    let isValid = true;
    let message = '';
    
    // Check for AMEX cards which use 4-digit CVC
    const cardNumberField = document.getElementById('cardNumber');
    const isAmex = cardNumberField && /^3[47]/.test(cardNumberField.value.replace(/\s/g, ''));
    
    if (value === '') {
        isValid = false;
        message = 'Please enter the CVC';
    } else if (!cvcPattern.test(value)) {
        isValid = false;
        message = 'CVC should be 3-4 digits';
    } else if (isAmex && value.length !== 4) {
        isValid = false;
        message = 'American Express cards require a 4-digit CVC';
    } else if (!isAmex && value.length !== 3) {
        isValid = false;
        message = 'CVC should be 3 digits';
    }
    
    field.setCustomValidity(isValid ? '' : message);
    showFeedback(field, isValid ? 'Valid CVC' : message, isValid);
    return isValid;
}

// Format card number with spaces
function formatCardNumber(event) {
    const input = event.target;
    let value = input.value.replace(/\s+/g, '');
    
    // Add space after every 4 digits
    if (value.length > 0) {
        value = value.match(new RegExp('.{1,4}', 'g')).join(' ');
    }
    
    input.value = value;
}

// Format expiry date as MM/YY
function formatExpiryDate(event) {
    const input = event.target;
    let value = input.value.replace(/[^\d]/g, '');
    
    if (value.length > 2) {
        value = value.slice(0, 2) + '/' + value.slice(2, 4);
    }
    
    input.value = value;
}

// Luhn algorithm for credit card validation
function luhnCheck(cardNumber) {
    let sum = 0;
    let shouldDouble = false;
    
    // Loop from right to left
    for (let i = cardNumber.length - 1; i >= 0; i--) {
        let digit = parseInt(cardNumber.charAt(i));
        
        if (shouldDouble) {
            digit *= 2;
            if (digit > 9) digit -= 9;
        }
        
        sum += digit;
        shouldDouble = !shouldDouble;
    }
    
    return sum % 10 === 0;
}

// Add event listeners for credit card form
document.addEventListener("DOMContentLoaded", function() {
    const cardNumber = document.getElementById('cardNumber');
    const cardName = document.getElementById('cardName');
    const cardExpiry = document.getElementById('cardExpiry');
    const cardCVC = document.getElementById('cardCVC');
    const creditCardForm = document.querySelector('#credit-card-form form');
    
    // Format card number as user types
    if (cardNumber) {
        cardNumber.addEventListener('input', formatCardNumber);
        
        // Real-time validation with slight delay
        let typingTimer;
        cardNumber.addEventListener('input', function() {
            clearTimeout(typingTimer);
            typingTimer = setTimeout(function() {
                validateCardNumber(cardNumber);
            }, 500);
        });
        
        // Also validate on blur
        cardNumber.addEventListener('blur', function() {
            validateCardNumber(cardNumber);
        });
    }
    
    // Real-time validation for card name
    if (cardName) {
        let typingTimer;
        cardName.addEventListener('input', function() {
            clearTimeout(typingTimer);
            typingTimer = setTimeout(function() {
                validateCardName(cardName);
            }, 500);
        });
        
        cardName.addEventListener('blur', function() {
            validateCardName(cardName);
        });
    }
    
    // Format expiry date as user types
    if (cardExpiry) {
        cardExpiry.addEventListener('input', formatExpiryDate);
        
        // Real-time validation
        let typingTimer;
        cardExpiry.addEventListener('input', function() {
            clearTimeout(typingTimer);
            typingTimer = setTimeout(function() {
                validateCardExpiry(cardExpiry);
            }, 500);
        });
        
        cardExpiry.addEventListener('blur', function() {
            validateCardExpiry(cardExpiry);
        });
    }
    
    // Real-time validation for CVC
    if (cardCVC) {
        let typingTimer;
        cardCVC.addEventListener('input', function() {
            clearTimeout(typingTimer);
            typingTimer = setTimeout(function() {
                validateCardCVC(cardCVC);
            }, 500);
        });
        
        cardCVC.addEventListener('blur', function() {
            validateCardCVC(cardCVC);
        });
    }
    
    // Form submission validation
    if (creditCardForm) {
        creditCardForm.addEventListener('submit', function(event) {
            if (!validateCreditCard()) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    }
    
    // Add "is-invalid" and "is-valid" classes to show validation state
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            // Clear validation status while typing
            input.classList.remove('is-invalid', 'is-valid');
        });
    });
});
