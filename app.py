# kyc/app.py

import streamlit as st
from services.gemini_service import verify_identity_with_gemini
from utils.pdf_generator import create_pdf
import io

# ---------------------------
# Sidebar Progress Tracker
# ---------------------------
def render_progress():
    steps_list = [
        "Enter API Key",
        "Personal Info",
        "Upload Document",
        "Capture Selfie",
        "Verification",
        "Results"
    ]
    st.sidebar.markdown("## 📍 Progress")
    for i, label in enumerate(steps_list):
        if i == st.session_state.step:
            st.sidebar.write(f"➡️ **{label}**")
        elif i < st.session_state.step:
            st.sidebar.write(f"✅ {label}")
        else:
            st.sidebar.write(f"🔒 {label}")

# ---------------------------
# Step 0: Gemini API Key Entry
# ---------------------------
def step_enter_api_key():
    st.title("🔐 Enter Gemini API Key")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        st.session_state.api_key = api_key
        st.session_state.step = 1
        st.rerun()

# ---------------------------
# Step 1: Personal Information
# ---------------------------
def step_personal_info():
    st.title("📝 Step 1: Personal Information")
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
    st.title("🪪 Step 2: Upload ID Document")
    doc_type = st.selectbox("Document Type", ["Passport", "Driver's License", "National ID"])
    doc_file = st.file_uploader("Upload your ID (jpg, png, pdf)", type=["jpg", "jpeg", "png", "pdf"])
    if st.button("Continue"):
        if doc_file:
            import mimetypes
            mime_type, _ = mimetypes.guess_type(doc_file.name)

            st.session_state.user_data["doc_type"] = doc_type
            st.session_state.user_data["doc_file"] = doc_file.read()
            st.session_state.user_data["doc_mime_type"] = mime_type or "image/jpeg"  # fallback
            st.session_state.step = 3
            st.rerun()
        else:
            st.warning("Please upload a document.")

# ---------------------------
# Step 3: Capture Selfie
# ---------------------------
def step_face_capture():
    st.title("🤳 Step 3: Capture Selfie")
    selfie = st.camera_input("Take a clear selfie")
    if selfie:
        st.session_state.user_data["selfie"] = selfie.read()
    if st.button("Continue") and "selfie" in st.session_state.user_data:
        st.session_state.step = 4
        st.rerun()

# ---------------------------
# Step 4: Verification (Gemini)
# ---------------------------
def step_verification():
    st.title("🔎 Step 4: AI Verification in Progress...")

    user_data = st.session_state.user_data
    api_key = st.session_state.api_key

    with st.spinner("Processing with Gemini..."):
        result = verify_identity_with_gemini(
            api_key=api_key,
            id_image_bytes=user_data["doc_file"],
            selfie_bytes=user_data["selfie"],
            input_data=user_data,
            id_mime_type=user_data.get("doc_mime_type", "image/jpeg")
        )

    st.session_state.result = result
    st.session_state.step = 5
    st.rerun()

# ---------------------------
# Step 5: Results + PDF
# ---------------------------
def step_result():
    st.title("✅ Step 5: Verification Result")

    result = st.session_state.result
    passed = result["status"] == "APPROVED"

    if passed:
        st.success("✅ Identity Verified Successfully!")
    elif result["status"] == "ERROR":
        st.error("❌ An error occurred during verification.")
        st.code(result.get("message", "No details."))
        if st.button("🔁 Retry Verification"):
            st.session_state.step = 4
            st.rerun()
        return
    else:
        st.error("❌ Verification Failed.")

    st.markdown("### 🔍 Verification Details")
    st.json(result)

    client_pdf = create_pdf(result, recipient="client")
    company_pdf = create_pdf(result, recipient="company")

    st.download_button("📄 Download Client PDF", data=client_pdf, file_name="client_kyc.pdf", mime="application/pdf")
    st.download_button("🏢 Download Company PDF", data=company_pdf, file_name="company_summary.pdf", mime="application/pdf")

    if st.button("🔄 Start Over"):
        st.session_state.clear()
        st.rerun()

# ---------------------------
# Main Router
# ---------------------------
def main():
    if "step" not in st.session_state:
        st.session_state.step = 0

    render_progress()

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
