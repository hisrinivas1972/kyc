# kyc/app.py


import streamlit as st
from services.face_verification_service import verify_identity_with_deepface
from utils.pdf_generator import create_pdf

# ---------------------------
# Step 0: API Key Entry (Optional)
# ---------------------------
def step_enter_api_key():
    st.title("🔐 Start KYC Verification")
    if st.button("Start"):
        st.session_state.step = 1
        st.rerun()

# ---------------------------
# Step 1: Personal Information
# ---------------------------
def step_personal_info():
    st.title("Step 1: Personal Information")
    full_name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth")
    id_number = st.text_input("ID Number")
    address = st.text_area("Address")
    if st.button("Continue"):
        st.session_state.user_data = {
            "full_name": full_name,
            "dob": str(dob),
            "id_number": id_number,
            "address": address,
        }
        st.session_state.step = 2
        st.rerun()

# ---------------------------
# Step 2: Upload ID Document
# ---------------------------
def step_upload_document():
    st.title("Step 2: Upload ID Document")
    doc_type = st.selectbox("Document Type", ["Passport", "Driver's License", "National ID"])
    doc_file = st.file_uploader("Upload your ID (jpg, png, pdf)", type=["jpg", "jpeg", "png"])
    if st.button("Continue"):
        if doc_file:
            st.session_state.user_data["doc_type"] = doc_type
            st.session_state.user_data["doc_file"] = doc_file.read()
            st.session_state.step = 3
            st.rerun()
        else:
            st.warning("Please upload a document.")

# ---------------------------
# Step 3: Capture Selfie
# ---------------------------
def step_face_capture():
    st.title("Step 3: Capture Selfie")
    selfie = st.camera_input("Take a clear selfie")
    if selfie:
        st.session_state.user_data["selfie"] = selfie.read()
    if st.button("Continue") and "selfie" in st.session_state.user_data:
        st.session_state.step = 4
        st.rerun()
# ---------------------------
# Step 4: Verification (DeepFace)
# ---------------------------
def step_verification():
    st.title("Step 4: AI Verification in Progress...")

    user_data = st.session_state.user_data

    with st.spinner("Analyzing images with DeepFace..."):
        result = verify_identity_with_deepface(
            id_image_bytes=user_data["doc_file"],
            selfie_bytes=user_data["selfie"],
            input_data=user_data
        )

    st.session_state.result = result
    st.session_state.step = 5
    st.rerun()


# ---------------------------
# Step 5: Results + PDF
# ---------------------------
def step_result():
    st.title("✅ Verification Result")

    result = st.session_state.result
    passed = result["status"] == "APPROVED"

    if passed:
        st.success("✅ Identity Verified Successfully!")
    else:
        st.error("❌ Verification Failed.")

    st.markdown("### Verification Details")
    st.json(result)

    client_pdf = create_pdf(result, recipient="client")
    company_pdf = create_pdf(result, recipient="company")

    st.download_button("📄 Download Client PDF", data=client_pdf, file_name="client_kyc.pdf", mime="application/pdf")
    st.download_button("🏢 Download Company PDF", data=company_pdf, file_name="company_summary.pdf", mime="application/pdf")

    if st.button("🔄 Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ---------------------------
# Main Router
# ---------------------------
def main():
    if "step" not in st.session_state:
        st.session_state.step = 0

    steps = {
        0: step_enter_api_key,
        1: step_personal_info,
        2: step_upload_document,
        3: step_face_capture,
        4: step_verification,
        5: step_result
    }

    steps[st.session_state.step]()

if __name__ == "__main__":
    main()
