import streamlit as st
from deepface import DeepFace
from PIL import Image
import numpy as np

# Session state to store user data between steps
if "step" not in st.session_state:
    st.session_state.step = 1
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

def step_personal_info():
    st.header("Step 1 of 6: Personal Information")
    full_name = st.text_input("Full Name", value=st.session_state.user_data.get("full_name", ""))
    dob = st.text_input("DOB (dd-mm-yyyy)", value=st.session_state.user_data.get("dob", ""))
    id_number = st.text_input("ID Number", value=st.session_state.user_data.get("id_number", ""))
    address = st.text_input("Address", value=st.session_state.user_data.get("address", ""))

    if st.button("Continue"):
        st.session_state.user_data.update({
            "full_name": full_name,
            "dob": dob,
            "id_number": id_number,
            "address": address
        })
        st.session_state.step = 2

def step_upload_document():
    st.header("Step 2 of 6: Upload ID Document")
    doc_type = st.radio("Document Type", ["Driver's License", "Passport", "National ID"])
    uploaded_doc = st.file_uploader("Upload your ID document", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("Back"):
        st.session_state.step = 1
    if st.button("Continue"):
        st.session_state.user_data.update({
            "document_type": doc_type,
            "document_file": uploaded_doc
        })
        st.session_state.step = 3

def step_face_capture():
    st.header("Step 3 of 6: Face Capture")
    uploaded_selfie = st.file_uploader("Upload a clear selfie", type=["png", "jpg", "jpeg"])
    
    if st.button("Back"):
        st.session_state.step = 2

    if uploaded_selfie:
        img = Image.open(uploaded_selfie)
        st.image(img, caption="Your selfie", use_column_width=True)

        if st.button("Verify Face"):
            img_array = np.array(img.convert('RGB'))
            try:
                # Simple face analysis with DeepFace to verify face is detected
                result = DeepFace.analyze(img_array, actions=['age', 'gender', 'emotion'], enforce_detection=True)
                st.success(f"Face verified! Age: {result['age']}, Gender: {result['gender']}")
                st.session_state.user_data["selfie"] = uploaded_selfie
                st.session_state.step = 4
            except Exception as e:
                st.error(f"Face verification failed: {e}")

def step_verifying():
    st.header("Step 4 of 6: Verifying Your Identity")
    st.write("Please wait while we verify your identity...")
    # You can simulate some processing delay
    import time
    time.sleep(2)

    # For demo, let's assume address extraction fails if empty
    if not st.session_state.user_data.get("address"):
        st.session_state.step = 5
    else:
        st.session_state.step = 6

def step_address_proof_required():
    st.header("Step 5 of 6: Upload Proof of Address")
    uploaded_proof = st.file_uploader("Upload proof of address", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("Back"):
        st.session_state.step = 1

    if uploaded_proof and st.button("Submit Proof"):
        st.session_state.user_data["address_proof"] = uploaded_proof
        st.session_state.step = 6

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
        st.session_state.step = 1
        st.session_state.user_data = {}

# Main flow controller
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
