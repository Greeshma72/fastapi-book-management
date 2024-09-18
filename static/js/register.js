const form = document.getElementById('registerForm');
const messageDiv = document.getElementById('message');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const username = document.getElementById('username').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch('/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, email, password })
    });

    if (response.ok) {

      alert("Registration successful!!")
      window.location.href='/login'
      form.reset();

    } else {
      const error = await response.json();
      messageDiv.textContent = error.detail;
    }
  } catch (error) {
    messageDiv.textContent = 'An error occurred during registration.';
    console.error(error);
  }
});
