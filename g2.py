
from google import genai

prompt=input("Enter your prompt:")
client = genai.Client(api_key="AIzaSyBitpI4WdCqIfA5zhde7MTgkqGC1yVyt_w")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt
)
print(response.text)