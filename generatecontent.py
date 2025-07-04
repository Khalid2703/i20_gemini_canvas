from google import genai

prompt=input("Enter your prompt:")
client = genai.Client(api_key="AIzaSyDn8qVqu6Sqhv-_agnP2A18JTPq-4Fp4AM")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt
)
print(response.text)