document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("mySidebar");
    const overlay = document.getElementById("overlay");
    const openBtn = document.getElementById("openSidebar");
    const searchInput = document.getElementById("searchPlayer");
    const listaMercato = document.getElementById("listaMercato");
    const miaRosaContenitore = document.getElementById("miaRosaContenitore");
    const countRosa = document.getElementById("countRosa");

    let miaRosa = [];

    // --- SIDEBAR HOVER ---
    openBtn.addEventListener("mouseenter", () => { sidebar.classList.add("active"); overlay.classList.add("active"); });
    sidebar.addEventListener("mouseleave", () => { sidebar.classList.remove("active"); overlay.classList.remove("active"); });

    // --- SIMULAZIONE DATI MERCATO ---
    const databaseCalciatori = [
        { id: 10, nome: "Dybala", ruolo: "A" },
        { id: 11, nome: "Vlahovic", ruolo: "A" },
        { id: 12, nome: "Dyrella", ruolo: "C" },
        { id: 13, nome: "Dylhanoglu", ruolo: "C" },
        { id: 14, nome: "Dy Lorenzo", ruolo: "D" },
        { id: 15, nome: "Dyignan", ruolo: "P" },
        { id: 15, nome: "Dyignan", ruolo: "P" },
        { id: 15, nome: "Dyignan", ruolo: "P" },
        { id: 15, nome: "Dyignan", ruolo: "P" },
        { id: 15, nome: "Dyignan", ruolo: "P" }
    ];

    // --- FUNZIONE RICERCA ---
    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        if (query.length < 2) return;

        const filtrati = databaseCalciatori.filter(p => p.nome.toLowerCase().includes(query));
        renderMercato(filtrati);
    });

    function renderMercato(calciatori) {
        listaMercato.innerHTML = "";
        calciatori.forEach(p => {
            const row = document.createElement("div");
            row.className = "player-row";
            row.innerHTML = `
                <div class="player-info">
                    <span class="player-role">${p.ruolo}</span>
                    <span class="player-name">${p.nome}</span>
                </div>
                <button class="btn-add" onclick="aggiungiGiocatore(${p.id}, '${p.nome}', '${p.ruolo}')">Aggiungi</button>
            `;
            listaMercato.appendChild(row);
        });
    }

    // --- GESTIONE ROSA LOCALE ---
    window.aggiungiGiocatore = (id, nome, ruolo) => {
        if (miaRosa.find(p => p.id === id)) return alert("Giocatore già in rosa!");
        if (miaRosa.length >= 25) return alert("Rosa completa!");

        miaRosa.push({ id, nome, ruolo });
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
                    <span class="player-role">${p.ruolo}</span>
                    <span class="player-name">${p.nome}</span>
                </div>
                <button class="btn-remove" onclick="rimuoviGiocatore(${p.id})">X</button>
            `;
            miaRosaContenitore.appendChild(row);
        });
        countRosa.innerText = miaRosa.length;
    }
});