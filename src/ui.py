
import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="Chat with Your Documents",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- UI Elements ---
st.title("💬 Chat with Your Documents")
st.markdown("This app allows you to ask questions about your documents. Type your question below and press 'Ask' to get an answer from the RAG model.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Backend Communication ---
API_URL = "http://127.0.0.1:8000/query/"

# --- User Input and Interaction ---
if prompt := st.chat_input("What is your question?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Call the backend API
        response = requests.post(API_URL, json={"question": prompt})
        response.raise_for_status()  # Raise an exception for bad status codes

        # Get the answer from the response
        answer = response.json().get("answer", "Sorry, I couldn't get an answer.")

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(answer)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend API: {e}")

