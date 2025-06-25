import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="JEE Marks Analyzer", layout="centered")

# --- TITLE ---
st.title("📈 JEE Marks Analyzer with AI Tips")
st.markdown("Analyze your performance and get smart AI feedback for PCM subjects.")

# --- GOOGLE SHEET SETUP ---
SHEET_ID = "1P9Nj77HlgM7Jg7JhdU8y7pYTU_UWK03zjoYBrrL5eWc"
SHEET_NAME = "Sheet1"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# --- LOAD DATA ---
try:
    df = pd.read_csv(CSV_URL)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by="Date")
    st.success("✅ Marks loaded from Google Sheets successfully!")
except Exception as e:
    st.error("❌ Failed to load data from Google Sheets.")
    st.exception(e)
    st.stop()

# --- INPUT FORM ---
with st.form("new_test_form"):
    st.subheader("➕ Add New Test Result")
    date = st.date_input("Test Date", datetime.today())
    physics = st.number_input("Physics Marks", 0, 100)
    chemistry = st.number_input("Chemistry Marks", 0, 100)
    maths = st.number_input("Maths Marks", 0, 100)
    submit = st.form_submit_button("Add to Sheet")

if submit:
    new_row = {
        "Date": date.strftime("%Y-%m-%d"),
        "Physics": physics,
        "Chemistry": chemistry,
        "Maths": maths,
    }
    try:
        # Append using gspread (add your credentials if you want full write access)
        sheet = pd.read_csv(CSV_URL)
        sheet = pd.concat([sheet, pd.DataFrame([new_row])], ignore_index=True)
        sheet.to_csv("updated.csv", index=False)
        st.success("✅ Marks added! (You can update manually in Sheet)")
    except Exception as e:
        st.error("⚠️ Failed to write to sheet directly. Try adding manually.")
        st.exception(e)

# --- SHOW GRAPH ---
st.subheader("📊 Score Trends")

for subject in ['Physics', 'Chemistry', 'Maths']:
    st.markdown(f"**{subject}**")
    plt.figure()
    plt.plot(df['Date'], df[subject], marker='o')
    plt.ylabel("Marks")
    plt.xticks(rotation=45)
    st.pyplot(plt)

# --- GPT-BASED AI FEEDBACK ---
st.subheader("🧠 AI Performance Feedback")

# You can replace with your own API key
openai.api_key = "sk-..."  # Replace with your OpenAI API key

try:
    avg_scores = df[['Physics', 'Chemistry', 'Maths']].mean().round(1)
    prompt = (
        f"I'm a JEE aspirant. Based on my average scores: "
        f"Physics: {avg_scores['Physics']}, Chemistry: {avg_scores['Chemistry']}, Maths: {avg_scores['Maths']}. "
        f"Give subject-wise study suggestions and tips to improve."
    )

    with st.spinner("Generating smart tips..."):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        st.success("✅ Here's what AI recommends:")
        st.write(response.choices[0].message.content)
except Exception as e:
    st.warning("⚠️ Couldn't fetch AI feedback. Check your API key or internet.")
