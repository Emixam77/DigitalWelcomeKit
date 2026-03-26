import os
import qrcode
import shutil
import argparse

def generate_welcome_kit(data):
    """
    Generates a personalized welcome kit folder.
    """
    prop_name = data.get('property_name', 'Mon Logement')
    safe_name = "".join(x for x in prop_name if x.isalnum())
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist", safe_name)
    template_path = os.path.join(base_dir, "templates", "index.html")
    
    os.makedirs(dist_dir, exist_ok=True)
    
    # 1. Generate QR Codes
    # 1a. Page URL QR Code
    final_url = f"https://mapvitrine.com/welcome/{safe_name}"
    qr_page = qrcode.QRCode(version=1, box_size=10, border=5)
    qr_page.add_data(final_url)
    qr_page.make(fit=True)
    img_page = qr_page.make_image(fill_color="black", back_color="white")
    img_page.save(os.path.join(dist_dir, "qrcode_page.png"))
    
    # 1b. Wi-Fi Direct Connect QR Code
    ssid = data.get('wifi_ssid', 'WIFI_FREE')
    password = data.get('wifi_pass', 'password123')
    wifi_data = f"WIFI:S:{ssid};T:WPA;P:{password};;"
    qr_wifi = qrcode.QRCode(version=1, box_size=10, border=5)
    qr_wifi.add_data(wifi_data)
    qr_wifi.make(fit=True)
    img_wifi = qr_wifi.make_image(fill_color="black", back_color="white")
    img_wifi.save(os.path.join(dist_dir, "qrcode_wifi.png"))
    
    # 2. Render Template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prepare Map Embed
    maps_key = os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY")
    encoded_addr = data.get('address', 'Paris').replace(' ', '+')
    map_url = f"https://www.google.com/maps/embed/v1/place?key={maps_key}&q={encoded_addr}"
    
    # Prepare Restaurants List HTML with Google Maps links
    restaurants = data.get('restaurants', [])
    restos_html = ""
    for r in restaurants:
        name = r.get("name", "Lieu utile")
        addr = r.get("address", "")
        # Create a Google Maps Search Link
        gmaps_link = f"https://www.google.com/maps/search/?api=1&query={name.replace(' ', '+')}+{addr.replace(' ', '+')}"
        
        restos_html += f"""
        <a href="{gmaps_link}" target="_blank" class="flex justify-between items-center bg-white/40 p-3 rounded-xl text-sm border border-white/50 hover:bg-indigo-50 transition-colors shadow-sm">
            <span class="font-bold text-indigo-900">📍 {name}</span>
            <span class="opacity-40 italic text-[10px] ml-2 truncate max-w-[150px]">{addr}</span>
            <i data-lucide="external-link" class="w-3 h-3 ml-2 opacity-30"></i>
        </a>"""
    
    # Capture Email (Simulated for Brevo integration)
    email = data.get('email', 'non-renseigné')
    print(f"📧 Prospect Email Captured: {email}")
    
    placeholders = {
        "{{PROPERTY_NAME}}": prop_name,
        "{{WIFI_SSID}}": data.get('wifi_ssid', 'WIFI_FREE'),
        "{{WIFI_PASSWORD}}": data.get('wifi_pass', 'password123'),
        "{{ARRIVAL_INSTRUCTIONS}}": data.get('instructions', 'Les clés sont dans la boîte.').replace('\n', '<br>'),
        "{{MAP_EMBED_URL}}": map_url,
        "{{RESTAURANTS_LIST}}": restos_html,
        "{{HOST_PHONE}}": data.get('host_phone', '06 00 00 00 00')
    }
    
    for key, value in placeholders.items():
        content = content.replace(key, str(value))
    
    # 3. Save Final HTML
    output_path = os.path.join(dist_dir, "index.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"✅ Kit de Bienvenue généré avec succès pour {prop_name} !")
    print(f"📍 Emplacement : {dist_dir}")
    return dist_dir

if __name__ == "__main__":
    # Mock data for v3 testing
    test_data = {
        "property_name": "Le Mas des Glycines",
        "address": "Sarlat-la-Canéda, France",
        "wifi_ssid": "GLYCINES_GUEST",
        "wifi_pass": "vacances2026",
        "host_phone": "06 12 34 56 78",
        "email": "contact@prospect-immobilier.fr",
        "instructions": "Le digicode du portail est le 1234.\nLa clé se trouve dans le boîtier à gauche de la porte d'entrée (code 0808).",
        "restaurants": [
            {"name": "Le Grand Bleu", "address": "Sarlat-la-Canéda"},
            {"name": "L'Adresse", "address": "Place de la Liberté, Sarlat"},
            {"name": "Côté Jardin", "address": "Sarlat Centre"}
        ]
    }
    generate_welcome_kit(test_data)
