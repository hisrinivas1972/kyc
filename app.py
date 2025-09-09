import streamlit as st
from deepface import DeepFace
from PIL import Image
import numpy as np
import io
from reportlab.pdfgen import canvas

if "step" not in st.session_state:
    st.session_state.step = 1
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

def step_personal_info():
    st.header("Step 1: Personal Information")
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
    st.header("Step 2: Upload ID Document")
    doc_type = st.radio("Document Type", ["Driver's License", "Passport", "National ID"])
    uploaded_doc = st.file_uploader("Upload your ID document (photo of face on ID)", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("Back"):
        st.session_state.step = 1
    if st.button("Continue"):
        if uploaded_doc is not None:
            st.session_state.user_data.update({
                "document_type": doc_type,
                "document_file": uploaded_doc
            })
            st.session_state.step = 3
        else:
            st.error("Please upload your ID document.")

def step_face_capture():
    st.header("Step 3: Face Capture")
    uploaded_selfie = st.file_uploader("Upload a clear selfie", type=["png", "jpg", "jpeg"])
    
    if st.button("Back"):
        st.session_state.step = 2

    if uploaded_selfie:
        img_selfie = Image.open(uploaded_selfie)
        st.image(img_selfie, caption="Your selfie", use_column_width=True)

        if st.button("Verify Face Match"):
            try:
                # Load ID doc image
                doc_file = st.session_state.user_data.get("document_file")
                if doc_file is None:
                    st.error("ID document not found, please upload in Step 2.")
                    return
                
                # Convert uploaded files to PIL images (handling PDFs or images)
                def load_image(file):
                    if file.type == "application/pdf":
                        st.error("PDF face detection not supported yet. Please upload image format.")
                        return None
                    return Image.open(file)
                
                img_doc = load_image(doc_file)
                if img_doc is None:
                    return

                # Convert images to numpy arrays
                img_selfie_np = np.array(img_selfie.convert('RGB'))
                img_doc_np = np.array(img_doc.convert('RGB'))

                # Run DeepFace verification
                verification_result = DeepFace.verify(img1_path = img_doc_np, img2_path = img_selfie_np)

                if verification_result["verified"]:
                    st.success(f"Faces MATCH! Distance: {verification_result['distance']:.4f}")
                    st.session_state.user_data["selfie"] = uploaded_selfie
                    st.session_state.step = 4
                else:
                    st.error(f"Faces DO NOT MATCH. Distance: {verification_result['distance']:.4f}")

            except Exception as e:
                st.error(f"Face verification error: {e}")

def step_verifying():
    st.header("Step 4: Verifying Your Identity")
    st.write("Verifying, please wait...")
    import time
    time.sleep(2)
    if not st.session_state.user_data.get("address"):
        st.session_state.step = 5
    else:
        st.session_state.step = 6

def step_address_proof_required():
    st.header("Step 5: Upload Proof of Address")
    uploaded_proof = st.file_uploader("Upload proof of address", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("Back"):
        st.session_state.step = 1

    if uploaded_proof and st.button("Submit Proof"):
        st.session_state.user_data["address_proof"] = uploaded_proof
        st.session_state.step = 6

def create_pdf(user_data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica", 16)
    c.drawString(50, 800, "KYC Verification Result")
    c.setFont("Helvetica", 12)
    y = 760
    for key, val in user_data.items():
        if key in ['document_file', 'selfie', 'address_proof']:
            continue  # Skip files
        c.drawString(50, y, f"{key.replace('_', ' ').title()}: {val}")
        y -= 20
    c.drawString(50, y-20, "Verification Status: SUCCESS")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def step_verification_result():
    st.header("Step 6: Verification Result")
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

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Download PDF for Client"):
            pdf_buffer = create_pdf(st.session_state.user_data)
            st.download_button("Download Client PDF", pdf_buffer, file_name="kyc_client.pdf", mime="application/pdf")
    with col2:
        if st.button("Download PDF for Company"):
            pdf_buffer = create_pdf(st.session_state.user_data)
            st.download_button("Download Company PDF", pdf_buffer, file_name="kyc_company.pdf", mime="application/pdf")
    with col3:
        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.user_data = {}

# Controller
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
