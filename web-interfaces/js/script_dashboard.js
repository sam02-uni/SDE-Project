/**
 * FantaNews - Script Dashboard Lega
 * Gestisce: Sidebar (Hover), Modal Formazione, Popolamento Dati
 */
LEGHE_URL="http://localhost:8007/process/league-management/info_webapp_home"
PROCESS_BASE_URL="http://localhost:8007/process/league-management"
MATCHDAY_URL="http://localhost:8017/process/matchday-management"

let formazione = {
    titolari: [], // Max 11
    panchina: []  // Max 7
};

function selectRole(element, playerId, tipo) {
    // Invece di getElementById, cerchiamo il genitore comune
    const container = element.closest('.formation-controls');
    
    if (!container) {
        console.error("Errore: contenitore .formation-controls non trovato!");
        return;
    }

    const isAlreadySelected = element.classList.contains('selected-t') || element.classList.contains('selected-p');

    if (isAlreadySelected) {
        // 1. Rimuoviamo graficamente il colore
        element.classList.remove('selected-t', 'selected-p');
        
        // 2. Rimuoviamo l'ID dagli array
        formazione.titolari = formazione.titolari.filter(id => id !== playerId);
        formazione.panchina = formazione.panchina.filter(id => id !== playerId);
        
        console.log(`Rimosso giocatore ${playerId}. Titolari: ${formazione.titolari.length}, Panchina: ${formazione.panchina.length}`);
        return; // Usciamo dalla funzione, il lavoro è finito!
    }

    // Ora che abbiamo il container, troviamo i bottoni al suo INTERNO
    const buttons = container.querySelectorAll('.btn-sel');

    // 1. Reset grafico per questa riga
    buttons.forEach(btn => btn.classList.remove('selected-t', 'selected-p'));

    // 2. Logica di aggiornamento (Rimuovi da entrambi per evitare duplicati)
    formazione.titolari = formazione.titolari.filter(id => id !== playerId);
    formazione.panchina = formazione.panchina.filter(id => id !== playerId);

    // 3. Aggiunta e colore
    if (tipo === 't') {
        if (formazione.titolari.length < 11) {
            formazione.titolari.push(parseInt(playerId));
            element.classList.add('selected-t');
        } else {
            alert("Hai già 11 titolari!");
        }
    } else if (tipo === 'p') {
        if (formazione.panchina.length < 7) {
            formazione.panchina.push(parseInt(playerId));
            element.classList.add('selected-p');
        } else {
            alert("La panchina è piena (max 7)!");
        }
    }
}


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
    const scadenzaFormazione = document.getElementById("scadenza") // TODO
    const btnCalcoloGiornata = document.getElementById("btnCalcolaGiornata");
    const leagueName = document.getElementById("leagueNameDisplay");
    const board = document.getElementById("leaderboardBody");
    const prioritaRuoli = { "G": 1, "D": 2, "M": 3, "A": 4 };

    let playerSquad;

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
            formazione.titolari = [];
            formazione.panchina = [];
            caricaCalciatori();
        });
    }

    if (closeModal) {
        closeModal.addEventListener("click", () => {
            modal.style.display = "none";
            overlay.classList.remove("active");
        });
    }
    async function saveFormation(){            
        console.log("Salvataggio formazione, ID selezionati:  T:", formazione.titolari, " P:", formazione.panchina);
        let squadId = localStorage.getItem("squad_id");
        let current = localStorage.getItem("current_matchday");
        modal.style.display = "none";
        overlay.classList.remove("active");
        
        // Chiamata al process per inserire la formazione
        try{
            const token = localStorage.getItem('access_token');
            let url_completo = `${MATCHDAY_URL}/lineups`;
            let url = new URL(url_completo);
            let response = await fetch(url, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` 
                },
                body: JSON.stringify({  
                    "squad_id" : parseInt(squadId),
                    "matchday_number" : parseInt(current),
                    "starting_ids" : formazione.titolari,
                    "bench_ids" : formazione.panchina
                })
            });

            if (response.status != 201){
                alert("Errore imprevisto nel salvataggio della formazione");
            } else {
                alert("Formazione salvata correttamente");
            }

        } catch (error){
            console.error('Unexpected error', error);
        }
    }
    // --- 4. SALVATAGGIO FORMAZIONE ---
    saveBtn.addEventListener("click", saveFormation);

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
                scadenzaFormazione.textContent = '';
            } else {
                btnFormazione.style.display = 'block';
            }
            // Display del numero di giornata
            numeroGiornata.textContent = `Giornata ${infoLega.currentMatchday}`;
            let nome_lega = localStorage.getItem('nome_lega');
            localStorage.setItem("current_matchday", infoLega.currentMatchday);
            localStorage.setItem('squad_id', infoLega.squad.id);
            playerSquad = infoLega.squad.players;
            leagueName.textContent = `${nome_lega} - Serie A`;

            // visualizzazione della classifica
            table = infoLega.table;

            if ((table == null) || (table.length == 0)){
                // no squads
                return;
            }
            
            console.log(table)

            let counter_classifica = 1
            table.forEach(squad_in_table => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${counter_classifica}</td><td>${squad_in_table.name}</td><td>${squad_in_table.score}</td>
                `;
                counter_classifica++;
                board.appendChild(row)
            });

        } catch(error){
            console.error("Errore nel caricamento delle informazioni della lega:", error);
        }
    }

    // --- 3. POPOLAMENTO GIOCATORI (SIMULAZIONE DATI) ---
    async function caricaCalciatori() {
        const lista = document.getElementById("listaCalciatori");

        lista.innerHTML = ""; // Svuota la lista precedente

        const calciatoriOrdinati = Object.entries(playerSquad).sort(([, a], [, b]) => {
            return prioritaRuoli[a.role] - prioritaRuoli[b.role];
        });

        calciatoriOrdinati.forEach(([id, player]) => {
            const row = document.createElement("div");
            row.className = "player-row";
            row.innerHTML = `
                <div class="player-info">
                    <span class="player-role">${player.role} - ${player.serie_a_team}</span>
                    <span class="player-name">${player.name} ${player.surname}</span>
                <div class="formation-controls">
                    <button type="button" class="btn-sel t-btn" onclick="selectRole(this, '${player.id}', 't')">T</button>
                    <button type="button" class="btn-sel p-btn" onclick="selectRole(this, '${player.id}', 'p')">P</button>
                </div>
            `;
            lista.appendChild(row);
        });
    }

    async function renderFormazione() {
        const divTitolari = document.getElementById('listaTitolari');
        const divPanchina = document.getElementById('listaPanchina');
        let titolari;
        let panchina;
        // Svuota i contenitori
        divTitolari.innerHTML = '';
        divPanchina.innerHTML = '';
        if (formazione.titolari != [] && formazione.panchina != []){
            titolari = formazione.titolari.map(id => {
                return playerSquad[id]; 
                }).filter(player => player !== undefined);

            panchina = formazione.panchina.map(id => {
                return playerSquad[id]; 
                }).filter(player => player !== undefined);
        } else {
            // Chiamata per recuperare la formazione schierata
            
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
            } catch (error){
                console.error("Errore nel recuper info formazione:", error);
            }
        }
        // Ciclo Titolari
        titolari.forEach(p => {
            divTitolari.innerHTML += `
                <div class="player-card starter">
                    <span class="p-role">${p.role} - ${p.serie_a_team}</span>
                    <span class="p-name">${p.name} ${p.surname}</span>
                </div>`;
        });

        // Ciclo Panchina
        panchina.forEach(p => {
            divPanchina.innerHTML += `
                <div class="player-card bench">
                    <span class="p-role">${p.role} - ${p.serie_a_team}</span>
                    <span class="p-name">${p.name} ${p.surname}</span>
                </div>`;
        });
    }

    function renderRosaUnica() {
        const container = document.getElementById('listaCompletaRosa');
        if (!container) return;

        // 1. Trasformiamo l'oggetto playerSquad in un array
        const calciatori = Object.values(playerSquad);

        // 2. Ordiniamo per ruolo (G -> D -> M -> A)
        calciatori.sort((a, b) => {
            return prioritaRuoli[a.role] - prioritaRuoli[b.role];
        });

        // 3. Generiamo l'HTML
        container.innerHTML = calciatori.map(player => `
            <div class="player-card">
                <span class="p-role role-${player.role}">${player.role}</span>
                <div class="p-details">
                    <span class="p-name">${player.name} ${player.surname}</span>
                    <span class="p-team">${player.serie_a_team}</span>
                </div>
                ${player.mean_rating > 0 ? `<span class="p-rating">⭐ ${player.mean_rating}</span>` : ''}
            </div>
        `).join('');
    }

    //Carico le informazioni necessarie per la paginasave
    caricaLeghe();
    infoLega();
    controlloLega();
    // renderRosaUnica();
    setTimeout(() => { renderRosaUnica(); }, 2000);

});