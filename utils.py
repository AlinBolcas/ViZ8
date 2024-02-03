# utils.py
from io import BytesIO
from zipfile import ZipFile
import base64
import datetime
import streamlit as st
from PIL import Image

import math, time, random, os, json
from pathlib import Path

import os
import glob

# --------------------------------------------
# used
# --------------------------------------------

def chaos_trigger():
    # Rename the chaotic trigger function for consistency
    t = time.time() % 30  
    return abs(math.sin(t))

def download_all(images, conversation_history):
    # Get current date and time to append to the zip file name
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    zip_filename = f"ViZ-content-{current_datetime}.zip"

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:  # Use 'w' for write mode
        img_folder = 'images/'
        combined_descriptions = "# Conversation History\n\n"

        for i, entry in enumerate(conversation_history, 1):
            human_msg = entry.get("human", "")
            ai_reply = entry.get("ai", "")
            image_prompt = entry.get("image_prompt", "")
            image_ids = entry.get("image_ids", [])

            combined_descriptions += f"## Entry {i}\n\n"
            combined_descriptions += f"**You:** {human_msg}\n\n"
            combined_descriptions += f"**ViZ:** {ai_reply}\n\n"
            if image_prompt:
                combined_descriptions += f"**Image Prompt:** {image_prompt}\n\n"

            for img_id in image_ids:
                if img_id < len(images):
                    img = images[img_id]
                    img_byte_arr = BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    img_filename = f"{img_folder}image_{str(i).zfill(4)}_{str(img_id).zfill(4)}.jpg"
                    zip_file.writestr(img_filename, img_byte_arr.getvalue())
                    combined_descriptions += f"![Image {str(i).zfill(4)}_{str(img_id).zfill(4)}]({img_filename})\n\n"

        zip_file.writestr("conversation.md", combined_descriptions)

    zip_buffer.seek(0)
    return zip_buffer.getvalue(), zip_filename


def calc_dynamic_height(content, is_full_width=True):
    """
    Calculate the dynamic height for a text_area in Streamlit based on the content length.
    
    Parameters:
    - content (str): The text content of the text_area.
    - is_full_width (bool): Indicates whether the text_area spans the full width or half width of the layout.
    
    Returns:
    - int: The calculated dynamic height in pixels.
    """
    # Configurations
    full_width_pixels = 1200  # Approximate width of a full-width text_area in pixels
    half_width_pixels = int(full_width_pixels/2)  # Approximate width for half-width (next to an image)
    average_char_width_pixels = 8  # Estimated average width of a character in pixels
    height_per_line_pixels = 25  # Estimated height per line in pixels, including padding
    
    # Determine the appropriate width based on layout
    text_area_width_pixels = full_width_pixels if is_full_width else half_width_pixels
    
    # Calculate characters per line and total estimated lines
    chars_per_line = text_area_width_pixels // average_char_width_pixels
    content_length = len(content.replace('\n', ' '))  # Replace new lines with spaces for calculation
    estimated_lines = content_length / chars_per_line
    
    # Calculate and return the dynamic height
    dynamic_height = max(100, int(estimated_lines * height_per_line_pixels))  # Ensuring a minimum height
    return dynamic_height

# --------------------------------------------
# legacy
# --------------------------------------------

# def save_image(image, base_name="img_", extension=".png"):
#     if image:
#         output_directory = output_dir()  # Get the output directory
#         existing_files = glob.glob(os.path.join(output_directory, base_name + "*"))
#         next_number = len(existing_files) + 1
#         filename = f"{base_name}{next_number:03}{extension}"
#         path = os.path.join(output_directory, filename)

#         image.save(path)
#         print(f"Image saved as {path}\n")
#         # os.system(f"open {path}")  # Opens the image; adjust command based on your OS
#     else:
#         print("Failed to save image.")
       

# def save_speech(speech_data, filename):
#     try:
#         output_directory = output_dir()  # Get the output directory
#         file_path = os.path.join(output_directory, filename)
        
#         # Assuming speech_data is raw audio data that needs to be written to a file
#         with open(file_path, "wb") as file:
#             file.write(speech_data)
        
#         print(f"Speech saved as {file_path}")
#     except Exception as e:
#         print(f"Failed to save speech: {e}")


# def create_mood_board(directory, output_file, board_size, img_size):
#     images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
#     # Create a new image for the mood board
#     mood_board = Image.new('RGB', board_size, (255, 255, 255))  # white background

#     x_offset = 0
#     y_offset = 0
#     for img_path in images:
#         # Open the image and resize it
#         img = Image.open(img_path)
#         img = img.resize(img_size)

#         # Paste the image into the mood board
#         mood_board.paste(img, (x_offset, y_offset))

#         # Update the x_offset and y_offset for the next image
#         x_offset += img_size[0]
#         if x_offset >= mood_board.width:
#             x_offset = 0
#             y_offset += img_size[1]

#     # Save the mood board
#     mood_board.save(output_file)