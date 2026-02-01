// Configuration variables
const API_URL = "http://localhost:8005/news";
const FILTER_URL = "http://localhost:8005/news-filter";
const TOKEN_URL = "http://localhost:8000/auth/refresh";
const LEGHE_URL="http://localhost:8007/process/league-management/info_webapp_home"
const itemsPerPage = 12;
const tags = ["infortunio", "stop", "scelte", "formazione", "voti", "ufficiale", "rientro"];
let allNews = [];
let filteredNews = [];
let selectedTags = [];
let currentPage = 1;

// Dom elements
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

// Eseguito subito all'apertura della pagina 
const urlParams = new URLSearchParams(window.location.search);
const tokenDaUrl = urlParams.get('token');
if (tokenDaUrl) {
    localStorage.setItem('access_token', tokenDaUrl);
    // Pulisce l'URL per estetica
    const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl);
}

// Checklist generation
tags.forEach(tag => {
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" value="${tag}"> ${tag.charAt(0).toUpperCase() + tag.slice(1)}`;
    tagChecklist.appendChild(label);
});

// Filter logic
filterBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    filterMenu.classList.toggle("active");
});

// Close menu if outside click
document.addEventListener("click", () => filterMenu.classList.remove("active"));
filterMenu.addEventListener("click", (e) => e.stopPropagation());

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

// Retrieve the news from process centric service
async function fetchNews() {
    try {
        // Recuperiamo il token attuale dal localStorage
    let token = localStorage.getItem('access_token');

    let response = await fetch(API_URL, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
});

    //Controllo se l'Access Token è scaduto 
    if (response.status === 401) {
        console.log("E ANDATO L'ERRORE")
        console.warn("Access token scaduto, tentativo di refresh in corso...");
    
    // Questa funzione aggiornerà il localStorage con il nuovo token
    const success = await refreshAccessToken();
    
    if (success) {
        // Recuperiamo il NUOVO token appena salvato
        token = localStorage.getItem('access_token');
        
        //Riproviamo la GET con il nuovo token
        response = await fetch(API_URL, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
    } else {
        console.error("Refresh fallito o sessione scaduta.");
        window.location.href = 'login.html';
        return;
    }

}

    //Controllo finale sulla riuscita della richiesta
    if (!response.ok) {
            window.location.href = 'login.html';
            return;
        }
        
    const data = await response.json();
    console.log("Dati ricevuti dal server:", data);
    if (data.Response && data.Response.Filter) {
        allNews = data.Response.Filter; 
        } 
    else if (data.Response) {
        allNews = data.Response;
        }
    else if (Array.isArray(data)) {
        allNews = data;
        }

    filteredNews = allNews;
    renderPage();
    } catch (error) {
        console.error("Errore fetch:", error);
        newsGrid.innerHTML = `<p>Errore nel caricamento: ${error.message}</p>`;
    }
}

// Rendering
function renderPage() {
    newsGrid.innerHTML = "";
    
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageItems = filteredNews.slice(start, end);

    if (pageItems.length === 0) {
        newsGrid.innerHTML = "<p>Nessuna notizia trovata.</p>";
    }

    pageItems.forEach(item => {
        const article = document.createElement("article");
        article.className = "box-titolo";
        article.innerHTML = `
            <div class="fonte">${item.fonte || 'News'}</div>
            <h3>${item.titolo}</h3>
            <p>${item.riassunto || 'Nessuna anteprima disponibile.'}</p>
            <a href="${item.link}" target="_blank">Leggi notizia →</a>
        `;
        newsGrid.appendChild(article);
    });

    // Aggiorna stato paginazione
    pageInfo.innerText = `Pagina ${currentPage}`;
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = end >= filteredNews.length;
}

// Filter function
async function applyFilters() {
    const checkboxes = tagChecklist.querySelectorAll("input:checked");
    const selectedTags = Array.from(checkboxes).map(cb => cb.value);
    
    // Build the query string
    let url = new URL(FILTER_URL);
    selectedTags.forEach(tag => url.searchParams.append("tags", tag));

    try {
        // Verify token
       // Recuperiamo il token aggiornato dal localStorage
    let token = localStorage.getItem('access_token');

    
    let response = await fetch(url, {
        method: 'GET', 
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
    }
});

    if (response.status === 401) {
        console.warn("Access token scaduto, tentativo di refresh in corso...");
        
        const success = await refreshAccessToken();
        console.log("GENERO NUOVO ACCESS TOKEN DA NEWS")
        if (success) {
            // Se il refresh ha avuto successo, prendiamo il NUOVO token dal localStorage
            token = localStorage.getItem('access_token');
        
            // Riproviamo la fetch con il nuovo token
            response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
    }   else {
            console.error("Refresh fallito, reindirizzamento al login.");
            window.location.href = 'login.html';
            return;
    }
}

        if (!response.ok) {
            window.location.href = 'login.html';
            return;
        }

        // Retrieve data
        const data = await response.json();
        allNews = data.Response.Filter || [];
        filteredNews = allNews;
        
        currentPage = 1;
        renderPage();
        filterMenu.classList.remove("active");
    } catch (error) {
        console.error("Errore durante il filtraggio:", error);
    }
}

applyBtn.addEventListener("click", applyFilters);

// Navigation between pages
function changePage(direction) {
    currentPage += direction;
    renderPage();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

prevBtn.addEventListener("click", () => changePage(-1));
nextBtn.addEventListener("click", () => changePage(1));

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

//Carico le leghe
caricaLeghe()
// Start
fetchNews();
