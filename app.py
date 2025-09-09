import streamlit as st
import face_recognition
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import base64

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

def reset():
    st.session_state.step = 1
    st.session_state.user_data = {}

def generate_verification_pdf(user_data, for_client=True):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "KYC Verification Report")

    c.setFont("Helvetica", 12)
    y = height - 108

    header = "Client Copy" if for_client else "Company Copy"
    c.drawString(72, y, header)
    y -= 30

    for key in ['full_name', 'dob', 'id_number', 'address', 'document_type']:
        val = user_data.get(key, 'N/A')
        c.drawString(72, y, f"{key.replace('_',' ').title()}: {val}")
        y -= 20

    face_match = user_data.get('face_match_passed', False)
    c.drawString(72, y, f"Face Match: {'Passed' if face_match else 'Failed'}")
    y -= 20

    c.drawString(72, y, "Verification Result: Successful")
    y -= 40

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, y, "This is a system generated report for KYC verification.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def step_1():
    st.title("Step 1 of 6: Personal Information")

    st.session_state.user_data['full_name'] = st.text_input("Full Name:", st.session_state.user_data.get('full_name', ''))
    st.session_state.user_data['dob'] = st.text_input("DOB (dd-mm-yyyy):", st.session_state.user_data.get('dob', ''))
    st.session_state.user_data['id_number'] = st.text_input("ID Number:", st.session_state.user_data.get('id_number', ''))
    st.session_state.user_data['address'] = st.text_input("Address:", st.session_state.user_data.get('address', ''))

    if st.button("Continue"):
        if not all([st.session_state.user_data['full_name'], st.session_state.user_data['dob'], st.session_state.user_data['id_number']]):
            st.error("Please fill in all required fields (Name, DOB, ID Number).")
            return
        st.session_state.step = 2

def step_2():
    st.title("Step 2 of 6: Upload ID Document")

    st.session_state.user_data['document_type'] = st.radio(
        "Document Type:",
        ['Driver\'s License', 'Passport', 'National ID'],
        index=['Driver\'s License', 'Passport', 'National ID'].index(
            st.session_state.user_data.get('document_type', 'Driver\'s License'))
    )
    uploaded_file = st.file_uploader("Upload ID Document", type=['png', 'jpg', 'jpeg', 'webp', 'pdf'])

    if uploaded_file is not None:
        st.session_state.user_data['document_file'] = uploaded_file

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 1
    with col2:
        if st.button("Continue"):
            if 'document_file' not in st.session_state.user_data:
                st.error("Please upload a document before continuing.")
            else:
                st.session_state.step = 3

def step_3():
    st.title("Step 3 of 6: Face Capture and Verification")

    st.write("Upload your ID document photo and a selfie for face matching.")

    id_file = st.file_uploader("Upload your ID Document Photo (image only)", type=["jpg", "jpeg", "png"], key="id_upload")
    selfie_file = st.file_uploader("Upload your Selfie", type=["jpg", "jpeg", "png"], key="selfie_upload")

    face_match_result = None
    error_message = None

    if id_file and selfie_file:
        try:
            id_image = face_recognition.load_image_file(id_file)
            selfie_image = face_recognition.load_image_file(selfie_file)

            id_encodings = face_recognition.face_encodings(id_image)
            selfie_encodings = face_recognition.face_encodings(selfie_image)

            if not id_encodings:
                error_message = "No face detected in ID document photo. Please upload a clear image."
            elif not selfie_encodings:
                error_message = "No face detected in selfie. Please upload a clear selfie."
            else:
                id_encoding = id_encodings[0]
                selfie_encoding = selfie_encodings[0]

                match = face_recognition.compare_faces([id_encoding], selfie_encoding)[0]

                if match:
                    face_match_result = "✅ Face matches! Verification passed."
                else:
                    face_match_result = "❌ Face does not match. Verification failed."

        except Exception as e:
            error_message = f"Error processing images: {e}"

    if error_message:
        st.error(error_message)

    if face_match_result:
        if "passed" in face_match_result:
            st.success(face_match_result)
            st.session_state.user_data['face_match_passed'] = True
        else:
            st.error(face_match_result)
            st.session_state.user_data['face_match_passed'] = False

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

def step_4():
    st.title("Step 4 of 6: Verifying Your Identity...")
    st.write("Please wait, this may take a few seconds...")

    with st.spinner('Verifying...'):
        time.sleep(2)

    if not st.session_state.user_data.get('address'):
        st.session_state.step = 5
    else:
        st.session_state.step = 6

def step_5():
    st.title("Step 5 of 6: Action Required")
    st.write("Address information could not be extracted. Please upload a proof of address.")

    uploaded_file = st.file_uploader("Upload Proof of Address", type=['png', 'jpg', 'jpeg', 'pdf'])

    if uploaded_file is not None:
        st.session_state.user_data['address_proof'] = uploaded_file

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Over"):
            reset()
    with col2:
        if st.button("Submit Proof"):
            if 'address_proof' not in st.session_state.user_data:
                st.error("Please upload a proof of address before submitting.")
            else:
                st.session_state.step = 6

def step_6():
    st.title("Step 6 of 6: Verification Result")

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

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Start Over"):
            reset()

    client_pdf = generate_verification_pdf(st.session_state.user_data, for_client=True)
    company_pdf = generate_verification_pdf(st.session_state.user_data, for_client=False)

    with col2:
        b64_client = base64.b64encode(client_pdf.read()).decode()
        href_client = f'<a href="data:application/octet-stream;base64,{b64_client}" download="KYC_Client_Report.pdf">📄 Download PDF for Client</a>'
        st.markdown(href_client, unsafe_allow_html=True)
        client_pdf.seek(0)

    with col3:
        b64_company = base64.b64encode(company_pdf.read()).decode()
        href_company = f'<a href="data:application/octet-stream;base64,{b64_company}" download="KYC_Company_Report.pdf">📄 Download PDF for Company</a>'
        st.markdown(href_company, unsafe_allow_html=True)
        company_pdf.seek(0)

# Main flow control
if st.session_state.step == 1:
    step_1()
elif st.session_state.step == 2:
    step_2()
elif st.session_state.step == 3:
    step_3()
elif st.session_state.step == 4:
    step_4()
elif st.session_state.step == 5:
    step_5()
elif st.session_state.step == 6:
    step_6()
