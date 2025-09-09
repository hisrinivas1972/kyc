import streamlit as st
from fpdf import FPDF
import io
import time
import numpy as np
from PIL import Image
import face_recognition

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output = io.BytesIO(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output

# Step 1: Personal Info
def step_personal_info():
    st.header("Step 1 of 6: Personal Information")

    full_name = st.text_input("Full Name:", st.session_state.user_data.get('full_name', ''))
    dob = st.text_input("DOB (dd-mm-yyyy):", st.session_state.user_data.get('dob', ''))
    id_number = st.text_input("ID Number:", st.session_state.user_data.get('id_number', ''))
    address = st.text_area("Address:", st.session_state.user_data.get('address', ''))

    if st.button("Continue"):
        if not full_name or not dob or not id_number or not address:
            st.warning("Please fill in all fields.")
            return

        st.session_state.user_data.update({
            'full_name': full_name,
            'dob': dob,
            'id_number': id_number,
            'address': address
        })
        if 'verification_done' in st.session_state:
            del st.session_state['verification_done']
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
            if 'verification_done' in st.session_state:
                del st.session_state['verification_done']
            st.session_state.step = 1
            st.experimental_rerun()
    with col2:
        if st.button("Continue"):
            if uploaded_file is None:
                st.warning("Please upload a document.")
                return
            st.session_state.user_data['document_type'] = doc_type
            st.session_state.user_data['document_file'] = uploaded_file.getvalue()
            if 'verification_done' in st.session_state:
                del st.session_state['verification_done']
            st.session_state.step = 3
            st.experimental_rerun()

# Step 3: Face Capture and Face Matching
def step_face_capture():
    st.header("Step 3 of 6: Face Capture and Verification")

    selfie = st.camera_input("Take a clear selfie")

    if selfie is not None:
        st.session_state.user_data['selfie'] = selfie.getvalue()
        st.image(selfie, caption="Captured selfie", width=200)

    if st.button("Verify Face Match"):
        doc_bytes = st.session_state.user_data.get('document_file')
        selfie_bytes = st.session_state.user_data.get('selfie')

        if not doc_bytes or not selfie_bytes:
            st.error("Both ID document and selfie must be uploaded/captured.")
            return

        try:
            doc_image = np.array(Image.open(io.BytesIO(doc_bytes)))
            selfie_image = np.array(Image.open(io.BytesIO(selfie_bytes)))

            doc_encodings = face_recognition.face_encodings(doc_image)
            selfie_encodings = face_recognition.face_encodings(selfie_image)

            if not doc_encodings:
                st.error("No face detected in the uploaded ID document image.")
                return
            if not selfie_encodings:
                st.error("No face detected in the selfie image.")
                return

            doc_encoding = doc_encodings[0]
            selfie_encoding = selfie_encodings[0]

            results = face_recognition.compare_faces([doc_encoding], selfie_encoding)
            face_distance = face_recognition.face_distance([doc_encoding], selfie_encoding)[0]
            match = results[0]

            st.write(f"Face match distance score: {face_distance:.4f} (lower is better)")

            if match:
                st.success("Face match successful!")
                st.session_state.user_data['face_match_score'] = int((1 - face_distance) * 100)
                if 'verification_done' in st.session_state:
                    del st.session_state['verification_done']
                st.session_state.step = 4
                st.experimental_rerun()
            else:
                st.error("Face match failed, please try again.")
        except Exception as e:
            st.error(f"Error processing images: {e}")

    if st.button("Back"):
        if 'verification_done' in st.session_state:
            del st.session_state['verification_done']
        st.session_state.step = 2
        st.experimental_rerun()

# Step 4: Verifying (simulate delay)
def step_verifying():
    st.header("Step 4 of 6: Verifying Your Identity...")
    st.write("Please wait, this may take a few seconds...")

    if 'verification_done' not in st.session_state:
        time.sleep(2)  # simulate processing

        face_match_score = st.session_state.user_data.get('face_match_score', 0)
        st.session_state['verification_done'] = True

        # Simple logic: pass if face_match_score > 75 and address is provided
        if face_match_score >= 75 and st.session_state.user_data.get('address'):
            st.session_state.verification_passed = True
            st.session_state.step = 6
        else:
            # If address missing but face matches, require address proof
            if face_match_score >= 75 and not st.session_state.user_data.get('address'):
                st.session_state.verification_passed = False
                st.session_state.step = 5
            else:
                # Face match fail
                st.session_state.verification_passed = False
                st.session_state.step = 7

        st.experimental_rerun()
    else:
        st.write("Verification complete, redirecting...")

# Step 5: Address Proof Upload (if required)
def step_address_proof_required():
    st.header("Step 5 of 6: Proof of Address Required")
    st.write("Address information could not be verified. Please upload proof of address.")

    uploaded_proof = st.file_uploader("Upload Proof of Address (png, jpg, jpeg, pdf):", 
                                      type=['png', 'jpg', 'jpeg', 'pdf'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Over"):
            if 'verification_done' in st.session_state:
                del st.session_state['verification_done']
            st.session_state.step = 1
            st.session_state.user_data = {}
            st.experimental_rerun()
    with col2:
        if st.button("Submit Proof"):
            if uploaded_proof is not None:
                st.session_state.user_data['address_proof'] = uploaded_proof.getvalue()
                if 'verification_done' in st.session_state:
                    del st.session_state['verification_done']
                st.session_state.step = 6
                st.experimental_rerun()
            else:
                st.warning("Please upload proof of address.")

# Step 6: Verification Result (Pass/Fail)
def step_verification_result():
    st.header("Step 6 of 6: Verification Result")

    passed = st.session_state.get('verification_passed', False)
    face_match_passed = st.session_state.user_data.get('face_match_score', 0) >= 75
    address_present = bool(st.session_state.user_data.get('address'))

    if passed:
        st.success("✅ Your identity has been successfully verified!")
        verification_status = "PASSED"
    else:
        st.error("❌ Verification Failed.")
        verification_status = "FAILED"

    st.write("**Verification Details:**")
    st.markdown(f"""
    - Name Match: {'✅ Passed' if passed else '❌ Failed'}  
    - Date of Birth Match: {'✅ Passed' if passed else '❌ Failed'}  
    - ID Number Match: {'✅ Passed' if passed else '❌ Failed'}  
    - Address Match: {'✅ Passed' if address_present else '❌ Failed'}  
    - Face Match: {'✅ Passed' if face_match_passed else '❌ Failed'}  
    - Document Authenticity: {'✅ Passed' if passed else '❌ Failed'}  
    """)

    client_pdf_text = f"""
Client KYC Verification Result

Name: {st.session_state.user_data.get('full_name', '')}
DOB: {st.session_state.user_data.get('dob', '')}
ID Number: {st.session_state.user_data.get('id_number', '')}
Address: {st.session_state.user_data.get('address', '')}
Verification Status: {verification_status}
Face Match Score: {st.session_state.user_data.get('face_match_score', 0)}%
    """

    pdf_file = create_pdf(client_pdf_text)

    st.download_button(
        label="Download Verification Report (PDF)",
        data=pdf_file,
        file_name="kyc_verification_report.pdf",
        mime="application/pdf"
    )

    if st.button("Start Over"):
        st.session_state.step = 1
        st.session_state.user_data = {}
        if 'verification_done' in st.session_state:
            del st.session_state['verification_done']
        st.experimental_rerun()

# Step 7: Verification Fail Screen (face mismatch or other failures)
def step_verification_failed():
    st.header("Verification Failed")
    st.error("Unfortunately, your identity could not be verified. Please try again or contact support.")

    if st.button("Start Over"):
        st.session_state.step = 1
        st.session_state.user_data = {}
        if 'verification_done' in st.session_state:
            del st.session_state['verification_done']
        st.experimental_rerun()

def main():
    st.title("KYC Verification App")

    step = st.session_state.step
    st.write(f"--- DEBUG: Current step = {step} ---")

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
    else:
        st.error("Unknown step!")

if __name__ == "__main__":
    main()
