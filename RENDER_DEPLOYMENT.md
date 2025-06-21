# Render Deployment Guide

This guide will help you deploy the Aspirant backend to Render.

## Prerequisites

1. A Render account (free tier available)
2. Your code pushed to a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Repository

Make sure your repository has the following files:
- `render.yaml` - Render configuration
- `runtime.txt` - Python version specification
- `build.sh` - Build script
- `start.sh` - Start script
- `backend/requirements.txt` - Python dependencies
- `backend/main.py` - FastAPI application

## Step 2: Deploy to Render

### Option A: Using render.yaml (Recommended)

1. **Connect your repository:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" and select "Blueprint"
   - Connect your Git repository
   - Render will automatically detect the `render.yaml` file

2. **Deploy:**
   - Render will create both the web service and database
   - The deployment will start automatically
   - Monitor the build logs for any issues

### Option B: Manual Deployment

1. **Create a PostgreSQL database:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" and select "PostgreSQL"
   - Choose "Starter" plan (free)
   - Note down the database URL

2. **Create a web service:**
   - Click "New +" and select "Web Service"
   - Connect your Git repository
   - Configure the service:
     - **Name:** `aspirant-backend`
     - **Environment:** `Python`
     - **Build Command:** `pip install -r backend/requirements.txt`
     - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
     - **Plan:** `Starter` (free)

3. **Set environment variables:**
   - Go to your web service settings
   - Add the following environment variables:
     ```
     DATABASE_URL=<your-postgresql-url-from-step-1>
     SECRET_KEY=<generate-a-secure-secret-key>
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     TOGETHER_API_KEY=39b58efc9f06bc95aeb6a246badf5561100d6247136a4cd33bc6f2c96cc9d6bf
     ENVIRONMENT=production
     DEBUG=false
     LOG_LEVEL=INFO
     ```

## Step 3: Configure Environment Variables

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `SECRET_KEY` | JWT secret key | `your-super-secret-key-here` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `TOGETHER_API_KEY` | Together AI API key | `your-together-api-key` |
| `ENVIRONMENT` | Environment name | `production` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Optional Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `RAZORPAY_KEY_ID` | Razorpay key ID | `rzp_test_...` |
| `RAZORPAY_KEY_SECRET` | Razorpay secret key | `your-razorpay-secret` |

## Step 4: Update Frontend Configuration

After deployment, update your frontend's `config.js` file with the new backend URL:

```javascript
const API_CONFIG = {
    baseUrl: 'https://your-app-name.onrender.com',  // Replace with your Render URL
    // ... rest of config
};
```

## Step 5: Test Your Deployment

1. **Health Check:**
   - Visit: `https://your-app-name.onrender.com/health`
   - Should return: `{"status": "healthy", "timestamp": "...", "version": "1.0.0"}`

2. **API Documentation:**
   - Visit: `https://your-app-name.onrender.com/docs`
   - Should show FastAPI automatic documentation

3. **Test Endpoints:**
   - Test signup: `POST https://your-app-name.onrender.com/signup`
   - Test login: `POST https://your-app-name.onrender.com/token`

## Troubleshooting

### Common Issues

1. **Build Failures:**
   - Check the build logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version in `runtime.txt`

2. **Database Connection Issues:**
   - Verify `DATABASE_URL` environment variable
   - Check if PostgreSQL service is running
   - Ensure database credentials are correct

3. **CORS Issues:**
   - Update CORS origins in `main.py` to include your frontend domain
   - Check browser console for CORS errors

4. **Environment Variables:**
   - Ensure all required environment variables are set
   - Check for typos in variable names
   - Restart the service after adding new variables

### Logs and Monitoring

- **View Logs:** Go to your service dashboard and click "Logs"
- **Real-time Logs:** Use the "Live" tab for real-time log monitoring
- **Metrics:** Monitor CPU, memory, and request metrics in the dashboard

## Performance Optimization

1. **Database Connection Pooling:**
   - The current setup uses SQLAlchemy's default connection pooling
   - For high traffic, consider adjusting pool settings

2. **Caching:**
   - Consider adding Redis for caching frequently accessed data
   - Implement response caching for static content

3. **CDN:**
   - Use a CDN for static assets
   - Consider Cloudflare for additional performance

## Security Considerations

1. **Environment Variables:**
   - Never commit sensitive data to your repository
   - Use Render's environment variable feature
   - Rotate secrets regularly

2. **HTTPS:**
   - Render automatically provides HTTPS
   - Ensure your frontend also uses HTTPS

3. **Rate Limiting:**
   - Consider implementing rate limiting for API endpoints
   - Monitor for abuse and implement protection

## Scaling

1. **Free Tier Limits:**
   - Free tier has limitations on requests and compute time
   - Consider upgrading for production use

2. **Upgrading Plans:**
   - Starter: $7/month - Good for development and small production
   - Standard: $25/month - Better for production workloads
   - Pro: $85/month - High-performance production

## Support

- **Render Documentation:** [https://render.com/docs](https://render.com/docs)
- **Render Support:** [https://render.com/support](https://render.com/support)
- **FastAPI Documentation:** [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

## Next Steps

After successful deployment:

1. Set up monitoring and alerting
2. Configure custom domain (optional)
3. Set up CI/CD for automatic deployments
4. Implement backup strategies for your database
5. Set up logging aggregation 