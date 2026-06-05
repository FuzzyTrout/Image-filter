from PIL import Image
from filter import filters

img = Image.open("images/3.jpg").convert("RGB")

f = filters()
img1 = f.sketch(img)

img1.save("images/filtered/sk3.png")
