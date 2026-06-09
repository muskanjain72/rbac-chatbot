import streamlit as st
import requests

st.set_page_config(page_title="RBAC Chatbot", layout="wide")

st.title("Enterprise RAG-based RBAC Chatbot")
# st.caption("Streamlit frontend for secure, role-aware Q&A")
# st.write("Frontend scaffold is ready.")

query = st.text_input("Ask a question")

if st.button("Send"):
    st.write("User asked:", query)
    
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "query": query
    }
)
#Post request to backend and display response
#the backend server runs on localhost:8000 and has a /chat endpoint that accepts POST requests with a JSON body containing the query. 
# The response from the backend is expected to be a JSON object with an "answer" field that contains the chatbot's response to the user's query.
st.write("Chatbot response:", response.json().get("answer", "No answer received"))