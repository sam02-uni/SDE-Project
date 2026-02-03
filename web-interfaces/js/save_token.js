// Eseguito subito all'apertura della pagina 
const urlParams = new URLSearchParams(window.location.search);
const tokenDaUrl = urlParams.get('token');
if (tokenDaUrl) {
    localStorage.setItem('access_token', tokenDaUrl);
    // Pulisce l'URL per estetica
    const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl);
}


window.location.href = "home_news.html"