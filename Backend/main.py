# from pymongo import MongoClient

# mongo_client = MongoClient("mongodb+srv://amitmukherjeecse308:peTpA38Q1A4xyCV8@cluster0.2t23wsj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# db = mongo_client["web_beauty_db"]
# collection = db["Web_Beautifier"]
# mongo_images = list(collection.find({"component_type": "header"}))
# print(mongo_images)



# --- your imports (unchanged) ---
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import asyncio
from playwright.async_api import async_playwright
import json
import uuid
import cv2
import numpy as np
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity
import glob
import cloudinary
import cloudinary.uploader
import requests
import certifi
from pathlib import Path
from pymongo import MongoClient
from urllib.request import urlretrieve
import shutil
import os
from dotenv import load_dotenv
load_dotenv()
# --- your app setup (unchanged) ---
app = Flask(__name__, template_folder="template")
CORS(app)


# --- Cloudinary config (unchanged) ---
cloudinary.config( 
  cloud_name = 'dbjsgdva8', 
  api_key = '721484968887235', 
  api_secret = '02uVqFiSkRwrYJpCfgMkC3beZl8' 
)

# --- MongoDB Atlas config ---
mongo_client = MongoClient(os.getenv("mongodb+srv://amitmukherjeecse308:dCNmVsacubD83Bss@cluster0.u1mkl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"))
db = mongo_client["web_beauty_db"]
collection = db["Web_Beautifier"]
folder_path = "captures/"



# --- LLM AI Config ---
AI_API_URL = os.getenv('URL')
AI_API_KEY = os.getenv('API_KEY')
MODEL = "gpt-3.5-turbo"

# --- upload image to cloudinary ---
def upload_to_cloudinary(image_path):
    response = cloudinary.uploader.upload(image_path)
    return response["secure_url"]

# --- create prompt from data.json ---
def create_ai_prompt(data):
    prompt_template = """As a web design expert, analyze these sections and suggest improvements focusing on:
1. Clarity - Make text instantly understandable
2. Impact - Increase emotional engagement  
3. Brevity - Reduce wordiness without losing meaning
4. Call-to-action - Where applicable

Provide specific suggestions in bullet points for each section.

{content}"""
    
    sections_info = []
    for section in ['header', 'hero', 'footer']:
        if section in data:
            sections_info.append(
                f"👉 {section.upper()} SECTION:\n"
                f"{data[section]['text']}\n"
                f"Current issues: (analyze below)\n"
            )
    
    return prompt_template.format(content="\n".join(sections_info))


