from deepface import DeepFace

def verify_faces(id_img_path: str, captured_img_path: str) -> dict:
    """
    Verify if two images contain the same face using DeepFace.

    Args:
        id_img_path (str): Path to ID proof image.
        captured_img_path (str): Path to captured image.

    Returns:
        dict: Verification result containing 'verified', 'distance', 'threshold', etc.
    """
    try:
        result = DeepFace.verify(img1_path=id_img_path, img2_path=captured_img_path)
        return result
    except Exception as e:
        raise RuntimeError(f"Face verification failed: {e}")
