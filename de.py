import streamlit as st
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import re
from streamlit_drawable_canvas import st_canvas

# -------- PAGE CONFIG --------
st.set_page_config(page_title="AI Doc Editor Pro", layout="wide")

# -------- CUSTOM UI STYLE --------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #ffffff;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 AI Document Editor Pro")

# -------- SIDEBAR --------
st.sidebar.header("⚙️ Controls")
mode = st.sidebar.radio("Mode", ["Smart Fields", "Region Editor"])

uploaded_file = st.file_uploader("Upload Document Image", type=["png", "jpg", "jpeg"])

# -------- OCR FUNCTION --------
def extract_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)

# -------- FIELD DETECTION --------
def detect_fields(text):
    fields = {}

    patterns = {
        "Name": r"Name[:\-]?\s*(.+)",
        "Date": r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
        "Amount": r"\b\d+\.\d{2}\b"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[key] = match.group(1) if key == "Name" else match.group(0)

    return fields

# -------- DRAW TEXT ON IMAGE --------
def draw_text_on_image(image, regions):
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()

    for region in regions:
        x, y, w, h, text = region

        # Cover old area (semi-transparent effect)
        draw.rectangle([x, y, x+w, y+h], fill="white")

        # Draw new text
        draw.text((x + 5, y + 5), text, fill="black", font=font)

    return np.array(img_pil)

# -------- MAIN LOGIC --------
if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)

    col1, col2 = st.columns([1,1])

    with col1:
        st.subheader("📄 Original")
        st.image(image, channels="BGR")

    if mode == "Smart Fields":
        text = extract_text(image)

        st.subheader("🧾 Extracted Text")
        st.text_area("OCR Output", text, height=200)

        fields = detect_fields(text)

        st.subheader("✏️ Edit Fields")
        edited_fields = {}

        for key, value in fields.items():
            edited_fields[key] = st.text_input(key, value)

        if st.button("Generate Clean Version"):
            img = Image.new("RGB", (800, 1000), "white")
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("arial.ttf", 32)
            except:
                font = ImageFont.load_default()

            y = 100
            for k, v in edited_fields.items():
                draw.text((100, y), f"{k}: {v}", fill="black", font=font)
                y += 60

            st.image(img)

    elif mode == "Region Editor":
        st.subheader("🟦 Select Regions to Edit")

        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 255, 0.2)",
            stroke_width=2,
            stroke_color="#00FFAA",
            background_image=Image.fromarray(image),
            update_streamlit=True,
            height=500,
            drawing_mode="rect",
            key="canvas",
        )

        regions_data = []
        edited_regions = []

        if canvas_result.json_data:
            objects = canvas_result.json_data["objects"]

            st.subheader("✏️ Edit Selected Regions")

            for i, obj in enumerate(objects):
                x = int(obj["left"])
                y = int(obj["top"])
                w = int(obj["width"])
                h = int(obj["height"])

                text_val = st.text_input(f"Region {i+1}", "")

                regions_data.append((x, y, w, h))
                edited_regions.append((x, y, w, h, text_val))

        if st.button("Apply Edits to Image"):
            output = draw_text_on_image(image, edited_regions)

            with col2:
                st.subheader("🧾 Edited Output")
                st.image(output, channels="BGR")

            st.download_button(
                "Download Edited Image",
                data=cv2.imencode('.png', output)[1].tobytes(),
                file_name="edited.png",
                mime="image/png"
            )
