# Business Flow Designer

An AI-powered web application for generating business process flow diagrams through a conversational interface. The application generates diagrams in DrawIO XML format that can be opened and edited in [DrawIO](https://www.drawio.com/).

## Features

- **Conversational Interface**: Chat with an AI to describe your business process
- **Business Process Flows**: Generate business process diagrams with decision points
- **Interactive Diagram Viewer**: View generated flows using the mxGraph (DrawIO) framework
- **DrawIO Export**: Export all diagrams as `.drawio` files compatible with DrawIO/diagrams.net

## Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **AI/LLM**: LangChain + OpenAI Compatible APIs
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML/CSS/JavaScript (Vanilla) with mxGraph

## Project Structure

```
agent_drawio/
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
│       ├── js/drawio-viewer.js      # DrawIO/mxGraph viewer
│       ├── js/chat.js               # Chat interface
│       ├── js/app.js                # Main app logic
│       └── css/styles.css           # Styles
├── migrations/schema.sql            # Database schema
├── requirements.txt
└── .env.example
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- MySQL 5.7 or higher / MariaDB 10.3 or higher
- OpenAI Compatible API key (supports OpenAI, Qwen, etc.)

### 1. Clone and Navigate

```bash
cd agent_drawio
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

# OpenAI Compatible API
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

For Alibaba Cloud Qwen:
```bash
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus
```

### 6. Run the Application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

API documentation is available at `http://localhost:8000/api/docs`

## Usage

1. **Open the web interface**: Navigate to `http://localhost:8000`

2. **Describe your business process**: In the chat box, describe your business process.
   - Example: "Create an order processing flow with payment verification, inventory check, and shipping confirmation"

3. **View generated diagram**: The business process flow diagram will be displayed in the panel on the right using the interactive DrawIO viewer.

4. **Export diagrams**: Click "Export .drawio" to download the diagram that can be opened in DrawIO.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint - serves the main UI |
| `/health` | GET | Health check endpoint |
| `/api/v1/chat/conversation` | POST | Create new conversation |
| `/api/v1/chat/conversation/{id}` | GET | Get conversation details |
| `/api/v1/chat/message` | POST | Send message and get AI response with diagram |
| `/api/v1/export/drawio/{id}` | GET | Export diagram as .drawio file |

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_API_BASE` | OpenAI API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | OpenAI model to use | `qwen-plus` |
| `OPENAI_TEMPERATURE` | LLM temperature (0-1) | `0.7` |
| `DEBUG` | Enable debug mode | `false` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

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

**API Error**
- Verify OPENAI_API_KEY is set correctly
- Check API key has credits available
- Try a different model (e.g., `gpt-4o-mini` instead of `gpt-4`)

**Port Already in Use**
- Change port in `.env`: `PORT=8001`

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
