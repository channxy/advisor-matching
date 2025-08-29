# AdvisorConnect - Integrated System Guide

## 🎯 **System Overview**

This is a **fully integrated AI-powered advisor matching system** that combines:
- **Excel data processing** for historical transaction analysis
- **Machine learning** for advisor recommendations
- **Real-time case submission** with AI matching
- **Dynamic advisor profile generation** from transaction data

## 🏗️ **Architecture & Integration**

### **Core Components Working Together:**

1. **ExcelProcessor** - Processes historical transaction data
2. **MLService** - Machine learning for advisor recommendations
3. **MatchingService** - Real-time advisor matching algorithm
4. **AIService** - Case classification and complexity scoring
5. **Frontend Components** - Integrated UI for all workflows

---

## 🚀 **How to Use the Integrated System**

### **1. Initial Setup (Excel Data Processing)**

**Step 1: Upload Excel Data**
- Click "Upload Excel" button in Admin Cases page
- Select your `transactions.xlsx` file
- System automatically:
  - Processes all transactions
  - Generates advisor profiles from "Current Case Owner" data
  - Creates cases and assignments
  - Trains the ML model

**Step 2: View Generated Data**
- Check "All Cases" page to see processed cases
- Check "Advisor Profiles" page to see generated advisor profiles
- All data comes from your Excel file, not static seed data

### **2. Real-Time Case Submission with AI Matching**

**Step 1: Submit New Case**
- Click "New Case" button in Admin Cases page
- Fill in case details (topic, subtopic, query, etc.)
- Click "Get Recommendations"

**Step 2: AI Recommendations**
- System shows top 3 advisor recommendations
- Each recommendation includes:
  - Confidence score
  - Expertise tags
  - Success rate
  - Source (ML Model or Matching Service)

**Step 3: Submit Case**
- Review recommendations
- Click "Submit Case"
- System creates case and assignments using MatchingService

---

## 🔧 **Technical Integration Details**

### **Backend Integration:**

```python
# Excel Upload API uses:
excel_processor.process_excel_and_generate_profiles()  # Process Excel data
ml_service._train_model()  # Train ML model

# Recommendation API uses:
ml_service.recommend_advisors()  # ML-based recommendations
matching_service.find_best_advisors()  # Rule-based matching

# Case Submission API uses:
matching_service.find_best_advisors()  # Find best advisors
matching_service.create_assignments()  # Create assignments
```

### **Frontend Integration:**

```javascript
// Excel Upload Component:
excelAPI.uploadExcel(file)  // Upload and process Excel

// Case Submission Component:
excelAPI.getRecommendations(caseData)  // Get AI recommendations
casesAPI.submitCase(caseData)  // Submit case with matching
```

---

## 📊 **Data Flow**

### **Excel Processing Flow:**
```
Excel File → ExcelProcessor → Advisor Profiles → Cases → Assignments → ML Model Training
```

### **Case Submission Flow:**
```
New Case → AIService (Classification) → MatchingService (Find Advisors) → Create Assignments
```

### **Recommendation Flow:**
```
Case Data → MLService (ML Recommendations) + MatchingService (Rule-based) → Combined Results
```

---

## 🎯 **Key Features**

### **1. Dynamic Advisor Profile Generation**
- **No static seed data** - all profiles generated from Excel
- **Automatic expertise extraction** from transaction history
- **Performance metrics calculation** (success rate, resolution time)
- **Complexity preference learning** from historical cases

### **2. Dual Recommendation System**
- **ML Model**: Trained on Excel data, uses RandomForest classifier
- **Matching Service**: Rule-based matching with multiple criteria
- **Combined Results**: Merges both approaches for better recommendations

### **3. Real-Time Case Management**
- **Live case submission** with immediate advisor matching
- **Assignment creation** using MatchingService
- **Status tracking** and workflow management

### **4. Integrated Frontend**
- **Excel upload interface** with drag-and-drop
- **Multi-step case submission** with recommendations
- **Real-time data refresh** after operations
- **Unified dashboard** for all operations

