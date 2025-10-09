# 🚀 Quick Start - PDF Reports & Email

## Installation (2 minutes)

```bash
# Windows
install_report_features.bat

# Linux/Mac
./install_report_features.sh
```

Or manually:
```bash
cd backend
pip install fpdf2 fastapi-mail aiosmtplib
```

## Email Setup (Optional - 3 minutes)

1. Copy template:
```bash
cd backend
cp .env.example .env
```

2. Edit `.env` and add:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

3. Get Gmail App Password:
- Go to: https://myaccount.google.com/apppasswords
- Enable 2FA first
- Generate app password
- Paste in `.env`

## Usage

### From UI
1. Open simulation page
2. Enter email (optional) at bottom
3. Run simulation
4. For Orange/Red: Download links appear!

### From API
```bash
POST http://localhost:8000/simulate
{
  "attendance": 60,
  "cgpa": 5.5,
  "backlogs": 3,
  "email": "student@example.com"
}
```

## Download Reports

Individual:
- `GET /report/{simulation_id}?language=en`
- `GET /report/{simulation_id}?language=hi`
- `GET /report/{simulation_id}?language=rj`

All (ZIP):
- `GET /report/{simulation_id}/all`

## Features

✅ Automatic PDF generation (Orange/Red only)  
✅ 3 languages: English, Hindi, Rajasthani  
✅ Optional email delivery  
✅ Professional layout  
✅ Color-coded risk levels  
✅ Specific recommendations  

## Testing

1. Run simulation with:
   - Attendance: 60%
   - CGPA: 5.5
   - Backlogs: 3
   - Fees: Unpaid

2. Should result in **Orange** risk

3. Check:
   - ✅ 3 PDFs in `backend/app/reports/`
   - ✅ Download links in UI
   - ✅ Email sent (if configured)

## No Email? No Problem!

Reports work **without email** configuration:
- PDFs still generated
- Download links still appear
- Just no email delivery

## Troubleshooting

### Reports not generating?
- Check backend logs
- Verify simulation is Orange/Red
- Check `backend/app/reports/` exists

### Email not sending?
- Verify `.env` configuration
- Use Gmail App Password (not regular password)
- Check internet connection

### Download 404?
- Copy correct `report_id` from response
- Verify backend is running
- Check files exist

## File Locations

```
backend/
├── app/
│   ├── reports/              # PDFs stored here
│   │   └── sim_*/
│   │       ├── report_en.pdf
│   │       ├── report_hi.pdf
│   │       └── report_rj.pdf
│   └── services/
│       ├── report_service.py
│       └── email_service.py
└── .env                      # Your email config
```

## Need Help?

📖 **Full Guide**: `REPORT_EMAIL_SETUP.md`  
📝 **Summary**: `REPORT_EMAIL_IMPLEMENTATION_SUMMARY.md`  
⚙️ **Config Template**: `backend/.env.example`

## Quick Commands

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start backend
cd backend
python -m uvicorn app.main:app --reload

# Check reports
ls backend/app/reports/

# Test email config (optional)
# Add to main.py test endpoint
```

---

**That's it!** 🎉 You're ready to generate reports!
