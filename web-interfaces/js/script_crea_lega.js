/**
 * FantaNews - Gestione Creazione Lega e Sidebar Hover
 */

document.addEventListener("DOMContentLoaded", () => {
    // --- ELEMENTI DOM ---
    const sidebar = document.getElementById("mySidebar");
    const overlay = document.getElementById("overlay");
    const openBtn = document.getElementById("openSidebar"); // Il trigger
    const btnCrea = document.getElementById("btnCreaLega");
    const logoutBtn = document.getElementById("logoutBtn");

    // --- LOGICA SIDEBAR (HOVER) ---

    const openNav = () => { 
        sidebar.classList.add("active"); 
        overlay.classList.add("active"); 
    };

    const closeNav = () => { 
        sidebar.classList.remove("active"); 
        overlay.classList.remove("active"); 
    };

    // Apre quando il mouse entra nel bottone/area menu
    openBtn.addEventListener("mouseenter", openNav);

    // Chiude quando il mouse esce dalla sidebar
    sidebar.addEventListener("mouseleave", closeNav);

    // Chiude se si clicca sull'oscuramento (overlay)
    overlay.addEventListener("click", closeNav);


    // --- LOGICA DI BUSINESS: CREAZIONE LEGA ---

    if (btnCrea) {
        btnCrea.addEventListener("click", async () => {
            const nome = document.getElementById("nomeLega").value;
            const crediti = document.getElementById("creditiLega").value;

            if (!nome || !crediti) {
                alert("⚠️ Per favore, compila tutti i campi!");
                return;
            }

            // Simulazione chiamata al Data Service (Business Layer)
            console.log("Inviando dati al server:", { nome, crediti });
            
            // Qui andrà la tua fetch verso il data-service
            alert(`✅ Lega "${nome}" creata con successo!`);
        });
    }

    // --- LOGICA DI BUSINESS: LOGOUT ---

    if (logoutBtn) {
        logoutBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            if (confirm("Vuoi davvero uscire?")) {
                try {
                    const response = await fetch("http://localhost:8000/auth/logout", {
                        method: "POST"
                    });
                    if (response.ok) {
                        window.location.href = "/static/login.html";
                    }
                } catch (err) {
                    console.error("Errore logout:", err);
                }
            }
        });
    }
});