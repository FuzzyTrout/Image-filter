# Image Filter Studio — Project Report

**Project Name:** Filtro — Image Filter Studio  
**Date:** June 2026  
**Status:** Complete (Backend & Frontend)

---

## 1. Executive Summary

This project is a **web-based image filter application** that allows users to upload images and apply a variety of filters to transform them. The application consists of two parts:

- **Backend:** Python Flask server that processes images using PIL (Pillow), with all filter algorithms implemented from scratch in pure Python
- **Frontend:** Modern web interface (HTML/CSS/JavaScript) with a dark theme and drag-and-drop upload

Users upload an image, select a filter from a sidebar, click "Apply," and see a before/after comparison. They can download the filtered result as a JPEG file.

---

## 2. Project Overview

### 2.1 Purpose

The project demonstrates how to build a practical image processing tool with a clean, user-friendly interface. It showcases:
- Image manipulation techniques (filters implemented from scratch)
- Web application architecture (Flask backend + HTML/CSS/JS frontend)
- File handling and real-time feedback
- Professional UI/UX design

### 2.2 What It Does

1. User uploads an image (JPG, PNG, WEBP)
2. User selects a filter from the sidebar
3. Backend processes the image through the selected filter
4. Frontend displays original and filtered images side-by-side
5. User can download the filtered image

### 2.3 Available Filters

| Filter | Description |
|--------|-------------|
| **Grayscale** | Converts image to black and white using luminosity weighting |
| **Blur** | Smooths the image using a 7×7 Gaussian kernel |
| **Sharpen** | Enhances edges using a 3×3 sharpening kernel |
| **Invert** | Reverses all pixel values (light becomes dark, dark becomes light) |
| **Edge Detection** | Detects edges using Sobel operators with non-maximum suppression and hysteresis thresholding |
| **Painterly** | Makes image look like an oil painting by finding dominant colors in local neighborhoods |
| **Sepia** | Applies warm, brownish vintage tone using a color matrix |
| **Horizontal Flip** | Mirrors image left-to-right |
| **Vertical Flip** | Mirrors image top-to-bottom |
| **Sketch** | Pencil sketch effect by combining grayscale + edge detection + invert |
| **Pixelate** | Reduces resolution to create a blocky, pixelated effect |
| **Vignette** | Darkens the edges of the image, drawing focus to the center |
| **Cartoon** | Combines blur, color quantization, and edge detection for a cartoon look |
| **Emboss** | Creates a raised, embossed texture effect |
| **Chromatic Aberration** | Applies a color grading effect based on pixel brightness |
| **Quantize** | Reduces the number of distinct colors in the image |

> **Note:** The `negative` filter currently has a bug — the function body exists but the `def negative(self, image):` signature line is missing, so it cannot be called. It needs to be fixed before use.

---

## 3. Architecture Overview

### 3.1 System Design

```
┌─────────────────────────────────────────────────────────┐
│                     USER BROWSER                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │           Frontend (index.html)                    │ │
│  │  - Upload zone (drag & drop)                       │ │
│  │  - Filter selection sidebar                        │ │
│  │  - Before/after image comparison                   │ │
│  │  - Download button                                 │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP POST /apply
                   │ (image + filter name)
┌──────────────────▼──────────────────────────────────────┐
│              FLASK BACKEND (app.py)                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │          Filter Class (filters.py)                 │ │
│  │  - grayscale()       - blur()                      │ │
│  │  - sharpen()         - invert()                    │ │
│  │  - edge_detect()     - painterly()                 │ │
│  │  - sepia()           - sketch()                    │ │
│  │  - pixelate()        - vigennete()                 │ │
│  │  - cartoon()         - emboss()                    │ │
│  │  - chromatic_aberration()  - quantize()            │ │
│  └────────────────────────────────────────────────────┘ │
│                       ↓                                   │
│  ┌────────────────────────────────────────────────────┐ │
│  │     Image Processing Libraries                     │ │
│  │  - PIL/Pillow (image loading, pixel access)        │ │
│  │  - math (sqrt, atan2, degrees — for edge detect)   │ │
│  │  - random (for chromatic aberration effect)        │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────┘
                   │ JSON response
                   │ (base64 encoded image)
                   ▼
             [Displayed in Browser]
```

### 3.2 Technology Stack

**Backend:**
- Python 3.x
- Flask (web framework)
- PIL/Pillow (image loading and pixel manipulation)
- `math` standard library (used in edge detection)
- `random` standard library (used in chromatic aberration)

