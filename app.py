import streamlit as st
import numpy as np
from PIL import Image
import io
import base64
import json
import zlib

# -------------------------------
# Helper functions
# -------------------------------

def image_to_symbolic(img, grid_size=32):
    """Convert image to low-res symbolic representation."""
    img_small = img.resize((grid_size, grid_size))
    img_arr = np.array(img_small)
    symbolic = []
    for y in range(grid_size):
        for x in range(grid_size):
            color = img_arr[y, x].tolist()
            symbolic.append({"x": x, "y": y, "color": color})
    return symbolic, img_small.size

def extract_patches(img, patch_size=16, threshold=30):
    """Extract patches where color differs from low-res symbolic image."""
    img_arr = np.array(img)
    patches = []
    h, w = img_arr.shape[:2]
    for y in range(0, h, patch_size):
        for x in range(0, w, patch_size):
            patch = img_arr[y:y+patch_size, x:x+patch_size]
            # Calculate variance to decide if patch is needed
            if patch.var() > threshold:
                pil_patch = Image.fromarray(patch)
                buf = io.BytesIO()
                pil_patch.save(buf, format="PNG", optimize=True)
                b64 = base64.b64encode(buf.getvalue()).decode()
                patches.append({"x": x, "y": y, "data": b64})
    return patches

def encode_image(img, grid_size=32, patch_size=16):
    symbolic, size = image_to_symbolic(img, grid_size)
    patches = extract_patches(img, patch_size)
    encoded = {
        "width": img.width,
        "height": img.height,
        "grid_size": grid_size,
        "patch_size": patch_size,
        "symbolic": symbolic,
        "patches": patches
    }
    return encoded

def decode_image(encoded):
    width = encoded["width"]
    height = encoded["height"]
    grid_size = encoded["grid_size"]
    patch_size = encoded["patch_size"]
    
    canvas = Image.new("RGB", (width, height))
    symbolic = encoded["symbolic"]
    sym_img = Image.new("RGB", (grid_size, grid_size))
    sym_pixels = sym_img.load()
    for p in symbolic:
        x, y = p["x"], p["y"]
        sym_pixels[x, y] = tuple(p["color"])
    # Upscale symbolic to full size
    sym_full = sym_img.resize((width, height), Image.NEAREST)
    canvas.paste(sym_full)
    
    # Apply patches
    for patch in encoded["patches"]:
        patch_data = base64.b64decode(patch["data"])
        patch_img = Image.open(io.BytesIO(patch_data))
        canvas.paste(patch_img, (patch["x"], patch["y"]))
    return canvas

# -------------------------------
# Streamlit UI
# -------------------------------

st.title("Hybrid Symbolic + Patch Image Codec")

# Upload image
uploaded_file = st.file_uploader("Upload Image (PNG/JPG)", type=["png", "jpg", "jpeg"])
if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Original Image", use_column_width=True)
    
    # Encode
    encoded = encode_image(img)
    json_bytes = json.dumps(encoded, indent=2).encode()
    
    st.success(f"Image encoded! JSON size: {len(json_bytes)//1024} KB")
    
    # Download JSON
    st.download_button(
        label="Download Encoded JSON",
        data=json_bytes,
        file_name="encoded_image.json",
        mime="application/json"
    )

# Upload JSON to decode
json_file = st.file_uploader("Upload Encoded JSON to Decode", type=["json"])
if json_file:
    encoded_data = json.load(json_file)
    canvas = decode_image(encoded_data)
    st.image(canvas, caption="Decoded Image", use_column_width=True)
    
    # Download decoded PNG
    buf = io.BytesIO()
    canvas.save(buf, format="PNG", optimize=True)
    st.download_button(
        label="Download Decoded PNG",
        data=buf.getvalue(),
        file_name="decoded.png",
        mime="image/png"
    )
