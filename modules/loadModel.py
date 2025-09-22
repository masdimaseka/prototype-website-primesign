import streamlit as st
import os

@st.cache_resource
def load_model_files():
    MODEL_DIR = 'weights'
    model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith('.pt')]
    return model_files