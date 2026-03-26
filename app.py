import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from generator import generate_welcome_kit
from brevo_utils import BrevoManager
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
DIST_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
brevo = BrevoManager()

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'builder.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email')
        if not email:
            return jsonify({"error": "Email is required"}), 400

        # 1. Generate the Welcome Kit locally
        print(f"🛠️ Generating kit for: {data.get('property_name')}")
        dist_path = generate_welcome_kit(data)
        
        # 2. Sync lead to Brevo
        print(f"📧 Syncing lead to Brevo: {email}")
        brevo_res = brevo.add_contact(email)
        
        return jsonify({
            "status": "success",
            "message": "Kit généré et lead synchronisé !",
            "preview_url": f"/dist/{data.get('property_name').replace(' ', '')}/index.html",
            "brevo_status": "synced" if brevo_res else "failed_sync"
        })

    except Exception as e:
        print(f"❌ Error during generation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory(DIST_BASE_DIR, path)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
