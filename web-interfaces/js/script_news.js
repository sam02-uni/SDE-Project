// Configuration variables
const API_URL = "http://localhost:8005/news";
const FILTER_URL = "http://localhost:8005/news-filter";
const TOKEN_URL = "http://localhost:8000/auth/refresh";
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
            credentials: 'include' 
        });

        if (!refreshResp.ok) {
            throw new Error('Sessione scaduta, effettuare login');
        }
        return true; 
    } catch (err) {
        console.error('Errore refresh:', err);
        return false;
    }
}

// Retrieve the news from process centric service
async function fetchNews() {
    try {
        // Token verify
        const response = await fetch(API_URL, {credential: "includes"});
        if (response.status === 401) {
            console.warn("Access token scaduto, tentativo di refresh in corso...")
            const success = await refreshAccessToken();
            if (success) {
                response = await fetch(API_URL, {credentials: 'include'});
            } else {
                // window.location.href = '/login';
                return;
            }
        }

        if (!response.ok) {
            // window.location.href = '/login';
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
        const response = await fetch(url, {credential: "includes"});
        if (response.status === 401) {
            console.warn("Access token scaduto, tentativo di refresh in corso...")
            const success = await refreshAccessToken();
            if (success) {
                response = await fetch(url, {credentials: 'include'});
            } else {
                // window.location.href = '/login';
                return;
            }
        }

        if (!response.ok) {
            // window.location.href = '/login';
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

// Start
fetchNews();
