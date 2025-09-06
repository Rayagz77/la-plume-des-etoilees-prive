// static/js/script.js
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

document.addEventListener('DOMContentLoaded', () => {
  const priceRange = document.getElementById('price-range');
  const priceValue = document.getElementById('price-value');
  if (priceRange && priceValue) {
    priceRange.addEventListener('input', function () {
      priceValue.textContent = this.value;
    });
  } else {
    // Pas de filtre prix sur cette page : on ne fait rien.
  }
});
