# Deployment Instructions

## Deploy to Render.com (Free Tier)

### 1. Prerequisites
- Push code to your GitHub repo
- Get Groq API key from https://console.groq.com (free tier)

### 2. Create Render Account
1. Go to https://render.com and sign up
2. Connect your GitHub account

### 3. Deploy Service
1. Click "New+" → "Web Service"
2. Select your `rag-portfolio` GitHub repo
3. Configure:
   - **Name**: `rag-portfolio-backend`
   - **Runtime**: `Docker`
   - **Branch**: `master`
   - **Build Command**: (leave empty, uses Dockerfile)
   - **Start Command**: (leave empty, uses Dockerfile CMD)
   - **Plan**: Free
4. Add Environment Variable:
   - **Key**: `GROQ_API_KEY`
   - **Value**: Your Groq API key
5. Click "Deploy"

### 4. After Deployment
- Render will show you the service URL (e.g., `https://rag-portfolio-backend.onrender.com`)
- Update your frontend with this URL
- First request will have ~10-15s cold start (acceptable)
- Subsequent requests will be instant

### 5. Testing Deployment
```bash
# Health check
curl https://rag-portfolio-backend.onrender.com/health

# Suggested questions
curl https://rag-portfolio-backend.onrender.com/suggested-questions

# Chat query
curl -X POST https://rag-portfolio-backend.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Tell me about IncidentCopilot"}'
```

## Frontend Integration

Update your Vercel frontend to use the backend:

### 1. Health Check on Page Load
```javascript
// On component mount
useEffect(() => {
  fetch('https://rag-portfolio-backend.onrender.com/health')
    .then(() => console.log('Backend warmed up'))
    .catch(err => console.log('Backend warming up...'))
}, [])
```

### 2. Fetch Suggested Questions
```javascript
const fetchQuestions = async () => {
  const res = await fetch('https://rag-portfolio-backend.onrender.com/suggested-questions')
  const data = await res.json()
  return data.questions
}
```

### 3. Chat with Streaming
```javascript
const chat = async (message) => {
  const res = await fetch('https://rag-portfolio-backend.onrender.com/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  })
  
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    const text = decoder.decode(value)
    const lines = text.split('\n')
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const token = line.slice(6)
        console.log(token) // stream to UI
      }
    }
  }
}
```

## Monitoring & Debugging

### View Logs
On Render dashboard, click service → "Logs" to see real-time logs

### Common Issues
- **GROQ_API_KEY not set**: Check environment variables in Render settings
- **Cold start slow**: This is expected on free tier, will warm up after first request
- **CORS errors**: Verify frontend is making requests to `https://` (not `http://`)

## Cost Breakdown
- **Render.com**: Free tier (shared CPU, 0.5GB RAM)
- **Groq API**: Free tier (~500 req/day for portfolio scale)
- **Total**: $0/month until you exceed free tier limits

## Scaling Up
If you need to always-on (no cold starts):
- Upgrade to Render paid tier: $7/month (Pro instance)
- Or use Railway/Replit which have different free tier benefits
