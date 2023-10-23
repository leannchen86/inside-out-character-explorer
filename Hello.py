import streamlit as st
import os
from PIL import Image

# Streamlit app title
st.title("Inside Out Characters Sentiment Explorer")

# Directory path for the scenes
dir_path = 'scenes'

# Check if directory exists
if not os.path.exists(dir_path):
    st.error(f"Directory {dir_path} does not exist.")
    st.stop()

# Get list of available HTML files in the directory
html_files = [f for f in os.listdir(dir_path) if f.endswith('.html') and f.split('.')[0].isdigit()]
html_files.sort(key=lambda f: int(f.split('.')[0]))  # Sort by scene number

scene_numbers = [int(f.split('.')[0]) for f in html_files]

selected_scene = st.select_slider(
    "Select Scene",
    options=scene_numbers)

# Uncomment if you want to display the colorbar image
# colorbar_path = os.path.join(dir_path, "colorbar.png")
# if os.path.exists(colorbar_path):
#     colorbar_image = Image.open(colorbar_path)
#     st.image(colorbar_image, caption='Sentiment Scale')
# else:
#     st.warning(f"Colorbar image not found at {colorbar_path}")

# Ensure the HTML file exists before trying to open it

scene_file_path = os.path.join(dir_path, f"{selected_scene}.html")
if os.path.exists(scene_file_path):
    with open(scene_file_path, 'r', encoding='utf-8') as selected_files:
        st.components.v1.html(selected_files.read(), width=450, height=400, scrolling=False)
else:
    st.error(f"Scene file {selected_scene}.html does not exist.")
