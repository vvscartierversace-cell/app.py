import streamlit as st
import pdfplumber
import re
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="AI Credit Dispute System", layout="wide")

st.title("AI Credit Report Dispute Generator")

# ---------------------------
# Extract PDF Text
# ---------------------------
def extract_text(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

# ---------------------------
# Trigger Detection Engine
# ---------------------------
def analyze_text(text):
    triggers = []

    if "charge off" in text.lower():
        triggers.append("Charge-off account detected. Verify balance accuracy and post-charge-off reporting.")

    if "120 days late" in text.lower() and "charge off" in text.lower():
        triggers.append("Late payments reported after charge-off (possible structural reporting inconsistency).")

    if "date of first delinquency" not in text.lower():
        triggers.append("Missing Date of First Delinquency (possible reporting violation).")

    balance_matches = re.findall(r"balance[:\s]*\$?([\d,]+)", text.lower())
    if len(balance_matches) > 1:
        triggers.append("Multiple balance entries detected. Cross-check for inconsistencies.")

    if "consumer disputes" not in text.lower():
        triggers.append("Account may not be properly marked as disputed.")

    return triggers

# ---------------------------
# Generate Dispute Letter
# ---------------------------
def generate_letter(name, address, triggers):
    today = datetime.today().strftime("%B %d, %Y")

    letter = f"""{today}

{name}
{address}

RE: Formal Dispute Request

To Whom It May Concern,

This letter serves as a formal dispute regarding inaccurate information appearing on my credit report.

After review, I have identified the following concerns:

"""

    for t in triggers:
        letter += f"- {t}\n"

    letter += """

Please conduct a reasonable reinvestigation and correct or delete any information that cannot be properly verified.

Additionally, please provide the method of verification used in your investigation.

Please complete this investigation within the required timeframe.

Sincerely,

""" + name

    return letter

# ---------------------------
# UI
# ---------------------------
st.sidebar.header("Your Information")

name = st.sidebar.text_input("Full Name")
address = st.sidebar.text_area("Mailing Address")

uploaded_file = st.file_uploader("Upload Credit Report PDF", type=["pdf"])

if uploaded_file:
    st.success("File uploaded successfully.")

    text = extract_text(uploaded_file)
    triggers = analyze_text(text)

    st.subheader("Detected Issues")

    if triggers:
        for t in triggers:
            st.warning(t)
    else:
        st.success("No obvious structural issues detected.")

    if st.button("Generate Dispute Letter"):
        if name and address:
            letter = generate_letter(name, address, triggers)

            st.subheader("Generated Dispute Letter")
            st.text_area("Copy or Download:", letter, height=400)

            # Download button
            st.download_button(
                label="Download Letter",
                data=letter,
                file_name="dispute_letter.txt",
                mime="text/plain"
            )
        else:
            st.error("Please enter your name and address.")
