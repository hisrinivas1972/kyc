# kyc/app.py


import streamlit as st
from face_verification_service import verify_faces
from pdf_generator import generate_pdf

def main():
    st.title("KYC Verification with Face Recognition")

    id_proof = st.file_uploader("Upload ID Proof Image", type=["jpg", "jpeg", "png"])
    captured_img = st.file_uploader("Upload Captured Image", type=["jpg", "jpeg", "png"])

    if id_proof and captured_img:
        id_proof_path = f"temp_id_proof.{id_proof.name.split('.')[-1]}"
        captured_img_path = f"temp_captured.{captured_img.name.split('.')[-1]}"

        with open(id_proof_path, "wb") as f:
            f.write(id_proof.getbuffer())

        with open(captured_img_path, "wb") as f:
            f.write(captured_img.getbuffer())

        with st.spinner("Verifying faces..."):
            try:
                result = verify_faces(id_proof_path, captured_img_path)
            except Exception as e:
                st.error(f"Verification error: {e}")
                return

        if result:
            st.subheader("Verification Result:")
            st.write(f"**Match Found:** {result['verified']}")
            st.write(f"**Confidence Score:** {round(result['distance'], 4)}")
            st.json(result)

            if result["verified"]:
                if st.button("Generate Verification PDF"):
                    pdf_path = generate_pdf(result, id_proof_path, captured_img_path)
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="Download Verification Report PDF",
                            data=pdf_file,
                            file_name="verification_report.pdf",
                            mime="application/pdf"
                        )

if __name__ == "__main__":
    main()
