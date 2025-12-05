# app.py
import streamlit as st
import requests

st.set_page_config(page_title="Social Analytics Tool")

st.title("Social Analytics Tool — Railway Deployment")

platform = st.selectbox("Platform", ["Twitter", "Instagram"])
url = st.text_input("Enter URL")

if st.button("Fetch"):
    if not url:
        st.error("Enter a URL")
    else:
        endpoint = {
            "Twitter": "http://localhost:8000/scrape/twitter",
            "Instagram": "http://localhost:8000/scrape/instagram"
        }[platform]

        with st.spinner("Scraping..."):
            try:
                r = requests.get(endpoint, params={"url": url}, timeout=60)
                data = r.json()
                st.success(f"Fetched {data.get('count', 0)} comments")
                st.json(data)
            except Exception as e:
                st.error(str(e))
