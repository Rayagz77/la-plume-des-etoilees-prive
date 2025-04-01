document.addEventListener("DOMContentLoaded", function () {
    console.log("cart.js est bien chargé !");

    // Récupération des éléments
    const cartLink = document.getElementById("cart-link");
    const cartModal = document.getElementById("cart-modal");
    const closeBtn = document.querySelector(".close-btn");

    if (!cartLink || !cartModal || !closeBtn) {
        console.error("❌ Éléments du panier non trouvés !");
        return; // Arrêter l'exécution si les éléments sont manquants
    }

    // ✅ Ouvrir la modale du panier
    cartLink.addEventListener("click", function (event) {
        event.preventDefault();
        cartModal.style.display = "block";
    });

    // ✅ Fermer la modale
    closeBtn.addEventListener("click", function () {
        cartModal.style.display = "none";
    });

    // ✅ Fermer la modale en cliquant en dehors
    window.addEventListener("click", function (event) {
        if (event.target === cartModal) {
            cartModal.style.display = "none";
        }
    });
});
