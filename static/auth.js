document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');

    if (loginForm) {
        // Event listener for login form submission
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(loginForm);
            const data = {
                username: formData.get('username'),
                password: formData.get('password')
            };

            // Send login request to the server
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    // Redirect to home page on successful login
                    window.location.href = '/';
                } else {
                    // Show error message on failed login
                    showError('login-error', result.message);
                }
            })
            .catch(error => {
                // Show error message on network or server error
                showError('login-error', 'An error occurred. Please try again.');
            });
        });
    }

    if (signupForm) {
        // Event listener for signup form submission
        signupForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(signupForm);
            const data = {
                username: formData.get('username'),
                password: formData.get('password')
            };

            // Send signup request to the server
            fetch('/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    // Redirect to login page on successful signup
                    window.location.href = '/login';
                } else {
                    // Show error message on failed signup
                    showError('signup-error', result.message);
                }
            })
            .catch(error => {
                // Show error message on network or server error
                showError('signup-error', 'An error occurred. Please try again.');
            });
        });
    }
});

// Function to show error message
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    errorElement.innerText = message;
    errorElement.style.display = 'block';
}
