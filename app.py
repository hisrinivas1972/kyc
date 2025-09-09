import streamlit as st
from fpdf import FPDF
import io
import time
import requests  # For Gemini API call (replace with your SDK if needed)
import base64

# ------------- Utils ----------------

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output = io.BytesIO(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output

def call_gemini_api(api_key, id_doc_bytes, selfie_bytes, user_info):
    """
    Replace this with your actual Gemini API call.
    This simulates sending images and data and getting a JSON response.
    """

    # Example payload — adjust per your API requirements
    # For demo, we simulate a response:
    time.sleep(2)  # Simulate API latency

    # Fake logic for face match:
    # In real case, send id_doc_bytes and selfie_bytes to Gemini
    # Here we just simulate a 80% face match if images are present
    face_match_score = 80

    # Simulate verifying other data matches (you’d parse real response)
    verification_passed = True if face_match_score >= 75 else False

    response = {
        "face_match_score": face_match_score,
        "verification_passed": verification_passed,
        "details": {
            "name_match": True,
            "dob_match": True,
            "id_number_match": True,
            "address_match": bool(user_info.get('address')),
            "document_authenticity": True
        }
    }
    return response

# ----------- Step 0: Enter API Key -------------

def step_enter_api_key():
    st.header("Enter Gemini API Key to proceed")
    api_key_input = st.text_input("API Key", type="password")
    if st.button("Submit API Key"):
        if api_key_input.strip():
            st.session_state.api_key = api_key_input.strip()
            st.session_state.step = 1
            st.rerun()
        else:
            st.warning("API key cannot be empty. Please enter a valid API key.")

# ----------- Step 1: Personal Info -------------

def step_personal_info():
    st.header("Step 1 of 5: Personal Information")
    full_name = st.text_input("Full Name:", st.session_state.user_data.get('full_name', ''))
    dob = st.text_input("DOB (dd-mm-yyyy):", st.session_state.user_data.get('dob', ''))
    id_number = st.text_input("ID Number:", st.session_state.user_data.get('id_number', ''))
    address = st.text_area("Address:", st.session_state.user_data.get('address', ''))

    if st.button("Continue"):
        if full_name and dob and id_number and address:
            st.session_state.user_data.update({
                'full_name': full_name,
                'dob': dob,
                'id_number': id_number,
                'address': address
            })
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("Please fill all fields before continuing.")

# ----------- Step 2: Upload Document -------------

def step_upload_document():
    st.header("Step 2 of 5: Upload ID Document")

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
            st.rerun()
    with col2:
        if st.button("Continue"):
            if uploaded_file is not None:
                st.session_state.user_data['document_type'] = doc_type
                st.session_state.user_data['document_file'] = uploaded_file.read()
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning("Please upload a document before continuing.")

# ----------- Step 3: Face Capture -------------

def step_face_capture():
    st.header("Step 3 of 5: Capture Selfie")

    selfie = st.camera_input("Take a clear selfie")
    if selfie is not None:
        st.session_state.user_data['selfie'] = selfie.read()
        st.image(selfie, caption="Captured selfie", width=200)

    if st.button("Back"):
        st.session_state.step = 2
        st.rerun()

    if st.button("Continue"):
        if 'selfie' in st.session_state.user_data:
            st.session_state.step = 4
            st.rerun()
        else:
            st.warning("Please capture a selfie before continuing.")

# ----------- Step 4: Call Gemini & Verify -------------

def step_verifying():
    st.header("Step 4 of 5: Verifying your identity...")
    st.write("Please wait, this may take a few seconds.")

    if 'verification_result' not in st.session_state:
        api_key = st.session_state.api_key
        id_doc = st.session_state.user_data.get('document_file')
        selfie = st.session_state.user_data.get('selfie')
        user_info = st.session_state.user_data

        if not id_doc or not selfie:
            st.error("Missing document or selfie data. Please start over.")
            if st.button("Start Over"):
                st.session_state.step = 0
                st.session_state.user_data = {}
                st.rerun()
            return

        result = call_gemini_api(api_key, id_doc, selfie, user_info)
        st.session_state.verification_result = result
        st.session_state.step = 5
        st.rerun()
    else:
        st.write("Verification complete, redirecting...")
        time.sleep(1)
        st.session_state.step = 5
        st.rerun()

# ----------- Step 5: Show Result -------------

def step_verification_result():
    st.header("Step 5 of 5: Verification Result")

    result = st.session_state.get('verification_result', {})
    passed = result.get('verification_passed', False)
    face_match_score = result.get('face_match_score', 0)
    details = result.get('details', {})

    if passed:
        st.success("✅ Your identity has been successfully verified!")
        verification_status = "PASSED"
    else:
        st.error("❌ Verification failed.")
        verification_status = "FAILED"

    st.write("**Verification Details:**")
    st.markdown(f"""
    - Name Match: {'✅' if details.get('name_match') else '❌'}  
    - Date of Birth Match: {'✅' if details.get('dob_match') else '❌'}  
    - ID Number Match: {'✅' if details.get('id_number_match') else '❌'}  
    - Address Match: {'✅' if details.get('address_match') else '❌'}  
    - Face Match Score: {face_match_score}% {'✅' if face_match_score >= 75 else '❌'}  
    - Document Authenticity: {'✅' if details.get('document_authenticity') else '❌'}  
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
        st.session_state.step = 0
        st.session_state.user_data = {}
        st.session_state.pop('verification_result', None)
        st.rerun()

# ----------- Main Router -------------

def main():
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 0  # Start at API key input
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}

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
        step_verification_result()

if __name__ == "__main__":
    main()
