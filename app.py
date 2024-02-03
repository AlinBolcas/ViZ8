# app.py
import streamlit as st
import ui
import skills
from utils import download_all

DISPLAY_LIMIT = 50  # Limit for the number of images and responses to display
MAX_HISTORY_ENTRIES = 100  # Maximum number of entries to keep
MAX_IMAGES = 100  # Maximum number of images to keep

def main():
    # Set up layout configuration
    st.set_page_config(layout="wide", page_title="Elvirio ViZ 8.0", initial_sidebar_state="auto")

    # Apply custom CSS styles
    ui.set_custom_css()

    # Initialize session state variables if not already present
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Create top row for "Clear All" button, title, and "Download All" button
    topcol1, topcol2, topcol3 = st.columns([1, 4, 1])

    with topcol1:
        if st.button("Clear Chat", key='clear'):
            st.session_state.generated_images = []
            st.session_state.conversation_history = []

    with topcol2:
        # Title
        st.markdown("<h1 style='text-align: center; margin-top: -10px;'>Elvirio ViZ 8.0</h1>", unsafe_allow_html=True)
           # Tagline
        st.markdown("<h4 style='text-align: center;'>Explore the synergy of AI and creativity, visualizing your ideas with ease.</h4>", unsafe_allow_html=True)
        st.markdown("""
        <p style='text-align: center;'>
        Simply type to start a conversation, use keywords for image generation, and explore various styles with presets. Upload your own images for AI-enhanced transformations or experiment with batch generation for a multitude of ideas. Dive into a seamless blend of AI and creativity, bringing your visions to life.
        </p>
        """, unsafe_allow_html=True)

    with topcol3:
        zip_data, zip_filename = download_all(st.session_state.generated_images, st.session_state.conversation_history)
        st.download_button(label="Download Chat",
                        data=zip_data,
                        file_name=zip_filename,
                        mime="application/zip")
            
    # Adjust the column widths as needed to match your layout preference
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        uploaded_image = ui.upload_widget()

    with col2:
        # Use the multi-line text area for user input
        # default_text = "Decorated interior, Scandinavian style, aesthetic, property staging, interior design, realistic photography."
        default_text = "refurbished decoration, Scandinavian style, property staging, realistic photography"
        user_input = ui.instructions_field(default_text, key="user_input")
        generate_button = st.button('Send', key='send')

    with col3:
        image_nums = st.select_slider(
            label="Number of Images:",
            options=[1, 2, 4, 6, 8, 10],
            value=2  # Setting a default value, adjust as needed
        )
        # Set "Moderate" as the default option by specifying its index (1)
        image_presets = st.radio("Presets:", ["Subtle", "Moderate", "Creative"], index=1, horizontal=True)

        image_toggle = st.toggle("Batch Toggle (may take a while)", False, key="image_toggle")

    # Reserve space for the progress bar and spinner at the desired location
    progress_placeholder = st.empty()
        
    # Container for images and AI responses
    container = st.container()

    # Toggle the spinner based on button click
    show_spinner = False
    if generate_button:
        show_spinner = True

    if show_spinner:
        print("\nSENT BUTTON: PROCESSING REQUEST...\n")
        # Start processing and show spinner
        with st.spinner('Processing your request...'):
            # List of keywords to check in the user_input
            keywords = ["stage", "staging", "imagine", "create", "design", "image", "make", "art", "artwork", "viz", "visual", "visualize", "visualize", "etc"]
            # Convert user_input to lower case to make the check case-insensitive
            user_input_lower = user_input.lower()
            
            # Check if any of the keywords exist in user_input
            if any(keyword in user_input_lower for keyword in keywords):
                print("IMAGE GEN:", user_input_lower, "\n")

                # Generate AI response
                ai_response = skills.OAI_response(user_input, st.session_state.conversation_history)
                image_prompt = skills.format_prompt(ai_response)
                print("\nIMAGE PROMPT:", image_prompt, "\n")

                # Define a list to hold IDs of generated images
                image_ids = []

                # Generate images based on user selection
                if image_toggle:
                    # If batch image generation is toggled
                    generated_images = skills.batch_SDXL_Turbo(prompt=image_prompt, image=uploaded_image, preset=image_presets.lower())
                    for idx, generated_image in enumerate(generated_images):
                        st.session_state.generated_images.append(generated_image)
                        image_ids.append(len(st.session_state.generated_images) - 1)
                        # Update progress for each image in the batch
                        progress_placeholder.progress((idx + 1) / len(generated_images))
                        print("IMG NUMBER:", idx+1, "\n")
                else:
                    # Single image generation, possibly multiple times based on num_images_to_generate
                    for idx in range(image_nums):
                        generated_image = skills.SDXL_Turbo(prompt=image_prompt, image=uploaded_image, preset=image_presets.lower())
                        st.session_state.generated_images.append(generated_image)
                        image_ids.append(len(st.session_state.generated_images) - 1)
                        # Update progress for each image generation iteration
                        progress_placeholder.progress((idx + 1) / image_nums)
                        print("IMG NUMBER:", idx+1, "\n")

                # Update conversation history with generated images' IDs
                st.session_state.conversation_history.append({
                    "human": user_input,
                    "ai": ai_response,
                    "image_prompt": image_prompt,  # Include the image prompt used for generation
                    "image_ids": image_ids  # List of IDs for generated images
                })

            else:
                print("NORMAL TEXT...\n")
                # User input does not include '/stage', respond with message only
                ai_response = skills.OAI_response(user_input, st.session_state.conversation_history)
                st.session_state.conversation_history.append({"human": user_input, "ai": ai_response})
                print("AI RESPONSE:", ai_response, "\n")

            # Trim conversation_history if necessary
            if len(st.session_state.conversation_history) > MAX_HISTORY_ENTRIES:
                st.session_state.conversation_history = st.session_state.conversation_history[-MAX_HISTORY_ENTRIES:]

            # Trim generated_images if necessary
            if len(st.session_state.generated_images) > MAX_IMAGES:
                # When trimming images, ensure references in conversation_history remain valid.
                # This might require adjusting image_ids in conversation_history or implementing a more complex management strategy.
                st.session_state.generated_images = st.session_state.generated_images[-MAX_IMAGES:]
                # Example of debugging prints right after updating session state
                print("\nHISTORY:\n", st.session_state.conversation_history, "\n")
        # After all image processing and progress updates are complete
        progress_placeholder.empty()


    alternating = True  # Initialize alternating layout flag
    total_entries = len(st.session_state.conversation_history[:DISPLAY_LIMIT])
    for idx, entry in enumerate(reversed(st.session_state.conversation_history[:DISPLAY_LIMIT]), 1):
        with container:
            inverted_idx = total_entries - idx + 1  # Invert index for display
            alternating = ui.display_entry(entry, inverted_idx, alternating)
            
if __name__ == "__main__":
    main()