# Image Filter Studio — Project Report

**Project Name:** Filtro — Image Filter Studio  
**Date:** January 2025  
**Status:** Complete (Backend & Frontend)

---

## 1. Executive Summary

This project is a **web-based image filter application** that allows users to upload images and apply 10 different filters to transform them. The application consists of two parts:

- **Backend:** Python Flask server that processes images using PIL, NumPy, and OpenCV libraries
- **Frontend:** Modern web interface (HTML/CSS/JavaScript) with a dark theme and drag-and-drop upload

Users upload an image, select a filter from a sidebar, click "Apply," and see a before/after comparison. They can download the filtered result as a JPEG file.

---

## 2. Project Overview

### 2.1 Purpose

The project demonstrates how to build a practical image processing tool with a clean, user-friendly interface. It showcases:
- Image manipulation techniques (filters)
- Web application architecture (Flask backend + HTML/CSS/JS frontend)
- File handling and real-time feedback
- Professional UI/UX design

### 2.2 What It Does

1. User uploads an image (JPG, PNG, WEBP)
2. User selects a filter from a list of 10 options
3. Backend processes the image through the selected filter
4. Frontend displays original and filtered images side-by-side
5. User can download the filtered image

### 2.3 10 Available Filters

| Filter | Description |
|--------|-------------|
| **Grayscale** | Converts image to black and white by removing color information |
| **Invert** | Reverses all pixel values (light becomes dark, dark becomes light) |
| **Sepia** | Applies warm, brownish vintage tone using color matrix math |
| **Negative** | Creates photographic negative effect (mathematical complement) |
| **Edge Detection** | Detects and highlights edges/borders in the image (Canny algorithm) |
| **Sketch** | Creates pencil sketch effect by combining grayscale + edge detection |
| **Pixelate** | Reduces resolution to create blocky, pixelated effect |
| **Painterly** | Makes image look like oil painting using bilateral filtering |
| **Horizontal Flip** | Mirrors image left-to-right |
| **Vertical Flip** | Mirrors image top-to-bottom |

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
│  │          Filter Functions                          │ │
│  │  - apply_grayscale()                               │ │
│  │  - apply_invert()                                  │ │
│  │  - apply_sepia()                                   │ │
│  │  - ... (all 11 filters)                            │ │
│  └────────────────────────────────────────────────────┘ │
│                       ↓                                   │
│  ┌────────────────────────────────────────────────────┐ │
│  │     Image Processing Libraries                     │ │
│  │  - PIL (Image, ImageOps, ImageFilter)              │ │
│  │  - NumPy (array operations)                        │ │
│  │  - OpenCV (cv2) (advanced algorithms)              │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────┘
                   │ JSON response
                   │ (base64 encoded image)
                   ▼
             [Displayed in Browser]
```

### 3.2 Technology Stack

**Backend:**
- Python 3.14.5
- Flask (web framework)
- PIL/Pillow (image manipulation)
- NumPy (array math)
- OpenCV (cv2) (advanced image processing)

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
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np
import cv2
import io
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file limit
```

**What this does:**
- Imports Flask and image processing libraries
- Creates a Flask app with a 16MB upload size limit

### 4.2 Filter Functions

Each filter is a standalone function that takes a PIL Image, processes it, and returns a modified PIL Image.

**Example: Grayscale**
```python
def apply_grayscale(img):
    return img.convert("L").convert("RGB")
```
- `img.convert("L")` converts to grayscale (luminance channel)
- `.convert("RGB")` converts back to RGB so it stays compatible

**Example: Sepia (more complex)**
```python
def apply_sepia(img):
    img = img.convert("RGB")
    arr = np.array(img, dtype=np.float64)  # Convert to NumPy array
    r = np.clip(arr[:,:,0]*0.393 + arr[:,:,1]*0.769 + arr[:,:,2]*0.189, 0, 255)
    g = np.clip(arr[:,:,0]*0.349 + arr[:,:,1]*0.686 + arr[:,:,2]*0.168, 0, 255)
    b = np.clip(arr[:,:,0]*0.272 + arr[:,:,1]*0.534 + arr[:,:,2]*0.131, 0, 255)
    sepia = np.stack([r, g, b], axis=2).astype(np.uint8)
    return Image.fromarray(sepia)
```
- Converts image to NumPy array (width × height × 3 for RGB)
- Applies sepia matrix transform to each color channel
- `np.clip()` ensures values stay between 0-255
- Stacks channels back together and converts to PIL Image

