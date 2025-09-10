# gemini_service.py

import google.generativeai as genai
import json

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def verify_identity_with_gemini(api_key, id_image_bytes, selfie_bytes, input_data):
    configure_gemini(api_key)

    model = genai.GenerativeModel(model_name="gemini-pro-vision")

    prompt = f"""
    Compare the two images above and validate them against this user info:
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
            {"mime_type": "image/jpeg", "data": id_image_bytes},
            {"mime_type": "image/jpeg", "data": selfie_bytes},
            prompt
        ])

        result_text = response.text.strip()

        # Try to extract JSON from the response text
        response_data = json.loads(result_text)

        return {
            "status": response_data.get("verdict", "UNKNOWN"),
            "face_match_score": response_data.get("face_match_score"),
            "document_verified": response_data.get("document_verified"),
            "name_match": response_data.get("name_match"),
            "dob_match": response_data.get("dob_match"),
            "address_match": response_data.get("address_match"),
            "details": response_data
        }

    except Exception as e:
        return {"status": "ERROR", "message": f"Error in processing Gemini response: {str(e)}"}
