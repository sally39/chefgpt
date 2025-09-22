# app.py
import os
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

def extract_title(text: str) -> str:
    """
    Try to get a clean recipe title from the model's response.
    1) First non-empty line without markdown bullets/headers
    2) Fallback to a generic title
    """
    if not text:
        return "Recipe"
    # take first non-empty line
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # strip markdown symbols
        line = re.sub(r"^[#*\-•\s]+", "", line)
        # trim trailing punctuation
        line = line.strip(":-•— ")
        if line:
            return line[:120]
    return "Recipe"

@app.route("/", methods=["GET"])
def home():
    # If you’re using a template, render it. Otherwise this shows a simple message.
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify(error="Prompt is required"), 400

    system_msg = "You are ChefGPT, an expert personal chef."
    user_msg = (
        "Generate a complete Indian-friendly recipe matching the request.\n"
        "Return in this structure:\n"
        "Title\n\nIngredients (bulleted)\n\nSteps (numbered)\n\nPrep Time, Cook Time, Servings\n\nTips\n\n"
        f"User request: {prompt}"
    )

    try:
        chat = client.chat.completions.create(
            model="gpt-4o",  # you can switch to gpt-4 / gpt-4o-mini if desired
            temperature=0.8,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        recipe_text = chat.choices[0].message.content
        title = extract_title(recipe_text)
        return jsonify(recipe=recipe_text, title=title)
    except Exception as e:
        return jsonify(error=f"Generation failed: {str(e)}"), 500

@app.route("/generate_image", methods=["POST"])
def generate_image():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify(error="Recipe title required"), 400

    # Build a descriptive, Indian-context food photography prompt
    img_prompt = (
        f"High-resolution, appetizing food photograph of {title}. "
        "Indian cuisine styling, natural lighting, realistic plating, overhead shot."
    )

    try:
        img = client.images.generate(
            model="gpt-image-1",
            prompt=img_prompt,
            size="1024x1024",
        )
        url = img.data[0].url
        return jsonify(image_url=url)
    except Exception as e:
        return jsonify(error=f"Image generation failed: {str(e)}"), 500

if __name__ == "__main__":
    # debug=True is helpful during local dev
    app.run(debug=True)