---

## 🔍 **API Endpoints**

### **Excel & ML Endpoints:**
- `POST /api/v1/upload-excel` - Upload and process Excel data
- `POST /api/v1/recommend-advisors` - Get AI recommendations
- `POST /api/v1/update-advisor-profile` - Update advisor profiles
- `GET /api/v1/advisor-inbox/{advisor_id}` - Get advisor's cases

### **Case Management Endpoints:**
- `POST /cases/submit_case` - Submit new case with matching
- `GET /cases/` - List all cases
- `GET /cases/{case_id}` - Get case details
- `PUT /cases/{case_id}/resolve` - Resolve case

### **Assignment Endpoints:**
- `POST /assignments/case/{case_id}/accept` - Accept case assignment
- `POST /assignments/case/{case_id}/decline` - Decline case assignment
- `GET /assignments/case/{case_id}` - Get case assignments

---

## 🧪 **Testing the Integration**

### **1. Test Excel Upload:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload-excel" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_transactions.xlsx"
```

### **2. Test Recommendations:**
```bash
curl -X POST "http://localhost:8000/api/v1/recommend-advisors" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Corporate Tax",
    "subtopic": "Tax Planning", 
    "query": "Client needs tax optimization strategy",
    "complexity": 85,
    "business_function": "Tax Advisory",
    "country": "United States"
  }'
```

### **3. Test Case Submission:**
```bash
curl -X POST "http://localhost:8000/cases/submit_case" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Test Topic",
    "subtopic": "Test Subtopic",
    "query": "Test query",
    "casetype": "Test",
    "transaction_type": "Test",
    "business_function": "Test",
    "country": "Test"
  }'
```

---

## 🎉 **Success Indicators**

### **✅ System is Working When:**

1. **Excel Upload:**
   - Shows "Upload Successful" with case/advisor counts
   - Displays model accuracy percentage
   - Cases and advisors appear in respective pages

2. **Case Submission:**
   - Shows 3 advisor recommendations with confidence scores
   - Displays expertise tags and success rates
   - Case appears in cases list after submission

3. **Recommendations:**
   - Returns both ML and Matching Service results
   - Shows confidence scores and insights
   - Includes advisor expertise information

4. **Data Consistency:**
   - All advisors have profiles generated from Excel data
   - Cases show proper assignments and status
   - Frontend displays real data, not placeholder content

---

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"Case Detail Not Working"**
   - Check if case data exists in database
   - Verify API endpoints are responding
   - Check browser console for errors

2. **"No Recommendations"**
   - Ensure Excel data has been uploaded
   - Check if ML model has been trained
   - Verify case data format

3. **"Frontend Not Loading"**
   - Check if both backend (8000) and frontend (3000) are running
   - Verify CORS settings
   - Check network connectivity

### **Debug Commands:**
```bash
# Check if server is running
curl http://localhost:8000/health

# Check database content
sqlite3 advisor_connect.db "SELECT COUNT(*) FROM advisors;"
sqlite3 advisor_connect.db "SELECT COUNT(*) FROM cases;"

# Check API responses
curl http://localhost:8000/cases/ | python -m json.tool
curl http://localhost:8000/advisors/ | python -m json.tool
```

---

## 🚀 **Next Steps**

The system is now **fully integrated** and **production-ready**. All components work together:

- ✅ **ExcelProcessor** generates advisor profiles from transaction data
- ✅ **MatchingService** provides real-time advisor matching
- ✅ **MLService** offers ML-based recommendations
- ✅ **Frontend** provides unified interface for all operations
- ✅ **APIs** are properly connected and functional

**You can now:**
1. Upload Excel files to generate advisor profiles
2. Submit new cases and get AI recommendations
3. View all cases and advisor profiles
4. Manage case assignments and status
5. Use the integrated dashboard for all operations

The system successfully combines **historical data processing** with **real-time AI matching** for a complete advisor management solution!
