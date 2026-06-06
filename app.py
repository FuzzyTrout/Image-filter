from flask import Flask, request, jsonify, render_template
from PIL import Image
import io
import base64
import sys
sys.path.insert(0, '/app')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# ── Import your filter class ──────────────────────────────────────────────────
from filter import filters as FilterClass
f = FilterClass()

# ── Filter registry ───────────────────────────────────────────────────────────
# format: key -> (display label, method name, has_strength_param)
FILTERS = {
    "grayscale":           ("Grayscale",           "grayscale",           False),
    "invert":              ("Invert",               "invert",              False),
    "sepia":               ("Sepia",                "sepia",               False),
    "blur":                ("Blur",                 "blur",                False),
    "sharpen":             ("Sharpen",              "sharpen",             False),
    "edge_detection":      ("Edge Detection",       "edge_detect",         False),
    "sketch":              ("Sketch",               "sketch",              False),
    "pixelate":            ("Pixelate",             "pixelate",            False),
    "painterly":           ("Painterly",            "painterly",           False),
    "horizontal_flip":     ("Horizontal Flip",      "horizontal_flip",     False),
    "vertical_flip":       ("Vertical Flip",        "vertical_flip",       False),
    "vignette":            ("Vignette",             "vigennete",           True),
    "cartoon":             ("Cartoon",              "cartoon",             False),
    "emboss":              ("Emboss",               "emboss",              False),
    "chromatic_aberration":("Chromatic Aberration", "chromatic_aberration",False),
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
    filter_name   = request.form.get("filter", "grayscale")  # legacy fallback
    filter_keys   = [k.strip() for k in filters_param.split(",") if k.strip()] if filters_param else [filter_name]

    for key in filter_keys:
        if key not in FILTERS:
            return jsonify({"error": f"Unknown filter: {key}"}), 400

    try:
        img = Image.open(file.stream).convert("RGB")
        img.thumbnail((1200, 1200), Image.LANCZOS)

        for key in filter_keys:
            label, method_name, has_strength = FILTERS[key]
            fn = getattr(f, method_name)

            if has_strength:
                strength = float(request.form.get("strength", 1.0))
                strength = max(0.0, min(1.0, strength))
                img = fn(img, strength=strength)
            else:
                img = fn(img)

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
