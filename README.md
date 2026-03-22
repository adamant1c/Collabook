# 🎲 Collabook RPG

**Piattaforma di storytelling collaborativo con AI Dungeon Master**

Trasforma le tue idee creative in avventure epiche con gli amici! Collabook RPG combina storytelling collaborativo con meccaniche D&D autentiche, narrazione AI intelligente e un'interfaccia medievale.

[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](./LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](./docker-compose.yml)

---

## ✨ Funzionalità

### ⚔️ Meccaniche RPG
- **Combattimento D&D** – Tiri di dado, iniziativa, colpi critici
- **Progressione personaggio** – 5 statistiche di base, XP, livelli
- **Sistema di quest** – Quest principali e secondarie con ricompense
- **Incontri casuali** – Battaglie con 9 tipi di nemici
- **Sistema morte** – Resurrezione (1x) + morte permanente

### 🤖 AI-Powered
- **Narrazione contestuale** – Il DM risponde in modo intelligente alle azioni del giocatore
- **Multi-provider** – Supporta Ollama (locale, gratis), Google Gemini, Groq e OpenAI
- **Ottimizzazione token** – Riduzione del 70-85% dei costi rispetto agli approcci tradizionali

### 🌍 World Building
- **3 mondi di default** – Storico, Fantasy, Fantascienza
- **Mondi personalizzati** – Creati dall'amministratore
- **Editor quest & nemici** – Personalizza le sfide di gioco

### 🔒 Sicurezza
- **Autenticazione JWT** – Gestione sessioni sicura
- **Rate Limiting** – Protezione da attacchi brute force
- **Ruoli** – Admin e Giocatore
- **Reset password** – Recupero via email

---

## 🏗️ Architettura

Il progetto è composto da due applicazioni separate:

```
Collabook/
├── backend/               # API FastAPI (Python)
│   ├── app/
│   │   ├── api/          # Endpoint REST (auth, storie, quest, combattimento)
│   │   ├── core/         # Database, sicurezza, LLM client
│   │   ├── models/       # Modelli SQLAlchemy e Pydantic
│   │   └── agents/       # Agenti AI (narratore, world keeper)
│   └── requirements.txt
│
├── (root)                 # Frontend Django + blog + account
│   ├── core/             # Client API, context processors
│   ├── blog/             # Sistema blog
│   ├── character/        # Gestione personaggio
│   ├── world/            # Gestione mondi
│   ├── game/             # Interfaccia di gioco
│   └── requirements.txt
│
├── docker-compose.yml        # Servizi di sviluppo
├── docker-compose.prod.yml   # Configurazione produzione
└── .env.example              # Template variabili d'ambiente
```

---

## 🚀 Avvio Rapido

### Prerequisiti

- **Docker** e **Docker Compose**
- **Git**

### Installazione

**1. Clona il repository**
```bash
git clone <url-repository>
cd collabook
```

**2. Configura l'ambiente**
```bash
cp .env.example .env
# Genera una SECRET_KEY sicura
openssl rand -hex 32
# Incolla il risultato in .env come SECRET_KEY=<chiave-generata>
```

**3. Avvia i servizi**
```bash
docker-compose up --build
```

Questo avvia:
- **Backend** (FastAPI) su `http://localhost:8000`
- **Frontend** (Django) su `http://localhost:8501`
- **PostgreSQL** su porta `5432`
- **Redis** su porta `6379`

**4. Inizializza il database**
```bash
# In un nuovo terminale
docker-compose exec backend python manage.py create-admin
docker-compose exec backend python manage.py seed-worlds
docker-compose exec backend python manage.py seed-quests
docker-compose exec backend python manage.py seed-enemies
docker-compose exec backend python manage.py seed-items
```

**5. Accedi all'applicazione**
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

---

## ⚙️ Variabili d'Ambiente

| Variabile | Sviluppo | Produzione | Note |
|---|---|---|---|
| `ENVIRONMENT` | `development` | `production` | Obbligatoria in prod |
| `SECRET_KEY` | Auto-generata | **Richiesta** | Min 32 caratteri |
| `LLM_PROVIDER` | `ollama` | `gemini`/`groq` | Provider AI |
| `GEMINI_API_KEY` | — | Se usi Gemini | |
| `GROQ_API_KEY` | — | Se usi Groq | |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | — | Solo per Ollama locale |
| `DATABASE_URL` | Auto (postgres) | **Password forte** | |
| `REDIS_URL` | Auto (redis) | Auto (redis) | |
| `SMTP_HOST` | — | Per email | Reset password |

### Sviluppo vs Produzione

