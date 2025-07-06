from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = "mongodb+srv://tanmaygupta200427:Qr3CL9qljyoRxcyW@cluster0.e2b03fv.mongodb.net/webhookDB?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client["webhookDB"]
collection = db["events"]

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'pusher' in data:
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = data['head_commit']['timestamp']
        action = 'push'
        doc = {
            "author": author,
            "action": action,
            "from_branch": None,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
    elif 'pull_request' in data:
        pr = data['pull_request']
        author = pr['user']['login']
        from_branch = pr['head']['ref']
        to_branch = pr['base']['ref']
        timestamp = pr['created_at']
        action = 'merge' if pr.get('merged') else 'pull_request'
        doc = {
            "author": author,
            "action": action,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
    else:
        return jsonify({"message": "Unknown event"}), 400

    collection.insert_one(doc)
    return jsonify({"message": "Event stored"}), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {'_id': 0}))
    return jsonify(events)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
