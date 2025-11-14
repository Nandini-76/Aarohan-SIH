# AAROHAN API Documentation

Complete API reference for the AAROHAN backend service.

---

## 📋 Table of Contents

- [Base URL](#-base-url)
- [Authentication](#-authentication)
- [Endpoints](#-endpoints)
  - [Health Check](#health-check)
  - [Student Operations](#student-operations)
  - [Predictions](#predictions)
  - [Dashboard](#dashboard)
  - [Simulations](#simulations)
- [Data Models](#-data-models)
- [Error Handling](#-error-handling)
- [Rate Limiting](#-rate-limiting)

---

## 🌐 Base URL

**Production:** `https://arohann.onrender.com`  
**Development:** `http://localhost:8000`

---

## 🔐 Authentication

Currently, most endpoints are **publicly accessible** for development. In production, implement authentication:

```http
Authorization: Bearer <token>
```

---

## 📡 Endpoints

### Health Check

Check if the API is running and the ML model is loaded.

**Endpoint:** `GET /`

**Request:**
```http
GET / HTTP/1.1
Host: arohann.onrender.com
```

**Response:**
```json
{
  "status": "ok",
  "message": "AAROHAN API is running",
  "version": "2.0",
  "ml_model_loaded": true
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `500 Internal Server Error` - Service is down or ML model not loaded

---

### Student Operations

#### Get All Students

Retrieve all students and sync to Firebase.

**Endpoint:** `GET /api/students`

**Request:**
```http
GET /api/students HTTP/1.1
Host: arohann.onrender.com
```

**Response:**
```json
{
  "students": [
    {
      "enrollment_no": "2021CSE001",
      "name": "Rajesh Kumar",
      "department": "Computer Science",
      "year": 3,
      "attendance": 78.5,
      "cgpa": 7.2,
      "backlogs": 1,
      "marks_10th": 85.0,
      "marks_12th": 82.0,
      "fees_flag": 0,
      "suspension_flag": 0,
      "gender": "M",
      "phase": "Yellow",
      "lastUpdated": "2025-11-14T10:30:00Z"
    }
    // ... more students
  ],
  "count": 56,
  "firebase_synced": true
}
```

**Status Codes:**
- `200 OK` - Students retrieved successfully
- `500 Internal Server Error` - Database error

---

#### Get Single Student

Retrieve details for a specific student.

**Endpoint:** `GET /api/students/{enrollment_no}`

**Parameters:**
- `enrollment_no` (path) - Student enrollment number

**Request:**
```http
GET /api/students/2021CSE001 HTTP/1.1
Host: arohann.onrender.com
```

**Response:**
```json
{
  "enrollment_no": "2021CSE001",
  "name": "Rajesh Kumar",
  "department": "Computer Science",
  "year": 3,
  "attendance": 78.5,
  "cgpa": 7.2,
  "backlogs": 1,
  "marks_10th": 85.0,
  "marks_12th": 82.0,
  "fees_flag": 0,
  "suspension_flag": 0,
  "gender": "M",
  "phase": "Yellow",
  "predicted_risk": 0.35,
  "intervention_history": [
    {
      "date": "2025-10-15",
      "phase": "Yellow",
      "action": "Counselor notified for monitoring"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Student found
- `404 Not Found` - Student doesn't exist
- `400 Bad Request` - Invalid enrollment number

---

### Predictions

#### Predict Dropout Risk

Predict dropout risk for a student based on their data.

**Endpoint:** `POST /api/predict`

**Request Body:**
```json
{
  "enrollment_no": "2021CSE001",
  "attendance": 65.0,
  "cgpa": 5.8,
  "backlogs": 2,
  "marks_10th": 75.0,
  "marks_12th": 78.0,
  "fees_flag": 0,
  "suspension_flag": 0,
  "gender": "M"
}
```

**Field Descriptions:**
- `enrollment_no` (string) - Student ID
- `attendance` (float) - Attendance percentage (0-100)
- `cgpa` (float) - CGPA on 10-point scale (0-10)
- `backlogs` (int) - Number of failed subjects
- `marks_10th` (float) - 10th grade percentage
- `marks_12th` (float) - 12th grade percentage
- `fees_flag` (int) - Fee status (0=paid, 1=unpaid)
- `suspension_flag` (int) - Disciplinary status (0=none, 1=suspended)
- `gender` (string) - "M" or "F"

**Response:**
```json
{
  "enrollment_no": "2021CSE001",
  "name": "Rajesh Kumar",
  "model_phase": "Yellow",
  "final_phase": "Orange",
  "rule_override": true,
  "override_reason": "Attendance below 70% threshold - elevated to Orange",
  "ml_probability": 0.42,
  "confidence": 0.85,
  "features_used": {
    "attendance": 65.0,
    "cgpa": 5.8,
    "backlogs": 2,
    "att_cgpa_interaction": 3.77,
    "risk_index": 18.4
  },
  "recommendations": [
    "Schedule counseling session within 48 hours",
    "Assess attendance barriers",
    "Monitor academic performance closely"
  ],
  "notification_sent": true,
  "stakeholders_notified": ["counselor"]
}
```

**Status Codes:**
- `200 OK` - Prediction successful
- `400 Bad Request` - Invalid input data
- `422 Unprocessable Entity` - Missing required fields

---

### Dashboard

#### Get Dashboard Statistics

Retrieve summary statistics for the dashboard.

**Endpoint:** `GET /api/dashboard/stats`

**Request:**
```http
GET /api/dashboard/stats HTTP/1.1
Host: arohann.onrender.com
```

**Query Parameters (optional):**
- `department` - Filter by department (e.g., "Computer Science")
- `year` - Filter by year (e.g., 2, 3, 4)

**Response:**
```json
{
  "total_students": 1500,
  "risk_distribution": {
    "Green": 850,
    "Yellow": 420,
    "Orange": 180,
    "Red": 50
  },
  "department_breakdown": {
    "Computer Science": {
      "total": 400,
      "Green": 220,
      "Yellow": 120,
      "Orange": 50,
      "Red": 10
    },
    "Mechanical Engineering": {
      "total": 350,
      "Green": 200,
      "Yellow": 100,
      "Orange": 40,
      "Red": 10
    }
    // ... more departments
  },
  "intervention_outcomes": {
    "improved": 135,
    "stable": 45,
    "declined": 25
  },
  "average_attendance": 76.5,
  "average_cgpa": 6.8,
  "lastUpdated": "2025-11-14T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Statistics retrieved
- `500 Internal Server Error` - Database error

---

### Simulations

#### Run What-If Simulation

Test hypothetical scenarios by adjusting student parameters.

**Endpoint:** `POST /api/simulate`

**Request Body:**
```json
{
  "enrollment_no": "2021CSE001",
  "current_state": {
    "attendance": 65.0,
    "cgpa": 5.8,
    "backlogs": 2
  },
  "simulated_state": {
    "attendance": 80.0,
    "cgpa": 6.5,
    "backlogs": 1
  },
  "marks_10th": 75.0,
  "marks_12th": 78.0,
  "fees_flag": 0,
  "suspension_flag": 0,
  "gender": "M"
}
```

**Response:**
```json
{
  "enrollment_no": "2021CSE001",
  "current_prediction": {
    "phase": "Orange",
    "probability": 0.42,
    "confidence": 0.85
  },
  "simulated_prediction": {
    "phase": "Yellow",
    "probability": 0.28,
    "confidence": 0.88
  },
  "improvement": {
    "phase_change": "Orange → Yellow",
    "risk_reduction": 0.14,
    "percentage_improvement": "33%"
  },
  "recommendations": [
    "Focus on improving attendance to 80%",
    "Clear 1 backlog subject",
    "Maintain CGPA above 6.5"
  ]
}
```

**Status Codes:**
- `200 OK` - Simulation successful
- `400 Bad Request` - Invalid simulation parameters

---

## 📊 Data Models

### Student

```typescript
interface Student {
  enrollment_no: string;
  name: string;
  department: string;
  year: number;
  attendance: number;        // 0-100
  cgpa: number;             // 0-10
  backlogs: number;         // >= 0
  marks_10th: number;       // 0-100
  marks_12th: number;       // 0-100
  fees_flag: 0 | 1;        // 0=paid, 1=unpaid
  suspension_flag: 0 | 1;   // 0=none, 1=suspended
  gender: "M" | "F";
  phase?: "Green" | "Yellow" | "Orange" | "Red";
  predicted_risk?: number;  // 0-1
  lastUpdated?: string;     // ISO 8601 timestamp
}
```

### Prediction Result

```typescript
interface PredictionResult {
  enrollment_no: string;
  name: string;
  model_phase: "Green" | "Yellow" | "Orange" | "Red";
  final_phase: "Green" | "Yellow" | "Orange" | "Red";
  rule_override: boolean;
  override_reason?: string;
  ml_probability: number;   // 0-1
  confidence: number;       // 0-1
  features_used: Record<string, number>;
  recommendations: string[];
  notification_sent: boolean;
  stakeholders_notified: string[];
}
```

### Dashboard Stats

```typescript
interface DashboardStats {
  total_students: number;
  risk_distribution: {
    Green: number;
    Yellow: number;
    Orange: number;
    Red: number;
  };
  department_breakdown: Record<string, {
    total: number;
    Green: number;
    Yellow: number;
    Orange: number;
    Red: number;
  }>;
  intervention_outcomes: {
    improved: number;
    stable: number;
    declined: number;
  };
  average_attendance: number;
  average_cgpa: number;
  lastUpdated: string;
}
```

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "STUDENT_NOT_FOUND",
    "message": "Student with enrollment number 2021CSE999 not found",
    "details": {
      "enrollment_no": "2021CSE999"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `STUDENT_NOT_FOUND` | 404 | Student doesn't exist |
| `INVALID_INPUT` | 400 | Invalid request parameters |
| `MISSING_FIELD` | 422 | Required field missing |
| `ML_MODEL_ERROR` | 500 | ML prediction failed |
| `FIREBASE_ERROR` | 500 | Firebase operation failed |
| `DATABASE_ERROR` | 500 | Database operation failed |

---

## 🚦 Rate Limiting

**Current Limits:**
- 100 requests per minute per IP
- 1000 requests per hour per IP

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699876543
```

**Rate Limit Exceeded Response:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 60 seconds.",
    "retry_after": 60
  }
}
```

**Status Code:** `429 Too Many Requests`

---

## 📝 Usage Examples

### Python Example

```python
import requests

BASE_URL = "https://arohann.onrender.com"

# Health check
response = requests.get(f"{BASE_URL}/")
print(response.json())

# Predict dropout risk
student_data = {
    "enrollment_no": "2021CSE001",
    "attendance": 65.0,
    "cgpa": 5.8,
    "backlogs": 2,
    "marks_10th": 75.0,
    "marks_12th": 78.0,
    "fees_flag": 0,
    "suspension_flag": 0,
    "gender": "M"
}

response = requests.post(f"{BASE_URL}/api/predict", json=student_data)
prediction = response.json()
print(f"Risk Phase: {prediction['final_phase']}")
```

### JavaScript Example

```javascript
const BASE_URL = "https://arohann.onrender.com";

// Health check
const healthCheck = async () => {
  const response = await fetch(`${BASE_URL}/`);
  const data = await response.json();
  console.log(data);
};

// Predict dropout risk
const predictRisk = async (studentData) => {
  const response = await fetch(`${BASE_URL}/api/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(studentData),
  });
  
  const prediction = await response.json();
  console.log(`Risk Phase: ${prediction.final_phase}`);
};

// Usage
predictRisk({
  enrollment_no: "2021CSE001",
  attendance: 65.0,
  cgpa: 5.8,
  backlogs: 2,
  marks_10th: 75.0,
  marks_12th: 78.0,
  fees_flag: 0,
  suspension_flag: 0,
  gender: "M"
});
```

### cURL Example

```bash
# Health check
curl https://arohann.onrender.com/

# Predict dropout risk
curl -X POST https://arohann.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment_no": "2021CSE001",
    "attendance": 65.0,
    "cgpa": 5.8,
    "backlogs": 2,
    "marks_10th": 75.0,
    "marks_12th": 78.0,
    "fees_flag": 0,
    "suspension_flag": 0,
    "gender": "M"
  }'

# Get dashboard stats
curl https://arohann.onrender.com/api/dashboard/stats
```

---

## 📚 Additional Resources

- **Interactive API Docs:** https://arohann.onrender.com/docs
- **Alternative UI:** https://arohann.onrender.com/redoc
- **GitHub Repository:** https://github.com/Gaurav8302/AROHANN
- **Setup Guide:** [SETUP.md](./SETUP.md)
- **Deployment Guide:** [DEPLOYMENT.md](./DEPLOYMENT.md)

---

<div align="center">

**Questions about the API?**

Open an issue on [GitHub](https://github.com/Gaurav8302/AROHANN/issues)

</div>
