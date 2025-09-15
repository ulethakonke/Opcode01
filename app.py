# app.py
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import json
import zipfile
from io import BytesIO

st.title("Symbolic Image Encoder & Renderer")

# ---------------- Upload ---------------- #
uploaded_file = st.file_uploader(
    "Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Original Image", use_column_width=True)

    # ---------------- Encode ---------------- #
    def encode_image(image, max_shapes=50):
        """Convert image to symbolic shapes (triangles)"""
        image_small = image.resize((64, 64))
        data = np.array(image_small)
        h, w, _ = data.shape

        # Simple color quantization: take mean of blocks
        symbolic = []
        step = max(1, int(np.sqrt(64*64 / max_shapes)))
        idx = 0
        for y in range(0, h, step):
            for x in range(0, w, step):
                color_block = data[y:y+step, x:x+step].mean(axis=(0,1))
                color = [int(c) for c in color_block]
                points = [[x, y], [x+step, y], [x+step//2, y+step]]
                symbolic.append({
                    "type": "triangle",
                    "color": color,
                    "points": points
                })
                idx += 1
                if idx >= max_shapes:
                    break
            if idx >= max_shapes:
                break
        return symbolic

    symbolic = encode_image(img)
    st.write("Symbolic shapes generated:", len(symbolic))

    # ---------------- Render ---------------- #
    def render_symbols(symbolic, size=(512,512)):
        canvas = Image.new("RGB", size, (0,0,0))
        draw = ImageDraw.Draw(canvas)
        for op in symbolic:
            if op["type"] == "triangle":
                pts = [tuple(p) for p in op["points"]]
                draw.polygon(pts, fill=tuple(op["color"]))
        return canvas

    rendered = render_symbols(symbolic)
    st.image(rendered, caption="Rendered Symbolic Image", use_column_width=True)

    # ---------------- Download ---------------- #
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("symbolic.json", json.dumps(symbolic, indent=2))
    st.download_button(
        label="Download symbolic.zip",
        data=buffer.getvalue(),
        file_name="symbolic.zip",
        mime="application/zip"
    )
