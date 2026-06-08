from groq import Groq
import streamlit as st


def generate_root_cause_analysis(df, failures):

    try:

        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"]
        )

        issues = []

        for failure in failures:
            issues.append(failure["issue"])

        prompt = f"""
You are a Senior Data Quality Consultant.

Dataset:
Rows: {len(df)}
Columns: {len(df.columns)}

Issues Found:
{issues}

Generate ONLY:

1. Root Cause Analysis
2. Business Impact
3. Recommended Actions

Use bullet points.
Keep answer short and professional.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"AI Analysis Error: {str(e)}"