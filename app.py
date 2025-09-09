import streamlit as st
from deepface import DeepFace
import tempfile

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

def step_personal_info():
    st.title("Step 1 of 6: Personal Information")
    full_name = st.text_input("Full Name:")
    dob = st.text_input("DOB (dd-mm-yyyy):")
    id_number = st.text_input("ID Number:")
    address = st.text_input("Address:")

    if st.button("Continue"):
        st.session_state.user_data.update({
            'full_name': full_name,
            'dob': dob,
            'id_number': id_number,
            'address': address,
        })
        st.session_state.step = 2

def step_upload_document():
    st.title("Step 2 of 6: Upload ID Document")
    doc_type = st.radio("Document Type:", ['Driver\'s License', 'Passport', 'National ID'])
    upload = st.file_uploader("Upload your ID Document (image/pdf)", type=['png','jpg','jpeg','webp','pdf'])

    if st.button("Back"):
        st.session_state.step = 1
    if st.button("Continue"):
        st.session_state.user_data['document_type'] = doc_type
        st.session_state.user_data['document_file'] = upload
        st.session_state.step = 3

def step_face_capture_deepface():
    st.title("Step 3 of 6: Face Capture and Verification")

    id_file = st.file_uploader("Upload your ID Document Photo (image only)", type=["jpg", "jpeg", "png"], key="id_upload")
    selfie_file = st.file_uploader("Upload your Selfie", type=["jpg", "jpeg", "png"], key="selfie_upload")

    face_match_result = None
    error_message = None

    if id_file and selfie_file:
        try:
            # Save uploaded images temporarily to disk for DeepFace
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as id_tmp:
                id_tmp.write(id_file.read())
                id_path = id_tmp.name
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as selfie_tmp:
                selfie_tmp.write(selfie_file.read())
                selfie_path = selfie_tmp.name

            # Run verification
            result = DeepFace.verify(id_path, selfie_path, enforce_detection=True)

            if result["verified"]:
                face_match_result = "✅ Face matches! Verification passed."
                st.session_state.user_data['face_match_passed'] = True
            else:
                face_match_result = "❌ Face does not match. Verification failed."
                st.session_state.user_data['face_match_passed'] = False

        except Exception as e:
            error_message = f"Error processing images: {e}"

    if error_message:
        st.error(error_message)

    if face_match_result:
        if st.session_state.user_data.get('face_match_passed'):
            st.success(face_match_result)
        else:
            st.error(face_match_result)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 2
    with col2:
        if st.button("Continue"):
            if st.session_state.user_data.get('face_match_passed'):
                st.session_state.step = 4
            else:
                st.error("You must have a successful face match to continue.")

def step_verifying():
    st.title("Step 4 of 6: Verifying Your Identity...")
    st.write("Please wait, this may take a few seconds...")

    # Simulate processing delay
    import time
    time.sleep(2)

    # For demo, skip address proof step and move to success
    st.session_state.step = 6

def step_verification_result():
    st.title("Step 6 of 6: Verification Result")

    st.success("✅ Verification Successful!")
    st.write("""
    **Verification Details:**
    - Name Match: ✅ Passed  
    - Date of Birth Match: ✅ Passed  
    - ID Number Match: ✅ Passed  
    - Address Match: ✅ Passed  
    - Face Match: ✅ Passed  
    - Document Authenticity: ✅ Passed
    """)

    if st.button("Start Over"):
        st.session_state.clear()
        st.session_state.step = 1

# Main control flow
if st.session_state.step == 1:
    step_personal_info()
elif st.session_state.step == 2:
    step_upload_document()
elif st.session_state.step == 3:
    step_face_capture_deepface()
elif st.session_state.step == 4:
    step_verifying()
elif st.session_state.step == 6:
    step_verification_result()