> All filter algorithms are implemented from scratch using direct pixel manipulation — no NumPy or OpenCV are used in `filters.py`.

**Frontend:**
- HTML5 (structure)
- CSS3 (styling with dark theme)
- Vanilla JavaScript (interactivity, file handling, API calls)

**Deployment:**
- Flask development server (runs locally on `http://localhost:5000`)

---

## 4. Backend Explanation

### 4.1 Flask Server Setup (app.py)

```python
from flask import Flask, request, jsonify, render_template
from PIL import Image
import io
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file limit
```

### 4.2 Filter Class & Methods

All filters live inside the `filters` class in `filters.py`. Each method takes a PIL `Image` object, manipulates it by directly accessing pixels via `image.load()`, and returns the modified image.

**Example: Grayscale**
```python
def grayscale(self, image):
    image_load = image.load()
    width, height = image.size
    for row in range(width):
        for column in range(height):
            r, g, b = image_load[row, column]
            grey = round(0.299*r + 0.587*g + 0.114*b)
            image_load[row, column] = (grey, grey, grey)
    return image
```
Uses the standard luminosity formula — green is weighted most heavily because human eyes are most sensitive to it.

**Example: Blur / Gaussian Blur**
```python
kernel = [
    [0, 0, 1, 2, 1, 0, 0],
    [0, 3, 13, 22, 13, 3, 0],
    ...
]
```
Applies a 7×7 Gaussian kernel by hand — iterating over every pixel, sampling its neighborhood, weighting each neighbor by the kernel value, and dividing by the total weight. Uses a copy of the original image so already-modified pixels don't contaminate later calculations.

**Example: Edge Detection**

This is a full Canny-style pipeline implemented from scratch:

1. Convert to grayscale
2. Apply Gaussian blur (reduce noise)
3. Apply Sobel operators (compute gradient magnitude and direction at each pixel)
4. Non-maximum suppression (thin edges to 1-pixel width)
5. Double thresholding (classify pixels as strong, weak, or noise)
6. Hysteresis (keep weak edges only if connected to a strong edge)

```python
sobel_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
sobel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
```

**Example: Painterly**

For each pixel, looks at a 7×7 neighborhood and groups neighboring pixels into intensity buckets. It skips neighbors that differ too much in color (to avoid mixing across hard edges), finds the most common bucket, and replaces the pixel with the average color of that bucket blended with the original. This gives a flat, paint-like appearance.

**Example: Chromatic Aberration**

Despite the name, this is actually a **color grading** effect. It maps each pixel's brightness to a color along a three-stop gradient (dark purple → orange → light red), and applies it randomly to ~40% of pixels (`random.random() > 0.6`).

### 4.3 API Routes

**Route 1: Display the UI**
```python
@app.route("/")
def index():
    return render_template("index.html", filters=FILTERS)
```

**Route 2: Apply a filter**
```python
@app.route("/apply", methods=["POST"])
def apply_filter():
    file = request.files["image"]
    filter_name = request.form.get("filter", "grayscale")

    img = Image.open(file.stream).convert("RGB")
    img.thumbnail((1200, 1200), Image.LANCZOS)

    _, fn = FILTERS[filter_name]
    result = fn(img)

    buf = io.BytesIO()
    result.save(buf, format="JPEG", quality=90)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")

    return jsonify({"image": f"data:image/jpeg;base64,{encoded}"})
```

Step-by-step:
1. Receives the image file and filter name from the frontend
2. Opens the image with PIL and converts to RGB
3. Limits size to 1200×1200 for performance
4. Calls the correct filter method
5. Encodes result as base64 JPEG and returns as JSON

---

## 5. Frontend Explanation

### 5.1 Overall Design

The frontend uses a **sidebar + canvas** layout:
- **Left sidebar (280px):** Upload zone, filter list, apply button
- **Main canvas area:** Empty state → file info → before/after comparison

**Design choices:**
- Dark theme (modern, comfortable for long use)
- Monospace font (DM Mono) for technical labels
- Bright green accent color (`#c8f542`) for action buttons and highlights
- Smooth transitions and loading spinner for feedback

### 5.2 HTML Structure

```html
<aside>
  <div class="upload-zone" id="uploadZone">
    <input type="file" id="fileInput" accept="image/*">
    <span class="upload-icon">⬆</span>
    <div class="upload-text">Choose a file or drag & drop</div>
  </div>

  <div class="filter-list">
    {% for key, (label, _) in filters.items() %}
    <button class="filter-btn" data-filter="{{ key }}">{{ label }}</button>
    {% endfor %}
  </div>

  <button class="apply-btn" id="applyBtn">Apply filter</button>
</aside>
```

