from fpdf import FPDF

def generate_pdf(result: dict, id_img_path: str, captured_img_path: str) -> str:
    """
    Generate a PDF report for the face verification result.

    Args:
        result (dict): Verification result from DeepFace.
        id_img_path (str): Path to the ID proof image.
        captured_img_path (str): Path to the captured image.

    Returns:
        str: The filename of the generated PDF.
    """
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "KYC Face Verification Report", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Match Found: {result['verified']}", ln=True)
    pdf.cell(0, 10, f"Distance: {result['distance']:.4f}", ln=True)
    pdf.cell(0, 10, f"Threshold: {result['threshold']}", ln=True)
    pdf.cell(0, 10, f"Confidence: {result.get('confidence', 'N/A'):.2f}%", ln=True)

    # Optionally, add the images to the PDF
    pdf.ln(10)
    pdf.cell(0, 10, "ID Proof Image:", ln=True)
    pdf.image(id_img_path, x=10, w=80)
    
    pdf.ln(60)  # space for the first image
    pdf.cell(0, 10, "Captured Image:", ln=True)
    pdf.image(captured_img_path, x=10, w=80)

    output_pdf = "verification_report.pdf"
    pdf.output(output_pdf)

    return output_pdf
