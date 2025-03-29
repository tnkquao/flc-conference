document.addEventListener("DOMContentLoaded", function() {
    setupPaymentOptions();
    setupPaypalButton();
});

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
    const cardNumber = document.getElementById('cardNumber');
    const cardName = document.getElementById('cardName');
    const cardExpiry = document.getElementById('cardExpiry');
    const cardCVC = document.getElementById('cardCVC');
    let isValid = true;
    
    // Card number validation
    if (cardNumber) {
        const cardNumberValue = cardNumber.value.replace(/\s/g, '');
        if (cardNumberValue.length < 13 || cardNumberValue.length > 19 || !luhnCheck(cardNumberValue)) {
            showFeedback(cardNumber, 'Please enter a valid card number', false);
            isValid = false;
        } else {
            showFeedback(cardNumber, 'Valid card number', true);
        }
    }
    
    // Card name validation
    if (cardName && cardName.value.trim() === '') {
        showFeedback(cardName, 'Please enter the name on card', false);
        isValid = false;
    } else if (cardName) {
        showFeedback(cardName, 'Valid name', true);
    }
    
    // Card expiry validation
    if (cardExpiry) {
        const expiryPattern = /^(0[1-9]|1[0-2])\/([0-9]{2})$/;
        if (!expiryPattern.test(cardExpiry.value)) {
            showFeedback(cardExpiry, 'Please enter a valid expiry date (MM/YY)', false);
            isValid = false;
        } else {
            const parts = cardExpiry.value.split('/');
            const month = parseInt(parts[0], 10);
            const year = parseInt('20' + parts[1], 10);
            const now = new Date();
            const currentYear = now.getFullYear();
            const currentMonth = now.getMonth() + 1;
            
            if (year < currentYear || (year === currentYear && month < currentMonth)) {
                showFeedback(cardExpiry, 'Card has expired', false);
                isValid = false;
            } else {
                showFeedback(cardExpiry, 'Valid expiry date', true);
            }
        }
    }
    
    // CVC validation
    if (cardCVC) {
        const cvcPattern = /^[0-9]{3,4}$/;
        if (!cvcPattern.test(cardCVC.value)) {
            showFeedback(cardCVC, 'Please enter a valid CVC code (3-4 digits)', false);
            isValid = false;
        } else {
            showFeedback(cardCVC, 'Valid CVC', true);
        }
    }
    
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
    const cardExpiry = document.getElementById('cardExpiry');
    const creditCardForm = document.getElementById('credit-card-form');
    
    if (cardNumber) {
        cardNumber.addEventListener('input', formatCardNumber);
    }
    
    if (cardExpiry) {
        cardExpiry.addEventListener('input', formatExpiryDate);
    }
    
    if (creditCardForm) {
        creditCardForm.addEventListener('submit', function(event) {
            if (!validateCreditCard()) {
                event.preventDefault();
            }
        });
    }
});