| Aspetto | Sviluppo | Produzione |
|---|---|---|
| `SECRET_KEY` | Auto-generata | Obbligatoria (32+ chars) |
| CORS | Tutti gli origin | Solo il tuo dominio |
| Errori | Stack trace completo | Messaggi generici |
| HTTPS | Non richiesto | **Obbligatorio** |
| LLM | Ollama (locale, gratis) | Gemini/Groq |

---

## 🤖 Configurazione LLM

Il backend supporta 4 provider AI in ordine di priorità:

1. **Ollama** (locale, completamente gratuito) — imposta `OLLAMA_BASE_URL`
2. **Google Gemini** (piano gratuito disponibile) — imposta `GEMINI_API_KEY`
3. **Groq** (piano gratuito disponibile) — imposta `GROQ_API_KEY`
4. **OpenAI** — imposta `OPENAI_API_KEY`

```bash
# Installare Ollama (sviluppo locale)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

---

## 🚢 Deploy in Produzione

```bash
# 1. Genera SECRET_KEY
openssl rand -hex 32

# 2. Configura .env
ENVIRONMENT=production
SECRET_KEY=<chiave-generata>
LLM_PROVIDER=gemini
GEMINI_API_KEY=<tua-api-key>
DATABASE_URL=postgresql://collabook:PASSWORD_FORTE@db:5432/collabook

# 3. Avvia con config produzione
docker-compose -f docker-compose.prod.yml up -d --build
```

### Checklist Sicurezza Pre-deploy

- [ ] `ENVIRONMENT=production` in `.env`
- [ ] `SECRET_KEY` unica e >= 32 caratteri
- [ ] Password database robusta
- [ ] CORS configurato sul proprio dominio
- [ ] HTTPS/SSL abilitato
- [ ] Servizio email configurato (SendGrid o simili)
- [ ] Firewall attivo

---

## 🎮 Come si Gioca

1. **Registrati** – Crea account e scegli il nome del personaggio
2. **Scegli un mondo** – Storico, Fantasy o Fantascienza
3. **Descrivi le tue azioni** – Il DM AI risponde con la continuazione della storia
4. **Incontri casuali** – ~15-30% di probabilità di combattimento per turno
5. **Completa le quest** – Guadagna XP e oro
6. **Sali di livello** – Le statistiche aumentano automaticamente

### Combattimento
- **Attacca** – 1d20 + modificatore FOR vs CA
- **Magia** – 2d6 + modificatore MAG (costa 5 MP)
- **Difendi** – +2 CA, danno ridotto del 50%
- **Fuggi** – Prova DES per scappare

---

## 🛠️ Comandi di Gestione

```bash
# Utenti
docker-compose exec backend python manage.py list-users
docker-compose exec backend python manage.py deactivate-user

# Database
docker-compose exec backend python manage.py init-db

# Seed contenuti
docker-compose exec backend python manage.py seed-worlds
docker-compose exec backend python manage.py seed-quests
docker-compose exec backend python manage.py seed-enemies
docker-compose exec backend python manage.py seed-items
```

---

## 🧪 Test e Verifica

```bash
# Health check backend
curl http://localhost:8000/health

# Risposta attesa
# {"status": "healthy", "version": "...", "checks": {"database": "healthy", "redis": "healthy"}}
```

---

## 🐛 Risoluzione Problemi

**Il backend non si avvia (`SECRET_KEY not set`)**
```bash
openssl rand -hex 32
echo "SECRET_KEY=<chiave>" >> .env
docker-compose up --build
```

**Errori database**
```bash
# Reset completo (ATTENZIONE: cancella tutti i dati)
docker-compose down -v
docker-compose up --build
```

**Conflitti di porta**
```bash
lsof -i :8000   # Backend
lsof -i :8501   # Frontend (locale)
```

**Ollama non raggiungibile**
```bash
curl http://localhost:11434/api/tags
ollama pull llama3.2
```

---

## 🤝 Contributing

1. Fai un fork del repository
2. Crea un branch (`git checkout -b feature/NuovaFunzionalita`)
3. Commit delle modifiche (`git commit -m 'Aggiunge NuovaFunzionalita'`)
4. Push sul branch (`git push origin feature/NuovaFunzionalita`)
5. Apri una Pull Request

---

## 📝 Licenza

Questo progetto è rilasciato sotto la **GNU General Public License v3.0**.
Consulta il file [LICENSE](./LICENSE) per il testo completo e il file [NOTICE](./NOTICE) per le attribuzioni delle librerie di terze parti.

---

## 💛 Supporta il Progetto

Se trovi questo progetto utile, puoi offrire un caffè!

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Supporta%20il%20progetto-yellow)](https://buymeacoffee.com/)

---

<div align="center">

**Fatto con ⚔️ e 🎲**

</div>
