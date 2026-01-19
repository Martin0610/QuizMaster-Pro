# 🎮 QuizMaster Pro

An advanced quiz platform with beautiful UI/UX and comprehensive features.

## ✨ Features
- 🧪 **8 Quiz Categories** - Science, Programming, History, Sports, Food, Movies, Music, General Knowledge
- 👤 **User System** - Registration, login, profiles, and progress tracking
- 🏆 **Achievements** - Unlock badges and track your quiz mastery
- 📊 **Real-time Scoring** - Instant feedback with detailed explanations
- 📱 **Mobile Responsive** - Perfect experience on any device
- 🎨 **Modern UI** - Beautiful animations and smooth interactions

## 🚀 Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. **Fork this repository** to your GitHub account
2. **Go to [Render.com](https://render.com)** and create account
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub** and select this repository
5. **Deploy automatically** - Render will use the included configuration
6. **Access your live app** in 2-3 minutes!

## 🛠️ Local Development

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
pip install flask
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Access the Application
Open your web browser and go to:
```
http://localhost:5000
```

## 📋 Detailed Setup Instructions

### 1. Check Python Installation
```bash
python --version
```
If Python is not installed, download it from [python.org](https://python.org)

### 2. Install Flask
```bash
pip install flask
```

### 3. Navigate to Project Directory
```bash
cd path/to/your/quizmaster-project
```

### 4. Run the Application
```bash
python app.py
```

You should see output like:
```
============================================================
  🎮 QuizMaster Pro - Advanced Quiz Platform
============================================================

  🌐 Access at: http://localhost:5000
  🎯 Features: Quizzes, Leaderboards, Achievements
  🎨 Beautiful UI with animations and effects
  📱 Mobile-responsive design

============================================================
```

## 🎯 How to Use

### First Time Setup
1. **Start the application** using `python app.py`
2. **Open your browser** and go to `http://localhost:5000`
3. **Create an account** by clicking "Sign Up"
4. **Login** with your credentials
5. **Start taking quizzes** from the dashboard

### Features Available
- **Dashboard**: View your stats, recent games, and achievements
- **Categories**: Browse quizzes by category (Science, Programming, History, etc.)
- **Quiz Taking**: Interactive quiz interface with timer and scoring
- **Results**: Detailed results with explanations for each question
- **Achievements**: Unlock achievements as you play

## 🗂️ Project Structure
```
quizmaster-pro/
├── app.py                 # Main Flask application
├── quizmaster.db         # SQLite database (auto-created)
├── templates/            # HTML templates
│   ├── base.html
│   ├── landing.html
│   ├── auth.html
│   ├── dashboard.html
│   ├── category.html
│   ├── quiz.html
│   └── quiz_results.html
├── static/               # CSS, JS, and images
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
└── html_version/         # Standalone HTML version
    └── index.html
```

## 🔧 Troubleshooting

### Common Issues

**1. "Module not found" error**
```bash
pip install flask
```

**2. Port already in use**
The app runs on port 5000 by default. If it's busy, the app will show an error. Stop other applications using port 5000 or modify the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

**3. Database issues**
If you encounter database errors, delete `quizmaster.db` and restart the app. It will recreate the database with sample data.

**4. Permission errors**
Make sure you have write permissions in the project directory for the SQLite database.

## 🎮 Demo Account
The application will automatically create sample data including:
- 8 quiz categories
- Multiple quizzes per category
- Sample questions and answers
- Achievement system

## 🛠️ Development Mode
The app runs in debug mode by default, which means:
- Automatic reloading when you make changes
- Detailed error messages
- Debug toolbar available

## 📱 Mobile Access
The application is mobile-responsive. You can access it from your phone by:
1. Make sure your phone and computer are on the same network
2. Find your computer's IP address
3. Access `http://YOUR_IP_ADDRESS:5000` from your phone

## 🔒 Security Note
This is a development setup. For production use, you should:
- Change the secret key in `app.py`
- Use proper password hashing
- Use a production WSGI server like Gunicorn
- Set up proper database security

## 📞 Need Help?
If you encounter any issues:
1. Check that Python and Flask are properly installed
2. Ensure you're in the correct directory
3. Check the console output for error messages
4. Make sure port 5000 is available

Enjoy your QuizMaster Pro experience! 🎉