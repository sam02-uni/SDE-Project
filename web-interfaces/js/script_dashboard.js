/**
 * FantaNews - Script Dashboard Lega
 * Gestisce: Sidebar (Hover), Modal Formazione, Popolamento Dati
 */
LEGHE_URL="http://localhost:8007/process/league-management/info_webapp_home"
PROCESS_BASE_URL="http://localhost:8007/process/league-management"


document.addEventListener("DOMContentLoaded", () => {
    // --- ELEMENTI DOM ---
    const sidebar = document.getElementById("mySidebar");
    const overlay = document.getElementById("overlay");
    const openBtn = document.getElementById("openSidebar");
    
    const modal = document.getElementById("modalFormazione");
    const btnFormazione = document.getElementById("btnFormazione");
    const btnInserisciSquadra = document.getElementById("btnInserisciSquadra");
    const closeModal = document.getElementById("closeModal");
    const saveBtn = document.getElementById("saveFormazione");
    const containerLeagues = document.getElementById("userLeagues");
    const logoutForm = document.getElementById('logoutForm');
    const leagueId = localStorage.getItem("selected_league_id");
    const numeroGiornata = document.getElementById("numeroGiornata");
    const btnCalcoloGiornata = document.getElementById("btnCalcolaGiornata");
    const leagueName = document.getElementById("leagueNameDisplay");

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

    btnInserisciSquadra.addEventListener("click", () => {
        window.location.href="rosa_dashboard.html"
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

    // --- 4. SALVATAGGIO FORMAZIONE ---
    // TODO: cambiare in modo tale che salvi la formazione nel db
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
                    localStorage.removeItem('access_token'); // Rimuovi il token specifico
                    localStorage.clear(); 
                    window.location.href = "login.html"; 
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

    // Loading leagues
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
                console.log("MI HA DATO L'ERRORE (401 intercettato)");
                console.log("E ANDATO L'ERRORE")
                const success = await refreshAccessToken();
                console.log("GENERO NUOVO ACCESS TOKEN DA LEGHE")
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
        
            // 2. Pulisci il div dedicato alle leghe
            containerLeagues.innerHTML = ""; 

            leghe.forEach(lega => {
                const link = document.createElement('a');
                link.href = "lega_dashboard.html";
                link.className = 'lega-link';
                link.dataset.id=lega.id
                link.innerHTML = `🏆 ${lega.name}`;
            
                link.onclick = (e) => {
                    e.preventDefault();
                    // SE DOVESSE SERVIRE PER IL FRONTEND
                    localStorage.setItem('selected_league_id', lega.id);
                    localStorage.setItem('nome_lega', lega.name);
                    window.location.href = "lega_dashboard.html";
                };

                // 3. Aggiungi al contenitore specifico tra News e Logout
                containerLeagues.appendChild(link);
            });
        } catch (error) {
            console.error("Errore nel caricamento leghe:", error);
        }
    }


    // Controlla se abbiamo l'id lega nel localstorage
    function controlloLega(){
        if (!leagueId) {
            console.error("Nessuna lega selezionata! Torno alla home.");
            window.location.href = "login.html"; // Opzionale: rimanda indietro se manca l'ID
            return;
        }

        console.log("Stai visualizzando la lega con ID:", leagueId);
    }

    // Recupero le informazioni riguardo alla lega
    async function infoLega(){
        let url_completo = `${PROCESS_BASE_URL}/${leagueId}/info_dashboard_league`;
        let url = new URL(url_completo);
        try{
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
                console.log("MI HA DATO L'ERRORE (401 intercettato)");
                console.log("E ANDATO L'ERRORE")
                const success = await refreshAccessToken();
                console.log("GENERO NUOVO ACCESS TOKEN DA LEGHE")
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
            const infoLega = await response.json();
            console.log(infoLega);
            
            // Display dei vari pulsanti in base ad alcune info
            if (infoLega.isAdmin){
                btnInserisciSquadra.style.display = 'block';
                if (infoLega.lastMatchFinished){
                    btnCalcoloGiornata.style.display = 'block';
                } else {
                    btnCalcoloGiornata.style.display = 'none';
                }
            } else {
                btnInserisciSquadra.style.display = 'none';
            }

            if (infoLega.firstMatchStarted){
                btnFormazione.style.display = 'none';
            } else {
                btnFormazione.style.display = 'block';
            }
            // Display del numero di giornata
            numeroGiornata.textContent = `Giornata ${infoLega.currentMatchday}`;
            let nome_lega = localStorage.getItem('nome_lega');
            leagueName.textContent = `${nome_lega} - Serie A`;

        } catch(error){
            console.error("Errore nel caricamento delle informazioni della lega:", error);
        }
    }

    // --- 3. POPOLAMENTO GIOCATORI (SIMULAZIONE DATI) ---
    async function caricaCalciatori() {
        const lista = document.getElementById("listaCalciatori");
        
        // TODO: fare chiamata per recuperare la rosa dell'utente
        
        let url_completo = `${PROCESS_BASE_URL}/${leagueId}/info_dashboard_league`;
        let url = new URL(url_completo);
        try{
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
                console.log("MI HA DATO L'ERRORE (401 intercettato)");
                console.log("E ANDATO L'ERRORE")
                const success = await refreshAccessToken();
                console.log("GENERO NUOVO ACCESS TOKEN DA LEGHE")
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
            const infoLega = await response.json();
        
        } catch(error){
            console.error("Errore nel caricamento delle informazioni della lega:", error);
        }
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

    //Carico le leghe
    caricaLeghe();
    infoLega();
    controlloLega();

});