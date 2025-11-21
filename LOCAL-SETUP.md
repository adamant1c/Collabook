# Local Development with Ollama (100% FREE)

Run Collabook entirely on your PC with a local LLM - **no cloud, no costs!**

---

## Quick Start (15 minutes)

### Step 1: Install Ollama (5 min)

**Download Ollama:**
- Windows/Mac/Linux: https://ollama.com/download

**Install and start Ollama:**

```bash
# The installer will start Ollama automatically
# Verify it's running:
ollama --version
```

### Step 2: Download a Model (5 min)

**Recommended: Llama 3.2 (2GB)**

```bash
ollama pull llama3.2
```

**Alternative models:**
- `llama3.2:1b` - Smallest, fastest (1.3GB)
- `llama3.1:8b` - Better quality (4.7GB) 
- `mistral` - Good balance (4.1GB)
- `qwen2.5:7b` - Excellent for creative writing (4.7GB)

Wait for download to complete (~2-5 minutes depending on model)

### Step 3: Run Collabook (5 min)

**Navigate to project:**

```bash
cd /home/alessandro/Project/Collabook
```

**Create `.env` file for local setup:**

```bash
# No API keys needed!
nano .env
```

Paste this:

```bash
# Ollama (local LLM - completely free!)
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2

# Database (local)
DATABASE_URL=postgresql://collabook:collabook_pass@db:5432/collabook_db
REDIS_URL=redis://redis:6379/0

# Leave these empty (not needed for local)
GEMINI_API_KEY=
OPENAI_API_KEY=
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

**Start Collabook:**

```bash
docker-compose up
```

**Access the app:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000/docs

✅ **Done!** You're running 100% locally with no costs!

---

## How It Works

```
Your Browser → Streamlit (localhost:8501)
                    ↓
              FastAPI (localhost:8000)
                    ↓
              Ollama (localhost:11434)
                    ↓
              Local LLM Model (on your PC)
```

Everything runs on your computer. No internet needed (after initial download).

---

## System Requirements

### Minimum (for llama3.2:1b)
- **RAM**: 4GB
- **Storage**: 5GB free
- **CPU**: Any modern processor

### Recommended (for llama3.2 or llama3.1:8b)
- **RAM**: 8GB+
- **Storage**: 10GB free
- **CPU**: Multi-core processor
- **GPU**: Optional (makes it faster)

### With GPU Acceleration (Fast!)
- **NVIDIA GPU**: CUDA support (automatic in Ollama)
- **Apple Silicon**: Metal support (automatic)
- **AMD GPU**: ROCm support (Linux only)

---

## Model Comparison

| Model | Size | RAM Needed | Quality | Speed | Best For |
|-------|------|------------|---------|-------|----------|
| llama3.2:1b | 1.3GB | 2GB | ⭐⭐ | ⚡⚡⚡ | Testing |
| **llama3.2** | 2.0GB | 4GB | ⭐⭐⭐ | ⚡⚡⚡ | **Recommended** |
| llama3.1:8b | 4.7GB | 8GB | ⭐⭐⭐⭐ | ⚡⚡ | Better stories |
| qwen2.5:7b | 4.7GB | 8GB | ⭐⭐⭐⭐⭐ | ⚡⚡ | Best writing |

**Switch models anytime:**
```bash
# Pull a new model
ollama pull qwen2.5:7b

# Update .env
OLLAMA_MODEL=qwen2.5:7b

