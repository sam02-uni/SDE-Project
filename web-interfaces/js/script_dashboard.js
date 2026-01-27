/**
 * FantaNews - Script Dashboard Lega
 * Gestisce: Sidebar (Hover), Modal Formazione, Popolamento Dati
 */

document.addEventListener("DOMContentLoaded", () => {
    // --- ELEMENTI DOM ---
    const sidebar = document.getElementById("mySidebar");
    const overlay = document.getElementById("overlay");
    const openBtn = document.getElementById("openSidebar");
    
    const modal = document.getElementById("modalFormazione");
    const btnFormazione = document.getElementById("btnFormazione");
    const closeModal = document.getElementById("closeModal");
    const saveBtn = document.getElementById("saveFormazione");

    const logoutBtn = document.getElementById("logoutBtn");

    // --- 1. LOGICA SIDEBAR (TENDINA A SFIORAMENTO) ---
    const openNav = () => {
        sidebar.classList.add("active");
        overlay.classList.add("active");
    };

    const closeNav = () => {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    };

    // Apre quando il mouse entra nel bottone Menu
    openBtn.addEventListener("mouseenter", openNav);

    // Chiude quando il mouse esce dalla sidebar
    sidebar.addEventListener("mouseleave", closeNav);

    // Chiude se si clicca sull'oscuramento
    overlay.addEventListener("click", () => {
        closeNav();
        modal.style.display = "none"; // Chiude anche la modal se aperta
    });


    // --- 2. LOGICA MODAL FORMAZIONE ---
    if (btnFormazione) {
        btnFormazione.addEventListener("click", () => {
            modal.style.display = "block";
            overlay.classList.add("active"); // Mostra l'overlay anche per la modal
            caricaCalciatori();
        });
    }

    if (closeModal) {
        closeModal.addEventListener("click", () => {
            modal.style.display = "none";
            overlay.classList.remove("active");
        });
    }

    // --- 3. POPOLAMENTO GIOCATORI (SIMULAZIONE DATI) ---
    function caricaCalciatori() {
        const lista = document.getElementById("listaCalciatori");
        
        // Dati di esempio (questi arriveranno dal tuo Business Layer)
        const miaRosa = [
            { id: 1, nome: "Maignan", ruolo: "POR" },
            { id: 2, nome: "Theo Hernandez", ruolo: "D" },
            { id: 3, nome: "Bastoni", ruolo: "D" },
            { id: 4, nome: "Barella", ruolo: "C" },
            { id: 5, nome: "Pulisic", ruolo: "C" },
            { id: 6, nome: "Lautaro Martinez", ruolo: "A" }
        ];

        lista.innerHTML = ""; // Svuota la lista precedente

        miaRosa.forEach(player => {
            const row = document.createElement("div");
            row.className = "player-row";
            row.innerHTML = `
                <div class="player-info">
                    <span class="player-role">${player.ruolo}</span>
                    <span class="player-name">${player.nome}</span>
                </div>
                <input type="checkbox" class="player-checkbox" value="${player.id}">
            `;
            lista.appendChild(row);
        });
    }

    // --- 4. SALVATAGGIO FORMAZIONE ---
    if (saveBtn) {
        saveBtn.addEventListener("click", () => {
            const selezionati = Array.from(document.querySelectorAll('.player-checkbox:checked'))
                                     .map(cb => cb.value);
            
            console.log("Salvataggio formazione, ID selezionati:", selezionati);
            alert("Formazione salvata con successo!");
            modal.style.display = "none";
            overlay.classList.remove("active");
        });
    }

    // --- 5. LOGOUT (PROCESS CENTRIC) ---
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
                    console.error("Errore durante il logout:", err);
                }
            }
        });
    }
});