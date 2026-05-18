from PIL import image
from filters import grayscale, blur

img = open("images/1.png").convert("RGB")

img = grayscale(img)

img.save("out.png")
