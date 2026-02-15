# SDE-Project
Stack delle tecnologie:

**FastApi**: framework di python per realizzare servizi   
**SQLModel**: libreria che aiuta l'uso del db con python FastApi. Costruita sopra SQLAlchemy e Pydantic (sono installati auto di conseguenza)

# Docker Services & Port Mapping

This table provides a comprehensive overview of the microservices configuration as defined in the `docker-compose.yml` file.

| Functional Area | Service | Container Name | Host Port (Local) | Container Port |
| :--- | :--- | :--- | :--- | :--- |
| **Database** | `db` | `fanta-db` | **5432** | 5432 |
| **Frontend** | `web-interface` | *N/A* | **3000** | 80 |
| **Auth** | `auth-process-service` | `auth-process-service` | **8000** | 8000 |
| | `auth-core-service` | `auth-core-service` | **8010** | 8000 |
| **Data Layer** | `data-service` | `fanta-data-service` | **8001** | 8000 |
| **League** | `league-service` | `league-business-service` | **8004** | 8000 |
| | `squad-service` | `squad-business-service` | **8011** | 8000 |
| | `league-management-process-service` | `league-management-process-service` | **8007** | 8000 |
| **News** | `rss-feed-service` | `rss_feed_container` | **8002** | 8000 |
| | `aggregator-service` | `news_aggregator_container` | **8003** | 8000 |
| | `html-scrape-service` | `html_scraper_container` | **8034** | 8000 |
| | `html-aggregator-service` | `html_aggregator_container` | **8006** | 8000 |
| | `news-service` | `news_container` | **8005** | 8000 |
| **Matchday** | `grades-scraper-service` | `grades_scraper_service` | **8015** | 8000 |
| | `lineup-service` | `lineup-business-service` | **8016** | 8000 |
| | `matchday-management-service` | `matchday-management-service` | **8017** | 8000 |
| **Adapters** | `adapter-football-service` | `footballapi-adapter-service` | **8020** | 8000 |

### 📌 Technical Notes
* **Web Access:** The primary dashboard is accessible at `http://localhost:3000`.
* **Inter-Service Communication:** Within the Docker network, services communicate using their **service name** and the internal port **8000** (e.g., `http://data-service:8000`).
* **Database Access:** The PostgreSQL instance is exposed externally on the standard port `5432`.


