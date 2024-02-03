# ui.py
import streamlit as st
from PIL import Image
from utils import calc_dynamic_height

def set_custom_css():
    """Sets custom CSS styles for Streamlit elements."""
    st.markdown(
        """
        <style>
        /* Style for the "Clear All" button */
        button:contains("Clear All") {
            width: 60%; /* Smaller width for the button */
            height: 2em; /* Smaller height for the button */
            margin: 0 auto; /* Center button in the div */
        }
        div.stButton > button:first-child {
            width: 100%;
            height: 3em; /* Larger button */
            margin: 0 auto; /* Center button in the div */
        }
        /* Style for file uploader */
        div.stFileUploader > div {
            height: 2em; /* Smaller height for file uploader */
        }
        /* Style for text input */
        div.stTextInput > div > div > input {
            height: 3em; /* Larger input field */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def display_entry(entry, idx, alternating):
    """
    Display a single conversation entry with optional images in an alternating layout.
    """
    # Define combined message
    combined_message = f"You: {entry['human']}\n\nViZ: {entry['ai']}"
    if 'image_prompt' in entry:
        combined_message += f"\n\nImage Prompt: {entry['image_prompt']}"


    if 'image_ids' in entry and entry['image_ids']:
        # Calculate dynamic height for the text area
        dynamic_height = calc_dynamic_height(combined_message, False)  # Assuming full width for simplicity

        # When there's a single image
        if len(entry['image_ids'])==1:
            # Decide column order based on the alternating flag
            if alternating:
                col1, col2 = st.columns(2)
                with col1:
                    st.text_area(f"Reply: {idx}", combined_message, height=dynamic_height, key=f"message_{idx}")
                with col2:
                    img = st.session_state.generated_images[entry['image_ids'][0]]
                    image_caption = f"{entry['image_prompt'][:250]}..." if 'image_prompt' in entry else ""
                    st.image(img, caption=image_caption, use_column_width=True)
            else:
                col1, col2 = st.columns(2)
                with col2:
                    st.text_area(f"Reply: {idx}", combined_message, height=dynamic_height, key=f"message_{idx}")
                with col1:
                    img = st.session_state.generated_images[entry['image_ids'][0]]
                    image_caption = f"{entry['image_prompt'][:250]}..." if 'image_prompt' in entry else ""
                    st.image(img, caption=image_caption, use_column_width=True)
        else:
            # For multiple images, display them in a two-column grid below the combined message
            st.text_area(f"Reply: {idx}", combined_message, height=dynamic_height, key=f"message_{idx}")
            cols = st.columns(2)
            for i, image_id in enumerate(entry['image_ids']):
                img = st.session_state.generated_images[image_id]
                image_caption = f"{entry['image_prompt'][:250]}..." if 'image_prompt' in entry else ""
                cols[i % 2].image(img, caption=image_caption, use_column_width=True)
    else:
        # Calculate dynamic height for the text area
        dynamic_height = calc_dynamic_height(combined_message, True)  # Assuming full width for simplicity

        # If no images, just display the combined message
        st.text_area(f"Reply: {idx}", combined_message, height=dynamic_height, key=f"message_{idx}")

    # Flip the alternating flag for the next entry if there was an image to maintain pattern
    if 'image_ids' in entry and entry['image_ids']:
        alternating = not alternating

    return alternating

def upload_widget(key="image"):
    uploaded_file = st.file_uploader("Upload Image:", type=["jpg", "png"], key=key)
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            return image
        except Exception as e:
            st.error(f"Error: {e}")
    return None

def instructions_field(default_text='', key=None):
    """Create a multi-line text input field."""
    # name = "Chat: (generates images with any of the keywords: stage, art, make, image, design, etc)"
    return st.text_area("Chat:", value=default_text, height=100, key=key)  # ,  You can adjust the height as needed

def image_strength_slider(key="strength"):
    return st.slider("Image Influence:", 0.5, 1.0, 0.85, key=key)

def number_of_images_slider(key="num_images"):
    return 
