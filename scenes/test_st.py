import streamlit as st
import os
from PIL import Image

# Streamlit app title
st.title("Inside Out Characters Sentiment Explorer")

# Directory path for the scenes
dir_path = '/Users/leannchen/Downloads/scenes'

# Path to the colorbar image
colorbar_path = "/Users/leannchen/Downloads/scenes/colorbar.png"

# Get list of available HTML files in the directory
html_files = [f for f in os.listdir(dir_path) if f.endswith('.html') and f.split('.')[0].isdigit()]
html_files.sort(key=lambda f: int(f.split('.')[0]))  # Sort by scene number

scene_numbers = [int(f.split('.')[0]) for f in html_files]

selected_scene = st.select_slider(
    "Select Scene",
    options=scene_numbers)

# Display the colorbar
colorbar_image = Image.open(colorbar_path)
st.image(colorbar_image, caption="Sentiment Scale", use_column_width=False)

# Display the Pyvis visualization
selected_files = open(f"{dir_path}/{selected_scene}.html", 'r', encoding='utf-8')
st.components.v1.html(selected_files.read(), height=2000)
