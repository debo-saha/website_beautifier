from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from playwright.async_api import async_playwright
import json
import os
import uuid
import cv2
import numpy as np
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity
import cloudinary
import cloudinary.uploader
import requests
from urllib.request import urlretrieve
from pymongo import MongoClient
import shutil
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD'),
    api_key=os.getenv('CLOUDINARY_KEY'),
    api_secret=os.getenv('CLOUDINARY_SECRET')
)

# MongoDB config
mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client["web_beauty_db"]
collection = db["Web_Beautifier"]

# AI config
AI_API_URL = "https://api.openai.com/v1/chat/completions"
AI_API_KEY = os.getenv('API_KEY')
MODEL = "gpt-3.5-turbo"

# Initialize VGG16 model
vgg_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

class WebsiteCapture:
    async def capture_sections(self, url, folder_name):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
            )
            page = await context.new_page()
            
            try:
                os.makedirs(f"captures/{folder_name}", exist_ok=True)
                
                # Load the page
                await self._load_page_with_retries(page, url)
                
                # Capture and save each section separately
                sections = {
                    "header": await self._capture_section(page, "header", folder_name),
                    "hero": await self._capture_hero_section(page, folder_name),
                    "footer": await self._capture_section(page, "footer", folder_name)
                }
                
                # Save each section to separate JSON files
                for section_name, section_data in sections.items():
                    if section_data:
                        with open(f"captures/{folder_name}/{section_name}_data.json", "w") as f:
                            json.dump(section_data, f)
                
                return {
                    "status": "success",
                    "folder": folder_name,
                    "sections": {k: v is not None for k, v in sections.items()}
                }
            
            except Exception as e:
                return {"status": "error", "message": str(e)}
            finally:
                await browser.close()

    async def _load_page_with_retries(self, page, url, timeout=60000):
        try:
            await page.goto(url, wait_until="networkidle", timeout=timeout)
        except:
            try:
                await page.goto(url, wait_until="load", timeout=timeout)
            except:
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout)

    async def _capture_section(self, page, section_type, folder_name):
        selectors = {
            "header": ["header", "[role='banner']", ".header", "#header"],
            "footer": ["footer", "[role='contentinfo']", ".footer", "#footer"]
        }
        
        for selector in selectors[section_type]:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    box = await element.bounding_box()
                    if box and box['width'] > 50 and box['height'] > 20:
                        path = f"captures/{folder_name}/{section_type}.png"
                        await element.screenshot(path=path)
                        return {
                            "screenshot": path,
                            "text": await self._clean_text(element),
                            "dimensions": box
                        }
            except:
                continue
        return None

    async def _capture_hero_section(self, page, folder_name):
        hero_selectors = [
            ".hero", ".banner", ".jumbotron", "#hero", "#banner",
            ".hero-section", ".main-banner", ".intro", ".landing-hero"
        ]
        
        for selector in hero_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    box = await element.bounding_box()
                    if box and box['width'] > 300 and box['height'] > 200:
                        path = f"captures/{folder_name}/hero.png"
                        await element.screenshot(path=path)
                        return {
                            "screenshot": path,
                            "text": await self._clean_text(element),
                            "dimensions": box
                        }
            except:
                continue
        
        # Fallback to largest section at top
        sections = await page.query_selector_all("section, div, main")
        hero_candidate = None
        max_area = 0
        
        for section in sections:
            if await section.is_visible():
                box = await section.bounding_box()
                if box:
                    area = box['width'] * box['height']
                    if box['y'] < 500 and area > max_area and area > 100000:
                        max_area = area
                        hero_candidate = section
        
        if hero_candidate:
            path = f"captures/{folder_name}/hero.png"
            await hero_candidate.screenshot(path=path)
            return {
                "screenshot": path,
                "text": await self._clean_text(hero_candidate),
                "dimensions": await hero_candidate.bounding_box(),
                "is_fallback": True
            }
        
        return None

    async def _clean_text(self, element):
        text = await element.inner_text()
        return ' '.join(text.split()).strip()[:1000]

def upload_to_cloudinary(image_path):
    try:
        response = cloudinary.uploader.upload(image_path)
        return response["secure_url"]
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None

def create_ai_prompt(section_data):
    prompt_template = """Analyze this website section and suggest improvements:
    
Section Text:
{text}

Focus on:
1. Clarity
2. Visual hierarchy  
3. Call-to-action effectiveness
4. Mobile responsiveness

Provide specific suggestions:"""
    
    return prompt_template.format(text=section_data.get('text', ''))

def get_ai_suggestions(section_data):
    try:
        prompt = create_ai_prompt(section_data)
        
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
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def extract_vgg_features(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        features = vgg_model.predict(img_array)
        return features.flatten()
    except Exception as e:
        print(f"VGG feature extraction error: {e}")
        return None

def find_top_matches(component_type, query_image_path, top_n=3):
    results = []
    query_vgg_features = extract_vgg_features(query_image_path)
    if query_vgg_features is None:
        return []

    mongo_images = list(collection.find({"component_type": component_type}))
    temp_dir = f"temp_{component_type}"
    os.makedirs(temp_dir, exist_ok=True)

    for item in mongo_images:
        image_url = item.get(f"{component_type}_link")
        if not image_url: continue

        filename = os.path.join(temp_dir, str(uuid.uuid4()) + ".png")
        try:
            urlretrieve(image_url, filename)

            db_vgg_features = extract_vgg_features(filename)
            if db_vgg_features is None:
                continue

            similarity = float(cosine_similarity([query_vgg_features], [db_vgg_features])[0][0])
            results.append({
                "url": image_url, 
                "score": round(similarity * 100, 2)
            })
        except Exception as e:
            print(f"Error processing {image_url}: {e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/capture', methods=['POST'])
def capture_and_match():
    data = request.get_json()
    urls = data.get('urls', [])
    
    if len(urls) != 3:
        return jsonify({"error": "Exactly 3 URLs required"}), 400
    
    # Clean previous captures
    if os.path.exists("captures"):
        shutil.rmtree("captures")
    os.makedirs("captures", exist_ok=True)
    
    folders = [f"site_{i+1}" for i in range(3)]
    capturer = WebsiteCapture()
    
    all_results = []
    
    for url, folder in zip(urls, folders):
        try:
            # Capture website sections
            capture_result = run_async(capturer.capture_sections(url, folder))
            if capture_result["status"] != "success":
                all_results.append({
                    "url": url,
                    "status": "error",
                    "message": capture_result.get("message", "Capture failed")
                })
                continue
            
            folder_path = f"captures/{folder}"
            sections_data = {}
            
            # Process each section from its separate JSON file
            for section in ["header", "hero", "footer"]:
                json_path = f"{folder_path}/{section}_data.json"
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        section_data = json.load(f)
                    
                    # Upload image to Cloudinary
                    cloudinary_url = upload_to_cloudinary(section_data["screenshot"])
                    
                    # Get matches and suggestions
                    matches = find_top_matches(section, section_data["screenshot"])
                    ai_suggestions = get_ai_suggestions(section_data)
                    
                    sections_data[section] = {
                        "image_url": cloudinary_url,
                        "text_content": section_data.get("text", ""),
                        "top_matches": matches,
                        "suggestions": ai_suggestions or "No suggestions available"
                    }
            
            all_results.append({
                "url": url,
                "status": "success",
                "sections": sections_data
            })
        
        except Exception as e:
            all_results.append({
                "url": url,
                "status": "error",
                "message": str(e)
            })

    return jsonify({"results": all_results})

if __name__ == '__main__':
    os.makedirs("captures", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)