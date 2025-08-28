# AdvisorConnect GenAI v2 - Hackathon POC

A comprehensive AI-powered advisor matching system that dynamically profiles advisors and intelligently matches them to cases based on expertise, performance, and domain knowledge.

## 🚀 Features

- **AI-Powered Advisor Profiling**: Dynamic advisor profiles with tags, performance metrics, and learning curves
- **Intelligent Case Matching**: AI-driven matching with percentage scores and detailed insights
- **Case Management Workflow**: Accept/decline functionality with reason tracking
- **Real-time Dashboards**: Advisor and admin dashboards with performance analytics
- **Semantic Search**: OpenAI-powered embeddings for intelligent case classification

## 🏗️ Architecture

```
advisor-matching/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # AI services & business logic
│   │   ├── api/           # API endpoints
│   │   └── utils/         # Utilities
│   ├── requirements.txt
│   └── main.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── utils/        # Utilities
│   ├── package.json
│   └── tailwind.config.js
└── data/                  # Sample data & migrations
```

## 🚀 Quick Start (One Command)

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (optional)

### One-Line Setup & Run
```bash
# Clone and run in one command
git clone <repository-url> && cd advisor-matching && ./start.sh

# Or if already cloned, just run:
./start.sh
```

### Manual Setup (Alternative)
```bash
# Set OpenAI API key (optional)
export OPENAI_API_KEY="your-openai-api-key"

# Backend setup
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python seed_data.py && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# Frontend setup (in another terminal)
cd frontend && npm install && npm start
```

### What the startup script does:
1. ✅ Creates Python virtual environment
2. ✅ Installs all dependencies (Python & Node.js)
3. ✅ Seeds the database with sample data
4. ✅ Starts backend server on port 8000
5. ✅ Starts frontend server on port 3000
6. ✅ Opens the application in your browser

## 🎯 Key Features Demonstrated

### Advisor Dashboard
- View incoming cases with AI matching scores
- Accept/decline cases with reason tracking
- Performance metrics and learning curve visualization
- Historical case management

### AI Matching Engine
- Dynamic advisor profiling based on case history
- Semantic similarity scoring using OpenAI embeddings
- Detailed matching insights and reasoning
- Automatic profile updates after case resolution

### Admin Interface
- Comprehensive case management across all advisors
- Advisor performance analytics and profiles
- Learning curve visualization
- System-wide metrics and insights

## 🔧 API Endpoints

### Cases
- `POST /submit_case` - Submit new case
- `GET /cases` - List all cases (filterable)
- `GET /case/{id}` - Get case details
- `POST /case/{id}/accept` - Accept case
- `POST /case/{id}/decline` - Decline case

### Advisors
- `GET /advisors` - List all advisors
- `GET /advisor/{id}` - Get advisor profile
- `GET /dashboard/advisor/{id}` - Get advisor dashboard data

## 📊 Sample Data

The application includes sample data for:
- 10 advisors across different departments and countries
- 50+ historical cases with various topics and complexity levels
- Transfer patterns and performance metrics
- Department and business function mappings

## 🎨 UI/UX Features

- **Material-UI Components**: Modern, accessible UI components
- **Tailwind CSS**: Utility-first styling for rapid development
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live notifications and status updates
- **Interactive Charts**: Performance visualization with Recharts

## 🔮 Future Enhancements

- Real-time notifications using WebSockets
- Advanced ML models for better matching
- Integration with external case management systems
- Mobile app development
- Advanced analytics and reporting

## 📝 License

This is a hackathon POC for demonstration purposes.
