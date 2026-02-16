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
    const container = element.closest('.formation-controls');
    
    if (!container) {
        console.error("Errore: contenitore .formation-controls non trovato!");
        return;
    }

    const isAlreadySelected = element.classList.contains('selected-t') || element.classList.contains('selected-p');
    let p_id= parseInt(playerId)

    if (isAlreadySelected) {
        // Graphical remove of the color
        element.classList.remove('selected-t', 'selected-p');
        
        // Remove the IDs from the array
        formazione.titolari = formazione.titolari.filter(id => id !== p_id);
        console.log("Titolari prima:", formazione.titolari);
        formazione.panchina = formazione.panchina.filter(id => id !== p_idd);
        
        console.log(`Rimosso giocatore ${playerId}. Titolari: ${formazione.titolari.length}, Panchina: ${formazione.panchina.length}`);
        return; 
    }

    // Search some buttons inside the container
    const buttons = container.querySelectorAll('.btn-sel');

    // Graphic reset for each button
    buttons.forEach(btn => btn.classList.remove('selected-t', 'selected-p'));

    // Update logic for each IDs with no duplicates
    formazione.titolari = formazione.titolari.filter(id => id !== p_id);
    formazione.panchina = formazione.panchina.filter(id => id !== p_id);

    if (tipo === 't') {
        if (formazione.titolari.length < 11) {
            formazione.titolari.push(p_id);
            element.classList.add('selected-t');
        } else {
            alert("Hai già 11 titolari!");
        }
    } else if (tipo === 'p') {
        if (formazione.panchina.length < 7) {
            formazione.panchina.push(p_id);
            element.classList.add('selected-p');
        } else {
            alert("La panchina è piena (max 7)!");
        }
    }
}


