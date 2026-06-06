# Filtro — Image Filter Studio

A Flask web app with 10 image filters built using PIL, NumPy, and OpenCV.

## Filters

| Filter | Description |
|---|---|
| Grayscale | Removes all colour, converts to luminance |
| Invert | Flips every pixel value (255 - value) |
| Sepia | Warm brownish tone using matrix transform |
| Negative | Mathematical complement of original |
| Edge Detection | Canny edge detection via OpenCV |
| Sketch | Pencil-sketch effect using dodge blend |
| Pixelate | Reduces resolution to block pixels |
| Painterly | Oil-paint effect via bilateral filtering |
| Horizontal Flip | Mirrors image left-right |
| Vertical Flip | Mirrors image top-bottom |

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python app.py

# 3. Open in browser
# http://localhost:5000
```

## Project structure

```
image-filters/
├── app.py              ← Flask backend + all filter logic
├── requirements.txt    ← Python dependencies
├── templates/
│   └── index.html      ← Frontend UI
└── README.md
```

## Usage

1. Open the app in your browser
2. Upload any JPG, PNG or WEBP image
3. Select a filter from the sidebar
4. Click **Apply filter**
5. Download the result with the Save button
