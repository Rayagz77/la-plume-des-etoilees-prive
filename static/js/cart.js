// static/js/cart.js
document.addEventListener("DOMContentLoaded", function () {
  console.log("cart.js chargé");
  const cartLink  = document.getElementById("cart-link");
  const cartModal = document.getElementById("cart-modal");
  const closeBtn  = cartModal ? cartModal.querySelector(".close-btn") : null;

  if (!cartLink || !cartModal || !closeBtn) {
    console.warn("Panier: éléments non trouvés sur cette page (ok si page sans panier).");
    return;
  }

  cartLink.addEventListener("click", function (event) {
    event.preventDefault();
    cartModal.style.display = "block";
  });

  closeBtn.addEventListener("click", function () {
    cartModal.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target === cartModal) {
      cartModal.style.display = "none";
    }
  });
});
