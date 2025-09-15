# app.py
import streamlit as st
import numpy as np
import cv2
import json
import zipfile
from io import BytesIO

st.title("Symbolic Image Encoder & Renderer")

# ---------------- Upload ---------------- #
uploaded_file = st.file_uploader(
    "Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    # Read image
    file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    st.image(img_rgb, caption="Original Image", use_column_width=True)

    # ---------------- Encode ---------------- #
    def encode_image(image, max_shapes=50):
        """Convert image to symbolic shapes (triangles)"""
        h, w, _ = image.shape
        symbolic = []
        
        # Resize small for speed
        small = cv2.resize(image, (64, 64), interpolation=cv2.INTER_AREA)
        small_h, small_w, _ = small.shape
        
        # Simple color quantization
        Z = small.reshape((-1, 3))
        Z = np.float32(Z)
        K = min(max_shapes, 8)  # max colors
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        labels = labels.flatten()

        # Make symbolic shapes
        for i, c in enumerate(centers):
            # triangle example
            points = [[i*6, i*6], [i*6+5, i*6], [i*6+2, i*6+5]]
            symbolic.append({
                "type": "triangle",
                "color": [int(c[0]), int(c[1]), int(c[2])],
                "points": points
            })
        return symbolic

    symbolic = encode_image(img_rgb)
    st.write("Symbolic shapes generated:", len(symbolic))

    # ---------------- Render ---------------- #
    def render_symbols(symbolic, size=(512,512)):
        canvas = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        for op in symbolic:
            if op["type"] == "triangle":
                pts = np.array(op["points"], np.int32)
                cv2.fillPoly(canvas, [pts], color=op["color"].tolist())
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
