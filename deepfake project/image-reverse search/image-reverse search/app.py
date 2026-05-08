from flask import Flask, request, jsonify, render_template
import requests
import os
import cloudinary
import cloudinary.uploader
from bs4 import BeautifulSoup
import whois
from urllib.parse import urlparse
# API Key
SERP_API_KEY = "03f8b2d7d1b73df8351e995bd920d2272e4d59a8bb27779b010c473993596e20"
#cloudinary credentials
CLOUDINARY_CLOUD_NAME = "durc9i1mb"
CLOUDINARY_API_KEY = "354976945713988"
CLOUDINARY_API_SECRET = "esAJQblV-1TdU73VUDdZYSwGT8g"
UPLOAD_PRESET = "new_try" 
# API URL
SERPAPI_URL = "https://serpapi.com/search"


# Create 'uploads' folder if it doesn't exist
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def upload_to_cloudinary(image_path):
    url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload"
    files = {"file": open(image_path, "rb")}
    data = {"upload_preset": UPLOAD_PRESET}
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        return response.json()["secure_url"]
    else:
        print("Cloudinary Upload Error:", response.text)
        return None

def get_whois_info(url):
    try:
        domain = urlparse(url).netloc
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "updated_date": str(w.updated_date),
            "emails": w.emails,
            "country": w.country
        }
    except Exception as e:
        return {
            "domain": url,
            "registrar": "Unknown",
            "creation_date": "Unknown",
            "expiration_date": "Unknown",
            "updated_date": "Unknown",
            "emails": "Unknown",
            "country": "Unknown"
        }


def get_metadata(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        date = soup.find("meta", {"property": "article:published_time"})
        author = soup.find("meta", {"name": "author"})
        return {
            "date": date["content"] if date else "Unknown",
            "author": author["content"] if author else "Unknown"
        }
    except:
        return {"date": "Unknown", "author": "Unknown"}

def search_google(image_path):

    url = upload_to_cloudinary(image_path)
    print(url)
    """Fetch reverse image search results from Google (SerpAPI)"""
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_reverse_image",
        "image_url": url  # Use hosted image URL
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        print("SerpAPI Response:", response.text)  # Debugging output

        if response.status_code != 200:
            print("SerpAPI Error:", response.text)
            return

        data = response.json()
        results = []

        for result in data.get("image_results", [])[:5]:
            page_url = result.get("link", "")
            title = result.get("title", "No Title")
            thumbnail = result.get("thumbnail", "")

            if page_url:
                metadata = get_metadata(page_url)
                whois_data = get_whois_info(page_url)
                results.append({
                    "link": page_url,
                    "title": title,
                    "thumbnail": thumbnail,
                    "date": metadata["date"],
                    "author": metadata["author"],
                    "whois": whois_data
                })
    
    except Exception as e:
        print("Error fetching SerpAPI results:", e)
        results = []

    return results

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search', methods=['POST'])
def search_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files["image"]
    if image.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save uploaded image
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(image_path)

    # Perform Google reverse image search
    google_results = search_google(image_path)

    return jsonify({"google": google_results})

if __name__ == '__main__':
    app.run(debug=True)
