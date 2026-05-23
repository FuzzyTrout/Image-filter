class filters:

    # grayscale filter
    def grayscale(self, image):
        image_load = image.load()
        width, height = image.size
        for row in range(width):
           for column in range(height):
             r,g,b = image_load[row,column]
             grey = round(0.299*r + 0.587*g + 0.114*b)
             image_load[row,column]= (grey,grey,grey)
        
        return image

    def blur(self, image):
        pass

    def sharpen(self, image):
        pass

    # makes the image look like a canvas painting by replacing each pixel with the average color of the most common intensity level in its neighborhood
    def canvasify(self,image): # Done by Zabi

        img = image.load()
        width, height = image.size
        copy = image.load()
            
        # print(image.size)

        # reach for each row and column of the image
        for row in range(width):

            # print progress every 200 rows for seeing how much is done
            if row % 200 == 0:
                print(f"Row {row} done")
        
            for column in range(height):

                # 8 levels... 256/8 = 32... so each level is 32 intensity values. For example, level 0 is 0-31, level 1 is 32-63, and so on. This way we can group pixels based on their intensity and find the dominant intensity level in the neighborhood.
                # we check a 11x11 neighborhood around the pixel (row, column) and count how many pixels fall into each intensity level. We also sum up the r, g, b values for each level to calculate the average color later.
                levels = 8
                count = [0] * levels
                sum_r = [0] * levels
                sum_g = [0] * levels
                sum_b = [0] * levels

                # these 2 loops reach for 11x11 grid arround pixel in consideration.
                for i in range(-3,4):
                    for j in range(-3,4):

                        # we check if our frid is getting out of image boundaries, iif yes, then bound it to the edge of the image. This way we can handle edge pixels without going out of bounds.
                        if row+i >= 0 and row+i < width and column+j >= 0 and column+j < height:

                            r,g,b = copy[row+i,column+j]
                            
                            # calculate the intensity of the pixel and determine which level it belongs to. We use integer division to find the level index, and we also ensure that the level index does not exceed the maximum level.
                            intensity = (r + g + b) // 3
                            level = (intensity // (256 // levels))
                            level = min(level, levels - 1)

                            count[level] += 1
                            sum_r[level] += r
                            sum_g[level] += g
                            sum_b[level] += b
                
                # we find the index of highest count, which corresponds to the dominant intensity level in the neighborhood. Then we calculate the average r, g, b values for that level by dividing the sum of r, g, b by the count of pixels in that level. Finally, we set the pixel at (row, column) to the average color of the dominant intensity level.
                dominant = count.index(max(count))

                avg_r = sum_r[dominant] // count[dominant]
                avg_g = sum_g[dominant] // count[dominant]
                avg_b = sum_b[dominant] // count[dominant]

                img[row,column] = (avg_r, avg_g, avg_b)

        return image


    # sepia filter that gives the image a warm, brownish tone by applying a specific transformation to the r, g, b values of each pixel. The transformation is based on a common sepia formula that uses weighted sums of the original r, g, b values to calculate the new r, g, b values. We also ensure that the new r, g, b values do not exceed 255 to maintain valid color values.

    def sepia(self, image): #Done by Zabi

        img = image.load()
        width, height = image.size

        # reach for each pixel in the image
        for row in range(width):
            for column in range(height):

                r,g,b = img[row,column]

                # apply the sepia transformation to calculate the new r, g, b values. The transformation uses specific coefficients for r, g, b to create the sepia effect. We also round the results to get integer color values and ensure that they do not exceed 255.
                tr = round(0.393*r + 0.769*g + 0.189*b)
                tg = round(0.349*r + 0.686*g + 0.168*b)
                tb = round(0.272*r + 0.534*g + 0.131*b)
                if tr > 255:
                    tr = 255
                if tg > 255:
                    tg = 255
                if tb > 255:
                    tb = 255
                img[row,column] = (tr,tg,tb)
        
        return image

    # flips horizontally by swapping pixels on the left side of the image with corresponding pixels on the right side. We iterate through each row and swap pixels until we reach the middle of the image, effectively creating a mirror image along the vertical axis.
    def horizontal_flip(self, image): # Done by Zabi
        img = image.load()
        width, height = image.size
        for row in range(width // 2):
            for column in range(height):
                temp = img[row,column]
                img[row,column] = img[width-row-1,column]
                img[width-row-1,column] = temp

        return image
    
    # flips vertically by swapping pixels on the top half of the image with corresponding pixels on the bottom half. We iterate through each column and swap pixels until we reach the middle of the image, effectively creating a mirror image along the horizontal axis.
    def vertical_flip(self, image): # Done by Zabi
        img = image.load()
        width, height = image.size
        for row in range(width):
            for column in range(height // 2):
                temp = img[row,column]
                img[row,column] = img[row,height-column-1]
                img[row,height-column-1] = temp

        return image
    
    # fun filter that inverts the colors of the image by subtracting each r, g, b value from 255. This creates a negative effect where light areas become dark and dark areas become light. We iterate through each pixel and apply this transformation to achieve the desired result.
    def negative(self, image): # Done by Zabi
        img = image.load()
        width, height = image.size
        for row in range(width):
            for column in range(height):
                r,g,b = img[row,column]
                img[row,column] = (255-r, 255-g, 255-b)

        return image