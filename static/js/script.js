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

document.getElementById("price-range").addEventListener("input", function() {
    document.getElementById("price-value").textContent = this.value;
});
