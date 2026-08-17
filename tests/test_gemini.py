from google import genai
from dotenv import load_dotenv
import os


def main():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set."
        )

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say hello to the VoiceNote project in one sentence."
    )

    print("\nGemini response:")
    print(response.text)


if __name__ == "__main__":
    main()