### 4.3 API Routes

**Route 1: Display the UI**
```python
@app.route("/")
def index():
    return render_template("index.html", filters=FILTERS)
```
When user visits `http://localhost:5000`, Flask loads and displays the HTML interface.

**Route 2: Apply a filter**
```python
@app.route("/apply", methods=["POST"])
def apply_filter():
    file = request.files["image"]
    filter_name = request.form.get("filter", "grayscale")
    
    img = Image.open(file.stream).convert("RGB")
    img.thumbnail((1200, 1200), Image.LANCZOS)  # Limit size for speed
    
    _, fn = FILTERS[filter_name]
    result = fn(img)  # Apply the filter function
    
    buf = io.BytesIO()
    result.save(buf, format="JPEG", quality=90)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    
    return jsonify({"image": f"data:image/jpeg;base64,{encoded}"})
```

**What this does step-by-step:**
1. Receives image file and filter name from frontend
2. Opens the image using PIL
3. Limits image size to 1200×1200 for performance
4. Looks up and calls the filter function
5. Converts result to JPEG and encodes as base64
6. Returns as JSON with `data:image/jpeg;base64,...` format (can display directly in `<img>` tag)

### 4.4 Filter Dictionary

```python
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
    "vigennete":       ("Vigennete",        apply_vigennete)
}
```

Maps filter ID (used in URLs) → (display name, function). The frontend loops through this to generate the filter list.

---

## 5. Frontend Explanation

### 5.1 Overall Design

The frontend uses a **sidebar + canvas** layout:
- **Left sidebar (280px):** Upload zone, filter list, apply button
- **Main canvas area:** Empty state → file info → before/after comparison

