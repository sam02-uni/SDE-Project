document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("mySidebar");
    const overlay = document.getElementById("overlay");
    const openBtn = document.getElementById("openSidebar");
    const btnCalcola = document.getElementById("btnCalcola");
    const contenitoreVoti = document.getElementById("formazioneVoti");

    // --- SIDEBAR HOVER ---
    openBtn.addEventListener("mouseenter", () => { sidebar.classList.add("active"); overlay.classList.add("active"); });
    sidebar.addEventListener("mouseleave", () => { sidebar.classList.remove("active"); overlay.classList.remove("active"); });

    // --- SIMULAZIONE DATI VOTI ---
    const datiVoti = [
        { nome: "Maignan", ruolo: "POR", voto: 6.5 },
        { nome: "Theo Hernandez", ruolo: "D", voto: 7.0 },
        { nome: "Dimarco", ruolo: "D", voto: 5.5 },
        { nome: "Barella", ruolo: "C", voto: 6.0 },
        { nome: "Pulisic", ruolo: "C", voto: 7.5 },
        { nome: "Lautaro Martinez", ruolo: "A", voto: 8.0 }
    ];

    btnCalcola.addEventListener("click", () => {
        // Simula chiamata al backend
        btnCalcola.innerText = "Calcolo in corso...";
        btnCalcola.disabled = true;

        setTimeout(() => {
            renderVoti(datiVoti);
            btnCalcola.innerText = "Calcola Giornata";
            btnCalcola.disabled = false;
            alert("Giornata calcolata con successo!");
        }, 1500);
    });

    function renderVoti(giocatori) {
        contenitoreVoti.innerHTML = "";
        giocatori.forEach(g => {
            const row = document.createElement("div");
            row.className = "player-row";
            
            // Determina colore voto
            let colorClass = "vote-neutral";
            if (g.voto >= 7) colorClass = "vote-high";
            if (g.voto <= 5.5) colorClass = "vote-low";

            row.innerHTML = `
                <div class="player-info">
                    <span class="player-role">${g.ruolo}</span>
                    <span class="player-name">${g.nome}</span>
                </div>
                <div class="vote-badge ${colorClass}">${g.voto.toFixed(1)}</div>
            `;
            contenitoreVoti.appendChild(row);
        });
    }
});