The `{% for ... %}` syntax is Jinja2 templating (built into Flask). The loop generates a button for each filter from the `FILTERS` dict passed by the backend.

### 5.3 JavaScript Functionality

**Apply a filter:**
```javascript
async function applyFilter() {
  const formData = new FormData();
  formData.append('image', currentFile);
  formData.append('filter', selectedFilter);

  applyBtn.classList.add('loading');

  const res = await fetch('/apply', { method: 'POST', body: formData });
  const data = await res.json();

  filteredImg.src = data.image;
  downloadBtn.href = data.image;

  applyBtn.classList.remove('loading');
}
```

### 5.4 User Experience Flow

```
1. Page loads
   ↓
2. User drags/clicks to upload image
   ↓
3. Original image displays in left card
   ↓
4. User clicks a filter name (green highlight shows selection)
   ↓
5. User clicks "Apply filter" (spinning loader appears)
   ↓
6. Backend processes image
   ↓
7. Filtered image appears in right card with "↓ Save" button
   ↓
8. User downloads result OR selects a different filter and applies again
```

---

## 7. Installation & Running

### 7.1 Prerequisites

- Python 3.x installed
- `uv` package manager (optional, but recommended)

### 7.2 Setup

**Step 1: Install dependencies**
```bash
uv add flask pillow
```
Or with pip:
```bash
pip install flask pillow
```

**Step 2: Run the server**
```bash
uv run app.py
```
Or:
```bash
python app.py
```

**Step 3: Open in browser**
```
http://localhost:5000
```

### 7.3 Project Structure

```
image-filters/
├── app.py                 ← Flask backend + route handling
├── filters.py             ← All filter implementations (filters class)
├── templates/
│   └── index.html        ← Frontend (HTML/CSS/JS)
└── requirements.txt      ← Dependency list (flask, pillow)
```

---

## 8. Filter Algorithm Reference

| Filter | Algorithm | Neighborhood |
|--------|-----------|--------------|
| Grayscale | Luminosity formula: `0.299R + 0.587G + 0.114B` | Per pixel |
| Blur / Gaussian Blur | 7×7 weighted Gaussian kernel convolution | 7×7 |
| Sharpen | 3×3 sharpening kernel (`center=5, neighbors=-1`) | 3×3 |
| Invert | `(255-R, 255-G, 255-B)` | Per pixel |
| Edge Detection | Grayscale → Gaussian blur → Sobel → NMS → hysteresis | 3×3 Sobel |
| Painterly | Dominant intensity bucket in neighborhood, edge-aware blending | 7×7 |
| Sepia | Fixed color matrix multiplication | Per pixel |
| Flip (H/V) | Pixel swap around axis | Per pixel |
| Sketch | Grayscale → Edge Detect → Invert | — |
| Pixelate | Average color per block, repaint entire block | Block (40×40) |
| Vignette | Distance-based darkening from center | Per pixel |
| Cartoon | Gaussian blur + Quantize + Edge detect overlay | — |
| Emboss | 3×3 kernel `n = (i+1)*(j+1)`, normalized to 0-255 | 3×3 |
| Chromatic Aberration | Brightness → 3-stop color gradient, 40% random application | Per pixel |
| Quantize | `(value // 64) * 64` per channel | Per pixel |

---

## 9. Potential Improvements

**Correctness:**
- Fix the missing `def negative(self, image):` signature
- Fix `painterly` to use a true image copy (`image.copy().load()`) instead of reading from the live pixel accessor

**Performance:**
- Use NumPy vectorized operations instead of nested Python loops — would make most filters 10-100× faster
- Add image resizing before processing (already done in `painterly`, should be applied globally)

**Features:**
- Filter chaining (apply multiple filters in sequence)
- Intensity/strength sliders per filter
- Undo/redo history
- Real-time preview on smaller thumbnail

---

## 10. API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Display HTML interface |
| `/apply` | POST | Process image with selected filter |

**POST `/apply` parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `image` | File | The uploaded image (JPG, PNG, WEBP) |
| `filter` | String | Filter key (e.g. `grayscale`, `sepia`, `cartoon`) |

**Response:**
```json
{ "image": "data:image/jpeg;base64,..." }
```

---

**Generated:** June 2026  
**Project Status:** Complete ✓ (with known issues noted above)
