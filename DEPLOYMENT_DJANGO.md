# 🚀 Guida al Test e Deploy (Frontend Django)

Questa guida spiega come testare il nuovo frontend Django in locale e come distribuirlo sul server di produzione.

---

## 💻 1. Test in Locale (Senza Docker)

Segui questi passaggi per testare il frontend sulla tua macchina locale.

### Preparazione
1. **Installa le dipendenze**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configura il database locale (SQLite)**:
   ```bash
   python manage.py migrate
   ```

### Esecuzione
1. **Avvia il server**:
   ```bash
   python manage.py runserver
   ```
2. **Accedi**:
   Apri [http://127.0.0.1:8000](http://127.0.0.1:8000) nel browser.

> [!NOTE]
> Assicurati che il **backend** sia attivo (in locale o tramite Docker) affinché le funzionalità di gioco siano operative.

---

## ☁️ 2. Deploy in Produzione (VM Remota)

Segui questi passaggi dopo aver caricato le modifiche su GitHub/GitLab.

### Aggiornamento Codice
1. **Accedi alla VM**:
   ```bash
   ssh utente@ip-della-tua-vm
   ```
2. **Scarica le modifiche**:
   ```bash
   cd /path/to/Collabook
   git pull origin main
   ```

### Aggiornamento Container
1. **Riavvia con build**:
   ```bash
   # Ferma i vecchi container
   docker compose down
   
   # Ricostruisci e avvia
   docker compose up --build -d
   ```

### Verifica
1. **Controlla lo stato**:
   ```bash
   docker compose ps
   ```
2. **Controlla i log (se necessario)**:
   ```bash
   docker compose logs frontend
   ```

**Accesso**: L'app sarà disponibile sulla porta **3000** (es. `http://tuo-ip:3000`).
