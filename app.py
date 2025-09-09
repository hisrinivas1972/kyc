import streamlit as st
from fpdf import FPDF
import io
import time

# Add face_recognition import
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

# Function to get face encoding
def get_face_encoding(img_bytes):
    img = face_recognition.load_image_file(io.BytesIO(img_bytes))
    enc = face_recognition.face_encodings(img)
    return enc[0] if enc else None

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
        st.session_state.verification_done = False
        st.session_state.verification_passed = False
        st.session_state.step = 2
        st.rerun()

# Step 2: Upload Document
def step_upload_document():
    st.header("Step 2 of 6: Upload ID Document")
    doc_type = st.radio("Document Type:", ['Driver\'s License', 'Passport', 'National ID'],
        index=['Driver\'s License','Passport','National ID'].index(
            st.session_state.user_data.get('document_type','Driver\'s License')))
    uploaded_file = st.file_uploader("Upload Document (png, jpg, jpeg, pdf):", type=['png','jpg','jpeg','pdf'])
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Continue"):
            if not uploaded_file:
                st.warning("Please upload a document.")
                return
            st.session_state.user_data['document_type'] = doc_type
            st.session_state.user_data['document_file'] = uploaded_file.getvalue()
            st.session_state.verification_done = False
            st.session_state.verification_passed = False
            st.session_state.step = 3
            st.rerun()

# Step 3: Face Capture & Matching
def step_face_capture():
    st.header("Step 3 of 6: Face Capture & Match")
    selfie = st.camera_input("Take a clear selfie")
    if selfie:
        st.session_state.user_data['selfie'] = selfie.getvalue()
        st.image(selfie, caption="Your Selfie", width=200)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Continue"):
            if 'selfie' not in st.session_state.user_data:
                st.warning("Please capture a selfie.")
                return
            id_enc = get_face_encoding(st.session_state.user_data.get('document_file', b''))
            selfie_enc = get_face_encoding(st.session_state.user_data['selfie'])
            if not id_enc or not selfie_enc:
                st.error("Face not detected in ID or selfie. Try again.")
                return
            distance = face_recognition.face_distance([id_enc], selfie_enc)[0]
            match = distance < 0.6  # Tune threshold
            st.session_state.user_data['face_match'] = match
            st.session_state.user_data['face_distance'] = distance
            st.session_state.step = 4
            st.rerun()

# Step 4: Verifying
def step_verifying():
    st.header("Step 4 of 6: Verifying")
    st.write("Simulating verification…")
    time.sleep(2)
    face_match = st.session_state.user_data.get('face_match', False)
    address_present = bool(st.session_state.user_data.get('address'))
    if face_match and address_present:
        st.session_state.verification_passed = True
        st.session_state.step = 6
    elif face_match:
        st.session_state.verification_passed = False
        st.session_state.step = 5
    else:
        st.session_state.verification_passed = False
        st.session_state.step = 7
    st.rerun()

# Step 5: Proof of Address
def step_address_proof():
    st.header("Step 5 of 6: Proof of Address Required")
    uploaded = st.file_uploader("Upload Proof of Address (png, jpg, jpeg, pdf):", type=['png','jpg','jpeg','pdf'])
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.user_data = {}
            st.rerun()
    with col2:
        if st.button("Submit"):
            if not uploaded:
                st.warning("Upload proof first.")
                return
            st.session_state.user_data['address_proof'] = uploaded.getvalue()
            st.session_state.step = 6
            st.rerun()

# Step 6: Result
def step_result():
    st.header("Step 6: Verification Result")
    passed = st.session_state.verification_passed
    face_dist = st.session_state.user_data.get('face_distance', None)
    st.write("Face Match:", "✅" if passed else "❌")
    if face_dist is not None:
        st.write(f"Face Distance: {face_dist:.3f}")
    address_present = "Yes" if st.session_state.user_data.get('address') or st.session_state.user_data.get('address_proof') else "No"
    st.write("Address Present:", address_present)

    client_pdf_text = f"""Client Name: {st.session_state.user_data.get('full_name')}\nVerification: {('PASS' if passed else 'FAIL')}"""
    company_pdf_text = client_pdf_text

    if st.button("Download PDFs"):
        st.download_button("Client PDF", data=create_pdf(client_pdf_text),
                           file_name="client_result.pdf", mime="application/pdf")
        st.download_button("Company PDF", data=create_pdf(company_pdf_text),
                           file_name="company_summary.pdf", mime="application/pdf")
    if st.button("Start Over"):
        st.session_state.user_data = {}
        st.session_state.verification_passed = False
        st.session_state.step = 1
        st.rerun()

# Step 7: Failed
def step_failed():
    st.header("Step 7: Face Match Failed")
    st.error("Your face did not match the ID.")
    if st.button("Try Again"):
        st.session_state.step = 3
        st.rerun()
    if st.button("Start Over"):
        st.session_state.user_data = {}
        st.session_state.step = 1
        st.rerun()

# Main router
def main():
    st.write(f"DEBUG: Current STEP = {st.session_state.step}")
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
        step_address_proof()
    elif step == 6:
        step_result()
    elif step == 7:
        step_failed()

if __name__ == "__main__":
    main()
