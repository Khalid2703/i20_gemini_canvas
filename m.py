from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words",
)

print(response.text)

#AIzaSyDn8qVqu6Sqhv-_agnP2A18JTPq-4Fp4AM