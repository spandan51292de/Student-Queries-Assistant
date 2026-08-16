import streamlit as st
import requests

st.set_page_config(page_title="Student AI Assistant", page_icon="🎓", layout="wide")
st.title("🎓 Student RAG Assistant")

API_BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{API_BASE_URL}/auth/login"
UPLOAD_URL = f"{API_BASE_URL}/documents/upload"
CHAT_URL = f"{API_BASE_URL}/chat/query"

if "token" not in st.session_state:
    st.session_state.token = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "active_course" not in st.session_state:
    st.session_state.active_course = 1

with st.sidebar:
    st.header("Authentication")
    if not st.session_state.token:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            auth_response = requests.post(LOGIN_URL, data={"username": username, "password": password})
            if auth_response.status_code == 200:
                st.session_state.token = auth_response.json().get("access_token")
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Login failed. Check credentials.")
    else:
        st.success("Authenticated ✅")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

        st.divider()
        
        st.header("Course Selection")
        selected_course = st.number_input("Course ID", min_value=1, value=st.session_state.active_course)
        
        if selected_course != st.session_state.active_course:
            st.session_state.active_course = selected_course
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

        st.divider()
        st.header("Document Upload")
        uploaded_file = st.file_uploader("Upload a Course PDF", type=["pdf"])
        
        if uploaded_file and st.button("Ingest PDF"):
            with st.spinner(f"Ingesting into Course {selected_course}..."):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"course_id": selected_course} 
                
                upload_res = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
                
                if upload_res.status_code in [200, 202]:
                    st.success(f"PDF strictly added to Course {selected_course}!")
                else:
                    st.error(f"Upload failed: {upload_res.text}")

if st.session_state.token:
    st.caption(f"Currently chatting with context from **Course {st.session_state.active_course}**")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(f"Ask about Course {st.session_state.active_course} materials..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                payload = {
                    "message": prompt,
                    "conversation_id": st.session_state.conversation_id,
                    "course_id": st.session_state.active_course 
                }
                
                response = requests.post(CHAT_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    
                    if not st.session_state.conversation_id:
                        st.session_state.conversation_id = data.get("conversation_id")
                    
                    st.markdown(answer)
                    
                    citations = data.get("citations", [])
                    if citations:
                        with st.expander("View Sources"):
                            for idx, cite in enumerate(citations):
                                st.markdown(f"**Source {idx + 1}:** {cite.get('document_title')}")
                                st.caption(cite.get('snippet'))
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error communicating with backend: {response.status_code}")
else:
    st.info("👈 Please login using the sidebar to start chatting.")