document.addEventListener("DOMContentLoaded", () => {
    // DOM elements
    const sidebar = document.getElementById("mySidebar");
    const overlay = document.getElementById("overlay");
    const openBtn = document.getElementById("openSidebar");
    
    const modalFormazione = document.getElementById("modalFormazione");
    const modalCalcola= document.getElementById("modalCalcolaGiornata")
    const btnFormazione = document.getElementById("btnFormazione");
    const btnInserisciSquadra = document.getElementById("btnInserisciSquadra");
    const closeModalFormazione = document.getElementById("closeModalFormazione");
    const closeModalCalcola= document.getElementById("closeModalCalcola")
    const saveBtn = document.getElementById("saveFormazione");
    const containerLeagues = document.getElementById("userLeagues");
    const logoutForm = document.getElementById('logoutForm');
    const leagueId = localStorage.getItem("selected_league_id");
    const numeroGiornata = document.getElementById("numeroGiornata");
    const scadenzaFormazione = document.getElementById("scadenza") // TODO
    const btnCalcoloGiornata = document.getElementById("btnCalcolaGiornata");
    const btnConfermaCalcolo= document.getElementById("confirm")
    const btnViewGrades = document.getElementById("btnViewGrades");
    const divLastScores = document.getElementById('divLastScores');
    const leagueName = document.getElementById("leagueNameDisplay");
    const board = document.getElementById("leaderboardBody");
    const divTitolari = document.getElementById('listaTitolari');
    const divPanchina = document.getElementById('listaPanchina');
    const prioritaRuoli = { "G": 1, "D": 2, "M": 3, "A": 4 };

    let playerSquad;


    // Sidebar logic
    const openNav = () => {
        sidebar.classList.add("active");
        overlay.classList.add("active");
    };

    const closeNav = () => {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    };

    // Open when the mouse are on the button
    openBtn.addEventListener("mouseenter", openNav);

    // Close when the mouse is not in the sidebar
    sidebar.addEventListener("mouseleave", closeNav);

    // Close if click on close
    overlay.addEventListener("click", () => {
        closeNav();
        modalFormazione.style.display = "none";
        modalCalcola.style.display = "none"; 
    });


    //btnDeleteLeague.addEventListener("click", () => {
        // TODO ? 
    //})

    // Some reference to the other pages
    btnInserisciSquadra.addEventListener("click", () => {
        window.location.href="rosa_dashboard.html"
    });

    btnViewGrades.addEventListener("click", () => {
        window.location.href= "grades_dashboard.html"
    })
    
    // Logic for the formation
    if (btnFormazione) {
        btnFormazione.addEventListener("click", () => {
            modalFormazione.style.display = "block";
            overlay.classList.add("active"); 
            formazione.titolari = [];
            formazione.panchina = [];
            caricaCalciatori();
        });
    }

    if (closeModalFormazione) {
        closeModalFormazione.addEventListener("click", () => {
            modalFormazione.style.display = "none";
            overlay.classList.remove("active");
        });
    }

    
    // Logic for calculate the grades
    if (btnCalcoloGiornata) {
        btnCalcoloGiornata.addEventListener("click", () => {
            modalCalcola.style.display = "block";
            overlay.classList.add("active");
            popolaGiornate();
        });
    }

    if (closeModalCalcola) {
        closeModalCalcola.addEventListener("click", () => {
            modalCalcola.style.display = "none";
            overlay.classList.remove("active");
        });
    }
    
    // Dashboard initialization
    async function inizializzaDashboard() {
    try {
        // League control
        controlloLega();

        // Take all the leagues
        await caricaLeghe();

        // Show league data and load palyer squad
        await infoLega();

        // Render of the data
        console.log("Dati pronti, inizio rendering...");
        renderRosaUnica();
        await renderFormazione();

        await renderLastScores();

    } catch (error) {
        console.error("Errore nell'inizializzazione dashboard:", error);
    }
}

    // Save formation logic
    async function saveFormation(){            
        console.log("Salvataggio formazione, ID selezionati:  T:", formazione.titolari, " P:", formazione.panchina);
        let squadId = localStorage.getItem("squad_id");
        let current = localStorage.getItem("current_matchday");
        modalFormazione.style.display = "none";
        overlay.classList.remove("active");
        
        // Call to the process to insert the formation
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
                renderFormazione()
                window.location.reload()
            }

        } catch (error){
            console.error('Unexpected error', error);
        }
    }
    
    // Compute score logic
    async function computeScores(){

            try {
                const token = localStorage.getItem('access_token');
                const league_id = localStorage.getItem("selected_league_id");
                
                const selectElement = document.getElementById("selectMatchday");
                const matchday = selectElement.value;

                if (!matchday) {
                    alert("Seleziona una giornata");
                    return;
                    }

                let url = `${MATCHDAY_URL}/leagues/${league_id}/lineups/calculate_scores?matchday_number=${matchday}`;

                let response = await fetch(url, {
                    method: "GET", 
                    headers: { 
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}` 
                    }
                });

                if (response.ok) {
                    alert("Giornata calcolata con successo!");
                    // This is to refresh the classific
                    window.location.reload(); 
                } else if (response.status === 401) {
                    const success = await refreshAccessToken();
                    if (success) {
                        const newToken=localStorage.getItem('access_token');
                        response= await fetch(url, {
                        method: 'GET', 
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${newToken}`
                        }
                        });
                    } else {
                        window.location.href = "login.html";
                    }
                } else {
                    alert("Errore: Impossibile calcolare la giornata");
                }

            } catch (error) {
                console.error("Errore durante il calcolo:", error);
            }

    }
    // Add the function to the respective button
    saveBtn.addEventListener("click", saveFormation);
    btnConfermaCalcolo.addEventListener("click", computeScores)

    // Refresh token logic
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

    // Load leagues
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
                    const newToken=localStorage.getItem('access_token');
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

                // Add the specific container between News and Logout
                containerLeagues.appendChild(link);
            });
        } catch (error) {
            console.error("Errore nel caricamento leghe:", error);
        }
    }

    // Control if there is the lega id
    function controlloLega(){
        if (!leagueId) {
            console.error("Nessuna lega selezionata! Torno alla home.");
            window.location.href = "login.html"; // Opzionale: rimanda indietro se manca l'ID
            return;
        }

        console.log("Stai visualizzando la lega con ID:", leagueId);
    }

    // Retrive info for the selected league
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
                const success = await refreshAccessToken();
                if (success) {
                    const newToken=localStorage.getItem('access_token');
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
            // Display of some buttons if some conditions are matched
            if (infoLega.isAdmin){
                btnInserisciSquadra.style.display = 'block';
                if (infoLega.lastMatchFinished){
                    btnCalcoloGiornata.style.display = 'block';
                } else {
                    btnViewGrades.style.display = 'block';
                }
            } else {
                btnInserisciSquadra.style.display = 'none';
            }

            if (infoLega.firstMatchStarted){
                //TODO TOGLI : btnFormazione.style.display = 'none';
                scadenzaFormazione.textContent = '';
            } else {
                btnFormazione.style.display = 'block';
            }
            // Display of the matchday number and some other info
            numeroGiornata.textContent = `Giornata ${infoLega.currentMatchday}`;
            let nome_lega = localStorage.getItem('nome_lega');
            localStorage.setItem("current_matchday", infoLega.currentMatchday);
            if (infoLega.squad != null){
                if (infoLega.squad.id){
                    localStorage.setItem('squad_id', infoLega.squad.id);
                    playerSquad = infoLega.squad.players;
                }
            }else {
                localStorage.removeItem('squad_id')
            }
        
                
            leagueName.textContent = `${nome_lega} - Serie A`;

            // Classific visualization
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


    // Player population
    async function caricaCalciatori() {
        const lista = document.getElementById("listaCalciatori");

        lista.innerHTML = ""; // Clear the previous list

        const calciatoriOrdinati = Object.entries(playerSquad).sort(([, a], [, b]) => {
            return prioritaRuoli[a.role] - prioritaRuoli[b.role];
        });

        calciatoriOrdinati.forEach(([id,player]) => {
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

    // Matchdays population
    function popolaGiornate() {

    const currentMatchday = localStorage.getItem("current_matchday") || "1";
    
    selectMatchday.innerHTML = ""; 

    for (let i = 1; i <= 38; i++) {
        const option = document.createElement("option");
        option.value = i;
        option.textContent = `Giornata ${i}`;
        
        if (i.toString() === currentMatchday.toString()) {
            option.selected = true;
        }
        
        selectMatchday.appendChild(option);
    }
}

    // Formation visualization if insert
    async function renderFormazione() {
        let squadId = localStorage.getItem("squad_id");
        if(!squadId) return;
        let currentMatchday = localStorage.getItem("current_matchday");

        if (!divTitolari || !divPanchina) return;

        divTitolari.innerHTML = '';
        divPanchina.innerHTML = '';

        let titolariData = [];
        let panchinaData = [];

        // If we upload now the formation we use that data
        if (formazione.titolari.length > 0) {
            titolariData = formazione.titolari.map(id => playerSquad[id]).filter(p => p);
            panchinaData = formazione.panchina.map(id => playerSquad[id]).filter(p => p);
        } 
        // Otherwise call at the server
        else {
            let url = `${MATCHDAY_URL}/squads/${squadId}/lineups?matchday_number=${currentMatchday}`;
            try {
                const token = localStorage.getItem('access_token');
                let response = await fetch(url, {
                    method: 'GET', 
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json(); 
                    console.log("Dati ricevuti:", data);

                    // Il backend restituisce un oggetto con una lista "players"
                    if (data && data.players) {
                        // Separiamo titolari e panchina usando il flag 'is_starting'
                        titolariData = data.players
                            .filter(item => item.is_starting === true)
                            .map(item => item.player); // Prendiamo l'oggetto player interno

                        panchinaData = data.players
                            .filter(item => item.is_starting === false)
                            .map(item => item.player);
                        
                        console.log("Titolari trovati:", titolariData.length);
                    }
                }
            } catch (error) {
                console.error("Errore nel recupero info formazione:", error);
            }
        }

        // DISEGNA I TITOLARI
        titolariData.forEach(p => {
            divTitolari.innerHTML += `
                <div class="player-card starter">
                    <span class="p-role role-${p.role}">${p.role}</span>
                    <div class="p-details">
                        <span class="p-team">${p.serie_a_team}</span>
                        <span class="p-name">${p.name} ${p.surname}</span>
                    </div>
                </div>`;
        });

        // DISEGNA LA PANCHINA
        panchinaData.forEach(p => {
            divPanchina.innerHTML += `
                <div class="player-card bench">
                    <span class="p-role role-${p.role}">${p.role}</span>
                    <div class="p-details">
                        <span class="p-team">${p.serie_a_team}</span>
                        <span class="p-name">${p.name} ${p.surname}</span>
                    </div>
                </div>`;
        });
    }

    // Visualization about the player squad
    function renderRosaUnica() {
        const container = document.getElementById('listaCompletaRosa');
        if (!container) return;
        if (playerSquad){
            // Transform from object into array
            const calciatori = Object.values(playerSquad);

            // Role ordination
            calciatori.sort((a, b) => {
                return prioritaRuoli[a.role] - prioritaRuoli[b.role];
            });

            // Generate the HTML
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
    }

    // Render the last score
    async function renderLastScores(){
        let squadId = localStorage.getItem("squad_id");
        if(!squadId) return;
        let currentMatchday = localStorage.getItem("current_matchday");
        squad_id=parseInt(squadId)
        matchday= parseInt(currentMatchday)

        let url = `${MATCHDAY_URL}/${squad_id}/last-scores?matchday_number=${matchday}`;
        
        try {
                const token = localStorage.getItem('access_token');
                let response = await fetch(url, {
                    method: 'GET', 
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json(); 
                    console.log("Dati ricevuti:", data);
                    divLastScores.innerHTML = data.map(d => `
                            <div class="score-row">
                            <span class="matchday-label">Matchday ${d.matchday_number}</span>
                            <span class="score-value">${d.score}</span>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error("Errore nel recupero info formazione:", error);
            }
    }

    // Logout logic
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
                window.location.href = "login.html";
            }
        });
    }

   inizializzaDashboard();

});