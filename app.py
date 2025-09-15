import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import json
import io

st.title("Symbolic Image Encoder / Decoder")

st.sidebar.header("1️⃣ Upload an Image to Encode")
uploaded_img = st.sidebar.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

tile_size = st.sidebar.slider("Tile size (smaller = more detail)", min_value=2, max_value=32, value=8)

if uploaded_img:
    img = Image.open(uploaded_img).convert("RGB")
    st.image(img, caption="Original Image", use_column_width=True)
    
    # Encode to symbolic JSON
    pixels = np.array(img)
    h, w = pixels.shape[:2]
    symbolic = []
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            tile = pixels[y:y+tile_size, x:x+tile_size]
            avg_color = tuple(tile.reshape(-1,3).mean(axis=0).astype(int))
            symbolic.append({
                "type": "rectangle",
                "color": list(avg_color),
                "coords": [int(x), int(y), int(min(x+tile_size, w)), int(min(y+tile_size, h))]
            })

    json_bytes = json.dumps(symbolic, indent=2).encode()
    st.download_button("Download Symbolic JSON", data=json_bytes, file_name="symbolic.json", mime="application/json")

st.sidebar.header("2️⃣ Upload Symbolic JSON to Decode")
uploaded_json = st.sidebar.file_uploader("Choose symbolic JSON", type=["json"])

if uploaded_json:
    symbolic_data = json.load(uploaded_json)
    
    # Determine canvas size
    max_x = max(op["coords"][2] if "coords" in op else 0 for op in symbolic_data)
    max_y = max(op["coords"][3] if "coords" in op else 0 for op in symbolic_data)
    
    canvas = Image.new("RGB", (max_x, max_y), (0,0,0))
    draw = ImageDraw.Draw(canvas)
    
    for op in symbolic_data:
        color = tuple(op["color"])
        if op["type"] == "rectangle":
            draw.rectangle(op["coords"], fill=color)
        elif op["type"] == "triangle":
            draw.polygon([tuple(p) for p in op["points"]], fill=color)
        elif op["type"] == "polygon":
            draw.polygon([tuple(p) for p in op["points"]], fill=color)
    
    st.image(canvas, caption="Decoded Image", use_column_width=True)
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("Download PNG", data=buf, file_name="decoded.png", mime="image/png")
