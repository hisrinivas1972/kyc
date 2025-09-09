import google.generativeai as genai
import base64
import json

def configure_gemini(api_key):
    """Configure the Gemini API with the provided API key."""
    genai.configure(api_key=api_key)

def verify_identity_with_gemini(api_key, id_image_bytes, selfie_bytes, input_data):
    """Verify identity using Gemini AI, processing ID image, selfie, and user data."""
    configure_gemini(api_key)

    # Convert images to base64 encoded strings (many APIs accept base64-encoded image data)
    id_image_b64 = base64.b64encode(id_image_bytes).decode("utf-8")
    selfie_b64 = base64.b64encode(selfie_bytes).decode("utf-8")

    # Create the prompt to ask Gemini to verify the images
    prompt = f"""
    Compare the following ID image and selfie image. Return a match score and indicate if it's the same person:
    
    User Information:
    Full Name: {input_data["full_name"]}
    Date of Birth: {input_data["dob"]}
    ID Number: {input_data["id_number"]}
    Address: {input_data["address"]}
    Document Type: {input_data["doc_type"]}
    
    ID Image (base64):
    {id_image_b64}
    
    Selfie Image (base64):
    {selfie_b64}
    
    Instructions:
    - Check if the images belong to the same person.
    - Ensure the documents are authentic and match the provided user data.
    - Return a JSON response with the face match score and a verdict (approved/rejected).
    """

    # Request to Gemini API (use the correct API call for your model)
    response = genai.chat(
        model="gemini-pro-vision",  # Adjust the model name as needed
        messages=[{"role": "user", "content": prompt}]
    )

    # Simulate parsing the response from Gemini
    try:
        response_data = json.loads(response['content'])
        face_match_score = response_data['face_match_score']
        document_verified = response_data['document_verified']
        name_match = response_data['name_match']
        dob_match = response_data['dob_match']
        address_match = response_data['address_match']

        result = {
            "status": "APPROVED" if face_match_score >= 75 and document_verified else "REJECTED",
            "face_match_score": face_match_score,
            "document_verified": document_verified,
            "name_match": name_match,
            "dob_match": dob_match,
            "address_match": address_match,
            "details": response_data
        }
        return result
    except Exception as e:
        return {"status": "ERROR", "message": f"Error in processing Gemini response: {str(e)}"}
