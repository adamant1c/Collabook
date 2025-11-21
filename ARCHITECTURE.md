# Collabook - Architecture Documentation

## Overview

Collabook is a collaborative story generation platform that allows multiple users to participate in interactive, AI-generated narratives. The system uses AI agents to generate coherent, engaging stories while maintaining world consistency.

## System Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Streamlit)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   Backend       │
│   (FastAPI)     │
└────┬───┬───┬────┘
     │   │   │
     │   │   └────────┐
     │   │            │
     ▼   ▼            ▼
┌────────┐  ┌─────────────┐
│ Redis  │  │ PostgreSQL  │
│ Cache  │  │ Database    │
└────────┘  └─────────────┘
```

## Components

### 1. Frontend (Streamlit)

**Purpose**: User interface for character creation, story selection, and gameplay.

**Key Features**:
- Session-based state management
- Real-time story interaction
- Character profile creation
- Story browsing and creation

**Files**:
- `frontend/app.py`: Main application with multi-page flow
- `frontend/api_client.py`: Backend communication layer

### 2. Backend (FastAPI)

**Purpose**: REST API server handling all business logic and database operations.

**Key Components**:

#### API Layer (`app/api/`)
- `users.py`: User profile management
- `stories.py`: Story creation and joining
- `interactions.py`: Turn-based gameplay interactions

#### Database Layer (`app/models/`)
- `db_models.py`: SQLAlchemy ORM models
  - User: Character profiles
  - Story: Story worlds and metadata
  - Character: User participation in stories
  - Turn: Interaction history
- `schemas.py`: Pydantic validation schemas for API requests/responses

#### Core Services (`app/core/`)
- `database.py`: PostgreSQL connection and session management
- `redis_client.py`: Redis caching for frequent lookups
- `llm_client.py`: LangChain integration with OpenAI

#### AI Agents (`app/agents/`)
Three specialized agents power the narrative engine:

1. **Narrator Agent** (`narrator.py`)
   - Generates story narration based on user actions
   - Maintains narrative voice and tone
   - Uses conversation history for context

2. **Matchmaker Agent** (`matchmaker.py`)
   - Analyzes character profiles and story states
   - Determines optimal insertion points for new characters
   - Ensures logical character placement

3. **World Keeper Agent** (`world_keeper.py`)
   - Validates user actions against world rules
   - Updates story state summaries
   - Maintains internal consistency

### 3. Database (PostgreSQL)

**Schema**:

```
users
├── id (PK)
├── name
├── profession
├── description
└── avatar_description

stories
├── id (PK)
├── title
├── world_description
├── genre
├── current_state
└── metadata (JSON)

characters
├── id (PK)
├── user_id (FK → users)
├── story_id (FK → stories)
├── insertion_point
└── status

turns
├── id (PK)
├── story_id (FK → stories)
├── character_id (FK → characters)
├── user_action
├── narration
└── turn_number
```

### 4. Cache (Redis)

**Cached Data**:
- Story context (world, state, metadata)
- User sessions
- Active character lists per story

**TTL**:
- Story context: 1 hour
- User sessions: 2 hours

## Data Flow

### Character Creation
1. User fills character form in frontend
2. Frontend sends POST to `/users/`
3. Backend creates User record in PostgreSQL
4. User ID stored in session state

### Story Creation
1. User defines world in frontend
2. Frontend sends POST to `/stories/`
3. Backend creates Story record
4. Story context cached in Redis
5. User automatically joins as first character

### Join Existing Story
1. User selects story from list
2. Frontend sends POST to `/stories/{id}/join`
3. Backend retrieves story context from Redis/DB
4. Matchmaker Agent determines insertion point
5. Character record created with insertion narrative

### Game Interaction
1. User enters action in frontend
2. Frontend sends POST to `/interact/`
3. Backend flow:
   - Retrieve story context (Redis → DB fallback)
   - World Keeper validates action
   - Retrieve conversation history (last 5 turns)
   - Narrator generates narration
   - World Keeper updates story state
   - Turn record created
   - Cache updated
4. Frontend displays narration

## Agent Architecture

### Narrator Agent

**Input**:
- Story context (world, genre, current state)
- Character info (name, profession, description)
- User action
- Conversation history

**Output**:
- 2-4 paragraphs of narrative text

**Prompt Strategy**:
- System: World rules, character context, narrative guidelines
- History: Previous turn actions and narrations
- User: Current action

### Matchmaker Agent

**Input**:
- Story context
- New character profile

**Output**:
- 2-3 sentence insertion point narrative

**Prompt Strategy**:
- Analyzes character traits vs. story needs
- Considers current plot state
- Suggests natural entry point

### World Keeper Agent

**Function 1: Validate Action**

**Input**: Story context, proposed action  
**Output**: `{valid: bool, reason: str}`

**Function 2: Update State**

**Input**: Current state, new events  
**Output**: Updated 2-3 sentence state summary

## Scalability Considerations

### Horizontal Scaling
- **Frontend**: Stateless, can be replicated
- **Backend**: Async FastAPI, multiple workers via Uvicorn
- **Database**: PostgreSQL read replicas
- **Redis**: Redis Cluster for distributed caching

### Load Balancing
- Nginx reverse proxy distributes requests
- Session affinity not required (stateless API)

### Containerization
- Docker Compose for development
- Docker Swarm or Kubernetes for production

### Performance Optimizations
1. **Redis Caching**: Reduces DB queries for hot stories
2. **Connection Pooling**: SQLAlchemy pool for DB connections
3. **Async I/O**: FastAPI async endpoints for concurrent requests
4. **LLM Response Caching**: Consider caching common narrative patterns

## Security Considerations

### Current Implementation
- Anonymous users (no authentication)
- CORS enabled for frontend access
- No GDPR requirements (anonymous)

### Production Recommendations
1. Rate limiting on API endpoints
2. Input validation and sanitization
3. Environment variable management
4. HTTPS/TLS encryption
5. Database connection encryption
6. Redis password authentication

## Deployment

### Development
```bash
docker-compose up --build
```

### Production (Docker Swarm)
```bash
docker swarm init
docker stack deploy -c docker-compose.yml collabook
```

### Environment Variables
- `OPENAI_API_KEY`: Required for LLM
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `BACKEND_URL`: Frontend → Backend communication

## Monitoring & Logging

### Recommended Tools
- **Application Logs**: FastAPI logging to stdout
- **Database Monitoring**: pg_stat_statements
- **Redis Monitoring**: redis-cli INFO
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry for request tracing

## Future Enhancements

1. **Multi-player Real-time**: WebSocket for live collaboration
2. **Advanced World Building**: Templates and wizards
3. **Story Forking**: Branching narratives
4. **Character Persistence**: Save/load characters
5. **LLM Provider Flexibility**: Support multiple providers
6. **Observability**: Detailed agent decision logging
7. **Content Moderation**: Filter inappropriate content
8. **Story Export**: PDF/ebook generation
