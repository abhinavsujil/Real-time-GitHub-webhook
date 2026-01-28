# DevStream - GitHub Webhook Dashboard

A real-time dashboard that displays GitHub repository activity (pushes, pull requests, merges).

## 🚀 Live Demo

**Dashboard:** https://githubwebhook.up.railway.app/

## Features

- ✅ Real-time GitHub webhook integration
- ✅ Tracks Push, Pull Request, and Merge events
- ✅ MongoDB Atlas cloud storage
- ✅ Auto-refreshing UI (15-second polling)
- ✅ Modern glassmorphism design

## How It Works

```
GitHub Repo → Webhook Event → Flask Server → MongoDB → Dashboard UI
```

## Quick Setup

### 1. Connect Your Repository

1. Visit `/setup` on the deployed app
2. Copy the webhook URL
3. Go to your GitHub repo → Settings → Webhooks → Add webhook
4. Paste the URL and select "Push" and "Pull requests" events

### 2. Start Making Changes

Push code, open PRs, or merge branches - events appear on the dashboard automatically!

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open http://localhost:5001
```

## Tech Stack

- **Backend:** Python Flask
- **Database:** MongoDB Atlas
- **Frontend:** Vanilla JS with CSS animations
- **Deployment:** Render.com

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/setup` | GET | Setup instructions |
| `/webhook` | POST | Receives GitHub webhooks |
| `/api/events` | GET | Returns latest 20 events |
| `/api/clear` | POST | Clears all events |

## MongoDB Schema

```json
{
    "request_id": "string",
    "author": "string",
    "action": "PUSH | PULL_REQUEST | MERGE",
    "from_branch": "string",
    "to_branch": "string",
    "repo": "string",
    "timestamp": "string"
}
```

## Author

Built by Abhinav for TechStax Developer Assessment
