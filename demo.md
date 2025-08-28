# AdvisorConnect GenAI v2 - Demo Guide

## 🎯 Demo Overview

This demo showcases a complete AI-powered advisor matching system with the following key features:

1. **AI-Powered Advisor Profiling** - Dynamic advisor profiles with performance metrics
2. **Intelligent Case Matching** - AI-driven matching with percentage scores and insights
3. **Case Management Workflow** - Accept/decline functionality with reason tracking
4. **Real-time Dashboards** - Advisor and admin dashboards with analytics
5. **Learning Curve Visualization** - Performance tracking over time

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (optional, for full AI functionality)

### Setup & Run
```bash
# Clone the repository
git clone <repository-url>
cd advisor-matching

# Set OpenAI API key (optional)
export OPENAI_API_KEY="your-openai-api-key"

# Start the application
./start.sh
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎭 Demo Scenarios

### Scenario 1: Advisor Dashboard Experience

**Objective**: Show the advisor's perspective with incoming cases and performance metrics

**Steps**:
1. Navigate to http://localhost:3000
2. View the advisor dashboard for Sarah Johnson (ADV001)
3. **Highlight Features**:
   - Performance metrics (success rate, cases handled, avg resolution time)
   - Incoming cases with AI matching scores
   - Expertise tags and profile summary
   - Recent activity and resolved cases

**Key Talking Points**:
- "The AI system automatically profiles advisors based on their case history"
- "Matching scores are calculated using multiple factors: topic expertise, complexity preference, geographic location, and performance"
- "The system learns and adapts advisor profiles over time"

### Scenario 2: Case Submission & AI Matching

**Objective**: Demonstrate the AI-powered case classification and advisor matching

**Steps**:
1. Go to "Manage Applications" page
2. Click "New Case" button
3. Submit a new case with the following details:
   - **Topic**: Tax Planning
   - **Subtopic**: Corporate Tax Optimization
   - **Query**: "Need assistance with corporate tax planning strategies for multinational operations in the US and Europe"
   - **Country**: United States
   - **Business Function**: Corporate Tax

4. **Observe the AI Processing**:
   - Case gets classified with complexity score
   - AI finds best matching advisors
   - Matching insights are generated

**Key Talking Points**:
- "The AI automatically classifies case complexity and domain relevance"
- "Multiple advisors are matched based on expertise, performance, and availability"
- "Each match includes detailed reasoning for why the advisor is suitable"

### Scenario 3: Case Acceptance/Decline Workflow

**Objective**: Show the complete case management workflow

**Steps**:
1. Go to "Manage Applications" page
2. Find a pending case (e.g., CASE001)
3. Click "View Details" to see case information
4. **Accept the case**:
   - Click "Accept Case" button
   - Confirm the action
   - Observe status change to "Assigned"

5. **Decline a case** (optional):
   - Click "Decline Case" button
   - Provide a reason (required)
   - Observe status change to "Declined"

**Key Talking Points**:
- "Advisors can accept or decline cases with full transparency"
- "Decline reasons are tracked for continuous improvement"
- "The system maintains audit trails of all actions"

### Scenario 4: Admin Dashboard & Analytics

**Objective**: Demonstrate comprehensive admin oversight and analytics

**Steps**:
1. Navigate to "All Cases" (Admin section)
2. **Show filtering capabilities**:
   - Filter by status, topic, country
   - Search across case IDs and descriptions
   - View case statistics

3. Go to "Advisor Profiles" (Admin section)
4. **Explore advisor analytics**:
   - View all advisor cards with performance metrics
   - Click on an advisor to see detailed profile
   - Show learning curve visualization
   - Demonstrate profile update functionality

**Key Talking Points**:
- "Admins have complete visibility into all cases and advisor performance"
- "Learning curves show how advisors improve over time"
- "AI continuously updates advisor profiles based on new case outcomes"

### Scenario 5: AI Profile Updates

**Objective**: Show how the AI system learns and adapts

**Steps**:
1. Go to an advisor detail page (e.g., Sarah Johnson)
2. Click "Update Profile" button
3. **Explain the AI process**:
   - System analyzes recent case history
   - Updates expertise tags and complexity preference
   - Generates new profile summary
   - Recalculates performance metrics

**Key Talking Points**:
- "The AI system continuously learns from case outcomes"
- "Advisor profiles are dynamically updated based on performance"
- "Expertise tags are automatically generated and refined"

## 🎨 UI/UX Highlights

### Design Features
- **Modern Material-UI Components**: Clean, professional interface
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live status changes and notifications
- **Interactive Charts**: Performance visualization with Recharts
- **Intuitive Navigation**: Clear sidebar with categorized sections

### Color Coding
- **Green**: Success rates, accepted cases
- **Blue**: Primary actions, pending cases
- **Orange**: Warnings, medium complexity
- **Red**: Errors, high complexity, declined cases

## 🔧 Technical Architecture

### Backend (FastAPI)
- **AI Services**: OpenAI integration for embeddings and text generation
- **Matching Algorithm**: Multi-factor scoring with weighted components
- **Database**: SQLAlchemy with SQLite (production-ready for PostgreSQL)
- **API Design**: RESTful endpoints with comprehensive documentation

### Frontend (React)
- **State Management**: React hooks for local state
- **API Integration**: Axios for backend communication
- **Styling**: Material-UI + Tailwind CSS for modern design
- **Charts**: Recharts for data visualization

### AI/ML Features
- **Semantic Search**: OpenAI embeddings for case classification
- **Text Generation**: GPT for matching insights and profile summaries
- **Performance Analytics**: Learning curves and trend analysis
- **Dynamic Profiling**: Continuous advisor profile updates

## 📊 Sample Data

The system comes pre-loaded with:
- **10 Advisors** across different departments and countries
- **5 Sample Cases** with various topics and complexity levels
- **Performance Metrics** including success rates and resolution times
- **Expertise Tags** generated by AI analysis

## 🎯 Key Differentiators

1. **AI-First Approach**: Every matching decision is AI-powered
2. **Dynamic Learning**: System continuously improves advisor profiles
3. **Transparent Reasoning**: Clear explanations for all matching decisions
4. **Comprehensive Analytics**: Detailed performance tracking and visualization
5. **Scalable Architecture**: Production-ready with proper separation of concerns

## 🚀 Future Enhancements

- Real-time notifications using WebSockets
- Advanced ML models for better matching
- Integration with external case management systems
- Mobile app development
- Advanced analytics and reporting
- Multi-language support

## 📝 Demo Script

**Opening**: "Welcome to AdvisorConnect GenAI v2, an AI-powered advisor matching system that revolutionizes how we connect expertise with client needs."

**Key Message**: "This system demonstrates how AI can enhance human expertise by providing intelligent matching, continuous learning, and transparent decision-making."

**Closing**: "This POC showcases the potential of AI in professional services, creating a more efficient, transparent, and intelligent advisor-client matching process."

---

*This demo represents a production-ready POC that can be extended and customized for specific business requirements.*
