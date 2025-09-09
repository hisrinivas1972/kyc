import streamlit as st
from PIL import Image
import time

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# Step 1: Personal Info
def step_personal_info():
    st.header("Step 1 of 6: Personal Information")

    full_name = st.text_input("Full Name:", st.session_state.user_data.get('full_name', ''))
    dob = st.text_input("DOB (dd-mm-yyyy):", st.session_state.user_data.get('dob', ''))
    id_number = st.text_input("ID Number:", st.session_state.user_data.get('id_number', ''))
    address = st.text_area("Address:", st.session_state.user_data.get('address', ''))

    if st.button("Continue"):
        st.session_state.user_data.update({
            'full_name': full_name,
            'dob': dob,
            'id_number': id_number,
            'address': address
        })
        st.session_state.step = 2
        st.experimental_rerun()

# Step 2: Upload Document
def step_upload_document():
    st.header("Step 2 of 6: Upload ID Document")

    doc_type = st.radio("Document Type:", ['Driver\'s License', 'Passport', 'National ID'],
                        index=['Driver\'s License', 'Passport', 'National ID'].index(
                            st.session_state.user_data.get('document_type', 'Driver\'s License')
                        ))

    uploaded_file = st.file_uploader("Upload Document (png, jpg, jpeg, pdf):", 
                                     type=['png', 'jpg', 'jpeg', 'pdf'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 1
            st.experimental_rerun()
    with col2:
        if st.button("Continue"):
            st.session_state.user_data['document_type'] = doc_type
            if uploaded_file is not None:
                st.session_state.user_data['document_file'] = uploaded_file.getvalue()
                st.session_state.step = 3
                st.experimental_rerun()
            else:
                st.warning("Please upload a document.")

# Step 3: Face Capture with simulated face match
def step_face_capture():
    st.header("Step 3 of 6: Face Capture")

    selfie = st.camera_input("Take a clear selfie")

    if selfie is not None:
        st.session_state.user_data['selfie'] = selfie.getvalue()

    if st.session_state.user_data.get('selfie'):
        st.image(st.session_state.user_data['selfie'], caption="Captured selfie", width=200)

    face_match_score = st.slider("Simulated Face Match Score (%)", 0, 100,
                                 st.session_state.user_data.get('face_match_score', 80))
    st.session_state.user_data['face_match_score'] = face_match_score

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 2
            st.experimental_rerun()
    with col2:
        if st.button("Continue"):
            if 'selfie' in st.session_state.user_data:
                st.session_state.step = 4
                st.experimental_rerun()
            else:
                st.warning("Please capture a selfie before continuing.")

# Step 4: Verifying Logic
def step_verifying():
    st.header("Step 4 of 6: Verifying Your Identity...")
    st.write("Please wait, this may take a few seconds...")

    time.sleep(2)  # Simulated processing delay

    face_match_score = st.session_state.user_data.get('face_match_score', 0)
    st.write(f"Simulated Face match score: {face_match_score}%")

    if face_match_score >= 75:
        if not st.session_state.user_data.get('address'):
            st.session_state.step = 5
        else:
            st.session_state.step = 6
    else:
        st.session_state.step = 7  # Verification failed

    st.experimental_rerun()

# Step 5: Upload Proof of Address
def step_address_proof_required():
    st.header("Step 5 of 6: Proof of Address Required")
    st.write("Address information could not be extracted. Please upload proof of address.")

    uploaded_proof = st.file_uploader("Upload Proof of Address (png, jpg, jpeg, pdf):", 
                                      type=['png', 'jpg', 'jpeg', 'pdf'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.user_data = {}
            st.experimental_rerun()
    with col2:
        if st.button("Submit Proof"):
            if uploaded_proof is not None:
                st.session_state.user_data['address_proof'] = uploaded_proof.getvalue()
                st.session_state.step = 6
                st.experimental_rerun()
            else:
                st.warning("Please upload proof of address.")

# Step 6: Verification Success
def step_verification_result():
    st.header("Step 6 of 6: ✅ Verification Successful")

    st.success("✅ Your identity has been successfully verified!")
    st.write("**Verification Details:**")
    st.markdown("""
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
        st.experimental_rerun()

# Step 7: Verification Failed
def step_verification_failed():
    st.header("❌ Verification Failed")
    st.error("Face match score was below 75%. Verification could not be completed.")
    st.markdown("Please try again by capturing a clearer selfie or using a valid ID document.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try Again"):
            st.session_state.step = 3  # Go back to face capture
            st.experimental_rerun()
    with col2:
        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.user_data = {}
            st.experimental_rerun()

# Main Step Router
def main():
    step = st.session_state.step

    if step == 1:
        step_personal_info()
    elif step == 2:
        step_upload_document()
    elif step == 3:
        step_face_capture()
    elif step == 4:
        step_verifying()
    elif step == 5:
        step_address_proof_required()
    elif step == 6:
        step_verification_result()
    elif step == 7:
        step_verification_failed()

# Run the app
if __name__ == "__main__":
    main()
