from groq import Groq
import streamlit as st

def generate_dataset_summary(df, failures, scores):

    try:

        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"]
        )

        issues = []

        for failure in failures:
            issues.append(failure["issue"])

        dataset_preview = df.head(50).to_string()

        prompt = f"""
You are a Data Quality Expert.

Dataset Information:
Rows: {len(df)}
Columns: {len(df.columns)}

Dataset Preview (first 50 rows):
{dataset_preview}

Issues Found:
{issues}

Data Quality Score:
Overall: {scores['overall']}

Completeness: {scores['completeness']}
Validity: {scores['validity']}
Uniqueness: {scores['uniqueness']}
Consistency: {scores['consistency']}

Generate:

1. Dataset Summary
2. Data Quality Score /100
3. Root Cause Analysis
4. Business Impact
5. Recommended Actions

Keep response professional and under 250 words.
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

        return f"""
AI Summary unavailable.

Reason:
{str(e)}
"""