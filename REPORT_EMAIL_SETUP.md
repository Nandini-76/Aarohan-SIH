# PDF Report Generation & Email Service Setup Guide

## 🎯 Overview

This guide explains how to set up the PDF report generation and email sending features for the dropout prediction system.

## ✅ Features Implemented

### Backend Features
1. **Multilingual PDF Reports** - Generates reports in 3 languages:
   - 🇬🇧 English
   - 🇮🇳 Hindi (हिंदी)
   - 🇮🇳 Rajasthani (राजस्थानी)

2. **Automatic Report Generation** - PDFs are generated for Orange and Red risk levels

3. **Email Service** - Optional email delivery with attachments

4. **Report Download Endpoints**:
   - `/report/{simulation_id}?language=en|hi|rj` - Download specific language
   - `/report/{simulation_id}/all` - Download all reports as ZIP

### Frontend Features
1. **Email Input Field** - Optional field to receive reports via email
2. **Report Status Display** - Shows generation and email status
3. **Download Links** - Direct links to download reports in all languages

## 📦 Installation

### 1. Install Backend Dependencies

```bash
cd backend
pip install fpdf2 fastapi-mail aiosmtplib
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Configure Email Service (Optional)

Create or update `.env` file in the `backend` directory:

```env
# Email Configuration (Optional - for sending reports)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

**Note**: If email is not configured, reports will still be generated and available for download.

## 🔐 Gmail Setup (Recommended)

To use Gmail for sending reports:

### Option 1: App Password (Recommended)
1. Go to Google Account Settings
2. Enable 2-Factor Authentication
3. Go to Security → 2-Step Verification → App Passwords
4. Generate an app password for "Mail"
5. Use this password in `MAIL_PASSWORD`

### Option 2: Less Secure Apps (Not Recommended)
1. Enable "Less secure app access" in Gmail settings
2. Use your regular Gmail password

**⚠️ Security Note**: Never commit `.env` files to version control!

## 🚀 Usage

### From the Simulation Page

1. **Adjust Simulation Parameters** as usual
2. **Enter Email (Optional)**: Add email address if you want the report emailed
3. **Run Simulation**
4. **For Orange/Red Results**:
   - PDF reports are automatically generated in 3 languages
   - If email was provided, reports are sent as attachments
   - Download links appear in the results panel

### API Usage

#### Run Simulation with Email
```bash
POST http://localhost:8000/simulate
Content-Type: application/json

{
  "attendance": 60,
  "cgpa": 5.5,
  "backlogs": 3,
  "fees_flag": 1,
  "suspension_flag": 0,
  "email": "student@example.com"
}
```

#### Download Report (Specific Language)
```bash
GET http://localhost:8000/report/{simulation_id}?language=en
GET http://localhost:8000/report/{simulation_id}?language=hi
GET http://localhost:8000/report/{simulation_id}?language=rj
```

#### Download All Reports (ZIP)
```bash
GET http://localhost:8000/report/{simulation_id}/all
```

## 📄 Report Contents

Each PDF report includes:

1. **Student Information**
   - Enrollment number
   - Gender

2. **Academic Performance**
   - Attendance percentage
   - CGPA
   - Number of backlogs
   - 10th and 12th grade marks

3. **Financial & Disciplinary Status**
   - Fees payment status
   - Suspension status

4. **Prediction Results**
   - ML model prediction
   - Final risk level (color-coded)
   - Dropout probability
   - Rule override status

5. **Risk Level Explanations**
   - Detailed description of each risk level

6. **Recommendations**
   - Specific action items based on risk level

## 🗂️ File Structure

```
backend/
├── app/
│   ├── main.py                    # Updated with report endpoints
│   ├── reports/                   # Generated PDF reports
│   │   └── {simulation_id}/
│   │       ├── report_en.pdf
│   │       ├── report_hi.pdf
│   │       └── report_rj.pdf
│   └── services/
│       ├── report_service.py      # PDF generation logic
│       └── email_service.py       # Email sending logic
└── requirements.txt               # Updated with new dependencies
```

## 🧪 Testing

### Test Report Generation
1. Run simulation with Orange or Red risk parameters
2. Check `backend/app/reports/` directory for generated PDFs
3. Verify all 3 language files are created

### Test Email Sending
1. Configure email credentials in `.env`
2. Run simulation with email address
3. Check recipient inbox for email with attachments
4. Verify all 3 PDF files are attached

### Test Report Download
1. Get `report_id` from simulation response
2. Visit: `http://localhost:8000/report/{report_id}?language=en`
3. PDF should download automatically

## 🔧 Troubleshooting

### Reports Not Generating
- Check backend logs for errors
- Verify `backend/app/reports/` directory exists and is writable
- Ensure simulation resulted in Orange or Red risk level

### Email Not Sending
- Verify email configuration in `.env`
- Check Gmail app password is correct
- Review backend logs for email service errors
- Ensure internet connection is available

### PDF Fonts Not Displaying Properly
- Install additional fonts if needed for Hindi/Rajasthani
- Use Unicode-compatible fonts (default Arial should work)

### Report Download 404 Error
- Verify `report_id` is correct
- Check that report files exist in `backend/app/reports/{simulation_id}/`
- Ensure backend server is running

## 🎨 Customization

### Adding More Languages
1. Add translations to `TRANSLATIONS` dict in `report_service.py`
2. Update language validation in `/report` endpoint
3. Add download link in frontend

### Customizing PDF Layout
- Edit `ReportPDF` class in `report_service.py`
- Modify colors in `RISK_COLORS` dict
- Adjust font sizes and spacing

### Customizing Email Template
- Edit HTML template in `send_report_email()` in `email_service.py`
- Update subject line and body content
- Add company logo/branding

## 📧 Email Template Preview

Subject: `Dropout Risk Assessment Report - [Student Name] [Risk Level]`

The email includes:
- Professional HTML formatting
- Color-coded risk level display
- Summary of assessment
- List of attached reports in all languages
- Confidentiality notice

## 🔒 Security Considerations

1. **Email Credentials**: Store securely in `.env`, never commit
2. **Report Cleanup**: Old reports auto-delete after 7 days
3. **Access Control**: Reports accessible only via unique simulation ID
4. **Data Privacy**: Mark reports as confidential

## 📊 Monitoring

### Check Email Service Status
```python
GET http://localhost:8000/health
# Returns email service configuration status
```

### View Report Storage
```bash
ls backend/app/reports/
# Lists all generated report directories
```

### Clean Old Reports Manually
```python
from services.report_service import cleanup_old_reports
cleanup_old_reports(days=7)  # Delete reports older than 7 days
```

## 🎯 Next Steps

1. **Set up email credentials** for production deployment
2. **Test with real student data** to verify report accuracy
3. **Customize PDF template** with institution branding
4. **Set up automated report cleanup** as scheduled task
5. **Monitor email delivery rates** and handle bounces

## 💡 Tips

- Reports are only generated for **Orange** and **Red** risk levels
- Email is **optional** - reports are always available for download
- All 3 languages are generated simultaneously
- Reports are stored for 7 days by default (configurable)
- Use app-specific passwords for Gmail (more secure)

## 🆘 Support

For issues or questions:
1. Check backend logs: `tail -f backend/app.log`
2. Review error messages in browser console
3. Verify all dependencies are installed
4. Ensure environment variables are set correctly

---

**Last Updated**: October 9, 2025
**Version**: 1.0.0