**Design choices:**
- Dark theme (modern, comfortable for long use)
- Monospace font (DM Mono) for technical labels
- Bright green accent color (#c8f542) for action buttons and highlights
- Smooth transitions and loading spinner for feedback

### 5.2 HTML Structure

**Key sections:**

```html
<header>
  <span class="logo">filtro/</span>
  <span class="logo-tag">image filter studio</span>
</header>

<main>
  <aside>
    <!-- Upload zone -->
    <div class="upload-zone" id="uploadZone">
      <input type="file" id="fileInput" accept="image/*">
      <span class="upload-icon">⬆</span>
      <div class="upload-text">Choose a file or drag & drop</div>
    </div>
    
    <!-- Filter list (generated from backend) -->
    <div class="filter-list">
      {% for key, (label, _) in filters.items() %}
      <button class="filter-btn" data-filter="{{ key }}">{{ label }}</button>
      {% endfor %}
    </div>
    
    <!-- Apply button -->
    <button class="apply-btn" id="applyBtn">Apply filter</button>
  </aside>

  <div class="canvas-area">
    <!-- Image comparison (hidden until image is uploaded) -->
    <div class="comparison" id="comparison">
      <div class="img-card">
        <img id="originalImg" src="">
      </div>
      <div class="img-card">
        <img id="filteredImg" src="">
        <a class="download-btn" id="downloadBtn">↓ Save</a>
      </div>
    </div>
  </div>
</main>
```

**Notes:**
- `{% for ... %}` syntax is **Jinja2 templating** (built into Flask)
- The loop generates a button for each filter from `filters` passed by backend
- Hidden elements (`display: none`) are shown/hidden by JavaScript

### 5.3 CSS Styling (Dark Theme)

**Color palette:**
```css
--bg: #0d0d0f;           /* Very dark background */
--surface: #17171a;      /* Slightly lighter card surfaces */
--text: #e8e8ec;         /* Light gray text */
--muted: #6b6b78;        /* Muted secondary text */
--accent: #c8f542;       /* Bright lime green for buttons/highlights */
```

**Layout:**
```css
main {
  display: grid;
  grid-template-columns: 280px 1fr;  /* Sidebar + canvas area */
  overflow: hidden;
}
```

Creates a 2-column layout. The sidebar is fixed width, canvas area takes remaining space.

### 5.4 JavaScript Functionality

**Key functions:**

1. **Select a filter:**
```javascript
function selectFilter(btn, key) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  selectedFilter = key;
}
```
Removes `active` class from all buttons, adds it to clicked button, updates `selectedFilter` variable.

2. **Handle file upload:**
```javascript
fileInput.addEventListener('change', e => {
  const file = e.target.files[0];
  loadFile(file);
});

uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) loadFile(file);
});
```
Listens for file input (click) and drag-and-drop, calls `loadFile()` to display it.

3. **Load and display original image:**
```javascript
function loadFile(file) {
  currentFile = file;
  const reader = new FileReader();
  reader.onload = ev => {
    originalImg.src = ev.target.result;  // Data URL
    comparison.classList.add('visible');  // Show comparison area
  };
  reader.readAsDataURL(file);  // Convert file to base64 data URL
}
```
Reads file as base64 data URL so it can display in `<img>` tag without uploading yet.

4. **Send to backend and display result:**
```javascript
async function applyFilter() {
  const formData = new FormData();
  formData.append('image', currentFile);
  formData.append('filter', selectedFilter);

  applyBtn.classList.add('loading');  // Show spinner
  
  const res = await fetch('/apply', { method: 'POST', body: formData });
  const data = await res.json();
  
  filteredImg.src = data.image;  // Display filtered image
  downloadBtn.href = data.image;  // Set download link
  
  applyBtn.classList.remove('loading');
}
```
- Creates FormData with image file + filter name
- Sends POST request to `/apply` route
- Backend returns JSON with base64 image
- Sets both display image and download link
- Shows/hides loading spinner

### 5.5 User Experience Flow

```
1. Page loads
   ↓
2. User drags/clicks to upload image
   ↓
3. Original image displays in left card, "Apply filter" button enabled
   ↓
4. User clicks filter name (green highlight shows selection)
   ↓
5. User clicks "Apply filter" button (spinning loader appears)
   ↓
6. Backend processes image (1-5 seconds depending on size/filter)
   ↓
7. Filtered image appears in right card with "↓ Save" button
   ↓
8. User can click "↓ Save" to download as JPEG
   OR select different filter and apply again
```

---

## 6. How They Work Together

### 6.1 Request/Response Flow

**1. Frontend sends request:**
```javascript
const formData = new FormData();
formData.append('image', currentFile);      // User's uploaded file
formData.append('filter', 'sepia');         // User's selected filter
await fetch('/apply', { method: 'POST', body: formData });
```

**2. Backend receives request:**
```python
@app.route("/apply", methods=["POST"])
def apply_filter():
    file = request.files["image"]           # Gets the file
    filter_name = request.form.get("filter") # Gets 'sepia'
```

**3. Backend processes:**
```python
img = Image.open(file.stream)
result = apply_sepia(img)  # Calls sepia filter function
```

**4. Backend sends response:**
```python
return jsonify({"image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."})
```

**5. Frontend receives and displays:**
```javascript
filteredImg.src = data.image;  // Sets <img> src to base64
```

The base64 format (`data:image/jpeg;base64,...`) is special — browsers recognize it and display it directly in `<img>` tags without needing a separate file.

### 6.2 File Size Optimization

**Frontend:** Only sends what's needed (file + filter ID)  
**Backend:** Compresses to 1200×1200 max, JPEG quality 90  
**Response:** Base64 encoded (≈33% larger than binary, but fits in JSON easily)

---

## 7. Code Quality & Improvements

### 7.1 Current Strengths

✅ Modular filter functions (easy to add new filters)  
✅ Separation of concerns (backend processes, frontend displays)  
✅ Error handling (try/catch on frontend, validation on backend)  
✅ Performance optimized (thumbnail resize, JPEG compression)  
✅ Professional UI (dark theme, smooth animations)  
✅ Drag-and-drop support  
✅ Loading feedback (spinner while processing)  

### 7.2 Potential Improvements

**For Production:**
- Add user authentication (save/load filter history)
- Implement image caching (avoid re-processing same image)
- Add filter chaining (apply multiple filters in sequence)
- Batch processing (upload multiple images)
- Filter strength/intensity sliders (e.g., blur radius, pixelate block size)
- Real-time preview (show filtered version while dragging slider)
- History/undo functionality

**For Performance:**
- Use WebWorkers for heavy filters (offload to background thread)
- Implement progressive upload (stream large files)
- Add image format selection (PNG, WebP, etc.)
- Client-side pre-scaling (reduce server load)

**For Accessibility:**
- Add alt text descriptions for filters
- Keyboard navigation (arrow keys to select filter)
- Screen reader support
- High contrast mode

---

## 8. Installation & Running

### 8.1 Prerequisites

- Python 3.x installed
- `uv` package manager (optional, but recommended)

### 8.2 Setup

**Step 1: Install dependencies**
```bash
uv add flask pillow numpy opencv-python
```

Or with pip:
```bash
pip install flask pillow numpy opencv-python
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

### 8.3 Project Structure

```
image-filters/
├── app.py                 ← Flask backend + filter functions
├── templates/
│   └── index.html        ← Frontend (HTML/CSS/JS)
├── requirements.txt      ← Dependency list
└── README.md            ← Quick start guide
```

---

## 9. Filter Details & Algorithms

### 9.1 Simple Filters (PIL-based)

**Grayscale**
- Converts RGB → single intensity value using luminosity formula
- `0.299*R + 0.587*G + 0.114*B` (humans perceive green brightest)

**Vigennte**
- Use the distance formula to find the maximum distance between the centre and the coners and from that blacken the pixels further away from the centre
- Use the distance formula. `((x2-x1)^2 - (y2-y1)^2)**0.5`

**Invert**
- Subtract each pixel from 255: `(255-R, 255-G, 255-B)`
- Creates photographic negative effect

**Horizontal/Vertical Flip**
- Mirrors by swapping pixel positions
- No math, just rearrangement

### 9.2 Matrix-Based Filters (NumPy)

**Sepia**
- Uses weighted sums across all three channels
- Creates warm, vintage tone
- Matrix: fixed coefficients that blend channels

**Negative**
- Similar to invert but mathematically verified

### 9.3 Advanced Filters (OpenCV)

**Edge Detection (Canny)**
- Multi-stage edge detection algorithm
- Detects pixel value changes (gradients)
- Thresholds determine sensitivity

**Sketch**
- Combines grayscale + edge detection + invert
- Edge lines become dark on light background

**Pixelate**
- Downsamples image to lower resolution
- Upsamples back to original size (creates blocky effect)
- Block size parameter controls intensity

**Painterly**
- Applies bilateral filter multiple times (preserves edges, smooths flat areas)
- Uses edge detection to mask color blending
- Creates oil-painting effect

---

## 10. Testing & Validation

### 10.1 What to Test

- Upload various image formats (JPG, PNG, WEBP)
- Test all 10 filters to ensure no crashes
- Upload very large images (should resize gracefully)
- Rapid filter changes (should queue properly)
- Download button creates valid image files

### 10.2 Known Limitations

- Large images (>5MB) may take 5-10 seconds to process
- Some filters (painterly, edge detection) are slower
- Mobile browsers show UI but may have small download links
- Internet Explorer not supported (modern browsers only)

---

## 11. Conclusion

**Filtro** is a complete, functional image filter application demonstrating:

1. **Backend architecture:** RESTful Flask API with modular filter functions
2. **Image processing:** PIL, NumPy, and OpenCV for different complexity levels
3. **Frontend design:** Professional dark-themed UI with modern interactions
4. **Web fundamentals:** HTML templating, CSS styling, JavaScript async/await

The project is ready for use and can be extended with additional filters or features. The modular design makes it easy to add new image processing algorithms.

---

## Appendix: Quick Reference

| Component | File | Purpose |
|-----------|------|---------|
| Web Server | `app.py` | Flask routes + filter functions |
| User Interface | `templates/index.html` | HTML structure, CSS styling, JavaScript logic |
| Dependencies | `requirements.txt` | Python package list |

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Display HTML interface |
| `/apply` | POST | Process image with selected filter |
| `/filters` | GET | Get list of available filters (JSON) |

---

**Generated:**  June, 2026
**Project Status:** Complete ✓
