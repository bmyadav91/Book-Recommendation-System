import os, sys
import requests
from src.exception import CustomException
from src.logger import logging


def GenerateDescription(prompt):
    try:
        api_key = os.getenv("GOOGLE_GEMINI_API")
        genai_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        
        # Prepare the JSON payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        # Make the POST request
        response = requests.post(genai_url, json=payload)
        response.raise_for_status()
        # Parse the response
        data = response.json()
        if "candidates" in data and data["candidates"]:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            content = content.replace("*", "")
            return content
        else:
            return None

    except requests.exceptions.RequestException as re:
        logging.error(f"Error in RequestException: {str(re)}")
        raise CustomException("rror in RequestException: ", sys)

    except Exception as e:
        logging.error(f"Error while generating description: {str(e)}")
        raise CustomException("Error while genrate description with gemini: ", sys)
    