import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env file (for API key)
load_dotenv()

# Configure API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Choose your model (flash is free-tier friendly)
model = genai.GenerativeModel("gemini-1.5-flash")

# Ask the user for input
prompt = input("What would you like to ask Gemini? ")

# Generate content
response = model.generate_content(prompt)

# Print the response
print("\n" + response.text)
