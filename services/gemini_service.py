# kyc/services/gemini_service.py

import google.generativeai as genai
import json
import re

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    else:
        raise ValueError("No valid JSON object found in Gemini response.")

def verify_identity_with_gemini(api_key, id_image_bytes, selfie_bytes, input_data, id_mime_type="image/jpeg"):
    configure_gemini(api_key)
    model = genai.GenerativeModel(model_name="gemini-pro-vision")

    prompt = f"""
    Compare the two images and validate them against this user info:
    Full Name: {input_data["full_name"]}
    Date of Birth: {input_data["dob"]}
    ID Number: {input_data["id_number"]}
    Address: {input_data["address"]}
    Document Type: {input_data["doc_type"]}

    Instructions:
    - Determine if the two images belong to the same person.
    - Check if the ID document appears valid and matches the provided data.
    - Return the result as a JSON with:
        - face_match_score (0-100),
        - document_verified (true/false),
        - name_match (true/false),
        - dob_match (true/false),
        - address_match (true/false),
        - verdict: "APPROVED" or "REJECTED".
    """

    try:
        response = model.generate_content([
            {"mime_type": id_mime_type, "data": id_image_bytes},
            {"mime_type": "image/jpeg", "data": selfie_bytes},
            prompt
        ])

        result_text = response.text.strip()
        response_data = extract_json(result_text)

        return {
            "status": response_data.get("verdict", "UNKNOWN"),
            "face_match_score": response_data.get("face_match_score"),
            "document_verified": response_data.get("document_verified"),
            "name_match": response_data.get("name_match"),
            "dob_match": response_data.get("dob_match"),
            "address_match": response_data.get("address_match"),
            "details": {
                **input_data,
                **response_data
            }
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Error processing Gemini response: {str(e)}"
        }
