#!/bin/bash

# Installation script for PDF Report & Email features

echo "================================================"
echo "Installing PDF Report & Email Dependencies"
echo "================================================"
echo ""

# Navigate to backend directory
cd backend

echo "📦 Installing Python dependencies..."
pip install fpdf2 fastapi-mail aiosmtplib

echo ""
echo "✅ Dependencies installed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy backend/.env.example to backend/.env"
echo "2. Configure email settings in .env (optional)"
echo "3. Restart the backend server"
echo "4. Test by running a simulation with Orange/Red risk"
echo ""
echo "📖 For detailed setup instructions, see:"
echo "   REPORT_EMAIL_SETUP.md"
echo ""
echo "================================================"
