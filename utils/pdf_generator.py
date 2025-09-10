# kyc/utils/pdf_generator.py

from fpdf import FPDF

def create_pdf(result, recipient="client"):
    """Generate a PDF for the client or company with the verification result."""
    pdf = FPDF()
    pdf.add_page()

    # Set title and font
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"{recipient.capitalize()} KYC Verification Result", ln=True, align="C")
    pdf.ln(10)  # Line break

    # Client Details
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Full Name: {result['details'].get('full_name', 'N/A')}", ln=True)
    pdf.cell(200, 10, f"DOB: {result['details'].get('dob', 'N/A')}", ln=True)
    pdf.cell(200, 10, f"ID Number: {result['details'].get('id_number', 'N/A')}", ln=True)
    pdf.cell(200, 10, f"Address: {result['details'].get('address', 'N/A')}", ln=True)
    pdf.ln(10)

    # Verification Details
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Verification Status: {result['status']}", ln=True)
    pdf.cell(200, 10, f"Face Match Score: {result['face_match_score']}%", ln=True)
    pdf.cell(200, 10, f"Document Verified: {'✅' if result['document_verified'] else '❌'}", ln=True)
    pdf.cell(200, 10, f"Name Match: {'✅' if result['name_match'] else '❌'}", ln=True)
    pdf.cell(200, 10, f"DOB Match: {'✅' if result['dob_match'] else '❌'}", ln=True)
    pdf.cell(200, 10, f"Address Match: {'✅' if result['address_match'] else '❌'}", ln=True)

    # Company-specific info
    if recipient == "company":
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Client Name: {result['details'].get('full_name', 'N/A')}", ln=True)
        pdf.cell(200, 10, f"Verified ID Type: {result['details'].get('doc_type', 'N/A')}", ln=True)
        pdf.cell(200, 10, f"Verification Outcome: {result['status']}", ln=True)

    # Output PDF to byte format
    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output
