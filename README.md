# Elvirio ViZ 8.0

The rest of this README is gpt4 generated.
### TODO:
- reorganising whole system structure
- using langchain
- async llm streaming with st.write_stream 
- async display of gen images for UX
- use of threading
- voice gen & other

---
## Sales Tag:
Explore the synergy of AI and creativity, visualizing concepts with ease. Elvirio - ViZ is a Streamlit app designed to bridge the gap between imagination and digital visualization, leveraging the power of AI to bring creative ideas to life.

## Features

- **Interactive AI Conversations**: Engage in a creative dialogue with AI, generating textual and visual content based on user prompts.
- **Visual Concept Generation**: Use AI to create images from text descriptions, enhancing creative projects with visual elements.
- **Customizable Image Generation**: Control the number of images, select presets for image styles, and toggle batch image generation for varied results.
- **Image and Chat Download**: Easily download the conversation history and generated images as a zipped file, preserving your creative session.
- **Dynamic Content Display**: Alternating layout for text and images, providing a seamless and engaging user experience.

## Getting Started

### Prerequisites

Ensure you have Python 3.6+ and pip installed on your system. This app relies on several libraries, including Streamlit, Diffusers, and PIL, among others.

### Installation

1. Clone the repository:

```
git clone git@github.com:AlinBolcas/ViZ8.git
```
2. Navigate to the project directory:

```
cd ViZ8
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. Make sure you paste your openai key in .env

### Running the App

Launch the app by running:

```
streamlit run app.py
```

Navigate to the URL provided in your terminal to interact with Elvirio - ViZ.

## Usage

Upon launching the app, follow the on-screen instructions to interact with the AI, generate images, and download your creative session's content.

## Contributing

Contributions to Elvirio - ViZ are welcome! Please refer to `CONTRIBUTING.md` for guidelines on how to make contributions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI and the creators of the Diffusers library for their incredible work on AI models.
- The Streamlit community for providing an excellent platform for developing interactive and beautiful web apps.

---

Elvirio - ViZ is a testament to the incredible possibilities at the intersection of AI and human creativity. We hope it inspires you to explore new creative horizons!
Feel free to modify and adapt this template to suit your project's needs.
