# AdvisorConnect he r v2 - AI-Powered Advisor Matching System

A comprehensive AI-powered advisor matching system that dynamically profiles advisors and intelligently matches them to cases using advanced machine learning models. The system learns from historical transaction data to create accurate advisor profiles and provides intelligent recommendations with detailed reasoning.

## 🚀 Features

### 🤖 **Advanced ML-Powered Matching**
- **Comprehensive ML Model**: RandomForest and GradientBoosting algorithms for intelligent advisor matching
- **Feature Engineering**: Topics, Sub-topics, Business Function, Department, Country, Category, Complexity analysis
- **Priority-Based Matching**: Topic → Subtopic → Business Function → Department → Country hierarchy
- **Detailed Reasoning**: Explains why each advisor matches with specific insights
- **Model Performance Dashboard**: Real-time metrics, feature importance, and accuracy tracking

### 📊 **Dynamic Advisor Profiling**
- **AI-Generated Profiles**: Created from historical transaction data
- **Expertise Tags**: Automatically generated from case topics and subtopics
- **Performance Metrics**: Success rate, resolution time, complexity preference
- **Learning Curves**: Track advisor development over time
- **Profile Updates**: Continuous learning from new case data

### 🎯 **Intelligent Case Management**
- **AI Recommendations**: Top 3 advisor matches with confidence scores
- **Accept/Decline Workflow**: With reason tracking and status updates
- **Case Assignment**: Automatic assignment based on ML recommendations
- **Status Tracking**: Real-time case status updates
- **Clickable Cases**: Navigate from lists to detailed case views

### 📈 **Real-time Dashboards**
- **Advisor Dashboard**: Incoming cases, performance metrics, resolved cases
- **Admin Dashboard**: System-wide case management and analytics
- **Model Performance**: ML model accuracy, feature importance, retraining capabilities
- **Interactive Charts**: Performance visualization with Recharts

### 📁 **Excel Data Integration**
- **Dynamic Data Processing**: Upload Excel files with transaction data
- **Automatic Profile Generation**: Creates advisor profiles from real data
- **ML Model Training**: Trains models on your actual transaction data
- **Retraining Capability**: Update models with new data
- **Multiple Sheet Support**: Handles complex Excel files with multiple sheets

### 🧠 **AI Gateway Integration**
- **Local AI Gateway Support**: Connect to your local AI gateway with multiple models
- **Model Options**: gpt4o, claude-3-5-sonnet, llama-3-3-70b, text3large, bgelarge
- **Automatic Fallback**: Offline processing when gateway unavailable
- **Enhanced AI Features**: Case classification, profile summaries, matching insights
- **Privacy-First**: All processing happens on your local network

## 🏗️ Architecture

```
advisor-matching/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # ML services & business logic
│   │   │   ├── ml_model_offline.py    # Offline ML model
│   │   │   ├── ai_service_gateway.py  # AI gateway service
│   │   │   ├── ml_service.py          # ML service integration
│   │   │   ├── matching_service.py    # Advisor matching logic
│   │   │   └── excel_processor.py     # Excel data processing
│   │   ├── api/           # API endpoints
│   │   └── schemas/       # Pydantic schemas
│   ├── models/            # Trained ML models
│   ├── requirements.txt
│   └── main.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   │   ├── ModelPerformance.js    # ML model dashboard
│   │   │   ├── ExcelUpload.js         # Excel upload interface
│   │   │   └── IntegratedCaseSubmission.js # Case submission
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── utils/        # Utilities
│   ├── package.json
│   └── tailwind.config.js
└── start.sh               # One-command startup script
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- AI Gateway (optional - system works offline)

### Option 1: Local Development (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd advisor-matching

# Run the application
./start.sh
```

