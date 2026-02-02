const LEGHE_URL="http://localhost:8007/process/league-management/info_webapp_home"
const PLAYERS_URL="http://localhost:8007/process/league-management/allPlayers"
const SQUAD_URL="http://localhost:8007/process/league-management"

document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("mySidebar");
    const overlay = document.getElementById("overlay");
    const openBtn = document.getElementById("openSidebar");
    const searchInput = document.getElementById("searchPlayer");
    const listaMercato = document.getElementById("listaMercato");
    const miaRosaContenitore = document.getElementById("miaRosaContenitore");
    const countRosa = document.getElementById("countRosa");
    const containerLeagues = document.getElementById("userLeagues");
    const saveSquad = document.getElementById("btnSalvaRosa");
    const selectedLegaId = localStorage.getItem('selected_league_id');

    let miaRosa = [];

    // --- SIDEBAR HOVER ---
    openBtn.addEventListener("mouseenter", () => { sidebar.classList.add("active"); overlay.classList.add("active"); });
    sidebar.addEventListener("mouseleave", () => { sidebar.classList.remove("active"); overlay.classList.remove("active"); });

    // --- GESTIONE ROSA LOCALE ---
    window.aggiungiGiocatore = (id, surname, role) => {
        if (miaRosa.find(p => p.id === id)) return alert("Giocatore già in rosa!");
        if (miaRosa.length >= 25) return alert("Rosa completa!");

        miaRosa.push({ id, surname, role });  
        aggiornaRosaUI();
    };

    window.rimuoviGiocatore = (id) => {
        miaRosa = miaRosa.filter(p => p.id !== id);
        aggiornaRosaUI();
    };

    function aggiornaRosaUI() {
        document.getElementById("emptyMsg").style.display = miaRosa.length > 0 ? "none" : "block";
        miaRosaContenitore.querySelectorAll(".player-row").forEach(el => el.remove());

        miaRosa.forEach(p => {
            const row = document.createElement("div");
            row.className = "player-row";
            row.innerHTML = `
                <div class="player-info">
                    <span class="player-role">${p.role}</span>
                    <span class="player-name">${p.surname}</span>
                </div>
                <button class="btn-remove" onclick="rimuoviGiocatore(${p.id})">X</button>
            `;
            miaRosaContenitore.appendChild(row);
        });
        countRosa.innerText = miaRosa.length;
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
    // Caricamento dinamico delle leghe
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
                    window.location.href = "lega_dashboard.html";
                };

            // Aggiungi al contenitore specifico tra News e Logout
                containerLeagues.appendChild(link);
            });
        } catch (error) {
            console.error("Errore nel caricamento leghe:", error);
        }
    }
    
    // Funzione che controlla che ci sia la lega
    function controlloLega(){
        if (!selectedLegaId) {
            console.error("Nessuna lega selezionata! Torno alla home.");
            window.location.href = "login.html"; // Opzionale: rimanda indietro se manca l'ID
            return;
        }

        console.log("Stai visualizzando la lega con ID:", selectedLegaId);
    }

    // Funzione che fa in POST l'inserimento della rosa
    async function inserisciSquadra(){
        const partecipant = document.getElementById("partecipant").value.trim();
        const squadName = document.getElementById("squadName").value.trim();
        const token = localStorage.getItem('access_token');
        if (partecipant && squadName){
            if (miaRosa.length == 25){
                const squad  = miaRosa.map(playerInRosa => {
                    return databaseCalciatori.find(c => c.id === playerInRosa.id);
                }); // Per ogni elemento in miaRosa, cerchiamo il corrispettivo nel database
                console.log(squad);
                // Chiamata POST per inserire la squadra
                let url_completo = `${SQUAD_URL}/${selectedLegaId}/add_participant`;
                let url = new URL(url_completo);
                console.log(JSON.stringify({ 
                        "email_user":partecipant,
                        "squad_name":squadName,
                        "players": squad
                    }));
                let response = await fetch(url, {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}` 
                    },
                    body: JSON.stringify({  
                        "email_user":partecipant,
                        "squad_name":squadName,
                        "players": squad
                    })
                });
                if (response.status != 201){
                    alert("Errore imprevisto nell'inserimento della squadra.");
                    console.log(response.status, response.body);
                } else {
                    alert("Inserimento avvenuto con successo!");
                    location.reload();
                }
            } else {
                alert("Numero di giocatori insufficienti, completare la rosa con 25 giocatori.");
            }
        } else {
            alert("Inserire un partecipante o un nome squadra valido.");
        }
    }

    saveSquad.addEventListener("click", inserisciSquadra);
    // Funzioni necessarie al recupero delle informazioni, ricerca e gestione dei calciatori
    let databaseCalciatori;

    async function recuperoGiocatori(){        
        let url=new URL(PLAYERS_URL);
        try {
        // Chiamata senza header Authorization
            let response = await fetch(url, {
                method: 'GET'
            });

            if (response.status === 200) {
                databaseCalciatori = await response.json();
                console.log("Giocatori caricati senza token:", databaseCalciatori);
            } else {
                console.error("Il server ha risposto con errore:", response.status);
            }
        } catch (error) {
            console.error("Errore durante la fetch:", error);
        }
    }

    // --- FUNZIONE RICERCA ---
    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        if (query.length < 2) return;

        const filtrati = databaseCalciatori.filter(p => p.surname.toLowerCase().includes(query));
        renderMercato(filtrati);
    });

    // Mostra i giocatori nello spazio sottostante
    function renderMercato(calciatori) {
        listaMercato.innerHTML = "";
        calciatori.forEach(p => {
            const row = document.createElement("div");
            row.className = "player-row";
            row.innerHTML = `
                <div class="player-info">
                    <span class="player-role">${p.role}</span>
                    <span class="player-name">${p.surname}</span>
                </div>
                <button class="btn-add" onclick="aggiungiGiocatore(${p.id}, '${p.surname}', '${p.role}')">Aggiungi</button>
            `;
            listaMercato.appendChild(row);
        });
    }

    // Invocazione delle funzioni necessarie al primo caricamento
    controlloLega();
    caricaLeghe();
    recuperoGiocatori(); 
});