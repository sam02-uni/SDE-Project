# SDE-Project

This SOA (Service Oriented Application) is a comprehensive platform designed for the creation and end-to-end management of fantasy football leagues. Built with a scalable microservices architecture, it enables users to orchestrate every aspect of the game—from team drafting and lineup management to real-time news aggregation and matchday scoring.

## Stack of technologies:

**FastAPI**: a Python framework for building services.  
**SQLModel**: A library designed to simplify database interactions in Python FastAPI applications. It is built on top of SQLAlchemy and Pydantic, which are included as automatic dependencies.  
**Postgres**:  
**Uvicorn**:  
**Docker Container / Compose**: is used for the container of each service.  
**Pyhton**  
**HTML, CSS & JS**: used for the Fronted of the application

### External sources
**RSS FEED** from "Corriere dello sport" and "Tuttosport" sites.  
**HTML scraping** from "Gazzetta dello sport" and "sosfanta" sites.   
**Google API**  
**Football Data API**: ([Football-data](https://www.football-data.org/)) API from which we get information on players, matches, matchdays   
**Fantacalcio.it**: Website from which we scrape the fantasy ratings for each matchday

## Docker Services & Port Mapping

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

## How to install

### 🔐 Security Configuration Guide

Follow these steps to configure Google OAuth and generate the necessary security keys for the application.

### 🌐 OAuth Configuration

1.  Search for **“Google Cloud Console”** and log in.
2.  In the Google Cloud platform, click on **Select a project**.
3.  In the pop-up window, click on **New Project**.
4.  Insert a **Project name** and click Create.
5.  In the dashboard, click again on **Select a project** and choose the project you just created.
6.  Click on **APIs & Services** from the main menu.
7.  In the left sidebar, select **OAuth consent screen**.
8.  Click on **Get started**.
9.  Complete the **OAuth Consent Screen** form:
    * **App Information:** Set an app name and insert your email address.
    * **Audience:** Select **External**.
    * **Contact Information:** Insert your email address again.
    * **Policy:** Agree to the User Data Policy, then click **Continue** and **Create**.
10. Now, click on **Credentials** (or **Create OAuth client** directly if prompted).
11. Click **+ Create Credentials** > **OAuth client ID**.
12. As **Application type**, select **Web application** and complete the form:
    * Set a name for the client.
    * In **Authorized redirect URIs**, add:  
        `http://localhost:8000/auth/google/callback`
    * Click on **Create**.
13. Click on **Download JSON** (or copy the values) to get your `Client ID` and `Client Secret`.
14. Copy the `.env.example` file and rename it to `.env`.
15. Fill in the following variables in the `.env` file:
    * `GOOGLE_CLIENT_ID`
    * `GOOGLE_CLIENT_SECRET`
    * `GOOGLE_REDIRECT_URI`

### 🔑 Secret Key Generation

To ensure secure token signing, you need to generate an RSA private key.

1.  Rename the folder `keys.example` to `keys`.
2.  Open your terminal, navigate to the `keys` directory, and run the following command:

```bash
cd keys
openssl genrsa -out private.pem 2048
```
---
### Football data API key
In order to make the Football Adapter Service work and therefore get data you need to have an API Key.
Go to this [site](https://www.football-data.org/client/register) and register with an email of yours to get access to the free plan. Then check your mailbox, the key will be there.  
Now create an **.env** file in the 'football-api-adapter' folder and put this into it: FOOTBALL_API_KEY = 'xxxxx...xxxx' replacing the text between the quotes with your key.

---
### SQL Dumps 
In the 'sql' folder there are different .sql files that contains instructions to insert data which is needed for the correct functioning of the application.  
For each .sql file inject it into the fanta-db container, where the Postgresql database run: open a terminal in the root folder of the project and type
```bash
docker cp sql/<file_name>.sql fanta-db:/
```
this command will copy the .sql file into the root of the container.  
Now TODO