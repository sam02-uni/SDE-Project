/**
 * FantaNews - Gestione Creazione Lega e Sidebar Hover
 */

LEGHE_URL="http://localhost:8007/process/league-management/info_webapp_home"

document.addEventListener("DOMContentLoaded", () => {
    // DOM element
    const sidebar = document.getElementById("mySidebar");
    const overlay = document.getElementById("overlay");
    const openBtn = document.getElementById("openSidebar"); // Il trigger
    const btnCrea = document.getElementById("btnCreaLega");
    const logoutBtn = document.getElementById("logoutBtn");
    const logoutForm = document.getElementById('logoutForm');
    const containerLeagues = document.getElementById("userLeagues");

    // Sidebar logic

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

// Refresh token function
async function refreshAccessToken() {
    try {
        const refreshResp = await fetch('http://localhost:8000/auth/refresh', {
            method: 'POST',
            credentials: 'include' // Invia il cookie refresh_token alla 8000
        });

        if (!refreshResp.ok) throw new Error('Sessione scaduta');

        const data = await refreshResp.json();
        // Salvo il nuovo access token il local storage
        localStorage.setItem('access_token', data.access_token); 
        return true; 
    } catch (err) {
        console.error('Errore refresh:', err);
        return false;
    }
}
    
    // User and leagues loading

async function caricaLeghe() {
    let url=new URL(LEGHE_URL);
    try {
        const token = localStorage.getItem('access_token');
        let response = await fetch(url, {
            method: 'GET', 
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        // Gestione del token scaduto
        if (response.status === 401) {
            const success = await refreshAccessToken();
            if (success) {
                const newToken = localStorage.getItem('access_token');
                response= await fetch(url, {
                method: 'GET', 
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${newToken}`
                }
        });
            } else {
                window.location.href = "login.html";
                return;
            }
        }

        const leghe = await response.json();
        containerLeagues.innerHTML = ""; 
        
        leghe.forEach(lega => {
            const link = document.createElement('a');
            link.href = "lega_dashboard.html";
            link.className = 'lega-link';
            link.dataset.id=lega.id
            link.innerHTML = `🏆 ${lega.name}`;
            
            link.onclick = (e) => {
                e.preventDefault();
                localStorage.setItem('selected_league_id', lega.id);
                localStorage.setItem('nome_lega', lega.name);
                window.location.href = "lega_dashboard.html";
            };

            // Aggiunta al contenitore specifico tra News e Logout
            containerLeagues.appendChild(link);
        });
    } catch (error) {
        console.error("Errore nel caricamento leghe:", error);
    }
}


// Chiamata al logout
if (logoutForm) {
    logoutForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Blocca l'invio normale che fallirebbe

        try {
            // Facciamo la chiamata alla porta del backend
            let response = await fetch('http://localhost:8000/auth/logout', {
                method: 'POST',
                credentials: 'include', 
                headers: {
                    'Accept': 'application/json'
                }
            });

            // Se il logout ha successo sul server (porta 8000)
            if (response.ok) {
                // Puliamo i dati locali sulla porta 3000
                localStorage.clear();
                sessionStorage.clear();
                
                // Spostiamo l'utente alla pagina di login (stessa porta del frontend)
                window.location.href = "/pages/login.html"; 
            } else {
                alert("Errore durante il logout. Riprova.");
            }
        } catch (error) {
            console.error("Errore di rete o CORS:", error);
            // In caso di errore CORS, spesso il logout avviene comunque sul server,
            // quindi forziamo il ritorno al login per sicurezza.
            window.location.href = "/pages/login.html";
        }
    });
}

    // Pulsante per la creazione della lega
    if (btnCrea) {
        btnCrea.addEventListener("click", async () => {
            // Recupera il token PIÙ RECENTE qui dentro
            let currentToken = localStorage.getItem('access_token');
            const nome = document.getElementById("nomeLega").value.trim();
            const crediti = parseInt(document.getElementById("creditiLega").value);

            if (!nome || !crediti) {
                alert("Please fill in all fields!");
                return;
            }

            btnCrea.disabled = true;
            btnCrea.textContent = "Creazione in corso...";

            try {
                let response = await fetch("http://localhost:8007/process/league-management/init", {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${currentToken}` 
                    },
                    body: JSON.stringify({ "name": nome, "max_credits": crediti })
                });

                // Gestione Token Scaduto anche qui
                if (response.status === 401) {
                    const success = await refreshAccessToken();
                    if (success) {
                        currentToken = localStorage.getItem('access_token');
                        // Riprova la POST
                        response = await fetch("http://localhost:8007/process/league-management/init", {
                            method: "POST",
                            headers: { 
                                "Content-Type": "application/json",
                                "Authorization": `Bearer ${currentToken}` 
                            },
                            body: JSON.stringify({ "name": nome, "max_credits": crediti })
                        });
                    }
                }

                if (response.ok) {
                    let legaId = await response.json();
                    alert(`League "${nome}" successfully created!`);
                    localStorage.setItem('selected_league_id', legaId);
                    localStorage.setItem('nome_lega', nome);
                    window.location.href = "lega_dashboard.html";
                } else {
                    const errorData = await response.json();
                    alert("Impossible to create the league: " + (errorData.detail || "Unknown error"));
                }
            } catch (err) {
                console.error("Errore di rete:", err);
                alert("Server connection error");
            } finally {
                btnCrea.disabled = false;
                btnCrea.textContent = "Crea Lega";
            }
        });
    }

    // Carica le leghe 
    caricaLeghe();
});
