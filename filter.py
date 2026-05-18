class filters:

    def grayscale(self, image):
        image_load = image.load()
        width, height = image.size
        for row in range(width):
            for column in range(height):
                r, g, b = image_load[row, column]
                grey = round(0.299 * r + 0.587 * g + 0.114 * b)
                image_load[row, column] = (grey, grey,  grey)
        
        return image

    def blur(self, image):
        pass
