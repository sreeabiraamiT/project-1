# services/digest_service.py
import os
import base64
from datetime import date
from typing import List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from pydantic import BaseModel

class DigestRequest(BaseModel):
    user_id: int
    consumer_number: str
    bill_month: date
    tariff_category: str
    units_consumed: float
    amount_due: float
    ai_summary: str
    saving_tips: List[str]

def create_pdf(data: DigestRequest) -> str:
    pdf_file = "/tmp/electricity_digest.pdf" # Using /tmp is safer for cloud deployments
    styles = getSampleStyleSheet()
    pdf = SimpleDocTemplate(pdf_file)
    
    content = [
        Paragraph("Monthly Electricity Digest", styles["Title"]),
        Spacer(1, 0.2 * inch),
        Paragraph(f"Consumer Number : {data.consumer_number}", styles["BodyText"]),
        Paragraph(f"Bill Month       : {data.bill_month.strftime('%B %Y')}", styles["BodyText"]),
        Paragraph(f"Tariff Category  : {data.tariff_category}", styles["BodyText"]),
        Paragraph(f"Units Consumed   : {data.units_consumed} kWh", styles["BodyText"]),
        Paragraph(f"Amount Due       : ₹{data.amount_due}", styles["BodyText"]),
        Spacer(1, 0.2 * inch),
        Paragraph("AI Summary", styles["Heading2"]),
        Paragraph(data.ai_summary, styles["BodyText"]),
        Spacer(1, 0.2 * inch),
        Paragraph("Energy Saving Tips", styles["Heading2"]),
    ]

    if data.saving_tips:
        tip_items = [ListItem(Paragraph(tip, styles["BodyText"]), bulletType="bullet") for tip in data.saving_tips]
        content.append(ListFlowable(tip_items, bulletType="bullet"))
    else:
        content.append(Paragraph("No energy-saving tips available.", styles["BodyText"]))

    pdf.build(content)
    return pdf_file

def send_email_with_pdf(to_email: str, pdf_path: str, data: DigestRequest):
    html_body = f"""
    <h2>Monthly Electricity Digest</h2>
    <p><strong>Consumer Number:</strong> {data.consumer_number}</p>
    <p><strong>Bill Month:</strong> {data.bill_month.strftime('%B %Y')}</p>
    <p><strong>Tariff Category:</strong> {data.tariff_category}</p>
    <p><strong>Units Consumed:</strong> {data.units_consumed} kWh</p>
    <p><strong>Amount Due:</strong> ₹{data.amount_due}</p>
    <hr>
    <h3>AI Summary</h3>
    <p>{data.ai_summary}</p>
    <hr>
    <h3>Energy Saving Tips</h3>
    <ul>
        {''.join(f'<li>{tip}</li>' for tip in data.saving_tips) or '<li>No tips available.</li>'}
    </ul>
    <p>Your full PDF report is attached.</p>
    """
    message = Mail(
        from_email=os.getenv("FROM_EMAIL", "lifegoeson1568@gmail.com"),
        to_emails=to_email,
        subject="Monthly Electricity Digest",
        html_content=html_body
    )

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    encoded_pdf = base64.b64encode(pdf_data).decode()
    attachment = Attachment(
        FileContent(encoded_pdf),
        FileName("electricity_digest.pdf"),
        FileType("application/pdf"),
        Disposition("attachment")
    )
    message.attachment = attachment

    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    sg.send(message)