The script will:
- Install Python dependencies
- Install Node.js dependencies
- Create sample data
- Start backend server (http://localhost:8000)
- Start frontend server (http://localhost:3000)

### Option 2: Docker Deployment

```bash
# Clone the repository
git clone <repository-url>
cd advisor-matching

# Configure AI Gateway (optional)
cp docker.env.example docker.env
# Edit docker.env with your AI gateway details

# Start with Docker
./docker-start.sh
```

## ⚙️ Configuration

### AI Gateway Setup (Optional)

To enable AI gateway features, create a `.env` file in the `backend/` directory:

```bash
# AI Gateway Configuration
OPENAI_API_BASE_URL=http://your-ai-gateway-url:port/v1
OPENAI_API_KEY=your-gateway-api-key
DEFAULT_AI_MODEL=gpt4o

# Database configuration
DATABASE_URL=sqlite:///./advisor_connect.db
```

**Available Models:**
- **Text Generation**: gpt4o, claude-3-5-sonnet, llama-3-3-70b, o3mini
- **Embeddings**: text3large, bgelarge

### Excel Data Format

Your Excel file should contain these columns:
- `Case ID` - Unique case identifier
- `Services` - Service type
- `Topics` - Main topic area
- `Current Sub-Topic` - Specific subtopic
- `Current Case Owner` - Current advisor ID
- `Status` - Case status (resolved, pending, etc.)
- `Business Function` - Business function area
- `Department` - Department
- `Country` - Country
- `Category` - Case category
- `Complexity` - Case complexity (0-100)
- `Please describe your query` - Case description/query

## 🎨 UI/UX Features

### **Modern Design**
- **Material-UI Components**: Professional, accessible UI components
- **Tailwind CSS**: Utility-first styling for rapid development
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Dark Theme**: Professional dark sidebar with light content area

### **Interactive Elements**
- **Real-time Updates**: Live notifications and status updates
- **Interactive Charts**: Performance visualization with Recharts
- **Clickable Tables**: Navigate from lists to detailed views
- **Loading States**: Smooth loading indicators and progress bars

## 🔮 Advanced Features

### **ML Model Capabilities**
- **Multi-Algorithm Training**: RandomForest and GradientBoosting comparison
- **Feature Engineering**: Advanced text processing and categorical encoding
- **Cross-Validation**: Robust model evaluation
- **Model Persistence**: Save and load trained models
- **Incremental Learning**: Update models with new data

### **Performance Optimization**
- **Efficient Data Processing**: Optimized Excel parsing and data handling
- **Smart Caching**: Cached model predictions and advisor profiles
- **Background Processing**: Non-blocking ML model training
- **Memory Management**: Efficient handling of large datasets

## 🛠️ Development

### **Local Development**
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start
```

### **Testing**
```bash
# Run integration tests
cd backend
python test_integration.py

# Test AI gateway
python test_ai_gateway.py
```

### **Docker Development**
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up --build -d
```

## 🐳 Docker Deployment

### **Production Deployment**
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up --build -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f
```

### **Environment Configuration**
```bash
# Copy environment template
cp docker.env.example docker.env

# Edit with your settings
nano docker.env
```

## 📊 API Endpoints

### **Core Endpoints**
- `GET /` - Health check
- `GET /docs` - API documentation
- `GET /cases/` - List all cases
- `GET /advisors/` - List all advisors
- `POST /api/v1/recommend-advisors` - Get advisor recommendations
- `GET /api/v1/advisor-inbox/{advisor_id}` - Get advisor inbox
- `GET /api/v1/model-performance` - Get ML model metrics

### **Admin Endpoints**
- `GET /admin/cases` - Admin case management
- `GET /admin/advisors` - Admin advisor management
- `POST /api/v1/retrain-model` - Retrain ML model

## 🎯 Use Cases

### **Perfect For:**
- **Secure Environments** - Air-gapped networks, government systems
- **Privacy-Conscious Organizations** - Healthcare, finance, legal
- **Cost-Sensitive Projects** - Startups, research, education
- **Reliability-Critical Systems** - Production environments, critical infrastructure

### **Ideal Scenarios:**
- **Hackathons** - Quick setup, no external dependencies
- **Proof of Concepts** - Fast iteration, reliable testing
- **Internal Tools** - Corporate environments with restrictions
- **Research Projects** - Reproducible, self-contained

## 🔧 Troubleshooting

### **Common Issues:**

1. **Port already in use**
   ```bash
   lsof -ti:8000 | xargs kill -9
   lsof -ti:3000 | xargs kill -9
   ```

2. **AI Gateway not connecting**
   - Check your `.env` file configuration
   - Verify gateway URL and API key
   - System will fall back to offline mode

3. **ML model not training**
   - Ensure Excel file has sufficient data
   - Check column names match expected format
   - Verify data quality and completeness

4. **Frontend not loading**
   - Check if backend is running on port 8000
   - Verify API endpoints are accessible
   - Check browser console for errors

## 📈 Performance

### **System Requirements:**
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Storage**: 1GB for application + data

### **Performance Metrics:**
- **Response Time**: < 500ms for API calls
- **ML Training**: < 30 seconds for 1000 records
- **Concurrent Users**: 50+ simultaneous users
- **Data Processing**: 10,000+ records per minute

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🎉 Ready to Use!

Your AdvisorConnect GenAI v2 system is ready to revolutionize advisor matching with AI-powered intelligence!

**Access your application:**
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000/admin/cases

**Key Features Available:**
- ML Model Performance Dashboard
- Excel Upload & Training
- AI Advisor Recommendations
- Real-time Case Management
- Intelligent Matching Insights

🚀 **Start matching advisors intelligently today!**
