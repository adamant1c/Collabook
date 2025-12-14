# Guida Billing e Upgrade AI 🧠

Questa guida spiega come gestire i costi e i limiti dell'Intelligenza Artificiale in Collabook.

---

## 1. Configurazione Attuale (Ibrida)

Il sistema è ora configurato per usare una strategia "Smart Fallback":

1.  **Primario**: Google Gemini Flash (Free Tier)
2.  **Fallback**: Groq (Free Tier)

Se Gemini raggiunge il limite di quota (Errore 429), il sistema passa automaticamente a Groq senza interrompere l'utente.

---

## 2. Come passare a Gemini a Pagamento (Pay-as-you-go)

Se decidi di passare al piano a pagamento di Google per rimuovere i limiti:

### Passo 1: Abilita il Billing su Google Cloud
1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Seleziona il progetto associato alla tua API Key attuale
3. Vai su "Billing" (Fatturazione) e collega una carta di credito

### Passo 2: Verifica API Key
**Non devi cambiare nulla nel codice o nel file .env!**
La tua `GEMINI_API_KEY` attuale funzionerà automaticamente come "Paid Tier" una volta abilitata la fatturazione sul progetto Google Cloud.

### Costi Stimati (Gemini 1.5 Flash)
- **Input**: $0.075 per 1 milione di token (~1.500.000 parole)
- **Output**: $0.30 per 1 milione di token
- **Esempio**: 100 utenti attivi che fanno 50 azioni al giorno costerebbero circa **$0.50 - $1.00 al mese**.

---

## 3. Come attivare Groq (Gratis)

Per usare Groq come fallback (o primario), devi ottenere una chiave gratuita:

1. Vai su [Groq Console](https://console.groq.com/keys)
2. Fai login (es. con GitHub o Google)
3. Clicca "Create API Key"
4. Copia la chiave (inizia con `gsk_...`)

### Configurazione Server
Aggiungi la chiave al file `.env` sul server:

```bash
# Apri il file .env
nano .env

# Aggiungi questa riga alla fine
GROQ_API_KEY=gsk_tuachiavequi...

# Salva e esci (Ctrl+O, Enter, Ctrl+X)
```

### Riavvia il Backend
```bash
docker-compose restart backend
```

---

## 4. Strategia Consigliata per Beta Test

1.  **Mantieni Gemini Free** come primario finché regge.
2.  **Configura Groq** come rete di sicurezza (fallback).
3.  **Monitora i log**: Se vedi che il sistema usa spesso Groq (cerca "Falling back to Groq" nei log), valuta se passare al piano a pagamento di Gemini o promuovere Groq a provider primario.

Per rendere Groq il provider **primario** (invece che fallback), basta rimuovere `GEMINI_API_KEY` dal file `.env` e lasciare solo `GROQ_API_KEY`.
