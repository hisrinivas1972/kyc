import streamlit as st
from PIL import Image
import numpy as np
from deepface import DeepFace

# Initialize session state variables
if "step" not in st.session_state:
    st.session_state.step = 1
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

def step_personal_info():
    st.header("Step 1 of 6: Personal Information")
    
    st.session_state.user_data['full_name'] = st.text_input("Full Name", st.session_state.user_data.get('full_name', ''))
    st.session_state.user_data['dob'] = st.text_input("DOB (dd-mm-yyyy)", st.session_state.user_data.get('dob', ''))
    st.session_state.user_data['id_number'] = st.text_input("ID Number", st.session_state.user_data.get('id_number', ''))
    st.session_state.user_data['address'] = st.text_input("Address", st.session_state.user_data.get('address', ''))

    if st.button("Continue"):
        st.session_state.step = 2
        st.experimental_rerun()

def step_upload_document():
    st.header("Step 2 of 6: Upload ID Document")

    doc_type = st.radio(
        "Document Type:",
        ['Driver\'s License', 'Passport', 'National ID'],
        index=['Driver\'s License', 'Passport', 'National ID'].index(st.session_state.user_data.get('document_type', 'Driver\'s License'))
    )
    st.session_state.user_data['document_type'] = doc_type

    uploaded_file = st.file_uploader("Upload Document Image or PDF", type=['png', 'jpg', 'jpeg', 'webp', 'pdf'])

    if uploaded_file is not None:
        st.session_state.user_data['document_file'] = uploaded_file

    if st.button("Back"):
        st.session_state.step = 1
        st.experimental_rerun()

    if st.button("Continue"):
        if 'document_file' not in st.session_state.user_data:
            st.warning("Please upload your document before continuing.")
        else:
            st.session_state.step = 3
            st.experimental_rerun()

def step_face_capture():
    st.header("Step 3 of 6: Face Capture")

    img_file_buffer = st.camera_input("Please take a clear selfie")

    if img_file_buffer:
        image = Image.open(img_file_buffer)
        img_array = np.array(image.convert('RGB'))
        st.image(img_array, caption="Captured Image", use_column_width=True)

        st.session_state.user_data['face_image'] = img_array

        if st.button("Continue"):
            # Optional: Run face detection now or in verification step
            try:
                st.info("Analyzing face...")
                _ = DeepFace.detectFace(img_array, enforce_detection=True)  # quick check
                st.success("Face detected successfully!")
                st.session_state.step = 4
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Face detection failed: {e}")
                st.warning("Please retake a clear selfie.")
    else:
        st.info("Waiting for selfie capture...")

    if st.button("Back"):
        st.session_state.step = 2
        st.experimental_rerun()

def step_verifying():
    st.header("Step 4 of 6: Verifying Your Identity...")
    st.write("Simulated verification... please wait.")

    # Simulate some verification logic or wait time
    import time
    time.sleep(2)

    # For demo: check if address exists else require proof of address
    if not st.session_state.user_data.get('address'):
        st.session_state.step = 5
    else:
        st.session_state.step = 6

    st.experimental_rerun()

def step_address_proof_required():
    st.header("Step 5 of 6: Proof of Address Required")
    st.write("Address not found or invalid. Please upload proof of address.")

    uploaded_proof = st.file_uploader("Upload Proof of Address", type=['png', 'jpg', 'jpeg', 'pdf'])

    if uploaded_proof is not None:
        st.session_state.user_data['address_proof'] = uploaded_proof

    if st.button("Submit Proof"):
        if 'address_proof' not in st.session_state.user_data:
            st.warning("Please upload proof of address before continuing.")
        else:
            st.session_state.step = 6
            st.experimental_rerun()

    if st.button("Start Over"):
        st.session_state.user_data.clear()
        st.session_state.step = 1
        st.experimental_rerun()

def step_verification_result():
    st.header("Step 6 of 6: Verification Result")

    st.success("✅ Verification Successful!")
    st.markdown("""
    **Verification Details:**

    - Name Match: ✅ Passed  
    - Date of Birth Match: ✅ Passed  
    - ID Number Match: ✅ Passed  
    - Address Match: ✅ Passed  
    - Face Match: ✅ Passed  
    - Document Authenticity: ✅ Passed  
    """)

    if st.button("Start Over"):
        st.session_state.user_data.clear()
        st.session_state.step = 1
        st.experimental_rerun()

def main():
    if st.session_state.step == 1:
        step_personal_info()
    elif st.session_state.step == 2:
        step_upload_document()
    elif st.session_state.step == 3:
        step_face_capture()
    elif st.session_state.step == 4:
        step_verifying()
    elif st.session_state.step == 5:
        step_address_proof_required()
    elif st.session_state.step == 6:
        step_verification_result()

if __name__ == "__main__":
    main()
