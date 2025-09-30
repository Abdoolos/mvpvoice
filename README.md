AI Callcenter Agent - Norsk Telecom Overholdelse

Dette er et AI-drevet analyseverktøy som hjelper telekomselskaper i Norge med å følge regelverket og GDPR-kravene når de analyserer kundesamtaler.

Hva kan systemet gjøre?

Norsk telecom-analyse:
- Sjekker at bindingstid blir forklart tydelig til kundene
- Kontrollerer at all prisinformasjon er komplett og riktig
- Oppdager hvis selgere bruker for høyt press eller utilbørlige teknikker
- Lager detaljerte rapporter om regelbrudd

Kunstig intelligens:
- Gjør om tale til tekst på norsk med høy kvalitet
- Skiller automatisk mellom kunde og selger i samtalen
- Analyserer stemning og tone i samtalen
- Plukker ut de viktigste øyeblikkene automatisk

GDPR og personvern:
- Fjerner automatisk personopplysninger som fødselsnummer og telefonnummer
- Behandler data sikkert for analyse
- Beholder kun det som er nødvendig
- Krypterer alt som lagres

Moderne brukergrensesnitt:
- Helt på norsk
- Oppdateres i sanntid
- Fine diagrammer og statistikk
- Mørk og lys modus

Slik kommer du i gang

Den enkleste måten:
1. Last ned prosjektet fra git
2. Kjør ./start.sh
3. Gå til http://localhost:3000

Hvis du vil gjøre det manuelt:
1. Kopier .env.example til .env
2. Kjør docker-compose up -d
3. Se logger med docker-compose logs -f

Tjenester du kan bruke:
- Hovedsiden: http://localhost:3000
- API: http://localhost:8000
- API-dokumentasjon: http://localhost:8000/docs
- Celery overvåkning: http://localhost:5555

Hvordan prosjektet er organisert

Frontend-mappen inneholder Next.js dashboard på norsk med alle komponenter for brukergrensesnittet.

Backend-mappen har FastAPI server med alle API-endepunkter, database-modeller, business-logikk, og Celery-oppgaver for asynkron behandling.

Data-mappen har eksempel-lydfiler for testing.

Docs-mappen inneholder dokumentasjon.

Ops-mappen har DevOps-konfigurasjon for deployment.

Utvikling

Du trenger Docker og Docker Compose installert. For lokal utvikling kan du også installere Node.js 18+ og Python 3.11+.

For backend-utvikling:
1. Gå til backend-mappen
2. Installer avhengigheter med pip install -r requirements.txt
3. Start med uvicorn main:app --reload

For frontend-utvikling:
1. Gå til frontend-mappen
2. Installer med npm install
3. Start med npm run dev

For å teste API-et kan du bruke curl eller Postman:
- Helsesjekk: curl http://localhost:8000/health
- Last opp lydfil: curl -X POST "http://localhost:8000/api/v1/upload/" -F "file=@audio.wav"
- Hent samtaler: curl http://localhost:8000/api/v1/calls/

Eksempel på bruk

1. Last opp en lydfil via API-et
2. Følg med på prosesseringen
3. Hent analyseresultatene

GDPR og sikkerhet

Systemet følger strenge sikkerhetskrav:
- Anonymiserer persondata automatisk
- Krypterer alt som lagres
- Sikre API-forbindelser
- Tilgangskontroll og logging
- Sletter data etter en bestemt tid

Dette følger norske telecom-regler, GDPR, og ISO 27001 prinsipper.

Produksjon

For produksjonsmiljø anbefaler vi å bruke Nginx:
1. Kjør docker-compose --profile production up -d
2. Systemet blir tilgjengelig på http://localhost

Husk å sette opp riktige environment-variabler i .env-filen.

Overvåkning

Du kan følge med på systemet ved å se på logger:
- docker-compose logs -f for alle tjenester
- docker-compose logs -f backend for kun backend

Celery Flower på http://localhost:5555 viser status på bakgrunnsoppgaver.

Bidrag til prosjektet

1. Fork repository
2. Lag en ny branch for din endring
3. Gjør endringene og commit
4. Push til din branch
5. Lag en Pull Request

Lisens

Dette prosjektet bruker MIT-lisens.

Dette systemet er laget spesielt for den norske telecom-industrien og hjelper bedrifter med å følge regelverket på en enkel måte.
