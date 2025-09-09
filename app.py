import streamlit as st
from fpdf import FPDF
import io
import time

# Initialize session state variables
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'verification_done' not in st.session_state:
    st.session_state.verification_done = False
if 'verification_passed' not in st.session_state:
    st.session_state.verification_passed = False

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output = io.BytesIO(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output

def step_personal_info():
    st.header("Step 1 of 6: Personal Information")
    full_name = st.text_input("Full Name:", st.session_state.user_data.get('full_name', ''))
    dob = st.text_input("DOB (dd-mm-yyyy):", st.session_state.user_data.get('dob', ''))
    id_number = st.text_input("ID Number:", st.session_state.user_data.get('id_number', ''))
    address = st.text_area("Address:", st.session_state.user_data.get('address', ''))

    if st.button("Continue"):
        # Save input data to session state
        st.session_state.user_data.update({
            'full_name': full_name,
            'dob': dob,
            'id_number': id_number,
            'address': address
        })
        # Reset verification flags if any
        st.session_state.verification_done = False
        st.session_state.verification_passed = False
        st.session_state.step = 2
        st.experimental_rerun()

def step_upload_document():
    st.header("Step 2 of 6: Upload ID Document")
    doc_options = ['Driver\'s License', 'Passport', 'National ID']
    current_doc = st.session_state.user_data.get('document_type', doc_options[0])
    doc_type = st.radio("Document Type:", doc_options, index=doc_options.index(current_doc))

    uploaded_file = st.file_uploader("Upload Document (png, jpg, jpeg, pdf):", 
                                     type=['png', 'jpg', 'jpeg', 'pdf'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.verification_done = False
            st.session_state.step = 1
            st.experimental_rerun()
    with col2:
        if st.button("Continue"):
            if uploaded_file is None:
                st.warning("Please upload a document before continuing.")
                return
            # Save uploaded document and type
            st.session_state.user_data['document_type'] = doc_type
            st.session_state.user_data['document_file'] = uploaded_file.getvalue()
            st.session_state.verification_done = False
            st.session_state.verification_passed = False
            st.session_state.step = 3
            st.experimental_rerun()

def step_face_capture():
    st.header("Step 3 of 6: Face Capture")
    selfie = st.camera_input("Take a clear selfie")

    if selfie is not None:
        st.session_state.user_data['selfie'] = selfie.getvalue()
        st.image(selfie, caption="Captured selfie", width=200)

    face_match_score = st.slider("Simulated Face Match Score (%)", 0, 100,
                                 st.session_state.user_data.get('face_match_score', 80))
    st.session_state.user_data['face_match_score'] = face_match_score

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.verification_done = False
            st.session_state.step = 2
            st.experimental_rerun()
    with col2:
        if st.button("Continue"):
            if 'selfie' not in st.session_state.user_data:
                st.warning("Please capture a selfie before continuing.")
                return
            st.session_state.verification_done = False
            st.session_state.verification_passed = False
            st.session_state.step = 4
            st.experimental_rerun()

def step_verifying():
    st.header("Step 4 of 6: Verifying Your Identity...")
    st.write("Please wait, this may take a few seconds...")

    if not st.session_state.verification_done:
        # Simulate verification delay
        time.sleep(2)

        face_match_score = st.session_state.user_data.get('face_match_score', 0)
        address_present = bool(st.session_state.user_data.get('address'))

        # Decide verification outcome
        if face_match_score >= 75:
            if not address_present:
                st.session_state.verification_passed = False
                st.session_state.step = 5  # Need proof of address upload
            else:
                st.session_state.verification_passed = True
                st.session_state.step = 6  # Verification passed
        else:
            st.session_state.verification_passed = False
            st.session_state.step = 7  # Verification failed due to face match

        st.session_state.verification_done = True
        st.experimental_rerun()
    else:
        st.write("Verification complete, redirecting...")
        time.sleep(1)
        st.experimental_rerun()

def step_address_proof_required():
    st.header("Step 5 of 6: Proof of Address Required")
    st.write("Address info could not be verified. Please upload proof of address.")

    uploaded_proof = st.file_uploader("Upload Proof of Address (png, jpg, jpeg, pdf):", 
                                      type=['png', 'jpg', 'jpeg', 'pdf'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Over"):
            st.session_state.user_data = {}
            st.session_state.verification_done = False
            st.session_state.verification_passed = False
            st.session_state.step = 1
            st.experimental_rerun()
    with col2:
        if st.button("Submit Proof"):
            if uploaded_proof is None:
                st.warning("Please upload proof of address before continuing.")
                return
            st.session_state.user_data['address_proof'] = uploaded_proof.getvalue()
            st.session_state.step = 6
            st.experimental_rerun()

def step_verification_result():
    st.header("Step 6 of 6: Verification Result")
    passed = st.session_state.verification_passed
    face_match_passed = st.session_state.user_data.get('face_match_score', 0) >= 75
    address_present = bool(st.session_state.user_data.get('address')) or 'address_proof' in st.session_state.user_data

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
"""

    company_pdf_text = f"""
Company KYC Verification Summary

Client Name: {st.session_state.user_data.get('full_name', '')}
Verified ID: {st.session_state.user_data.get('document_type', '')}
Verification Outcome: {verification_status}
"""

    if st.button("Generate PDFs"):
        client_pdf = create_pdf(client_pdf_text)
        company_pdf = create_pdf(company_pdf_text)

        st.download_button(
            label="Download PDF for Client",
            data=client_pdf,
            file_name="client_kyc_result.pdf",
            mime="application/pdf"
        )
        st.download_button(
            label="Download PDF for Company",
            data=company_pdf,
            file_name="company_kyc_summary.pdf",
            mime="application/pdf"
        )

    if st.button("Start Over"):
        st.session_state.user_data = {}
        st.session_state.verification_done = False
        st.session_state.verification_passed = False
        st.session_state.step = 1
        st.experimental_rerun()

def step_verification_failed():
    st.header("❌ Verification Failed")
    st.error("Face match score was below 75%. Verification could not be completed.")
    st.markdown("Please try again by capturing a clearer selfie or using a valid ID document.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try Again"):
            st.session_state.verification_done = False
            st.session_state.step = 3
            st.experimental_rerun()
    with col2:
        if st.button("Start Over"):
            st.session_state.user_data = {}
            st.session_state.verification_done = False
            st.session_state.verification_passed = False
            st.session_state.step = 1
            st.experimental_rerun()

def main():
    st.write(f"--- DEBUG: Current step = {st.session_state.step} ---")
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
    else:
        st.error("Unknown step. Resetting.")
        st.session_state.step = 1
        st.experimental_rerun()

if __name__ == "__main__":
    main()
