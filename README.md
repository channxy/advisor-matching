# AdvisorConnect GenAI v2 - AI-Powered Advisor Matching System

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
- **Retraining Capability**: Update models with new data every 3 days
- **Multiple Sheet Support**: Handles complex Excel files with multiple sheets

## 🏗️ Architecture

```
advisor-matching/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # ML services & business logic
│   │   │   ├── ml_model.py        # Comprehensive ML model
│   │   │   ├── ml_service.py      # ML service integration
│   │   │   ├── excel_processor.py # Excel data processing
│   │   │   └── matching_service.py # Advisor matching logic
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

## 🚀 Quick Start (Multiple Options)

### Option 1: Docker (Recommended - Plug & Play)
**Prerequisites**: Docker Desktop installed

```bash
# Clone and run with Docker (one command)
git clone <repository-url> && cd advisor-matching && ./docker-start.sh

# Or if already cloned, just run:
./docker-start.sh
```

### Option 2: Local Development
**Prerequisites**: Python 3.8+, Node.js 16+, Git

```bash
# Clone and run locally
git clone <repository-url> && cd advisor-matching && ./start.sh

# Or if already cloned, just run:
./start.sh
```

### Option 3: Manual Docker Commands
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### What the startup scripts do:

**Docker Startup (`./docker-start.sh`):**
1. ✅ **Checks Docker installation**
2. ✅ **Builds container images** (backend & frontend)
3. ✅ **Starts all services** with health checks
4. ✅ **Creates sample Excel data** for testing
5. ✅ **Opens the application** in your browser

**Local Startup (`./start.sh`):**
1. ✅ **Creates Python virtual environment**
2. ✅ **Installs all dependencies** (Python & Node.js)
3. ✅ **Creates sample Excel data** for testing
4. ✅ **Starts backend server** on port 8000
5. ✅ **Starts frontend server** on port 3000
6. ✅ **Opens the application** in your browser

## 🎯 Key Features Demonstrated

### **ML Model Performance Dashboard**
- **Real-time Model Metrics**: Test accuracy, training accuracy, cross-validation scores
- **Feature Importance Analysis**: Shows which factors most influence matching
- **Model Retraining**: Upload new data to improve model accuracy
- **Performance Visualization**: Interactive charts and progress indicators

### **Intelligent Advisor Matching**
- **Top 3 Recommendations**: With confidence scores and detailed reasoning
- **Priority-Based Matching**: Topic → Subtopic → Business Function → Department → Country
- **Matching Reasons**: Explains why each advisor is recommended
- **Success Rate Integration**: Considers advisor performance history

### **Excel Data Processing**
- **Dynamic Profile Creation**: Generates advisor profiles from transaction data
- **Automatic ML Training**: Trains models on your actual data
- **Multiple Column Support**: Handles complex Excel structures
- **Query Text Processing**: Combines multiple query-related columns

### **Case Management Workflow**
- **AI-Powered Recommendations**: Get intelligent advisor suggestions
- **Accept/Decline Functionality**: With reason tracking
- **Status Updates**: Real-time case status changes
- **Clickable Navigation**: From lists to detailed case views

## 🔧 API Endpoints

### **Core Endpoints**
- `GET /` - Health check
- `GET /docs` - API documentation (Swagger UI)

### **Cases Management**
- `GET /cases/` - List all cases (filterable)
- `GET /cases/{id}` - Get case details
- `GET /cases/advisor/{advisor_id}` - Get advisor-specific cases
- `POST /cases/submit_case` - Submit new case
- `PUT /cases/{id}/resolve` - Resolve case

### **Advisor Management**
- `GET /advisors/` - List all advisors
- `GET /advisors/{id}` - Get advisor profile
- `GET /advisors/dashboard/{id}` - Get advisor dashboard data

### **Assignments**
- `POST /assignments/case/{case_id}/accept` - Accept case assignment
- `POST /assignments/case/{case_id}/decline` - Decline case assignment
- `GET /assignments/case/{case_id}` - Get case assignments

### **ML & Excel Integration**
- `POST /api/v1/upload-excel` - Upload Excel data and train ML model
- `POST /api/v1/recommend-advisors` - Get AI-powered advisor recommendations
- `GET /api/v1/model-performance` - Get ML model performance metrics
- `POST /api/v1/retrain-model` - Retrain ML model with new data
- `POST /api/v1/update-advisor-profile` - Update advisor profile with new case data
- `GET /api/v1/advisor-inbox/{advisor_id}` - Get advisor's assigned cases

## 📊 Excel Data Integration

### **Expected Excel Columns**
Your Excel file should contain these columns (case-insensitive):
- `Case ID` - Unique case identifier
- `Services` - Service type
- `Topics` - Main topic area
- `Current Sub-Topic` - Specific subtopic
- `Previous Sub-Topic` - Previous subtopic (if transferred)
- `Date Created` - Case creation date
- `Date Submitted` - Case submission date
- `Created By (Bank ID)` - Creator identifier
- `Current Case Owner` - Current advisor ID
- `Previous Case Owner` - Previous advisor ID (if transferred)
- `Status` - Case status (resolved, pending, etc.)
- `Current Advisory Group` - Current advisory group
- `Previous Advisory Group` - Previous advisory group
- `Overall Case Age (Days)` - Case age in days
- `Business Function` - Business function area
- `Department` - Department
- `Country` - Country
- `Category` - Case category
- `Complexity` - Case complexity (0-100)
- `Time Spent` - Time spent on case
- `Please describe your query` - Case description/query

### **What the AI System Learns**
- **Advisor Expertise**: From topics, subtopics, and services handled
- **Performance Patterns**: From resolution times and success rates
- **Geographic Coverage**: From countries and regions handled
- **Complexity Preferences**: From case complexity patterns
- **Transfer Patterns**: From case transfer history
- **Business Function Specialization**: From business function patterns

### **ML Model Features**
- **Topics & Sub-topics**: Primary matching criteria
- **Business Function**: Secondary matching criteria
- **Department**: Organizational alignment
- **Country**: Geographic expertise
- **Category**: Case type specialization
- **Complexity**: Difficulty level preference

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

### **User Experience**
- **Intuitive Navigation**: Clear sidebar navigation with icons
- **Contextual Actions**: Relevant actions based on current view
- **Error Handling**: Graceful error messages and fallbacks
- **Success Feedback**: Clear confirmation of successful actions

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

### **Scalability Features**
- **Modular Architecture**: Easy to extend and maintain
- **API-First Design**: RESTful APIs for easy integration
- **Database Optimization**: Efficient queries and indexing
- **Error Recovery**: Robust error handling and recovery

## 🛠️ Development

### **Docker Development**
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up --build -d

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

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

### **Testing the ML Model**
```bash
# Docker
docker-compose exec backend python -c "from app.services.ml_model import AdvisorMatchingML; ml = AdvisorMatchingML(); print('ML Model loaded successfully')"

# Local
cd backend
python -c "from app.services.ml_model import AdvisorMatchingML; ml = AdvisorMatchingML(); print('ML Model loaded successfully')"
```

## 🐳 Docker Deployment

For complete Docker deployment instructions, see [DOCKER_README.md](DOCKER_README.md).

### **Production Deployment**
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up --build -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📝 License

This is a hackathon POC for demonstration purposes. The system showcases advanced ML integration, real-time data processing, and intelligent advisor matching capabilities.

## 🤝 Contributing

This project demonstrates:
- **Advanced ML Integration** in web applications
- **Real-time Data Processing** from Excel files
- **Intelligent Recommendation Systems** with explainable AI
- **Modern Full-Stack Development** with React and FastAPI
- **Production-Ready Architecture** with proper error handling and scalability
