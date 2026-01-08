## Descrizione Servizio

L'ultima riga del dockerfile esegue uvicorn che è il server Web

Nel docker compose avvio due container:
1. fanta-db: il container su cui runna PostegreSQL
2. fanta-data-service: il container su cui runna il servizio che fa da interfaccia al db
   - Espone diversi endpoint su un unica porta, questi endpoint corrispondono alle diverse tabelle presenti nel db