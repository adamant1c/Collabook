# Guida Setup HTTPS per Collabook 🔐

Questa guida ti accompagna passo-passo nella configurazione di HTTPS per Collabook, iniziando con un certificato self-signed e con istruzioni per l'apertura delle porte su Oracle Cloud.

---

## Parte 1: Generazione Certificato Self-Signed

### Passo 1: Genera il Certificato

Sul server dove è installato Collabook, esegui:

```bash
cd /path/to/collabook
chmod +x generate-selfsigned-cert.sh
./generate-selfsigned-cert.sh
```

Questo creerà:
- `ssl/selfsigned.key` - Chiave privata
- `ssl/selfsigned.crt` - Certificato pubblico

Il certificato sarà valido per 365 giorni.

### Passo 2: Verifica i File

```bash
ls -la ssl/
```

Dovresti vedere:
```
-rw-r--r-- 1 user user 1350 ssl/selfsigned.crt
-rw------- 1 user user 1704 ssl/selfsigned.key
```

---

## Parte 2: Configurazione Docker

### Passo 3: Riavvia Nginx

Il file `nginx.conf` è già configurato per usare i certificati self-signed. Riavvia il container nginx:

```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

### Passo 4: Verifica che nginx sia attivo

```bash
docker-compose -f docker-compose.prod.yml ps nginx
```

Controlla i log in caso di errori:

```bash
docker-compose -f docker-compose.prod.yml logs nginx
```

---

## Parte 3: Configurazione Oracle Cloud

### Passo 5: Apri Porta 443 nel Network Security Group

1. **Accedi alla Console Oracle Cloud**
   - Vai su https://cloud.oracle.com
   - Fai login con il tuo account

2. **Naviga alla tua Istanza**
   - Menu hamburger (☰) → **Compute** → **Instances**
   - Clicca sulla tua istanza VM

3. **Trova il Virtual Cloud Network (VCN)**
   - Nella pagina dell'istanza, nella sezione **Instance Details**
   - Clicca sul link del **Subnet** (sotto "Primary VNIC")

4. **Modifica il Security List**
   - Clicca su **Security Lists** nella sidebar sinistra
   - Clicca sul Security List associato (es. "Default Security List for...")

5. **Aggiungi Regola Ingress per HTTPS**
   - Clicca su **Add Ingress Rules**
   - Compila i campi:
     - **Stateless**: No (lascia deselezionato)
     - **Source Type**: CIDR
     - **Source CIDR**: `0.0.0.0/0` (tutto internet)
     - **IP Protocol**: TCP
     - **Source Port Range**: (lascia vuoto)
     - **Destination Port Range**: `443`
     - **Description**: `HTTPS access for Collabook`
   - Clicca **Add Ingress Rules**

6. **Verifica le regole**
   - Dovresti vedere ora sia la porta 80 che la 443 nelle regole ingress

### Passo 6: Configura il Firewall Linux

Sulla VM Oracle (accedi via SSH), esegui:

#### Per Oracle Linux con firewalld:

```bash
# Verifica stato firewall
sudo firewall-cmd --state

# Apri porta 443
sudo firewall-cmd --permanent --add-port=443/tcp

# Ricarica configurazione
sudo firewall-cmd --reload

# Verifica
sudo firewall-cmd --list-ports
```

#### Per Ubuntu con ufw:

```bash
# Verifica stato
sudo ufw status

# Apri porta 443
sudo ufw allow 443/tcp

# Verifica
sudo ufw status numbered
```

#### Per sistemi con iptables:

```bash
# Aggiungi regola
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT

# Salva regole (Oracle Linux)
sudo service iptables save

# O per Ubuntu
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

---

## Parte 4: Test e Verifica

### Passo 7: Test Locale (sulla VM)

```bash
# Test HTTPS locale
curl -k https://localhost

# Test HTTP (dovrebbe ancora funzionare)
curl http://localhost
```

Se ricevi una risposta HTML (la pagina Streamlit), tutto funziona!

### Passo 8: Test Esterno

Dal tuo computer locale (non dalla VM):

```bash
# Sostituisci <IP-PUBBLICO> con l'IP pubblico della tua VM Oracle
curl -k https://<IP-PUBBLICO>

# Esempio:
curl -k https://132.145.123.45
```

