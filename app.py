import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure page layout
st.set_page_config(page_title="SalesAI", layout="wide", page_icon="🚀")

# Initialize Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("GEMINI_API_KEY not found. Please add it to your .env file.")

# Set up the model
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 4096,
}

def generate_sales_content(name, title, company, industry, interesting_fact):
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config
    )
    
    prompt = f"""
    You are an expert sales copywriter and strategist. 
    Based on the following prospect details, generate personalized sales outreach content.
    
    Prospect Name: {name}
    Job Title: {title}
    Company Name: {company}
    Industry: {industry}
    Interesting Fact: {interesting_fact}
    
    Respond STRICTLY with a valid JSON object matching this structure:
    {{
      "messages": {{
        "casual": "<casual message under 140 chars>",
        "professional": "<professional message under 200 chars>",
        "bold_value_prop": "<bold message focusing on value under 180 chars>"
      }},
      "follow_up": {{
        "timing": "<Best timing, e.g., 3, 5, or 7 days>",
        "channel": "<Best channel, e.g., Email or LinkedIn>",
        "message": "<A ready-to-send follow-up message>"
      }},
      "objection_handling": [
        {{
          "objection": "<likely objection 1>",
          "response": "<smart response 1>"
        }},
        {{
          "objection": "<likely objection 2>",
          "response": "<smart response 2>"
        }}
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove markdown code blocks if the model included them
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        raw_text = getattr(response, "text", "No text generated") if 'response' in locals() else "No response"
        print(f"JSON Decode Error. Raw response was:\n{raw_text}")
        st.error(f"Error generating content: {e}")
        with st.expander("Show raw response for debugging"):
            st.code(raw_text)
        return None

# --- UI Layout ---

st.title("🚀 SalesAI - Personalized Outreach Generator")
st.markdown("Generate highly personalized sales messages, follow-up strategies, and objection handlers in seconds.")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("🎯 Prospect Details")
    with st.form("prospect_form"):
        prospect_name = st.text_input("Prospect Name", placeholder="e.g., Jane Doe")
        job_title = st.text_input("Job Title", placeholder="e.g., VP of Marketing")
        company_name = st.text_input("Company Name", placeholder="e.g., Acme Corp")
        industry = st.selectbox("Industry", ["SaaS", "Fintech", "Healthcare", "E-commerce", "Other"])
        interesting_fact = st.text_area("One interesting thing about them", placeholder="e.g., just raised Series A, recently won an award...")
        
        submit_button = st.form_submit_button("Generate Outreach Strategy", use_container_width=True)

with col2:
    if submit_button:
        if not api_key:
            st.warning("Please configure your Gemini API Key first.")
        elif not prospect_name or not company_name:
            st.warning("Please fill in at least the Prospect Name and Company Name.")
        else:
            with st.spinner("🧠 Analyzing prospect and crafting strategy..."):
                results = generate_sales_content(
                    prospect_name, job_title, company_name, industry, interesting_fact
                )
            
            if results:
                st.success("✨ Strategy generated successfully!")
                
                # Messages Section
                st.header("1️⃣ Outreach Messages")
                
                st.subheader("Casual (Short & Friendly)")
                st.info(results["messages"]["casual"])
                st.code(results["messages"]["casual"], language=None)
                
                st.subheader("Professional (Formal & Structured)")
                st.info(results["messages"]["professional"])
                st.code(results["messages"]["professional"], language=None)
                
                st.subheader("Bold Value Prop (Direct & Impactful)")
                st.info(results["messages"]["bold_value_prop"])
                st.code(results["messages"]["bold_value_prop"], language=None)
                
                st.divider()
                
                # Follow-up Strategy
                st.header("2️⃣ Follow-up Strategy")
                st.markdown(f"**Timing:** {results['follow_up']['timing']}")
                st.markdown(f"**Channel:** {results['follow_up']['channel']}")
                st.markdown("**Message:**")
                st.code(results['follow_up']['message'], language=None)
                
                st.divider()
                
                # Objection Handling
                st.header("3️⃣ Objection Handling")
                for i, objection in enumerate(results['objection_handling']):
                    with st.expander(f"🛑 Objection {i+1}: {objection['objection']}", expanded=True):
                        st.markdown(f"**Smart Response:**\n{objection['response']}")

