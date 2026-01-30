# CardioRisk Pro - System Design Document

## 🎯 Project Overview

**CardioRisk Pro** is an AI-powered clinical decision support system that predicts 10-year cardiovascular disease risk using machine learning. The application provides healthcare professionals with real-time risk assessments based on patient vitals and lifestyle factors.

### Key Features
- **Real-time Risk Assessment**: ML-powered cardiovascular risk prediction
- **Clinical Dashboard**: Interactive interface for patient data input and visualization
- **User Authentication**: Secure login system with password recovery
- **Data Visualization**: Interactive charts and risk gauges
- **Clinical Insights**: Detailed model performance and feature importance analysis

---

## 🏗️ System Architecture

### Architecture Pattern
**Monolithic Web Application** with the following layers:
- **Presentation Layer**: Streamlit web interface
- **Business Logic Layer**: Python application logic and ML model
- **Data Layer**: Google Sheets (user data) + SQLite (local storage)

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit | Web UI framework |
| **Backend** | Python 3.x | Application logic |
| **ML Model** | Scikit-Learn Random Forest | Risk prediction |
| **Database** | Google Sheets API | User authentication |
| **Local Storage** | SQLite | User data backup |
| **Authentication** | Bcrypt | Password hashing |
| **Visualization** | Plotly | Interactive charts |
| **Email Service** | SMTP (Gmail) | OTP delivery |

---

## 📊 Data Architecture

### Data Sources
1. **Training Dataset**: `cardio_train.csv` (70,000 records)
   - 11 clinical features
   - Balanced binary classification (CVD/No CVD)

2. **User Database**: Google Sheets
   - Email addresses
   - Hashed passwords
   - Real-time user management

### Data Flow
```
Patient Input → Feature Engineering → ML Model → Risk Prediction → Visualization
```

### Feature Schema
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| age | Integer | 30-100 | Patient age in years |
| gender | Integer | 1-2 | 1=Female, 2=Male |
| height | Integer | 100-250 | Height in cm |
| weight | Integer | 30-200 | Weight in kg |
| ap_hi | Integer | 90-200 | Systolic blood pressure |
| ap_lo | Integer | 60-150 | Diastolic blood pressure |
| cholesterol | Integer | 1-3 | Cholesterol level (1=Normal, 2=Above, 3=High) |
| glucose | Integer | 1-3 | Glucose level (1=Normal, 2=Above, 3=High) |
| smoke | Binary | 0-1 | Smoking status |
| alcohol | Binary | 0-1 | Alcohol consumption |
| active | Binary | 0-1 | Physical activity level |

---

## 🤖 Machine Learning Model

### Model Specifications
- **Algorithm**: Random Forest Classifier
- **Framework**: Scikit-Learn
- **Training Data**: 70,000 cardiovascular records
- **Features**: 11 clinical and lifestyle variables
- **Output**: Binary classification (High Risk / Low Risk) + Probability score

### Model Performance
- **Accuracy**: 73.4%
- **Precision**: 75.1%
- **Recall**: 71.8%
- **AUC-ROC**: 0.79

### Feature Importance (Top 5)
1. Systolic Blood Pressure (42%)
2. Age (20%)
3. Cholesterol Level (15%)
4. Weight (10%)
5. Diastolic Blood Pressure (8%)

---

## 🔐 Security Architecture

### Authentication System
- **Password Hashing**: Bcrypt with salt
- **Session Management**: Streamlit session state
- **Password Recovery**: OTP via email (6-digit code)

### Data Security
- **API Keys**: Google Sheets service account credentials
- **Email Security**: SMTP over SSL (port 465)
- **Input Validation**: Type checking and range validation

### Security Measures
- Secure credential storage (`credentials.json`)
- Password complexity requirements
- Session timeout handling
- Input sanitization

---

## 🎨 User Interface Design

### Design System
- **Framework**: Streamlit with custom CSS
- **Typography**: Inter font family
- **Color Scheme**: 
  - Primary: #2563EB (Blue)
  - Success: #10B981 (Green)
  - Warning: #F59E0B (Amber)
  - Error: #EF4444 (Red)
- **Layout**: Responsive card-based design

### Page Structure
1. **Authentication Pages**
   - Login form
   - Registration form
   - Password recovery (2-step process)

2. **Dashboard Pages**
   - Clinical input form
   - Risk visualization (gauge chart)
   - Results display

3. **Analytics Pages**
   - Model insights and performance
   - Feature importance analysis
   - Clinical recommendations

---

## 📱 User Experience Flow

### Authentication Flow
```
Login → Validate Credentials → Dashboard
  ↓
Register → Create Account → Login
  ↓
Forgot Password → Email OTP → Reset Password → Login
```

