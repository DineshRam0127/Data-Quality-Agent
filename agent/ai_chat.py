from groq import Groq
import streamlit as st

def ask_dataset_question(df, question):

    try:

        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"]
        )

        dataset_preview = df.head(50).to_string()

        prompt = f"""
You are a Data Quality Expert.

Dataset:

{dataset_preview}

User Question:
{question}

Answer based only on the dataset.
Keep answer professional.
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

        return f"Error: {str(e)}"