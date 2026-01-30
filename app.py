from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os
from datetime import datetime
import pytz
import certifi

app = Flask(__name__)

# MongoDB Config (Atlas Cloud) - Use environment variable in production
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://abhinavsujil1231_db_user:0KptpI0R5CHeyHyI@cluster0.bxzn59r.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = "webhook_db"
COLLECTION_NAME = "events"

try:
    # Use certifi for SSL certificates (fixes Railway/cloud deployment issues)
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    events_collection = db[COLLECTION_NAME]
    client.server_info()
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    events_collection = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup')
@app.route('/setup')
def setup():
    # Get the webhook URL dynamically, forcing HTTPS if in production
    scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
    host = request.headers.get('X-Forwarded-Host', request.host)
    # Railway/Render usually send 'http' but handle SSL, so we prefer https if forwarded
    if 'railway' in host or 'render' in host: 
        scheme = 'https'
        
    webhook_url = f"{scheme}://{host}/webhook"
    return render_template('setup.html', webhook_url=webhook_url)

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    if events_collection is None:
        return jsonify({"error": "Database not connected"}), 500
        
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    event_type = request.headers.get('X-GitHub-Event')
    parsed_event = None
    
    try:
        if event_type == 'push':
            author = data.get('pusher', {}).get('name') or data.get('sender', {}).get('login', 'unknown')
            ref = data.get('ref', '')
            to_branch = ref.split('/')[-1] if ref else 'unknown'
            commit_hash = data.get('after', 'unknown')
            repo_name = data.get('repository', {}).get('full_name', 'unknown')
            
            # Get the commit message from the head commit
            commits = data.get('commits', [])
            head_commit = data.get('head_commit', {})
            commit_message = head_commit.get('message', '') or (commits[0].get('message', '') if commits else '')
            
            parsed_event = {
                "request_id": commit_hash[:7] if commit_hash else 'unknown',
                "author": author,
                "action": "PUSH",
                "from_branch": None,
                "to_branch": to_branch,
                "repo": repo_name,
                "message": commit_message,
                "timestamp": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d %B %Y - %I:%M %p IST")
            }

        elif event_type == 'pull_request':
            action = data.get('action')
            pr = data.get('pull_request', {})
            merged = pr.get('merged', False)
            repo_name = data.get('repository', {}).get('full_name', 'unknown')
            
            if action == 'closed' and merged:
                parsed_event = {
                    "request_id": str(pr.get('number', 'unknown')),
                    "author": pr.get('user', {}).get('login', 'unknown'),
                    "action": "MERGE",
                    "from_branch": pr.get('head', {}).get('ref'),
                    "to_branch": pr.get('base', {}).get('ref'),
                    "repo": repo_name,
                    "timestamp": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d %B %Y - %I:%M %p IST")
                }
            elif action in ['opened', 'reopened']:
                parsed_event = {
                    "request_id": str(pr.get('number', 'unknown')),
                    "author": pr.get('user', {}).get('login', 'unknown'),
                    "action": "PULL_REQUEST",
                    "from_branch": pr.get('head', {}).get('ref'),
                    "to_branch": pr.get('base', {}).get('ref'),
                    "repo": repo_name,
                    "timestamp": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d %B %Y - %I:%M %p IST")
                }
        
        # Fallback for simulation script only (has 'action' in UPPERCASE)
        if not parsed_event and data.get('action') in ['PUSH', 'PULL_REQUEST', 'MERGE']:
            parsed_event = {
                "request_id": data.get('request_id'),
                "author": data.get('author'),
                "action": data.get('action'),
                "from_branch": data.get('from_branch'),
                "to_branch": data.get('to_branch'),
                "repo": data.get('repo', 'simulation'),
                "timestamp": data.get('timestamp') or datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d %B %Y - %I:%M %p IST")
            }

        if parsed_event:
            events_collection.insert_one(parsed_event)
            return jsonify({"status": "success", "event": str(parsed_event.get('_id'))}), 201
        else:
            return jsonify({"status": "ignored", "reason": "Event type not tracked"}), 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    if events_collection is None:
        return jsonify({"error": "Database not connected"}), 500
    try:
        events = list(events_collection.find({}, {'_id': 0}).sort('_id', -1).limit(20))
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_events():
    """Clear all events - useful for demo reset"""
    if events_collection is None:
        return jsonify({"error": "Database not connected"}), 500
    try:
        events_collection.delete_many({})
        return jsonify({"status": "cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
