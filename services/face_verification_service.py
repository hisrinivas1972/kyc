# kyc/services/face_verification_service.py

import tempfile
from deepface import DeepFace
import numpy as np
import cv2

def verify_identity_with_deepface(id_image_bytes, selfie_bytes, input_data):
    # Save ID and selfie images temporarily
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as id_file, \
         tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as selfie_file:
        
        id_image_path = id_file.name
        selfie_image_path = selfie_file.name

        # Convert bytes to images and save
        id_img = cv2.imdecode(np.frombuffer(id_image_bytes, np.uint8), cv2.IMREAD_COLOR)
        selfie_img = cv2.imdecode(np.frombuffer(selfie_bytes, np.uint8), cv2.IMREAD_COLOR)

        cv2.imwrite(id_image_path, id_img)
        cv2.imwrite(selfie_image_path, selfie_img)

        try:
            result = DeepFace.verify(
                img1_path=selfie_image_path,
                img2_path=id_image_path,
                model_name="Facenet",
                detector_backend="opencv",
                enforce_detection=False
            )

            face_match_score = round(result["distance"] * 100, 2) if result["verified"] else 0

            response_data = {
                "verdict": "APPROVED" if result["verified"] else "REJECTED",
                "face_match_score": 100 - face_match_score,
                "document_verified": result["verified"],
                "name_match": True,
                "dob_match": True,
                "address_match": True,
                "full_name": input_data["full_name"],
                "dob": input_data["dob"],
                "id_number": input_data["id_number"],
                "address": input_data["address"],
                "doc_type": input_data["doc_type"]
            }

            return {
                "status": response_data["verdict"],
                "face_match_score": response_data["face_match_score"],
                "document_verified": response_data["document_verified"],
                "name_match": response_data["name_match"],
                "dob_match": response_data["dob_match"],
                "address_match": response_data["address_match"],
                "details": response_data
            }

        except Exception as e:
            return {"status": "ERROR", "message": f"DeepFace verification failed: {str(e)}"}
