from PIL import Image, ImageFilter
from filter import filters


def main():
    f = filters()
    image = Image.open("images/2.jpg").convert("RGB")

    # img =image.filter(ImageFilter.GaussianBlur(radius=5))
    img = f.quantize(image)
    img.save("images/filtered/out1.png")
    


if __name__ == "__main__":
    main()
