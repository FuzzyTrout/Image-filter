from flask import Flask, request, jsonify, render_template, send_file
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np
import io
import base64
import cv2
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# ── Filters ──────────────────────────────────────────────────────────────────

def apply_grayscale(img, params=None):
    return img.convert("L").convert("RGB")

def apply_invert(img, params=None):
    return ImageOps.invert(img.convert("RGB"))

def apply_sepia(img, params=None):
    img = img.convert("RGB")
    arr = np.array(img, dtype=np.float64)
    r = np.clip(arr[:,:,0]*0.393 + arr[:,:,1]*0.769 + arr[:,:,2]*0.189, 0, 255)
    g = np.clip(arr[:,:,0]*0.349 + arr[:,:,1]*0.686 + arr[:,:,2]*0.168, 0, 255)
    b = np.clip(arr[:,:,0]*0.272 + arr[:,:,1]*0.534 + arr[:,:,2]*0.131, 0, 255)
    sepia = np.stack([r, g, b], axis=2).astype(np.uint8)
    return Image.fromarray(sepia)

def apply_negative(img, params=None):
    arr = np.array(img.convert("RGB"))
    return Image.fromarray(255 - arr)

def apply_edge_detection(img, params=None):
    gray = np.array(img.convert("L"))
    edges = cv2.Canny(gray, 100, 200)
    return Image.fromarray(edges).convert("RGB")

def apply_sketch(img, params=None):
    gray = np.array(img.convert("L"))
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return Image.fromarray(sketch).convert("RGB")

def apply_pixelate(img, params=None):
    pixel_size = int((params or {}).get("pixel_size", 16))
    w, h = img.size
    small = img.resize((max(1, w // pixel_size), max(1, h // pixel_size)), Image.NEAREST)
    return small.resize((w, h), Image.NEAREST)

def apply_painterly(img, params=None):
    arr = np.array(img.convert("RGB"))
    for _ in range(4):
        arr = cv2.bilateralFilter(arr, 9, 75, 75)
    edges = cv2.Canny(cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY), 80, 120)
    edges_inv = cv2.cvtColor(255 - edges, cv2.COLOR_GRAY2RGB)
    result = cv2.bitwise_and(arr, edges_inv)
    return Image.fromarray(result)

def apply_horizontal_flip(img, params=None):
    return ImageOps.mirror(img)

def apply_vertical_flip(img, params=None):
    return ImageOps.flip(img)

def apply_vignette(img, params=None):
    strength = float((params or {}).get("strength", 1.0))
    strength = max(0.0, min(1.0, strength))
    img = img.convert("RGB")
    arr = np.array(img, dtype=np.float64)
    height, width = arr.shape[:2]

    cx, cy = width / 2.0, height / 2.0
    max_dist = (cx**2 + cy**2) ** 0.5

    xs = np.arange(width)
    ys = np.arange(height)
    xx, yy = np.meshgrid(xs, ys)

    dist = ((xx - cx)**2 + (yy - cy)**2) ** 0.5
    fraction = (dist / max_dist) * strength
    fraction = np.clip(fraction, 0, 1)

    factor = (1.0 - fraction)[:, :, np.newaxis]
    result = np.clip(arr * factor, 0, 255).astype(np.uint8)
    return Image.fromarray(result)


FILTERS = {
    "grayscale":       ("Grayscale",        apply_grayscale),
    "invert":          ("Invert",           apply_invert),
    "sepia":           ("Sepia",            apply_sepia),
    "negative":        ("Negative",         apply_negative),
    "edge_detection":  ("Edge Detection",   apply_edge_detection),
    "sketch":          ("Sketch",           apply_sketch),
    "pixelate":        ("Pixelate",         apply_pixelate),
    "painterly":       ("Painterly",        apply_painterly),
    "horizontal_flip": ("Horizontal Flip",  apply_horizontal_flip),
    "vertical_flip":   ("Vertical Flip",    apply_vertical_flip),
    "vignette":        ("Vignette",         apply_vignette),
}

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", filters=FILTERS)

@app.route("/apply", methods=["POST"])
def apply_filter():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]

    # Support multi-filter: "filters" is a comma-separated list
    filters_param = request.form.get("filters", "")
    filter_name   = request.form.get("filter", "grayscale")   # legacy single-filter

    filter_keys = [f.strip() for f in filters_param.split(",") if f.strip()] if filters_param else [filter_name]

    for key in filter_keys:
        if key not in FILTERS:
            return jsonify({"error": f"Unknown filter: {key}"}), 400

    try:
        img = Image.open(file.stream).convert("RGB")
        img.thumbnail((1200, 1200), Image.LANCZOS)

        for key in filter_keys:
            _, fn = FILTERS[key]
            # Collect any per-filter params from the form (e.g. strength for vignette)
            params = {}
            if key == "vignette":
                params["strength"] = request.form.get("strength", 1.0)
            if key == "pixelate":
                params["pixel_size"] = request.form.get("pixel_size", 16)
            img = fn(img, params=params)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")

        return jsonify({"image": f"data:image/jpeg;base64,{encoded}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/filters")
def list_filters():
    return jsonify({k: v[0] for k, v in FILTERS.items()})

if __name__ == "__main__":
    app.run(debug=True)
