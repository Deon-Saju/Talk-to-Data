import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Talk to Data", page_icon="💬", layout="centered")
st.title("💬 Talk to Data")
st.caption("Ask business questions about the Olist e-commerce data in plain English.")

if "history" not in st.session_state:
    st.session_state.history = []

def render_result(result: dict):
    """Show SQL and data tables for one answer."""
    if result.get("sql"):
        with st.expander("Show SQL"):
            for q in result["sql"]:
                st.code(q, language="sql")
    data = result.get("data")
    if data and data.get("rows"):
        df = pd.DataFrame(data["rows"], columns=data["columns"])
        st.dataframe(df, use_container_width=True)
        # simple chart: one text column + one numeric column
        if df.shape[1] == 2 and pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
            st.bar_chart(df.set_index(df.columns[0]))

# replay earlier messages
for item in st.session_state.history:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item["role"] == "assistant" and item.get("result"):
            render_result(item["result"])

question = st.chat_input("e.g. Which 5 product categories have the highest revenue?")

if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=120)
                resp.raise_for_status()
                result = resp.json()
                st.markdown(result["answer"])
                render_result(result)
                st.session_state.history.append(
                    {"role": "assistant", "content": result["answer"], "result": result}
                )
            except requests.exceptions.ConnectionError:
                st.error("Can't reach the API. Is `uvicorn src.api:app --reload` running?")
            except requests.exceptions.HTTPError:
                st.error(f"The API returned an error: {resp.text[:300]}")
            except Exception as e:
                st.error(f"Something went wrong: {e}")