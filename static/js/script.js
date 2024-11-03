function showPopup(title, description, price, image) {
    const popup = document.createElement('div');
    popup.className = 'popup';
    popup.innerHTML = `
        <div class="popup-content">
            <span class="close" onclick="this.parentElement.parentElement.remove();">&times;</span>
            <img src="${image}" alt="${title}">
            <h2>${title}</h2>
            <p>Prix : ${price} €</p>
            <p>${description}</p>
        </div>
    `;
    document.body.appendChild(popup);
}

document.addEventListener('DOMContentLoaded', function() {
    const categoryFilter = document.getElementById('category-filter');
    categoryFilter.addEventListener('change', filterBooks);
});

function filterBooks() {
    const category = document.getElementById('category-filter').value;

    // Appel AJAX pour récupérer les livres filtrés
    fetch(`/filter_books?category=${encodeURIComponent(category)}`)
        .then(response => response.json())
        .then(data => {
            // Effacer les livres existants
            const booksContainer = document.querySelector('.book-list');
            booksContainer.innerHTML = '';

            // Ajouter les livres filtrés
            if (data.error) {
                booksContainer.innerHTML = `<p>Erreur: ${data.error}</p>`;
            } else if (data.length === 0) {
                booksContainer.innerHTML = '<p>Aucun livre trouvé pour cette catégorie.</p>';
            } else {
                data.forEach(book => {
                    const bookElement = document.createElement('div');
                    bookElement.classList.add('book-box');
                    bookElement.innerHTML = `
                        <img src="${book.book_image_url}" alt="Image de ${book.book_title}" class="book-image">
                        <h4>${book.book_title}</h4>
                        <p>Auteur: ${book.author_firstname} ${book.author_lastname}</p>
                        <p>Prix: ${book.book_price} €</p>
                        <button>Ajouter au Panier</button>
                    `;
                    booksContainer.appendChild(bookElement);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}



document.getElementById("price-range").addEventListener("input", function() {
    document.getElementById("price-value").textContent = this.value;
});
