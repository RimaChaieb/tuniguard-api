# 🛡️ TuniGuard - AI Telecom Security Platform

Advanced AI-powered threat detection system for Tunisian telecom networks. Detects SMS phishing, payment scams, and other cyber threats using Google Gemini AI.

## ✨ Features

- 🔍 **AI-Powered Detection** - Uses Google Gemini AI for threat analysis
- 📱 **Multi-Content Type** - SMS, Calls, App Messages
- 🌍 **Regional Tracking** - Track threats by region and carrier
- 📊 **Analytics Dashboard** - Real-time threat statistics
- 💬 **AI Chatbot** - Interactive threat explanation
- 🔐 **JWT Authentication** - Secure user accounts
- 📈 **Threat Intelligence** - Trend analysis and forecasting
- 🇹🇳 **Tunisia-Specific** - 15 localized threat types

## 🏗️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite
- **Authentication**: JWT (Flask-JWT-Extended)
- **AI**: Google Gemini 2.5 Flash
- **ORM**: SQLAlchemy

### Frontend
- **HTML5/CSS3/JavaScript**
- **Responsive Design**
- **REST API Integration**

### DevOps
- **Docker & Docker Compose**
- **Render.com Deployment**

## 📊 Database Models

- **User** - User accounts with regional tracking
- **Threat** - 15 Tunisia-specific threat catalog
- **Scan** - Individual threat detections
- **Conversation** - AI chatbot history
- **ThreatIntel** - Aggregated threat intelligence
- **APIMetric** - Performance monitoring

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/tuniguard-api.git
cd tuniguard-api

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# Initialize database
python tuniguard/init_db.py

# Run server
python run.py
```

Server runs on: http://localhost:5000

### Docker

```bash
# Build and run
docker-compose up --build

# Access at http://localhost:5000
```

## 📚 API Endpoints

### Authentication
- `POST /api/register` - Create account
- `POST /api/login` - Login
- `POST /api/logout` - Logout
- `POST /api/refresh` - Refresh token

### Threat Detection
- `POST /api/scan` - Scan message for threats
- `GET /api/threats` - List all threat types
- `GET /api/threats/trending` - Trending threats

### Analytics
- `GET /api/analytics/national` - National dashboard
- `GET /api/analytics/stats` - User statistics
- `GET /api/threats/regional-dashboard` - Regional threats

### Chat
- `POST /api/chat` - Send chat message
- `GET /api/chat/history/<scan_id>` - Conversation history

## 🔐 Security

- ✅ Bcrypt password hashing
- ✅ JWT authentication
- ✅ GDPR compliant (data export/deletion)
- ✅ Anonymized user tracking
- ✅ HTTPS ready
- ✅ Rate limiting

## 📋 Requirements

- Python 3.11+
- Docker (optional)
- Google Gemini API key

## 🔑 Environment Variables

See `.env.example` for all variables. Required:

```
GEMINI_API_KEY=your_key_here
FLASK_ENV=production
SECRET_KEY=your_secret_here
```

## 📖 Documentation

API documentation available at: `/api/docs` (Swagger)

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - See LICENSE file

## 👤 Author

Created for Tunisia's telecom security

## 🙏 Acknowledgments

- Google Gemini AI
- Flask Community
- Render.com

---

**Status**: Production Ready ✅

For issues or questions: Create GitHub Issue