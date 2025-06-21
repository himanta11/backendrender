# Aspirant - Exam Preparation Platform

A comprehensive exam preparation platform with AI-powered question explanations, mock tests, and PYQ practice.

## Features

- **User Authentication**: Secure JWT-based authentication
- **PYQ Practice**: Previous Year Questions with AI explanations
- **Mock Tests**: Timed mock tests with detailed analytics
- **AI Explanations**: Intelligent question explanations using Together AI
- **Payment Integration**: Razorpay payment gateway for premium features
- **User Limits**: Tier-based usage limits (Free/Pro)
- **Responsive Design**: Mobile-first responsive UI

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Primary database
- **SQLite**: Fallback database
- **JWT**: Authentication
- **Together AI**: AI explanations
- **Razorpay**: Payment processing

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Vanilla JS with ES6+ features
- **Font Awesome**: Icons
- **Canvas Confetti**: Celebrations

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd appbackup
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Run the backend**
   ```bash
   python main.py
   ```

4. **Open frontend**
   - Open `frontend/index.html` in your browser
   - Or serve with a local server

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Frontend: http://localhost
   - API: http://localhost/api
   - Health check: http://localhost/health

## Deployment

### Render Deployment (Recommended)

1. **Push your code to a Git repository**

2. **Deploy using render.yaml (Automatic)**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically deploy using `render.yaml`

3. **Manual Deployment**
   - Create a PostgreSQL database on Render
   - Create a web service pointing to your repository
   - Set environment variables (see `RENDER_DEPLOYMENT.md`)

### Environment Variables

Required for production:
```
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key
TOGETHER_API_KEY=your-together-api-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=false
```

## API Endpoints

### Authentication
- `POST /signup` - User registration
- `POST /token` - User login
- `GET /users/me` - Get current user

### Questions
- `POST /questions/` - Get questions with filters
- `POST /questions/explain` - Get AI explanation

### Payments
- `GET /payment/plans` - Get available plans
- `POST /payment/create-order` - Create payment order
- `POST /payment/verify` - Verify payment

### User Limits
- `GET /user/limits` - Get user limits status
- `POST /user/check-limit/{usage_type}` - Check usage limit
- `POST /user/record-usage/{usage_type}` - Record usage

## Project Structure

```
appbackup/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # Database configuration
│   ├── auth.py              # Authentication logic
│   ├── questions.py         # Questions API
│   ├── payment_service.py   # Payment integration
│   ├── utils.py             # Utility functions
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main page
│   ├── auth.html            # Authentication page
│   ├── pyq.html             # PYQ practice page
│   ├── mocktest.html        # Mock tests page
│   ├── config.js            # API configuration
│   └── auth-utils.js        # Authentication utilities
├── render.yaml              # Render deployment config
├── docker-compose.yml       # Docker configuration
├── Dockerfile               # Docker image
└── README.md                # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For deployment issues, see `RENDER_DEPLOYMENT.md`
For general questions, create an issue in the repository. 