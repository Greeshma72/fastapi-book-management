document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('loginForm');
    alert("Hi");
    if (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            const formData = new URLSearchParams();
            formData.append("username", username);
            formData.append("password", password);

            try {
                const response = await fetch("/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: formData
                });

                if (response.ok) {
                    console.log("Login successful, redirecting to books page...");
                    alert("Login successful!");
                    window.location.href = "/books";
                } else {
                    const errorData = await response.json();
                    console.error("Error during login:", errorData.detail);
                    alert(`Error during login: ${errorData.detail}`);
                }
            } catch (error) {
                console.error("Error during login:", error);
                alert("An unexpected error occurred. Please try again later.");
            }
        });
    } else {
        console.error("Login form element not found");
    }
});
