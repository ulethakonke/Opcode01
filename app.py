import streamlit as st
import numpy as np
import cv2
import json

st.title("Symbol Renderer")

# --- File uploader for your own symbolic data ---
uploaded_file = st.file_uploader("Upload your symbolic.json", type="json")

if uploaded_file is not None:
    symbolic = json.load(uploaded_file)

    def render_symbols(symbolic):
        canvas = np.ones((800, 800, 3), dtype=np.uint8) * 255  # bigger canvas

        for op in symbolic:
            pts = np.array(op.get("points", []), dtype=np.int32)

            if pts.size == 0:
                continue  

            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(canvas, [pts], isClosed=True, color=(0, 0, 0), thickness=2)
            cv2.fillPoly(canvas, [pts], color=(200, 200, 200))

        return canvas

    try:
        decoded = render_symbols(symbolic)
        st.image(decoded, channels="BGR", caption="Rendered Symbols")
    except Exception as e:
        st.error(f"Rendering failed: {e}")
else:
    st.info("👆 Upload a symbolic.json file to render your real shapes.")
