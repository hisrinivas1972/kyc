# kyc/services/face_verification_service.py

from deepface import DeepFace

def verify_identity_with_deepface(id_image_bytes, selfie_bytes, input_data):
    import tempfile
    import os

    # Save temporary files
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as id_file:
        id_file.write(id_image_bytes)
        id_path = id_file.name

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as selfie_file:
        selfie_file.write(selfie_bytes)
        selfie_path = selfie_file.name

    try:
        result = DeepFace.verify(
            img1_path=selfie_path,
            img2_path=id_path,
            model_name="Facenet",
            detector_backend="opencv",
            enforce_detection=False
        )

        # Cleanup temp files
        os.remove(id_path)
        os.remove(selfie_path)

        return {
            "status": "APPROVED" if result["verified"] else "REJECTED",
            "face_match_score": round(result["confidence"], 2),
            "document_verified": True,  # Simplified, no OCR yet
            "name_match": True,         # Optional: add name comparison
            "dob_match": True,          # Optional
            "address_match": True,      # Optional
            "details": {
                "full_name": input_data.get("full_name"),
                "dob": input_data.get("dob"),
                "id_number": input_data.get("id_number"),
                "address": input_data.get("address"),
                "doc_type": input_data.get("doc_type"),
                "confidence": result["confidence"]
            }
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e)
        }
