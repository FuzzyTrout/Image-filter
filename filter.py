class filters:

    def graysclae(self, img):
        image_load = image.load()
        width, height = image.size
        for row in range(width):
           for column in range(height):
             r,g,b = image_load[row,column]
             grey = round(0.299*r + 0.587*g + 0.114*b)
             image_load[row,column]= [grey,grey,grey]
        save = image.save("file_name")
        return save

    def blur(self, img):
        pass