# --- fetch text suggestion using OpenAI ---
def get_ai_suggestions(json_path):
    if not os.path.exists(json_path): return None
    with open(json_path, 'r') as f:
        data = json.load(f)
    prompt = create_ai_prompt(data)

    try:
        headers = {
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            AI_API_URL,
            headers=headers,
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        ai_data = response.json()
        return ai_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI Error: {e}")
        return None

# --- capture logic (unchanged) ---
class WebsiteCapture:
    async def capture_sections(self, url, folder_name):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                os.makedirs(f"captures/{folder_name}", exist_ok=True)
                await page.goto(url, wait_until="networkidle", timeout=180000)

                for section in ["header", "hero", "footer"]:
                    element = await self._find_section(page, section)
                    if element:
                        screenshot_path = f"captures/{folder_name}/{section}.png"
                        await element.screenshot(path=screenshot_path)
                        text = await element.inner_text()
                        text = ' '.join(text.split()).strip()[:500]

                        section_data = {
                            "screenshot": screenshot_path,
                            "text": text
                        }

                        with open(f"captures/{folder_name}/{section}.json", "w") as f:
                            json.dump({section: section_data}, f)

                return {"status": "success", "folder": folder_name}
            except Exception as e:
                return {"status": "error", "message": str(e)}
            finally:
                await browser.close()

    async def _find_section(self, page, section_type):
        selectors = {
            "header": ["header", "[role='banner']", ".header", "#header", ".site-header", ".page-header", ".main-header", ".top-header", "nav", ".navbar", ".nav-bar"],
            "hero": [".hero", ".banner", ".jumbotron", "#hero", "#banner", ".hero-section", ".main-banner", ".intro", ".landing-hero", ".top-section", ".hero-container", ".cover", ".splash"],
            "footer": ["footer", "[role='contentinfo']", ".footer", "#footer", ".site-footer", ".page-footer", ".main-footer", ".bottom-footer", ".footer-container"]
        }

        for selector in selectors[section_type]:
            element = await page.query_selector(selector)
            if element and await element.is_visible():
                return element
        return None

# --- VGG + SIFT matching (updated to return score) ---
vgg_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

def extract_vgg_features(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = vgg_model.predict(img_array)
    return features.flatten()

def sift_similarity(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        return 0
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)
    if des1 is None or des2 is None:
        return 0
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(des1, des2)
    return len(matches)

# Modify the find_top_matches function to convert numpy floats to native floats
def find_top_matches(component_type, query_image_path, top_n=3):
    results = []
    query_vgg_features = extract_vgg_features(query_image_path)

    mongo_images = list(collection.find({"component_type": component_type}))
    temp_dir = f"temp_{component_type}"
    os.makedirs(temp_dir, exist_ok=True)

    for item in mongo_images:
        image_url = item.get(f"{component_type}_link")
        if not image_url: continue

        filename = os.path.join(temp_dir, str(uuid.uuid4()) + ".png")
        try:
            urlretrieve(image_url, filename)

            min_sift = 0     # or use the lowest in your dataset
            max_sift = 1000  # or use the highest in your dataset
            
            # Extract features
            db_vgg_features = extract_vgg_features(filename)
            vgg_score = float(cosine_similarity([query_vgg_features], [db_vgg_features])[0][0])  # Convert to native float

            # Compute and normalize sift_score
            sift_score = sift_similarity(query_image_path, filename)
            normalized_sift = (sift_score - min_sift) / (max_sift - min_sift)
            normalized_sift = max(0, min(1, normalized_sift))  # Clamp between 0 and 1

            # Combine scores with appropriate weights
            vgg_weight = 0.6
            sift_weight = 0.4
            combined_score = (vgg_score * vgg_weight + normalized_sift * sift_weight) * 100
            results.append({
                "url": image_url, 
                "score": round(float(combined_score), 2)  # Convert to native float
            })
        except Exception as e:
            print(f"Error processing {image_url}: {e}")
        finally:
            # Clean up temporary files
            if os.path.exists(filename):
                os.remove(filename)

    # Clean up temp directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]

# --- async runner ---
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# --- main route with integrated AI ---

@app.route('/capture', methods=['POST','GET'])
def capture_and_match():
    # Define the main captures folder path
    main_captures_folder = "captures"
    
    # Clean up captures folder before starting
    if os.path.exists(main_captures_folder) and os.path.isdir(main_captures_folder):
        shutil.rmtree(main_captures_folder)
    os.makedirs(main_captures_folder, exist_ok=True)

    data = request.get_json()
    urls = data.get('urls', [])
    if len(urls) != 3:
        return jsonify({"error": "Exactly 3 URLs required"}), 400

    folders = [f"site_{i+1}" for i in range(3)]
    capturer = WebsiteCapture()

    capture_results = []
    final_output = {}

    for url, folder in zip(urls, folders):
        result = run_async(capturer.capture_sections(url, folder))
        capture_results.append({
            "url": url,
            "folder": folder,
            "status": result.get("status", "error"),
            "message": result.get("message", "")
        })

        site_result = {}
        current_site_folder = os.path.join(main_captures_folder, folder)
       
        ai_section_suggestions = {}
        
        for section in ["header", "hero", "footer"]:
            data_json_path = os.path.join(current_site_folder, f"{section}.json")
            llm_text_output = get_ai_suggestions(data_json_path) or ""
            ai_section_suggestions[section] = llm_text_output

        for section in ["header", "hero", "footer"]:
            query_image_path = os.path.join(current_site_folder, f"{section}.png")
            if os.path.exists(query_image_path):
                query_image_url = upload_to_cloudinary(query_image_path)
                top_matches = find_top_matches(section, query_image_path)

                site_result[section] = {
                    "captured_image_url": query_image_url,
                    "top_matches": top_matches,
                    "suggested_text": ai_section_suggestions.get(section, "")
                }

        final_output[folder] = site_result
    
    return jsonify({
        "capture_results": capture_results,
        "matching_results": final_output
    })

# --- start ---
if __name__ == '__main__':

    os.makedirs("captures", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
