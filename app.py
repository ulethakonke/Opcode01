# filename: app.py
import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import json
import io

st.set_page_config(page_title="Symbolic Image Codec", layout="wide")

st.title("🖼️ Symbolic Image Encoder & Decoder")

# -----------------------------
# Helper functions
# -----------------------------
def convert_for_json(obj):
    """Recursively convert NumPy numbers/arrays and tuples to Python types"""
    if isinstance(obj, dict):
        return {k: convert_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, np.ndarray)):
        return [convert_for_json(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    return obj

def encode_image(img: Image.Image):
    """Encode an image to symbolic JSON (triangles demo)"""
    img = img.convert("RGB")
    w, h = img.size
    arr = np.array(img)

    symbolic = []
    # Simple demo: split into 9x9 pixel blocks as triangles
    block_size = 9
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            block = arr[y:y+block_size, x:x+block_size]
            # Average color of the block
            avg_color = tuple(map(int, block.reshape(-1,3).mean(axis=0)))
            # Triangle coordinates
            triangle = {
                "type": "triangle",
                "color": avg_color,
                "points": [
                    [x, y],
                    [min(x+block_size, w), y],
                    [x + block_size//2, min(y+block_size, h)]
                ]
            }
            symbolic.append(triangle)
    return symbolic, w, h

def render_symbols(symbolic, width=None, height=None):
    """Render symbolic JSON into a PIL Image"""
    # Determine canvas size if not provided
    if width is None or height is None:
        max_x = max(max(p[0] for p in op["points"]) for op in symbolic) + 1
        max_y = max(max(p[1] for p in op["points"]) for op in symbolic) + 1
    else:
        max_x, max_y = width, height

    canvas = Image.new("RGB", (max_x, max_y), (0,0,0))
    draw = ImageDraw.Draw(canvas)
    for op in symbolic:
        color = tuple(map(int, op["color"]))
        if op["type"] == "triangle":
            points = [tuple(map(int, p)) for p in op["points"]]
            draw.polygon(points, fill=color)
        # Add more types here if needed
    return canvas

# -----------------------------
# Encode Section
# -----------------------------
st.header("1️⃣ Upload an Image to Encode")
uploaded_file = st.file_uploader("Choose an image file", type=["jpg","jpeg","png"])
if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Original Image", use_column_width=True)
    
    if st.button("Encode Image to JSON"):
        symbolic, w, h = encode_image(img)
        symbolic_clean = convert_for_json(symbolic)
        json_bytes = json.dumps(symbolic_clean, indent=2).encode()
        st.success(f"Image encoded successfully! Symbolic items: {len(symbolic)}")
        st.download_button(
            label="Download JSON",
            data=json_bytes,
            file_name="symbolic.json",
            mime="application/json"
        )

# -----------------------------
# Decode Section
# -----------------------------
st.header("2️⃣ Upload Symbolic JSON to Decode")
json_file = st.file_uploader("Choose a symbolic JSON file", type=["json"], key="json_decode")
if json_file:
    symbolic_data = json.load(json_file)
    canvas = render_symbols(symbolic_data)
    st.image(canvas, caption="Decoded Image", use_column_width=True)
    
    # Prepare PNG for download
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    buf.seek(0)
    st.download_button(
        label="Download PNG",
        data=buf,
        file_name="decoded.png",
        mime="image/png"
    )
