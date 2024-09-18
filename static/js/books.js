document.addEventListener("DOMContentLoaded", function () {
    // Load books when the page loads
    loadBooks();

    // Handle book form submission
    document.getElementById("bookForm").addEventListener("submit", async function (event) {
        event.preventDefault();

        const title = document.getElementById("title").value;
        const author = document.getElementById("author").value;

        try {
            const response = await fetch("/books/books/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ title, author })
            });

            if (response.ok) {
                alert("Book added successfully!");
                loadBooks();  // Reload the book list
            } else {
                const errorData = await response.json();
                alert(`Failed to add book: ${errorData.detail}`);
            }
        } catch (error) {
            console.error("Error adding book:", error);
            alert("An unexpected error occurred. Please try again later.");
        } finally {
            document.getElementById("bookForm").reset();
        }
    });
});

async function loadBooks() {
    try {
        const response = await fetch("/books/books/books/");
        if (response.ok) {
            const books = await response.json();
            const bookList = document.getElementById("bookList");
            bookList.innerHTML = "";  // Clear the list

            books.forEach(book => {
                const li = document.createElement("li");
                li.textContent = `${book.title} by ${book.author}`;

                // Add a link to view book details
                const viewLink = document.createElement("a");
                viewLink.href = "#";
                viewLink.textContent = " View Details";
                viewLink.addEventListener("click", function () {
                    viewBookDetails(book.id);
                });

                li.appendChild(viewLink);
                bookList.appendChild(li);
            });
        } else {
            console.error("Failed to load books");
        }
    } catch (error) {
        console.error("Error loading books:", error);
    }
}

async function viewBookDetails(bookId) {
    try {
        const response = await fetch(`/books/books/${bookId}`);
        if (response.ok) {
            const book = await response.json();

            // Create a section to display book details
            const bookDetailsSection = document.getElementById('bookDetails');
            bookDetailsSection.innerHTML = `
                <h3>${book.title}</h3>
                <p>Author: ${book.author}</p>
                <p>Reviews: ${book.reviews.length}</p>
                <button id="updateBook">Update Book</button>
                <button id="deleteBook">Delete Book</button>
            `;

            // Add event listeners for update and delete buttons
            document.getElementById("updateBook").addEventListener("click", function () {
                updateBook(book.id);
            });

            document.getElementById("deleteBook").addEventListener("click", function () {
                deleteBook(book.id);
            });

        } else {
            alert("Failed to fetch book details");
        }
    } catch (error) {
        console.error("Error fetching book details:", error);
        alert("An unexpected error occurred. Please try again later.");
    }
}

async function updateBook(bookId) {
    const newTitle = prompt("Enter new title:");
    const newAuthor = prompt("Enter new author:");

    if (newTitle && newAuthor) {
        try {
            const response = await fetch(`/books/books/${bookId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ title: newTitle, author: newAuthor })
            });

            const responseData = await response.json();
            if (response.ok) {
                alert("Book updated successfully!");
                loadBooks();
            } else {
                console.error("Failed to update book!:", responseData);
                alert(`Failed to update book: ${responseData.detail}`);
            }
        } catch (error) {
            console.error("Error updating book:", error);
            alert("An unexpected error occurred. Please try again later.");
        }
    } else {
        alert("Title and author cannot be empty.");
    }
}

async function deleteBook(bookId) {
    if (confirm("Are you sure you want to delete this book?")) {
        try {
            const response = await fetch(`/books/books/${bookId}`, {
                method: "DELETE"
            });

            if (response.ok) {
                alert("Book deleted successfully!");
                await loadBooks();  // Ensure the book list is reloaded after deletion
            } else {
                const responseData = await response.json(); // Parse response
                console.error("Failed to delete book:", responseData);
                alert(`Failed to delete book: ${responseData.detail}`);
            }
        } catch (error) {
            console.error("Error deleting book:", error);
            alert("An unexpected error occurred. Please try again later.");
        }
    }
}

async function loadBooks() {
    try {
        const response = await fetch("/books/read/books/");
        if (response.ok) {
            const books = await response.json();
            const bookList = document.getElementById("bookList");
            bookList.innerHTML = "";  // Clear the list

            books.forEach(book => {
                const li = document.createElement("li");
                li.textContent = `${book.title} by ${book.author}`;

                // Add a link to view book details
                const viewLink = document.createElement("a");
                viewLink.href = "#";
                viewLink.textContent = " View Details";
                viewLink.addEventListener("click", function () {
                    viewBookDetails(book.id);
                });

                li.appendChild(viewLink);
                bookList.appendChild(li);
            });
        } else {
            console.error("Failed to load books");
        }
    } catch (error) {
        console.error("Error loading books:", error);
    }
}
