import streamlit as st
from fpdf import FPDF
import io
import time

# -----------------------
# Session state defaults
# -----------------------
if 'step' not in st.session_state:
    st.session_state.step = 0  # Start at Step 0: API Key input
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

# ---------------
# PDF generation
# ---------------
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output = io.BytesIO(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output

# ----------------
# Step 0: API key
# ----------------
def step_enter_api_key():
    st.header("🔐 Enter Your Gemini API Key")
    api_key_input = st.text_input("Please enter your Google Gemini API Key:", type="password")
    if st.button("Continue"):
        if api_key_input.strip():
            st.session_state.api_key = api_key_input.strip()
            st.session_state.step = 1
            st.rerun()
        else:
            st.warning("API key cannot be empty. Please enter a valid key.")

# -------------------
# Step 1: Personal Info
# -------------------
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
        if 'verification_done' in st.session_state:
            del st.session_state['verification_done']
        st.session_state.step = 2
        st.rerun()

# ----------------------
# Step 2: Upload Document
# ----------------------
def step_upload_document():
    st.header("Step 2 of 6: Upload ID Document")

    doc_types = ['Driver\'s License', 'Passport', 'National ID']
    doc_type = st.radio("Document Type:", doc_types,
                        index=doc_types.index(st.session_state.user_data.get('document_type', 'Driver\'s License')))

    uploaded_file = st.file_uploader("Upload Document (png, jpg, jpeg, pdf):",
                                     type=['png', 'jpg', 'jpeg', 'pdf'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            if 'verification_done' in st.session_state:
                del st.session_state['verification_done']
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Continue"):
            st.session_state.user_data['document_type'] = doc_type
            if uploaded_file is not None:
                st.session_state.user_data['document_file'] = uploaded_file.getvalue()
                if 'verification_done' in st.session_state:
                    del st.session_state['verification_done']
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning("Please upload a document.")

# -----------------
# Step 3: Face Capture
# -----------------
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
            if 'verification_done' in st.session_state:
                del st.session_state['verification_done']
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Continue"):
            if 'selfie' in st.session_state.user_data:
                if 'verification_done' in st.session_state:
                    del st.session_state['verification_done']
                st.session_state.step = 4
                st.rerun()
            else:
                st.warning("Please capture a selfie before continuing.")

# -----------------
# Step 4: Verifying (Dummy Gemini Call)
# -----------------
def step_verifying():
    st.header("Step 4 of 6: Verifying Your Identity...")
    st.write("Please wait, this may take a few seconds...")

    if 'verification_done' not in st.session_state:
        # Simulate delay
        time.sleep(2)

        # Dummy check using face_match_score
        face_match_score = st.session_state.user_data.get('face_match_score', 0)

        # Here is where you'd call Gemini API, passing st.session_state.api_key
        # For example:
        # result = verify_identity_with_gemini(prompt, id_image, selfie_image, st.session_state.api_key)

        # For this example, fake verification result:
        st.session_state['verification_done'] = True

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

        st.rerun()
    else:
        st.write("Verification complete, redirecting...")

# --------------------------
# Step 5: Proof of Address Required
# --------------------------
def step_address_proof_required():
    st.header("Step 5 of 6: Proof of Address Required")
    st.write("Address information could not be extracted. Please upload proof of address.")

    uploaded_proof = st.file_uploader("Upload Proof of Address (png, jpg, jpeg, pdf):",
                                      type=['png', 'jpg', 'jpeg', 'pdf'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Over"):
            if 'verification_done' in st.session_state:
                del st.session_state['verification_done']
            st.session_state.step = 1
            st.session_state.user_data = {}
            st.rerun()
    with col2:
        if st.button("Submit Proof"):
            if uploaded_proof is not None:
                st.session_state.user_data['address_proof'] = uploaded_proof.getvalue()
                if 'verification_done' in st.session_state:
                    del st.session_state['verification_done']
                st.session_state.step = 6
                st.rerun()
            else:
                st.warning("Please upload proof of address.")

# -----------------
# Step 6: Verification Result
# -----------------
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
        if 'verification_done' in st.session_state:
            del st.session_state['verification_done']
        st.session_state.step = 1
        st.session_state.user_data = {}
        st.rerun()

# -------------------
# Step 7: Verification Failed
# -------------------
def step_verification_failed():
    st.header("❌ Verification Failed")
    st.error("Face match score was below 75%. Verification could not be completed.")
    st.markdown("Please try again by capturing a clearer selfie or using a valid ID document.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try Again"):
            if 'verification_done' in st.session_state:
                del st.session_state['verification_done']
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Start Over"):
            if 'verification_done' in st.session_state:
                del st.session_state['verification_done']
            st.session_state.step = 1
            st.session_state.user_data = {}
            st.rerun()

# -------------------
# Main router
# -------------------
def main():
    st.sidebar.title("KYC App Controls")
    if st.session_state.api_key:
        st.sidebar.success("🔐 Gemini API Key provided")
    else:
        st.sidebar.warning("⚠️ Gemini API Key missing")

    st.write(f"--- DEBUG: Current step = {st.session_state.step} ---")

    step = st.session_state.step

    if step == 0:
        step_enter_api_key()
    elif step == 1:
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
