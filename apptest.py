import io
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

st.set_page_config(page_title="AI Landscaping Visualizer", layout="centered")

client = genai.Client(api_key="AIzaSyAGOSBtvK_dJ26fxqeWftb1SwPyJDMh0C8")

st.title("AI Landscaping Visualizer")

uploaded_file = st.file_uploader("Upload a house image", type=["png", "jpg", "jpeg"])
description = st.text_area("Describe the project")
project_type = st.selectbox("Project Type", ["Landscaping", "House Addition", "New Construction"])
style = st.selectbox("Style", ["Modern", "Classic", "Brick", "Minimalist"])
theme_color = st.color_picker("Theme color", "#4CAF50")
budget = st.selectbox("Budget", ["Under $5,000", "$5,000 - $15,000", "$15,000+"])
audio_file = st.file_uploader("Audio (optional)", type=["mp3", "wav", "m4a"])

if st.button("Generate Plan"):
    if uploaded_file is None:
        st.error("Upload an image")

    elif description.strip() == "":
        st.error("Add a description")

    else:
        transcribed_text = ""

        if audio_file is not None:
            try:
                audio_response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=["Transcribe this audio file:", audio_file]
                )
                transcribed_text = audio_response.text

                st.subheader("Audio Transcription")
                st.write(transcribed_text)

            except Exception as e:
                st.error(f"Audio error: {e}")

        full_description = description

        if transcribed_text:
            full_description += "\n\nAdditional details from audio:\n" + transcribed_text

        image_input = Image.open(uploaded_file)

        image_prompt = f"""
Edit this house image into a realistic exterior redesign.

Project type: {project_type}
Style: {style}
Theme color: {theme_color}
Budget: {budget}
User request: {description}

Keep the house realistic and believable.
Preserve the main structure and camera angle.
Only change the exterior features needed for the redesign.
"""

        text_prompt = f"""
A homeowner wants a {style.lower()} {project_type.lower()} project.

Budget: {budget}
Color: {theme_color}
Description: {description}

Keep the response short and professional.

Format it exactly like this:

COST ESTIMATE
Labor: ...
Materials: ...
Permits: ...
Total: ...

TIMELINE
1. ...
2. ...
3. ...
4. ...

DISCLAIMER
This is an initial, informal, AI-generated ballpark estimate. It is non-binding and requires an on-site contractor visit for an official quote.

Do not include long explanations.
Do not include extra paragraphs.

Do NOT put everything on one line.
Use bullet points and spacing.
"""

        generated_image = None
        image_error = None

        try:
            image_response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=[image_prompt, image_input],
                config=types.GenerateContentConfig(response_modalities=["IMAGE"])
            )

            for candidate in image_response.candidates:
                for part in candidate.content.parts:
                    if getattr(part, "inline_data", None):
                        generated_image = part.inline_data.data
                        break
                if generated_image is not None:
                    break

        except Exception as e:
            image_error = str(e)

        try:
            text_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=text_prompt
            )
            text_output = text_response.text
        except Exception as e:
            text_output = f"Error: {e}"

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Before")
            st.image(image_input, use_container_width=True)

        with col2:
            st.subheader("After")
            if generated_image is not None:
                img = Image.open(io.BytesIO(generated_image))
                st.image(img, use_container_width=True)
            else:
                st.info("AI image generation is unavailable for the current API project quota.")
                if image_error:
                    st.caption(image_error)

        st.subheader("AI Estimate")
        st.markdown(text_output)

        if audio_file:
            st.write("Audio uploaded")