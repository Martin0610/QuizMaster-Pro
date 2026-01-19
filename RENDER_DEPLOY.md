# 🚀 Deploy QuizMaster Pro to Render

## One-Click Deploy Steps

1. **Go to [Render.com](https://render.com)** and sign up/login

2. **Click "New +" → "Web Service"**

3. **Connect GitHub** and select: `Martin0610/QuizMaster-Pro`

4. **Configure Service:**
   - **Name:** `quizmaster-pro` (or your preferred name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`

5. **Click "Create Web Service"**

6. **Wait 2-3 minutes** for deployment

7. **Your app is live!** 🎉

## What You Get

✅ **Live Quiz Platform** at your Render URL  
✅ **8 Quiz Categories** with 80+ questions  
✅ **User Registration/Login** system  
✅ **Achievement System** and scoring  
✅ **Mobile-Responsive** design  
✅ **Auto-Database Setup** with sample data  

## Test Your Deployment

1. Visit your Render URL
2. Click "Sign Up" to create account
3. Take a quiz to test functionality
4. Check your dashboard and achievements

## Free Tier Limits

- ✅ **Free hosting** on Render
- ✅ **Custom domain** support
- ✅ **HTTPS** included
- ⚠️ **Sleeps after 15min** of inactivity (free tier)
- ⚠️ **750 hours/month** limit (free tier)

---

**Repository:** https://github.com/Martin0610/QuizMaster-Pro  
**Live Demo:** Your Render URL after deployment