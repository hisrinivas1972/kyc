import streamlit as st
from fpdf import FPDF
import io
import time

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
        st.experimental_rerun()  # Only here, immediately after button press

def step_upload_document():
    st.header("Step 2 of 6: Upload ID Document")

    doc_types = ['Driver\'s License', 'Passport', 'National ID']
    current_doc_type = st.session_state.user_data.get('document_type', 'Driver\'s License')
    doc_type = st.radio("Document Type:", doc_types, index=doc_types.index(current_doc_type))

    uploaded_file = st.file_uploader("Upload Document (png, jpg, jpeg, pdf):", type=['png', 'jpg', 'jpeg', 'pdf'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 1
            st.experimental_rerun()
    with col2:
        if st.button("Continue"):
            if uploaded_file is not None:
                st.session_state.user_data['document_type'] = doc_type
                st.session_state.user_data['document_file'] = uploaded_file.getvalue()
                st.session_state.step = 3
                st.experimental_rerun()
            else:
                st.warning("Please upload a document.")

def step_face_capture():
    st.header("Step 3 of 6: Face Capture")

    selfie = st.camera_input("Take a clear selfie")
    if selfie is not None:
        st.session_state.user_data['selfie'] = selfie.getvalue()

    if 'selfie' in st.session_state.user_data:
        st.image(st.session_state.user_data['selfie'], caption="Captured selfie", width=200)

    face_match_score = st.slider("Simulated Face Match Score (%)", 0, 100, st.session_state.user_data.get('face_match_score', 80))
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

def step_verifying():
    st.header("Step 4 of 6: Verifying Your Identity...")

    with st.spinner("Verifying, please wait..."):
        time.sleep(2)

    face_match_score = st.session_state.user_data.get('face_match_score', 0)
    st.write(f"Simulated Face match score: {face_match_score}%")

    # Determine verification outcome
    if face_match_score >= 75:
        if not st.session_state.user_data.get('address'):
            st.session_state.verification_passed = False
            st.session_state.step = 5
        else:
            st.session_state.verification_passed = True
            st.session_state.step = 6
    else:
        st.session_state.verification_passed = False
        st.session_state.step = 7

    # Important: rerun only once after setting the step
    st.experimental_rerun()

def step_address_proof_required():
    st.header("Step 5 of 6: Proof of Address Required")
    st.write("Address information could not be extracted. Please upload proof of address.")

    uploaded_proof = st.file_uploader("Upload Proof of Address (png, jpg, jpeg, pdf):", type=['png', 'jpg', 'jpeg', 'pdf'])

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
        st.session_state.step = 1
        st.session_state.user_data = {}
        st.experimental_rerun()

def step_verification_failed():
    st.header("❌ Verification Failed")
    st.error("Face match score was below 75%. Verification could not be completed.")
    st.markdown("Please try again by capturing a clearer selfie or using a valid ID document.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try Again"):
            st.session_state.step = 3
            st.experimental_rerun()
    with col2:
        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.user_data = {}
            st.experimental_rerun()

def main():
    step = st.session_state.step

    # Debug info — remove or comment out in production
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

if __name__ == "__main__":
    main()
