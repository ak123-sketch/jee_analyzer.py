# jee_analyzer.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
CREDENTIALS_FILE = "jee-analyzer-bot@jee-analyzer.iam.gserviceaccount.com"



# --- Configuration ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1P9Nj77HlgM7Jg7JhdU8y7pYTU_UWK03zjoYBrrL5eWc/edit"
CREDENTIALS_FILE = "jee-analyzer-28e94c261564.json"  # <-- Replace this with your downloaded credentials file
openai.api_key = "your_openai_api_key"        # <-- Replace this with your OpenAI API key

# --- Setup Google Sheet Connection ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1

# --- Load DataFrame from Sheet ---
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("📊 JEE Marks Analyzer with AI Tips")
st.write("Analyze and track your performance in Physics, Chemistry, and Maths tests.")

# --- Input Section ---
with st.form("input_form"):
    test_name = st.text_input("Test Name")
    physics = st.number_input("Physics Marks", 0, 100)
    chemistry = st.number_input("Chemistry Marks", 0, 100)
    maths = st.number_input("Maths Marks", 0, 100)
    submitted = st.form_submit_button("Save & Analyze")

if submitted:
    total = physics + chemistry + maths
    new_row = {
        "Test Name": test_name,
        "Physics": physics,
        "Chemistry": chemistry,
        "Maths": maths,
        "Total": total
    }
    try:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success("✅ Test data added and sheet updated!")
    except Exception as e:
        st.warning(f"⚠️ Failed to write to sheet directly: {e}")

# --- Graph Section ---
if not df.empty:
    st.subheader("📈 Score Trend Over Time")
    st.line_chart(df.set_index("Test Name")[["Physics", "Chemistry", "Maths", "Total"]])

    # --- AI Tips ---
    if st.button("🧠 Get Smart GPT Tips"):
        prompt = f"""
        I am a class 12 JEE aspirant. Here are my recent scores:

        {df.tail(3).to_string(index=False)}

        Give me personalized, smart improvement suggestions for each subject in bullet points.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            advice = response.choices[0].message.content
            st.markdown("### 📌 Personalized Suggestions")
            st.markdown(advice)
        except Exception as e:
            st.error(f"❌ GPT failed: {e}")
else:
    st.info("No data yet. Add your first test above!")
