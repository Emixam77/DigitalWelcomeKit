import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from generator import generate_welcome_kit
from brevo_utils import BrevoManager
from ftp_utils import FTPManager
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
DIST_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
BASE_URL = os.getenv("BASE_WEB_URL", "https://mapvitrine.com/welcome")
brevo = BrevoManager()
ftp = FTPManager()

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
        prop_name_clean = data.get('property_name', 'rental').replace(' ', '')
        
        # 1. Generate the Welcome Kit locally
        print(f"🛠️ Phase 1: Generating kit locally for {prop_name_clean}")
        dist_path = generate_welcome_kit(data)
        
        # 2. Upload to FTP for Persistence
        print(f"📡 Phase 2: Uploading to FTP (mapvitrine.com)")
        local_kit_dir = os.path.join(DIST_BASE_DIR, prop_name_clean)
        ftp_success = ftp.upload_directory(local_kit_dir, prop_name_clean)
        
        # Construct permanent URL
        permanent_url = f"{BASE_URL}/{prop_name_clean}/index.html"
        
        # 3. Sync lead to Brevo with permanent KIT_URL attribute
        print(f"📧 Phase 3: Syncing lead to Brevo with KIT_URL: {permanent_url}")
        attributes = {
            "KIT_URL": permanent_url,
            "PRENOM": prop_name_clean # Fallback for greeting
        }
        brevo_res = brevo.add_contact(email, attributes=attributes)
        
        return jsonify({
            "status": "success",
            "message": "Kit généré, stocké sur FTP et synchronisé avec Brevo !",
            "preview_url": permanent_url,
            "ftp_status": "synced" if ftp_success else "failed",
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