### Passo 9: Test dal Browser

1. Apri il browser
2. Vai su `https://<IP-PUBBLICO>` (es. `https://132.145.123.45`)
3. **IMPORTANTE**: Il browser mostrerà un avviso di sicurezza perché il certificato è self-signed
4. Clicca su:
   - Chrome: "Advanced" → "Proceed to ... (unsafe)"
   - Firefox: "Advanced" → "Accept the Risk and Continue"
   - Safari: "Show Details" → "visit this website"
5. Dovresti vedere la pagina di login di Collabook! 🎉

---

## Parte 5: Troubleshooting

### Problema: Porta 443 non raggiungibile dall'esterno

**Verifica 1: Network Security Group**
```bash
# Dalla Oracle Cloud Console, verifica che la regola ingress per porta 443 sia presente
```

**Verifica 2: Firewall Linux**
```bash
# Oracle Linux
sudo firewall-cmd --list-all

# Ubuntu
sudo ufw status verbose

# Iptables
sudo iptables -L -n | grep 443
```

**Verifica 3: Nginx in ascolto**
```bash
docker exec <nginx-container-id> netstat -tlnp | grep 443
# Oppure
sudo netstat -tlnp | grep :443
```

### Problema: Certificato non trovato da nginx

**Verifica percorsi volume Docker**
```bash
# Controlla che la directory ssl/ esista
ls -la ssl/

# Verifica il mount nel container
docker exec <nginx-container-id> ls -la /etc/nginx/ssl/
```

### Problema: Browser non accetta il certificato

È normale! I certificati self-signed non sono riconosciuti dai browser. Devi manualmente accettare l'eccezione di sicurezza.

**Soluzione permanente**: Usa Let's Encrypt (vedi sezione successiva)

---

## Parte 6: Upgrade a Let's Encrypt (Opzionale)

Una volta che hai un dominio configurato (es. `collabook.example.com`), puoi ottenere un certificato valido gratuitamente:

### Prerequisiti
- Dominio registrato e puntato all'IP pubblico della VM
- DNS configurato correttamente

### Passaggi

1. **Ferma temporaneamente nginx** (per permettere a certbot di usare la porta 80):
   ```bash
   docker-compose -f docker-compose.prod.yml stop nginx
   ```

2. **Ottieni il certificato**:
   ```bash
   docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
     --standalone \
     -d tuodominio.com \
     -d www.tuodominio.com \
     --email tua@email.com \
     --agree-tos \
     --no-eff-email
   ```

3. **Modifica nginx.conf**:
   - Sostituisci `DOMAIN` con il tuo dominio nelle linee commentate per Let's Encrypt
   - Commenta le linee dei certificati self-signed
   - Decommenta le linee Let's Encrypt

4. **Riavvia nginx**:
   ```bash
   docker-compose -f docker-compose.prod.yml start nginx
   ```

5. **Opzionale: Abilita redirect HTTP → HTTPS**:
   - In `nginx.conf`, decommenta la linea:
     ```nginx
     return 301 https://$host$request_uri;
     ```
   - Riavvia nginx

---

## Riepilogo Comandi Rapidi

Per setup completo su Oracle Cloud:

```bash
# 1. Genera certificato
./generate-selfsigned-cert.sh

# 2. Riavvia nginx
docker-compose -f docker-compose.prod.yml restart nginx

# 3. Apri porta nel firewall Linux (Oracle Linux)
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# 4. Test
curl -k https://localhost
curl -k https://<IP-PUBBLICO>
```

**Non dimenticare**: Configura anche il Network Security Group dalla console Oracle Cloud!

---

## Note di Sicurezza ⚠️

1. **Certificati Self-Signed**: Ok per testing/sviluppo, ma per produzione usa Let's Encrypt
2. **Password forti**: Assicurati che le password in `.env` siano robuste
3. **Firewall**: Limita l'accesso SSH (porta 22) solo al tuo IP se possibile
4. **Aggiornamenti**: Mantieni il sistema aggiornato con `sudo apt update && sudo apt upgrade`

---

**Domande?** Apri un issue o consulta la documentazione Oracle Cloud per i dettagli specifici della tua configurazione.

🎲 Buon gaming sicuro! ⚔️
