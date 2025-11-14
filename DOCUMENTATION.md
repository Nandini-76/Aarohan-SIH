# AAROHAN Documentation

Welcome to AAROHAN - AI-Based Student Dropout Prediction & Counseling System

---

## 📚 Documentation Index

### Getting Started

1. **[README.md](./README.md)** - Start here!
   - Project overview
   - Features and highlights
   - Quick start guide
   - Live demo links

2. **[SETUP.md](./SETUP.md)** - Local development setup
   - System requirements
   - Backend configuration
   - Frontend configuration
   - Firebase setup
   - Troubleshooting guide

### Deployment & Operations

3. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment
   - Firebase setup
   - Render.com backend deployment
   - Vercel frontend deployment
   - Environment variables
   - Monitoring and maintenance

4. **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Testing procedures
   - Local testing
   - Production testing
   - Test scenarios
   - Performance testing
   - Troubleshooting

### Development

5. **[API.md](./API.md)** - API reference
   - All endpoints documented
   - Request/response examples
   - Data models
   - Error handling
   - Usage examples in Python, JavaScript, cURL

6. **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Contribution guidelines
   - How to contribute
   - Development workflow
   - Coding standards
   - Pull request process
   - Community guidelines

---

## 🚀 Quick Links

### For First-Time Users
1. Read [README.md](./README.md) for project overview
2. Follow [SETUP.md](./SETUP.md) to run locally
3. Check [TESTING_GUIDE.md](./TESTING_GUIDE.md) to verify everything works

### For Deploying to Production
1. Complete local setup first
2. Follow [DEPLOYMENT.md](./DEPLOYMENT.md) step-by-step
3. Use [TESTING_GUIDE.md](./TESTING_GUIDE.md) to verify deployment

### For Developers
1. Review [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines
2. Check [API.md](./API.md) for endpoint details
3. Follow coding standards in [CONTRIBUTING.md](./CONTRIBUTING.md)

### For API Integration
1. See [API.md](./API.md) for complete endpoint reference
2. Use provided code examples (Python, JavaScript, cURL)
3. Check [TESTING_GUIDE.md](./TESTING_GUIDE.md) for testing your integration

---

## 📁 Project Structure

```
AAROHAN/
├── README.md              # Project overview
├── SETUP.md               # Local setup guide
├── DEPLOYMENT.md          # Production deployment
├── TESTING_GUIDE.md       # Testing procedures
├── API.md                 # API documentation
├── CONTRIBUTING.md        # Contribution guide
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules
├── render.yaml            # Render config
├── vercel.json            # Vercel config
│
├── backend/               # Python FastAPI backend
│   ├── app/
│   │   ├── main.py       # API endpoints
│   │   ├── models/       # ML models
│   │   └── data/         # Training data
│   ├── requirements.txt
│   └── serviceAccountKey.json  # Firebase credentials (not in git)
│
└── frontend/              # React + TypeScript frontend
    ├── src/
    │   ├── pages/        # Dashboard, profiles, etc.
    │   ├── components/   # Reusable UI components
    │   └── services/     # API integration
    ├── package.json
    └── .env              # Environment variables (not in git)
```

---

## 🎯 Common Tasks

### Run Locally
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

### Deploy to Production
See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete instructions

### Run Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Make API Requests
```bash
# Health check
curl https://arohann.onrender.com/

# Predict dropout risk
curl -X POST https://arohann.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"enrollment_no":"TEST001", "attendance":65.0, ...}'
```

---

## 🆘 Need Help?

1. **Check Documentation**: Search through the guides above
2. **Common Issues**: See Troubleshooting sections in each guide
3. **GitHub Issues**: [Open an issue](https://github.com/Gaurav8302/AROHANN/issues)
4. **Discussions**: [GitHub Discussions](https://github.com/Gaurav8302/AROHANN/discussions)

---

## 📊 System Status

- **Production Backend**: https://arohann.onrender.com
- **Production Frontend**: https://aarohan.vercel.app (replace with your URL)
- **API Docs**: https://arohann.onrender.com/docs

---

## 🔄 Documentation Updates

This documentation was last updated: November 2025

If you find any issues or have suggestions for improvements:
- Open an issue on GitHub
- Submit a pull request with corrections
- Contact the maintainers

---

<div align="center">

**Built with ❤️ for accessible, equitable education**

[GitHub](https://github.com/Gaurav8302/AROHANN) • [Report Bug](https://github.com/Gaurav8302/AROHANN/issues) • [Request Feature](https://github.com/Gaurav8302/AROHANN/issues)

</div>
