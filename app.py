import streamlit as st
from PIL import Image
import numpy as np
import json
import io

# -----------------------------
# Helper functions
# -----------------------------

def quantize_image(img, num_colors=4):
    """
    Reduce image to num_colors using Pillow quantization
    """
    img_small = img.convert("RGB").quantize(colors=num_colors, method=Image.MEDIANCUT)
    palette = img_small.getpalette()[:num_colors*3]  # flat list of RGBs
    palette_rgb = [tuple(palette[i:i+3]) for i in range(0, len(palette), 3)]
    data = np.array(img_small)
    return palette_rgb, data

def encode_to_json(img, num_colors=4, downscale=16):
    """
    Encode image to compact JSON
    """
    img_small = img.resize((downscale, downscale))
    palette, indices = quantize_image(img_small, num_colors=num_colors)
    
    symbolic = {
        "width": downscale,
        "height": downscale,
        "palette": palette,
        "pixels": indices.tolist()
    }
    
    json_bytes = json.dumps(symbolic, separators=(',', ':')).encode()
    return symbolic, json_bytes

def decode_from_json(symbolic, upscale=32):
    """
    Decode JSON back to image
    """
    width = symbolic["width"]
    height = symbolic["height"]
    palette = symbolic["palette"]
    pixels = np.array(symbolic["pixels"], dtype=np.uint8)
    
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            img_array[i,j] = palette[pixels[i,j]]
    
    img = Image.fromarray(img_array)
    img_up = img.resize((upscale, upscale), Image.NEAREST)
    return img_up

# -----------------------------
# Streamlit App
# -----------------------------

st.title("Compact Image Encoder (~1 KB)")

st.markdown("""
Upload an image to encode it into a tiny JSON representation (~1 KB for small images) 
and decode it back to a PNG.
""")

# Upload image
uploaded_file = st.file_uploader("Upload an Image", type=["png","jpg","jpeg"])
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Original Image", use_column_width=True)
    
    # Encode
    symbolic, json_bytes = encode_to_json(img, num_colors=4, downscale=16)
    st.success(f"Image encoded successfully! JSON size: {len(json_bytes)} bytes")
    
    # Download JSON
    st.download_button(
        label="Download Encoded JSON",
        data=json_bytes,
        file_name="encoded_image.json",
        mime="application/json"
    )

# Upload JSON to decode
uploaded_json = st.file_uploader("Upload Symbolic JSON to Decode", type=["json"])
if uploaded_json is not None:
    symbolic_data = json.load(uploaded_json)
    canvas = decode_from_json(symbolic_data, upscale=128)
    st.image(canvas, caption="Decoded Image", use_column_width=True)
    
    # Download PNG
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(
        label="Download Decoded PNG",
        data=byte_im,
        file_name="decoded_image.png",
        mime="image/png"
    )
