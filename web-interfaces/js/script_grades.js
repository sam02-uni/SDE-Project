 
const TOKEN_URL = "http://localhost:8000/auth/refresh";
const LEGHE_URL="http://localhost:8007/process/league-management/info_webapp_home"
MATCHDAY_URL="http://localhost:8017/process/matchday-management"

const sidebar = document.getElementById("mySidebar");
const overlay = document.getElementById("overlay");
const triggerArea = document.getElementById("triggerArea");
const newsGrid = document.getElementById("newsGrid");
const searchBar = document.getElementById("searchBar");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const pageInfo = document.getElementById("pageInfo");
const filterBtn = document.getElementById("filterBtn");
const filterMenu = document.getElementById("filterMenu");
const tagChecklist = document.getElementById("tagChecklist");
const applyBtn = document.getElementById("applyFilters");
const logoutForm = document.getElementById('logoutForm');
const containerLeagues = document.getElementById("userLeagues");
const divTitolari = document.getElementById('listaVotiTitolari');
const divPanchina = document.getElementById('listaVotiPanchina');

let formazione = {
    titolari: [], // Max 11
    panchina: []  // Max 7
};

// Sidebar logic
const openNav = () => { sidebar.classList.add("active"); overlay.classList.add("active"); };
const closeNav = () => { sidebar.classList.remove("active"); overlay.classList.remove("active"); };

triggerArea.addEventListener("mouseenter", openNav);
sidebar.addEventListener("mouseleave", closeNav);
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

            // Aggiungi al contenitore specifico tra News e Logout
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
                localStorage.removeItem('access_token'); // Rimuovi il token specifico
                localStorage.clear(); 
                window.location.href = "login.html"; 
}           else {
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

function renderPlayerWithGrade(containerId, player, grade) {
    const container = document.getElementById(containerId);
    
    // Se il voto è un numero basso, possiamo cambiare colore (facoltativo)
    const gradeClass = grade < 6 ? 'p-grade low-grade' : 'p-grade';

    container.innerHTML += `
        <div class="player-card">
            <span class="p-role role-${player.role}">${player.role}</span>
            <div class="p-details">
                <span class="p-name">${player.name} ${player.surname}</span>
                <span class="p-team">${player.serie_a_team}</span>
            </div>
            <span class="${gradeClass}">${grade}</span>
        </div>
    `;
}


    // --- VISUALIZZA I VOTI ---
 async function renderLineupWithVotes() {
    let squadId = localStorage.getItem("squad_id");
    let currentMatchday = localStorage.getItem("current_matchday");
    const token = localStorage.getItem('access_token');

    if (!squadId || !divTitolari || !divPanchina) return;

    try {
        // 1. Recupera la formazione
        let url_lineup = `${MATCHDAY_URL}/lineups/${squadId}/${currentMatchday}`;
        let response = await fetch(url_lineup, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const lineupData = await response.json();
            const lineup_id = lineupData.id;

            // 2. Recupera i voti
            let url_grades = `${MATCHDAY_URL}/lineups/${lineup_id}/grades`;
            let response_votes = await fetch(url_grades, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            // Creiamo un "dizionario" dei voti per trovarli velocemente
            let gradesMap = {};
            if (response_votes.ok) {
                const votesList = await response_votes.json();
                votesList.forEach(v => {
                    // Mappa l'ID del giocatore al suo voto (es: { "10": 7.5, "25": 6 })
                    gradesMap[v.player_id] = v.grade; 
                });
            }

            // 3. Unione e Rendering
            divTitolari.innerHTML = '';
            divPanchina.innerHTML = '';

            lineupData.players.forEach(item => {
                const p = item.player;
                
                // Cerchiamo il voto corrispondente a questo giocatore nella mappa
                let voto=gradesMap[p.id]
                if (voto === undefined){
                    voto=gradesMap[p.id]="-"
                    }
                
                // Generiamo l'HTML usando la funzione che hai creato
                const cardHTML = creaCardGiocatoreVoto(p, voto);

                // Smistiamo tra titolari e panchina
                if (item.is_starting) {
                    divTitolari.innerHTML += cardHTML;
                } else {
                    divPanchina.innerHTML += cardHTML;
                }
            });
        }
    } catch (error) {
        console.error("Errore nel recupero dati:", error);
    }
}

function creaCardGiocatoreVoto(p, voto) {
    const gradeClass = (voto !== "-" && voto < 6) ? 'p-grade low-grade' : 'p-grade';
    
    return `
        <div class="player-card">
            <span class="p-role role-${p.role}">${p.role}</span>
            <div class="p-details">
                <span class="p-name">${p.name} ${p.surname}</span>
                <span class="p-team">${p.serie_a_team}</span>
            </div>
            <span class="${gradeClass}">${voto}</span>
        </div>
    `;
}

    // DISEGNA I TITOLARI
    /*titolariData.forEach(p => {
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
    });*/


//Carico le leghe
caricaLeghe();
renderLineupWithVotes();