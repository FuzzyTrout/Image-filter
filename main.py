from PIL import Image, ImageFilter
from filter import filters


def main():
    f = filters()
    image = Image.open("images/4.jpg").convert("RGB")

    # img =image.filter(ImageFilter.GaussianBlur(radius=5))
    img = f.edge_detect(image)
    img.save("images/filtered/out.png")
    


if __name__ == "__main__":
    main()
