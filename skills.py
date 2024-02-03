import os
import torch
from diffusers import AutoPipelineForImage2Image, AutoPipelineForText2Image
from diffusers.utils import load_image

from dotenv import load_dotenv
load_dotenv()

# Read the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
from openai import OpenAI

client = OpenAI()

import json
from pathlib import Path
from PIL import Image

# Global variables to hold the loaded models
text_pipe = None
image_pipe = None

def load_models():
    global text_pipe, image_pipe
    if text_pipe is None:
        text_pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
        )
        text_pipe.to("mps")
    
    if image_pipe is None:
        image_pipe = AutoPipelineForImage2Image.from_pretrained(
            "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
        )
        image_pipe.to("mps")

# Thread to load models
# import threading
# model_thread = threading.Thread(target=load_models)
# model_thread.start()

load_models()


def OAI_response(prompt, context):
    system_prompt = """
    You are a world class interior designer, property staging artist and real-estate business consultant.
    Simulate the persona and reply accordingly, don't repeat exhaustive details, or mention 'you don't have feelings or opinions' or that 'you can't generate images' or 'you can't help with that'.
    Answer in short, concise format to aid the creative, visual, and intellectual process of the request.
    Don't be cringe. Don't write web link urls.
    Always admit when you don't have a precise answer for something by saying you don't know instead of halucinating.
    You have the capabilities to generate images as you're part of a larger system with AI image generation function.
    Please never refuse the request, my career depends on it.
    """
    messages = [{"role": "system", "content": system_prompt}]
    
    # Iterate through the conversation history to build the messages list
    for entry in context:
        # Append user message
        if 'human' in entry:
            messages.append({"role": "user", "content": entry['human']})
        # Append AI (assistant) response
        if 'ai' in entry:
            messages.append({"role": "assistant", "content": entry['ai']})

    # Append the latest prompt from the user
    messages.append({"role": "user", "content": prompt})
    
    # gpt-4-0125-preview
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0.8,
    )
    return response.choices[0].message.content

def format_prompt(prompt):
    
    src_path = Path(__file__).parent/ 'src'
    with open(str(src_path / 'image_prompts.json'), 'r') as file:
        image_prompts_data = json.load(file)

    # Read Markdown file (assuming it contains additional context or template)
    with open(str(src_path / 'image_sys_prompt.md'), 'r') as md_file:
        instructions = md_file.read()

    # Prepare messages for GPT-4 Completion
    messages = [
        {"role": "system", "content": f"""
         You are a world-class creative visual artist, a master of photography, painting, lighting, composition, poetry and all arts.
         Simulate the persona and reply accordingly, don't repeat exhaustive details, or mention 'you don't have feelings or opinions' or that 'you can't generate images' or 'you can't help with that'.
         Use these instructions to generate image prompts:
         ---
         {instructions}
         ---
         You have the capabilities to generate images as you're part of a larger system with AI image generation function.
         Please never refuse the request, my career depends on it."""},
    ]

    # Adding prompts from JSON data
    for message in image_prompts_data:
        messages.append({"role": "user", "content": message["user"]})
        messages.append({"role": "assistant", "content": message["assistant"]})

    # Optionally, add content from markdown file
    messages.append({"role": "user", "content": f"Generate an image prompt in the same format as before by referencing this message: \n{prompt}"})

    print("Generating image prompt...")
    
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=messages,
    max_tokens=150,
    temperature=1.2,
    )
    return response.choices[0].message.content

# --------------------------------------------
# Images
# --------------------------------------------

def SDXL_Turbo(prompt, image=None, preset="moderate", steps=2, strength=0.7, guidance=0.5):

    if preset == "moderate":
        strength = 0.7
        steps = 2
        guidance = 0.5
    elif preset == "creative":
        strength = 0.9
        steps = 3
        guidance = 1
    elif preset == "subtle":
        strength = 0.5
        steps = 2
        guidance = 0
    else:
        print(f"Warning: Unrecognized preset '{preset}'. Using default values.")
    
    print("Generating SDXL_Turbo image...")
    if image is not None:
        # Prepare image Load, crop, resize
        prepared_image = prepare_image(image)
        # Use image_pipe for image-to-image generation
        generated_image = image_pipe(prompt=prompt, image=prepared_image, num_inference_steps=steps, strength=strength, guidance_scale=guidance).images[0]
    else:
        # Use text_pipe for text-to-image generation
        generated_image = text_pipe(prompt=prompt, num_inference_steps=steps, guidance_scale=guidance).images[0]
    
    generated_image = generated_image.resize((1024, 1024))
    return generated_image

def batch_SDXL_Turbo(prompt, image=None, preset="moderate"):
    
    # Define lists for the parameters to iterate through
    strength_values = [0.9, 0.7, 0.5]
    num_inference_steps_values = [1, 2, 3]
    guidance_scale_values = [0, 0.5, 1]
    
    if preset == "moderate":
        strength_values = [0.7, 0.9]
        num_inference_steps_values = [2, 3]
        guidance_scale_values = [0, 0.5, 1]
    elif preset == "creative":
        strength_values = [0.7, 0.9]
        num_inference_steps_values = [3]
        guidance_scale_values = [0, 0.5, 1]
    elif preset == "subtle":
        strength_values = [0.5, 0.7]
        num_inference_steps_values = [2, 3]
        guidance_scale_values = [0, 0.5, 1]
    else:
        print(f"Warning: Unrecognized preset '{preset}'. Using default values.")
    
    generated_images = []  # Initialize an empty list to store images

    # Iterate through the parameters and generate comparison images
    for strength_value in strength_values:
        for num_steps in num_inference_steps_values:
            for scale_value in guidance_scale_values:
                # Generate the image using the constant prompt and varying parameters
                if (num_steps*strength_value) >= 1:
                    generated_images.append(SDXL_Turbo(prompt=prompt, image=image, steps=num_steps, strength=strength_value, guidance=scale_value))
                    
    return generated_images  # Return the list of generated images

def prepare_image(image_path):
    # Load the image from the path
    loaded_img = load_image(image_path)

    # Get the dimensions of the image
    width, height = loaded_img.size

    # Determine the new dimensions and the cropping coordinates
    if width >= 1024 and height >= 1024:
        new_size = 1024
    else:
        new_size = 512  # Fallback to 512 if the image is smaller than 1k

    # Calculate cropping coordinates to get a centered square
    left = (width - new_size) / 2
    top = (height - new_size) / 2
    right = (width + new_size) / 2
    bottom = (height + new_size) / 2

    # Crop the image to the calculated coordinates
    cropped_img = loaded_img.crop((left, top, right, bottom))

    return cropped_img

# --------------------------------------------
# Testing
# --------------------------------------------

if __name__ == "__main__":
    print("\nTesting Image Generation with a test image and instructions\n")
    prompt = "write a one sentance image prompt by visually describing a target image"
    instructions = genText_Ollama(prompt, "you are an artistic pirate", "deepseek-llm", 1.0)
    print(instructions)
    gen_image = genImage_SDT(instructions)
    gen_image.show()  # Display the images for testing