# Restart
docker-compose restart backend
```

---

## Troubleshooting

### Problem: "Ollama not accessible"

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

Should return a JSON response.

**If not running:**
- Windows/Mac: Start Ollama from Applications
- Linux: `systemctl start ollama` or `ollama serve`

### Problem: Slow responses

**Normal!** Local LLMs are slower than cloud APIs:
- GPU: 2-5 seconds
- CPU only: 10-30 seconds

**Speed it up:**
- Use smaller model (`llama3.2:1b`)
- Close other applications
- Get a GPU if possible

### Problem: Out of memory

**Use smaller model:**
```bash
ollama pull llama3.2:1b
```

Update `.env`:
```bash
OLLAMA_MODEL=llama3.2:1b
```

### Problem: Docker can't reach Ollama

**Linux only:** Change URL in `.env`:
```bash
OLLAMA_BASE_URL=http://172.17.0.1:11434
```

Or use host network mode in docker-compose.

---

## Comparing Options

| Option | Cost | Setup | Quality | Speed | Privacy |
|--------|------|-------|---------|-------|---------|
| **Ollama (Local)** | **FREE** | Easy | Good | Slow | 100% |
| Google Gemini | FREE | Easiest | Excellent | Fast | Cloud |
| Hetzner + Gemini | €4/mo | Medium | Excellent | Fast | Cloud |
| OpenAI | $$$$ | Easy | Excellent | Fast | Cloud |

**Ollama is perfect for:**
- ✅ Testing and development
- ✅ Privacy-sensitive projects
- ✅ Learning and experimentation
- ✅ Offline usage
- ✅ Zero ongoing costs

**Use cloud LLM for:**
- Better quality (Gemini/GPT)
- Faster responses
- Public deployment
- 24/7 availability

---

## Switching Between Local and Cloud

**Local development:**
```bash
# .env
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2
```

**Production (cloud):**
```bash
# .env
OLLAMA_BASE_URL=  # Empty = skip Ollama
GEMINI_API_KEY=your_key_here
```

The LLM client **automatically chooses** the first available provider:
1. Ollama (if OLLAMA_BASE_URL is set and accessible)
2. Gemini (if GEMINI_API_KEY is set)
3. OpenAI (if OPENAI_API_KEY is set)

---

## Managing Ollama

### List downloaded models
```bash
ollama list
```

### Delete a model
```bash
ollama rm llama3.2
```

### Update Ollama
```bash
# Download latest from https://ollama.com/download
# Or on Mac with Homebrew:
brew upgrade ollama
```

### Run model manually (test)
```bash
ollama run llama3.2
```

Type messages and press Enter. Type `/bye` to exit.

---

## Advanced: GPU Acceleration

### NVIDIA GPU (Linux/Windows)

**Ollama automatically uses CUDA** if you have:
- NVIDIA GPU
- Latest drivers installed

Verify:
```bash
nvidia-smi
```

### Apple Silicon (M1/M2/M3)

**Ollama automatically uses Metal** on Apple Silicon Macs.

Much faster than CPU!

### Check GPU usage

While Ollama is generating, check:
- Windows: Task Manager → Performance → GPU
- Linux: `nvidia-smi`
- Mac: Activity Monitor → GPU

---

## Performance Tips

1. **Use GPU** if available (10x faster)
2. **Close other apps** while running
3. **Use smaller models** for faster response
4. **Increase `num_predict`** in llm_client.py for longer responses
5. **Enable prompt caching** (Ollama does this automatically)

---

## Development Workflow

**Best practice:**

1. **Develop locally** with Ollama (free, private)
2. **Test with Gemini API** (free tier)
3. **Deploy to production** with Gemini or paid LLM

**Commands:**

```bash
# Local development
docker-compose up

# Stop
docker-compose down

# Rebuild after changes
docker-compose up --build

# View logs
docker-compose logs -f backend
```

---

## Cost Comparison

### Local Setup (Ollama)
- **One-time**: Download models (free)
- **Ongoing**: Electricity (~€0.50/month)
- **Total**: ~€0.50/month

### Cloud Setup (Gemini)
- **One-time**: Get API key (free)
- **Ongoing**: €0/month (free tier)
- **Total**: €0/month

### Hybrid (Best of Both)
- **Development**: Ollama (local)
- **Production**: Gemini (free cloud)
- **Total**: €0/month

---

## Next Steps

1. ✅ Install Ollama
2. ✅ Download a model
3. ✅ Run `docker-compose up`
4. ✅ Create a test story!
5. Try different models to see quality differences
6. When ready, deploy to cloud with Gemini

**Enjoy your free, private, local AI storytelling platform!** 🎉