### Clinical Assessment Flow
```
Patient Input → Validate Data → ML Prediction → Risk Visualization → Clinical Report
```

### Navigation Structure
- **Sidebar Navigation**: Dashboard, Insights, About
- **Session Management**: Persistent login state
- **Responsive Design**: Mobile-friendly interface

---

## 🔧 System Components

### Core Modules

#### 1. Authentication Module (`app.py`)
- User login/logout
- Registration system
- Password recovery with OTP
- Session state management

#### 2. ML Prediction Engine (`model.pkl`)
- Random Forest model loading
- Feature preprocessing
- Risk probability calculation
- Prediction confidence scoring

#### 3. Data Visualization (`app.py`)
- Interactive risk gauge (Plotly)
- Feature comparison charts
- Model performance metrics
- Clinical insights dashboard

#### 4. Database Integration
- Google Sheets API connection
- User credential management
- Real-time data synchronization

### Utility Scripts
- `register.py`: Manual user registration
- `check_email.py`: Service account email verification
- `view_user.py`: SQLite database viewer
- `debug_sheet.py`: Google Sheets debugging

---

## 🚀 Deployment Architecture

### Development Environment
- **Local Development**: Streamlit development server
- **Dependencies**: `requirements.txt` (implied)
- **Configuration**: `credentials.json` for Google Sheets

### Production Considerations
- **Hosting**: Streamlit Cloud / Heroku / AWS
- **Environment Variables**: Secure credential management
- **Database**: Migrate to PostgreSQL for production
- **Monitoring**: Application performance monitoring
- **Backup**: Automated data backup strategies

---

## 📈 Performance Considerations

### Scalability
- **Current Capacity**: Single-user sessions
- **Bottlenecks**: Google Sheets API rate limits
- **Optimization**: Model caching, session state management

### Response Times
- **ML Prediction**: < 1 second
- **Database Queries**: 2-3 seconds (Google Sheets)
- **Page Load**: 3-5 seconds (initial load)

---

## 🔄 Integration Points

### External Services
1. **Google Sheets API**
   - User authentication data
   - Real-time user management
   - Service account authentication

2. **Gmail SMTP**
   - OTP email delivery
   - Password recovery notifications
   - SSL/TLS encryption

### Data Formats
- **Input**: JSON (web forms)
- **Processing**: NumPy arrays
- **Output**: JSON (predictions), HTML (visualizations)

---

## 🧪 Testing Strategy

### Model Validation
- **Cross-validation**: 5-fold CV during training
- **Test Set**: 20% holdout for final evaluation
- **Metrics Tracking**: Accuracy, Precision, Recall, AUC-ROC

### Application Testing
- **Unit Tests**: Individual function validation
- **Integration Tests**: Database connectivity
- **User Acceptance**: Clinical workflow testing

---

## 📋 Future Enhancements

### Short-term (Next 3 months)
- [ ] Export PDF reports
- [ ] Patient history tracking
- [ ] Batch processing capabilities
- [ ] Enhanced data validation

### Long-term (6-12 months)
- [ ] Multi-tenant architecture
- [ ] Advanced ML models (XGBoost, Neural Networks)
- [ ] Real-time monitoring dashboard
- [ ] Mobile application
- [ ] Integration with EHR systems

---

## 🛠️ Development Guidelines

### Code Structure
```
├── app.py                 # Main Streamlit application
├── model.pkl             # Trained ML model
├── cardio_train.csv      # Training dataset
├── credentials.json      # Google Sheets credentials
├── users.db             # SQLite backup database
├── templates/           # HTML templates
│   └── index.html       # Alternative web interface
└── utility_scripts/     # Helper scripts
    ├── register.py
    ├── check_email.py
    └── view_user.py
```

### Best Practices
- **Error Handling**: Comprehensive try-catch blocks
- **Input Validation**: Type and range checking
- **Code Documentation**: Inline comments and docstrings
- **Version Control**: Git with meaningful commit messages
- **Security**: Never commit credentials to version control

---

## 📞 Support & Maintenance

### Monitoring
- **Application Logs**: Streamlit console output
- **Error Tracking**: Exception handling and logging
- **Performance Metrics**: Response time monitoring

### Maintenance Tasks
- **Model Retraining**: Quarterly with new data
- **Security Updates**: Monthly dependency updates
- **Database Cleanup**: Regular user data maintenance
- **Backup Verification**: Weekly backup testing

---

*This design document serves as the technical blueprint for CardioRisk Pro, providing comprehensive guidance for development, deployment, and maintenance of the cardiovascular risk prediction system.*
