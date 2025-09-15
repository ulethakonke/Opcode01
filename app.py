import streamlit as st
import numpy as np
import cv2

# Dummy symbolic data for testing
symbolic = [
    {"points": [(50, 50), (150, 50), (100, 150)]},
    {"points": [(200, 200), (250, 220), (240, 280), (190, 260)]},
]

def render_symbols(symbolic):
    # Create a blank white canvas
    canvas = np.ones((400, 400, 3), dtype=np.uint8) * 255

    for op in symbolic:
        pts = np.array(op.get("points", []), dtype=np.int32)

        # ✅ Skip if empty or wrong shape
        if pts.size == 0:
            continue  

        # Reshape for cv2 polylines/polygons
        pts = pts.reshape((-1, 1, 2))

        # Draw polygon with black border
        cv2.polylines(canvas, [pts], isClosed=True, color=(0, 0, 0), thickness=2)
        cv2.fillPoly(canvas, [pts], color=(200, 200, 200))  # light gray fill

    return canvas

st.title("Symbol Renderer")

try:
    decoded = render_symbols(symbolic)
    st.image(decoded, channels="BGR", caption="Rendered Symbols")
except Exception as e:
    st.error(f"Rendering failed: {e}")
