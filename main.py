from PIL import Image
from filter import filters

img = Image.open("images/2.jpg").convert("RGB")

f = filters()
img1 = f.pixelate(img)

img1.save("images/filtered/out.png")
