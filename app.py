import streamlit as st
from PIL import Image
import io

# Initialize session state variables
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

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

def step_upload_document():
    st.header("Step 2 of 6: Upload ID Document")

    doc_type = st.radio("Document Type:", ['Driver\'s License', 'Passport', 'National ID'],
                        index=['Driver\'s License', 'Passport', 'National ID'].index(
                            st.session_state.user_data.get('document_type', 'Driver\'s License')
                        ))

    uploaded_file = st.file_uploader("Upload Document (png, jpg, jpeg, pdf):", 
                                     type=['png', 'jpg', 'jpeg', 'pdf'])

    if st.button("Back"):
        st.session_state.step = 1

    if st.button("Continue"):
        st.session_state.user_data['document_type'] = doc_type
        if uploaded_file is not None:
            st.session_state.user_data['document_file'] = uploaded_file.getvalue()
        else:
            st.warning("Please upload a document.")
            return
        st.session_state.step = 3

def step_face_capture():
    st.header("Step 3 of 6: Face Capture")

    selfie = st.camera_input("Take a clear selfie")

    if st.session_state.user_data.get('selfie'):
        st.image(st.session_state.user_data['selfie'], caption="Captured selfie", width=200)

    if selfie is not None:
        st.session_state.user_data['selfie'] = selfie.getvalue()

    # Add a slider to simulate face match percentage
    face_match_score = st.slider("Simulated Face Match Score (%)", 0, 100, 
                                 st.session_state.user_data.get('face_match_score', 80))
    st.session_state.user_data['face_match_score'] = face_match_score

    if st.button("Back"):
        st.session_state.step = 2

    if st.button("Continue"):
        if 'selfie' in st.session_state.user_data:
            if face_match_score >= 75:
                st.session_state.step = 4
            else:
                st.warning("Face match below 75%. Verification failed.")
        else:
            st.warning("Please capture a selfie before continuing.")

def step_verifying():
    st.header("Step 4 of 6: Verifying Your Identity...")
    st.write("Please wait, this may take a few seconds...")

    import time
    time.sleep(2)  # Simulate processing time

    # Use simulated face match score
    face_match_score = st.session_state.user_data.get('face_match_score', 0)

    st.write(f"Simulated Face match score: {face_match_score}%")

    if face_match_score >= 75:
        # If address missing, go to step 5 else success
        if not st.session_state.user_data.get('address'):
            st.session_state.step = 5
        else:
            st.session_state.step = 6
    else:
        st.error("Face match below 75%. Verification failed.")
        if st.button("Try Again"):
            st.session_state.step = 3

def step_address_proof_required():
    st.header("Step 5 of 6: Proof of Address Required")
    st.write("Address information could not be extracted. Please upload proof of address.")

    uploaded_proof = st.file_uploader("Upload Proof of Address (png, jpg, jpeg, pdf):", type=['png', 'jpg', 'jpeg', 'pdf'])

    if st.button("Start Over"):
        st.session_state.step = 1
        st.session_state.user_data = {}

    if st.button("Submit Proof"):
        if uploaded_proof is not None:
            st.session_state.user_data['address_proof'] = uploaded_proof.getvalue()
            st.session_state.step = 6
        else:
            st.warning("Please upload proof of address.")

def step_verification_result():
    st.header("Step 6 of 6: Verification Result")

    st.success("✅ Verification Successful!")
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
