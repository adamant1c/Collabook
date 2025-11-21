# Collabook

A collaborative story generation platform where users can create and join interactive stories powered by AI.

## Features

- 🎭 **Anonymous Character Creation**: Create characters with unique personalities and backgrounds
- 📚 **Story Management**: Create new story worlds or join existing ones
- 🤖 **AI-Powered Narration**: LLM agents generate dynamic narratives based on user actions
- 🌍 **World Consistency**: AI agents maintain story coherence and validate actions
- 🎮 **Interactive Gameplay**: Game-book style experience with branching narratives

## Architecture

### Tech Stack
- **Frontend**: Streamlit (Python)
- **Backend**: FastAPI (Async Python)
- **Database**: PostgreSQL
- **Cache**: Redis
- **LLM**: OpenAI GPT-4 (via LangChain)
- **Containerization**: Docker & Docker Compose

### AI Agents

The system uses three specialized agents:

1. **Narrator Agent**: Generates engaging story narration based on user actions
2. **Matchmaker Agent**: Intelligently places new characters into existing stories
3. **World Keeper Agent**: Validates actions and maintains world consistency

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Collabook
```

2. Create a `.env` file:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

3. Start the services:
```bash
docker-compose up --build
```

4. Access the application:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

1. **Create a Character**: Enter your character's name, profession, and description
2. **Choose Your Path**:
   - Create a new story world with custom settings
   - Join an existing story and be automatically placed by the AI
3. **Play**: Interact with the story by describing your actions and watch the narrative unfold

## API Endpoints

### Users
- `POST /users/` - Create user profile
- `GET /users/{user_id}` - Get user details

### Stories
- `POST /stories/` - Create new story
- `GET /stories/` - List all stories
- `GET /stories/{story_id}` - Get story details
- `POST /stories/{story_id}/join` - Join a story

### Interactions
- `POST /interact/` - Send action and receive narration

## Development

### Project Structure

```
Collabook/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent implementations
│   │   ├── api/             # API routes
│   │   ├── core/            # Database, Redis, LLM clients
│   │   ├── models/          # Data models and schemas
│   │   └── main.py          # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py               # Streamlit application
│   ├── api_client.py        # Backend API client
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend testing
cd frontend
streamlit run app.py
```

## Scaling

The architecture is designed for scalability:

- **Horizontal Scaling**: Use Docker Swarm or Kubernetes
- **Load Balancing**: Nginx for distributing traffic
- **Caching**: Redis reduces database load
- **Async API**: FastAPI handles concurrent requests efficiently

### Production Deployment

1. Update `docker-compose.yml` for production settings
2. Configure Nginx as reverse proxy
3. Set up proper CORS origins
4. Use environment-specific configurations
5. Deploy with Docker Swarm:

```bash
docker swarm init
docker stack deploy -c docker-compose.yml collabook
```

## License

GPL-3.0 (see LICENSE file)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Future Enhancements

- [ ] Multi-player real-time collaboration
- [ ] Character image generation
- [ ] Story export/sharing
- [ ] Advanced world building tools
- [ ] Voice narration
- [ ] Mobile app

## Support

For issues or questions, please open a GitHub issue.
