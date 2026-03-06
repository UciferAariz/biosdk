
import streamlit as st
import requests
import sys
import os
from PIL import Image

# Add sdk path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sdk.client import BioAuthClient

# --- Configuration ---
st.set_page_config(
    page_title="BioAuth Identity Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar starts closed, toggle works natively
)

# --- CSS Injection ---
def load_css():
    with open("dashboard/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css()
except FileNotFoundError:
    # Fallback if running from root without proper path, usually handled by Dockerfile WORKDIR
    pass

# --- Client Setup ---
api_url = os.getenv("API_URL", "http://localhost:8000")
client = BioAuthClient(base_url=api_url)

# --- Sidebar Navigation ---
st.sidebar.title("ACCESS CONTROL")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "MODULE SELECTION",
    ["COMMAND CENTER", "ENROLLMENT", "VERIFICATION", "IDENTIFICATION"]
)

st.sidebar.markdown("---")

# --- Helper Functions for Animations ---
def show_success(message):
    st.markdown(f"""
    <div class="glass-card success-glow">
        <h3 style="color: #00ff9d; margin:0;">ACCESS GRANTED</h3>
        <p style="margin:0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    st.balloons()

def show_failure(message):
    st.markdown(f"""
    <div class="glass-card failure-glow">
        <h3 style="color: #ff0055; margin:0;">ACCESS DENIED</h3>
        <p style="margin:0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)


# --- Pages ---

if page == "COMMAND CENTER":
    st.title("🛡️ SYSTEM STATUS DASHBOARD")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("BACKEND STATUS", "ONLINE", delta="Active")
    with col2:
        st.metric("DATABASE LINK", "SECURE", delta="Supabase")
    with col3:
        # Placeholder stats, could fetch from API if endpoint existed
        st.metric("ENRICHED IDENTITIES", "---") 
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("RUN SYSTEM DIAGNOSTICS"):
        try:
            with st.spinner("Pinging Neural Core..."):
                res = client.health()
                st.success(f"NEURAL CORE RESPONDING: {res['status'].upper()}")
        except Exception as e:
            st.error(f"SYSTEM FAILURE: {e}")

elif page == "ENROLLMENT":
    st.title("🧬 BIOMETRIC ENROLLMENT")
    st.markdown("Use the optical sensor to register a new identity.")
    
    col_input, col_cam = st.columns([1, 2])
    
    with col_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("IDENTITY DATA")
        name = st.text_input("FULL NAME", placeholder="Enter official name")
        st.caption("Data will be encrypted and stored in the Supabase Vault.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cam:
        st.subheader("OPTICAL SENSOR FEED")
        camera_image = st.camera_input("Scanner Active", label_visibility="hidden")

    if camera_image and name:
        if st.button("PROCESS & ENROLL"):
            with st.spinner("ENCRYPTING & ARCHIVING BIOMETRIC DATA... (This may take 30s on first run)"):
                try:
                    res = client.enroll_face(name, camera_image.getvalue())
                    st.session_state['enroll_status'] = 'success'
                    st.session_state['enroll_msg'] = f"IDENTITY CONFIRMED. ASSIGNED UUID: {res['user_id']}"
                except Exception as e:
                    st.session_state['enroll_status'] = 'failure'
                    st.session_state['enroll_msg'] = f"ENROLLMENT FAILED: {str(e)}"

    # Display persistent status
    if 'enroll_status' in st.session_state:
        if st.session_state['enroll_status'] == 'success':
            show_success(st.session_state['enroll_msg'])
        elif st.session_state['enroll_status'] == 'failure':
            show_failure(st.session_state['enroll_msg'])
        
        # Reset button
        if st.button("CLEAR & RESET"):
            del st.session_state['enroll_status']
            del st.session_state['enroll_msg']
            st.rerun()

elif page == "VERIFICATION":
    st.title("🔐 1:1 IDENTITY VERIFICATION")
    
    col_input, col_cam = st.columns([1, 2])
    
    with col_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("TARGET DATA")
        uid = st.text_input("TARGET UUID", placeholder="Enter User ID to verify")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_cam:
         st.subheader("OPTICAL SENSOR FEED")
         camera_image = st.camera_input("Scanner Active", key="verify_cam", label_visibility="hidden")

    if camera_image and uid:
        if st.button("INITIATE VERIFICATION"):
            with st.spinner("COMPARING BIOMETRIC SIGNATURES..."):
                try:
                    res = client.verify_face(uid, camera_image.getvalue())
                    if res['matched']:
                        st.session_state['verify_status'] = 'success'
                        st.session_state['verify_msg'] = f"IDENTITY VERIFIED. MATCH SCORE: {res['score']:.4f}"
                    else:
                        st.session_state['verify_status'] = 'failure'
                        st.session_state['verify_msg'] = f"IDENTITY MISMATCH. SCORE: {res['score']:.4f}"
                except Exception as e:
                    st.session_state['verify_status'] = 'failure'
                    st.session_state['verify_msg'] = f"PROTOCOL ERROR: {str(e)}"
    
    # Display persistent status
    if 'verify_status' in st.session_state:
        if st.session_state['verify_status'] == 'success':
            show_success(st.session_state['verify_msg'])
        else:
            show_failure(st.session_state['verify_msg'])
        
        if st.button("RESET SCAN"):
            del st.session_state['verify_status']
            del st.session_state['verify_msg']
            st.rerun()

elif page == "IDENTIFICATION":
    st.title("🔍 1:N IDENTIFICATION SEARCH")
    
    tab1, tab2 = st.tabs(["LIVE SCANNER", "EXTERNAL FILE UPLOAD"])
    
    with tab1:
        st.subheader("LIVE OPTICAL FEED")
        camera_image = st.camera_input("Scanner Active", key="ident_cam")
        
        if camera_image:
             if st.button("SCAN DATABASE", key="btn_scan"):
                with st.spinner("SEARCHING VECTOR INDEX..."):
                    try:
                        res = client.identify_face(camera_image.getvalue())
                        if res['matched']:
                            show_success(f"IDENTITY FOUND: USER {res['user_id']} ({res['score']:.4f})")
                        else:
                            st.warning("IDENTITY UNKNOWN / NOT FOUND IN DATABASE")
                    except Exception as e:
                        st.error(f"SEARCH ERROR: {e}")

    with tab2:
        st.subheader("EXTERNAL SOURCE")
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        if uploaded_file:
             if st.button("ANALYZE FILE", key="btn_upload"):
                with st.spinner("ANALYZING ARTIFACT..."):
                    try:
                         res = client.identify_face(uploaded_file.getvalue())
                         if res['matched']:
                            show_success(f"IDENTITY FOUND: USER {res['user_id']} ({res['score']:.4f})")
                         else:
                            st.warning("IDENTITY UNKNOWN")
                    except Exception as e:
                        st.error(f"ANALYSIS ERROR: {e}")
