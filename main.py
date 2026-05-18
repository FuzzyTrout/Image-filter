from PIL import Image
from filter import filters

img = Image.open("images/2.jpg").convert("RGB")

f = filters()
img = f.grayscale(img)

img.save("images/filtered/out.png")
