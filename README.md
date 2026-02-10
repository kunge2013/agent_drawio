# DrawIO Agent

An AI-powered web application for generating prototype designs, UI flow diagrams, and business process flows through a conversational interface. The application generates diagrams in DrawIO XML format that can be opened and edited in [DrawIO](https://www.drawio.com/).

## Features

- **Conversational Interface**: Chat with an AI to describe your product requirements
- **Prototype Design Generation**: Get detailed UI/UX prototype designs based on your requirements
- **UI Flow Diagrams**: Automatically generated user journey and navigation flow diagrams
- **Business Process Flows**: Generate business process diagrams with decision points
- **Design Documentation**: Comprehensive design documentation explaining design philosophy
- **DrawIO Export**: Export all diagrams as `.drawio` files compatible with DrawIO/diagrams.net

## Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **AI/LLM**: LangChain + OpenAI GPT
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML/CSS/JavaScript (Vanilla)

## Project Structure

```
/home/fk/workspace/github/agent_drawio/
├── app/
│   ├── main.py                      # FastAPI entry point
│   ├── config.py                    # Configuration
│   ├── api/v1/endpoints/            # API endpoints
│   ├── models/                      # SQLAlchemy models
│   ├── schemas/                     # Pydantic schemas
│   ├── services/                    # Business logic
│   ├── prompts/                     # LLM prompt templates
│   └── utils/                       # Utilities (DrawIO XML builder)
├── frontend/
│   ├── templates/index.html         # Main UI
│   └── static/                      # CSS and JS
├── migrations/schema.sql            # Database schema
├── requirements.txt
└── .env.example
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- MySQL 5.7 or higher / MariaDB 10.3 or higher
- OpenAI API key

### 1. Clone and Navigate

```bash
cd /home/fk/workspace/github/agent_drawio
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

Create the database and tables using the provided schema:

```bash
mysql -u root -p < migrations/schema.sql
```

Or manually:

```sql
CREATE DATABASE drawio_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Then run the SQL in migrations/schema.sql
```

### 5. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Database
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/drawio_agent

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

API documentation is available at `http://localhost:8000/api/docs`

## Usage

1. **Open the web interface**: Navigate to `http://localhost:8000`

2. **Describe your requirements**: In the chat box, describe what you want to build.
   - Example: "Create a task management app with user authentication, project boards, and team collaboration features"

3. **View generated content**: Switch between tabs to see:
   - **Prototype**: Detailed design with screens and components
   - **UI Flow**: Navigation flow between screens
   - **Business Flow**: Business process diagram
   - **Documentation**: Design philosophy and decisions

4. **Export diagrams**: Click "Export .drawio" to download diagrams that can be opened in DrawIO

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/` | GET | Health check |
| `/api/v1/chat/conversation` | POST | Create new conversation |
| `/api/v1/chat/conversation/{id}` | GET | Get conversation details |
| `/api/v1/chat/message` | POST | Send message and get AI response |
| `/api/v1/export/drawio/{id}` | GET | Export diagram as .drawio file |

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `OPENAI_TEMPERATURE` | LLM temperature (0-1) | `0.7` |
| `DEBUG` | Enable debug mode | `false` |

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black app/
isort app/
```

## Troubleshooting

**Database Connection Error**
- Verify MySQL is running
- Check DATABASE_URL in `.env`
- Ensure database exists: `mysql -u root -p -e "SHOW DATABASES LIKE 'drawio_agent';"`

**OpenAI API Error**
- Verify OPENAI_API_KEY is set correctly
- Check API key has credits available
- Try a different model (e.g., `gpt-4o-mini` instead of `gpt-4`)

**Port Already in Use**
- Change port: `uvicorn app.main:app --port 8001`

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
