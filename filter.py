from numpy import diff
from sympy import im


class filters:

    def grayscale(self, image):
        '''grayscale filter'''

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
    
    def invert(self, image):
        '''inverts image colors, ig black to white. not much used alone but in combinition with others'''

        image_load = image.load()
        width, height = image.size

        for row in range(width):
            for column in range(height):
                r,g,b = image_load[row,column]
                image_load[row,column] = (255-r, 255-g, 255-b)
        
        return image

    def edge_detect(self, image):
        image_load = image.load()
        copy = image.copy().load()
        width, height = image.size

        for row in range(width):
            for column in range(height):
                
                gxr = 0
                gxg = 0
                gxb = 0
                gyr = 0
                gyg = 0
                gyb = 0
                p1r = 0
                p1g = 0
                p1b = 0
                p2r = 0
                p2g = 0
                p2b = 0

                

                for i in range(-1,2):
                    for j in range(-1,2):

                        if (row+i >= 0 and row+i < width and column+j >= 0 and column+j < height):

                            if j == 0 :
                                p1r += 0
                                p1g += 0
                                p1b += 0

                            elif ( (j == -1 or j == 1) and (i == 0 or i == -1 or i == 1) ):
                                r, g, b = copy[row+i,column+j]
                                p1r += r * (j * (2 - (i**2)))
                                p1g += g * (j * (2 - i**2))
                                p1b += b * (j * (2 - i**2))

                            if ( i == 0):
                                p2r += 0
                                p2g += 0
                                p2b += 0

                            elif( ((i == -1) or (i == 1)) and ((j == 0) or (j == -1) or (j == 1)) ):
                                r, g, b = copy[row+i,column+j]
                                p2r += r * (i * (2 - (j**2)))
                                p2g += g * (i * (2 - j**2))
                                p2b += b * (i * (2 - j**2))

                gxr = p1r
                gxg = p1g
                gxb = p1b
                gyr = p2r
                gyg = p2g
                gyb = p2b

                gr = round((gxr**2 + gyr**2)**0.5)
                if gr > 255:
                    gr = 255
                gg = round((gxg**2 + gyg**2)**0.5)
                if gg > 255:
                    gg = 255
                gb = round((gxb**2 + gyb**2)**0.5)
                if gb > 255:
                    gb = 255

                image_load[row,column] = (gr, gg, gb)

                
        return image

    def painterly(self,image): 

        '''makes the image look like a canvas painting by replacing each pixel with the average color of the most common intensity level in its neighborhood'''

        print(image.size)
        
        # Optional: shrink very large images while preserving aspect ratio

        max_dimension = 1500
        
        width, height = image.size
        
        if max(width, height) > max_dimension:
            scale = max_dimension / max(width, height)
        
            new_width = int(width * scale)
            new_height = int(height * scale)
        
            image = image.resize((new_width, new_height))
        
            print(f"Resized: {width}x{height} -> {new_width}x{new_height}")

        img = image.load()
        width, height = image.size
        copy = image.load()

        # use there two variables as tunning knobs to controll filter strength. 
        levels = 4
        blend_strength = 0.9

        # reach for each row and column of the image
        for row in range(width):

            # print progress every 100 rows for seeing how much is done
            if row % 100 == 0:
                print(f"Row {row} done")
        
            for column in range(height):

                # 8 levels... 256/8 = 32... so each level is 32 intensity values. For example, level 0 is 0-31, level 1 is 32-63, and so on. This way we can group pixels based on their intensity and find the dominant intensity level in the neighborhood.
                # we check a 7x7 neighborhood around the pixel (row, column) and count how many pixels fall into each intensity level. We also sum up the r, g, b values for each level to calculate the average color later.
               
                count = [0] * levels
                sum_r = [0] * levels
                sum_g = [0] * levels
                sum_b = [0] * levels

                # these 2 loops reach for 7x7 grid arround pixel in consideration.
                for i in range(-3,4):
                    for j in range(-3,4):

                        # we check if our grid is getting out of image boundaries, iif yes, then bound it to the edge of the image. This way we can handle edge pixels without going out of bounds.
                        if row+i >= 0 and row+i < width and column+j >= 0 and column+j < height:

                            r,g,b = copy[row+i,column+j]

                            cr, cg, cb = copy[row, column] 
                            nr, ng, nb = copy[row + i, column + j]

                            diff = abs(cr - nr) + abs(cg - ng) + abs(cb - nb)

                            if diff > 100:
                                continue  # don't mix across edges
                            
                            # calculate the intensity of the pixel and determine which level it belongs to. We use integer division to find the level index, and we also ensure that the level index does not exceed the maximum level.
                            intensity = (r + g + b) // 3
                            level = (intensity * levels) // 256
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

                r, g, b = img[row, column]

                final_r = int(r * (1 - blend_strength) + avg_r * blend_strength)
                final_g = int(g * (1 - blend_strength) + avg_g * blend_strength)
                final_b = int(b * (1 - blend_strength) + avg_b * blend_strength)


                img[row,column] = (final_r, final_g, final_b)

        return image

    def sepia(self, image): 
        '''sepia filter that gives the image a warm, brownish tone by applying a specific transformation to the r, g, b values of each pixel. The transformation is based on a common sepia formula that uses weighted sums of the original r, g, b values to calculate the new r, g, b values. We also ensure that the new r, g, b values do not exceed 255 to maintain valid color values.'''

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

    def horizontal_flip(self, image): 
        '''flips horizontally by swapping pixels on the left side of the image with corresponding pixels on the right side. We iterate through each row and swap pixels until we reach the middle of the image, effectively creating a mirror image along the vertical axis.'''

        img = image.load()
        width, height = image.size
        for row in range(width // 2):
            for column in range(height):
                temp = img[row,column]
                img[row,column] = img[width-row-1,column]
                img[width-row-1,column] = temp

        return image
    
    def vertical_flip(self, image): 
        '''flips vertically by swapping pixels on the top half of the image with corresponding pixels on the bottom half. We iterate through each column and swap pixels until we reach the middle of the image, effectively creating a mirror image along the horizontal axis.'''

        img = image.load()
        width, height = image.size
        for row in range(width):
            for column in range(height // 2):
                temp = img[row,column]
                img[row,column] = img[row,height-column-1]
                img[row,height-column-1] = temp

        return image
    
    def negative(self, image):
        '''fun filter that inverts the colors of the image by subtracting each r, g, b value from 255. This creates a negative effect where light areas become dark and dark areas become light. We iterate through each pixel and apply this transformation to achieve the desired result.'''

        img = image.load()
        width, height = image.size
        for row in range(width):
            for column in range(height):
                r,g,b = img[row,column]
                img[row,column] = (255-r, 255-g, 255-b)

        return image

    def sketch(self, image):
        '''sketch filter that creates a pencil sketch effect by first converting the image to grayscale and then applying an edge detection algorithm. The edge detection highlights the contours of objects in the image, giving it a hand-drawn appearance. We can achieve this by using the edge_detect method we implemented earlier after converting the image to grayscale.'''

        gray_image = self.grayscale(image)
        sketch_image = self.edge_detect(gray_image)
        inverted_sketch = self.invert(sketch_image)
        return inverted_sketch

    def pixelate(self, image):
        image = image.convert("RGB")
        image_load = image.load()
        width, height = image.size
        block_size = 40

        for x in range(0, width, block_size):
            for y in range(0, height, block_size):

                # Collect all pixels in this block
                red, green, blue = 0, 0, 0
                count = 0

                for bx in range(block_size):
                    for by in range(block_size):
                        px = min(x + bx, width - 1)
                        py = min(y + by, height - 1)
                        r, g, b = image_load[px, py]
                        red   += r
                        green += g
                        blue  += b
                        count += 1

                # Average colour for the whole block (outside inner loops)
                avg_r = red   // count
                avg_g = green // count
                avg_b = blue  // count

                # Paint every pixel in the block with the average
                for bx in range(block_size):
                    for by in range(block_size):
                        px = min(x + bx, width - 1)
                        py = min(y + by, height - 1)
                        image_load[px, py] = (avg_r, avg_g, avg_b)

        return image


# create a filters object
# f = filters()

# # pick whichever filter you want to run
# result = f.pixelate(image)
# result = f.painterly(result)
# # save the result
# result.save("output.jpg")
# print("done!")
