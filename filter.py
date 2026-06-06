import math
import random
from PIL import Image


class filters:

    def grayscale(self, image):
        '''grayscale filter'''

        image_load = image.load()
        width, height = image.size
        for row in range(width):
            for column in range(height):
                r, g, b = image_load[row, column]
                grey = round(0.299 * r + 0.587 * g + 0.114 * b)
                image_load[row, column] = (grey, grey, grey)

        return image

    def blur(self, image):
        '''smooths the image using a 7x7 Gaussian kernel'''

        image_load = image.load()
        width, height = image.size
        copy = image.copy().load()

        kernel = [
            [0,  0,  1,  2,  1,  0, 0],
            [0,  3, 13, 22, 13,  3, 0],
            [1, 13, 59, 97, 59, 13, 1],
            [2, 22, 97,159, 97, 22, 2],
            [1, 13, 59, 97, 59, 13, 1],
            [0,  3, 13, 22, 13,  3, 0],
            [0,  0,  1,  2,  1,  0, 0],
        ]

        for row in range(width):
            if row % 100 == 0:
                print(f"Row {row} done")

            for column in range(height):

                r_total = 0
                g_total = 0
                b_total = 0
                count = 0

                for i in range(-3, 4):
                    for j in range(-3, 4):
                        if 0 <= row + i < width and 0 <= column + j < height:
                            n = kernel[i + 3][j + 3]
                            r, g, b = copy[row + i, column + j]
                            count += n
                            r_total += r * n
                            g_total += g * n
                            b_total += b * n

                image_load[row, column] = (r_total // count, g_total // count, b_total // count)

        return image

    def sharpen(self, image):
        '''sharpens edges using a 3x3 kernel'''

        image_load = image.load()
        copy = image.copy().load()
        width, height = image.size

        kernel = [
            [ 0, -1,  0],
            [-1,  5, -1],
            [ 0, -1,  0],
        ]

        for row in range(width):
            for column in range(height):

                r_total = 0
                g_total = 0
                b_total = 0

                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < width and 0 <= column + j < height:
                            r, g, b = copy[row + i, column + j]
                            n = kernel[i + 1][j + 1]
                            r_total += r * n
                            g_total += g * n
                            b_total += b * n

                r_total = max(0, min(255, r_total))
                g_total = max(0, min(255, g_total))
                b_total = max(0, min(255, b_total))

                image_load[row, column] = (r_total, g_total, b_total)

        return image

    def quantize(self, image):
        '''reduces the number of distinct colors by snapping each channel to the nearest multiple of 64'''

        image_load = image.load()
        width, height = image.size

        for x in range(width):
            for y in range(height):
                r, g, b = image_load[x, y]
                r = min((r // 64) * 64, 255)
                g = min((g // 64) * 64, 255)
                b = min((b // 64) * 64, 255)
                image_load[x, y] = (r, g, b)

        return image

    def invert(self, image):
        '''inverts image colors — black to white and vice versa'''

        image_load = image.load()
        width, height = image.size

        for row in range(width):
            for column in range(height):
                r, g, b = image_load[row, column]
                image_load[row, column] = (255 - r, 255 - g, 255 - b)

        return image

    def edge_detect(self, image):
        '''full Canny-style edge detection: grayscale → gaussian blur → sobel → NMS → hysteresis'''

        gray_image = self.grayscale(image)
        gaussian_image = self.blur(gray_image)

        image_load = gaussian_image.load()
        copy = gaussian_image.copy().load()
        width, height = gaussian_image.size

        magnitude = [[0] * height for _ in range(width)]
        direction = [[0] * height for _ in range(width)]

        sobel_x = [
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1],
        ]
        sobel_y = [
            [-1, -2, -1],
            [ 0,  0,  0],
            [ 1,  2,  1],
        ]

        for row in range(width):
            for column in range(height):

                gx = 0
                gy = 0

                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < width and 0 <= column + j < height:
                            p = copy[row + i, column + j][0]
                            gx += p * sobel_x[i + 1][j + 1]
                            gy += p * sobel_y[i + 1][j + 1]

                g = int(math.sqrt(gx ** 2 + gy ** 2))
                g = min(g, 255)

                angle = math.degrees(math.atan2(gy, gx))
                if angle < 0:
                    angle += 180

                if angle < 22.5 or angle >= 157.5:
                    angle = 0
                elif angle < 67.5:
                    angle = 45
                elif angle < 112.5:
                    angle = 90
                else:
                    angle = 135

                magnitude[row][column] = g
                direction[row][column] = angle

        # Non-maximum suppression
        nms = [[0] * height for _ in range(width)]

        for row in range(1, width - 1):
            for column in range(1, height - 1):

                current = magnitude[row][column]
                angle = direction[row][column]

                if angle == 0:
                    n1 = magnitude[row][column - 1]
                    n2 = magnitude[row][column + 1]
                elif angle == 45:
                    n1 = magnitude[row - 1][column + 1]
                    n2 = magnitude[row + 1][column - 1]
                elif angle == 90:
                    n1 = magnitude[row - 1][column]
                    n2 = magnitude[row + 1][column]
                else:  # 135
                    n1 = magnitude[row - 1][column - 1]
                    n2 = magnitude[row + 1][column + 1]

                nms[row][column] = current if current >= n1 and current >= n2 else 0

        # Double thresholding
        high = 30
        low = 15

        dt = [[0] * height for _ in range(width)]

        for row in range(width):
            for column in range(height):
                val = nms[row][column]
                if val >= high:
                    dt[row][column] = 255
                elif val >= low:
                    dt[row][column] = 75
                else:
                    dt[row][column] = 0

        # Hysteresis — keep weak edges only if connected to a strong edge
        final = [[0] * height for _ in range(width)]

        for row in range(1, width - 1):
            for column in range(1, height - 1):
                if dt[row][column] == 255:
                    final[row][column] = 255
                elif dt[row][column] == 75:
                    if any(
                        dt[row + di][column + dj] == 255
                        for di in range(-1, 2)
                        for dj in range(-1, 2)
                        if not (di == 0 and dj == 0)
                    ):
                        final[row][column] = 255

        for row in range(width):
            for column in range(height):
                v = final[row][column]
                image_load[row, column] = (v, v, v)

        return gaussian_image

    def painterly(self, image):
        '''makes the image look like a canvas painting by replacing each pixel
        with the average color of the most common intensity level in its neighborhood'''

        print(image.size)

        max_dimension = 1500
        width, height = image.size

        if max(width, height) > max_dimension:
            scale = max_dimension / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = image.resize((new_width, new_height))
            print(f"Resized: {width}x{height} -> {new_width}x{new_height}")

        # FIX: use a true copy so reads aren't contaminated by writes
        copy_image = image.copy()
        img = image.load()
        copy = copy_image.load()

        width, height = image.size

        levels = 4
        blend_strength = 0.9

        for row in range(width):
            if row % 100 == 0:
                print(f"Row {row} done")

            for column in range(height):

                count  = [0] * levels
                sum_r  = [0] * levels
                sum_g  = [0] * levels
                sum_b  = [0] * levels

                cr, cg, cb = copy[row, column]

                for i in range(-3, 4):
                    for j in range(-3, 4):
                        if 0 <= row + i < width and 0 <= column + j < height:

                            nr, ng, nb = copy[row + i, column + j]

                            diff = abs(cr - nr) + abs(cg - ng) + abs(cb - nb)
                            if diff > 100:
                                continue

                            intensity = (nr + ng + nb) // 3
                            level = min((intensity * levels) // 256, levels - 1)

                            count[level] += 1
                            sum_r[level] += nr
                            sum_g[level] += ng
                            sum_b[level] += nb

                dominant = count.index(max(count))

                # Guard against an empty bucket (all neighbors skipped by edge filter)
                if count[dominant] == 0:
                    continue

                avg_r = sum_r[dominant] // count[dominant]
                avg_g = sum_g[dominant] // count[dominant]
                avg_b = sum_b[dominant] // count[dominant]

                r, g, b = img[row, column]

                img[row, column] = (
                    int(r * (1 - blend_strength) + avg_r * blend_strength),
                    int(g * (1 - blend_strength) + avg_g * blend_strength),
                    int(b * (1 - blend_strength) + avg_b * blend_strength),
                )

        return image

    def sepia(self, image):
        '''warm, brownish vintage tone'''

        img = image.load()
        width, height = image.size

        for row in range(width):
            for column in range(height):
                r, g, b = img[row, column]
                tr = min(round(0.393 * r + 0.769 * g + 0.189 * b), 255)
                tg = min(round(0.349 * r + 0.686 * g + 0.168 * b), 255)
                tb = min(round(0.272 * r + 0.534 * g + 0.131 * b), 255)
                img[row, column] = (tr, tg, tb)

        return image

    def horizontal_flip(self, image):
        '''mirrors image left-to-right'''

        img = image.load()
        width, height = image.size

        for row in range(width // 2):
            for column in range(height):
                temp = img[row, column]
                img[row, column] = img[width - row - 1, column]
                img[width - row - 1, column] = temp

        return image

    def vertical_flip(self, image):
        '''mirrors image top-to-bottom'''

        img = image.load()
        width, height = image.size

        for row in range(width):
            for column in range(height // 2):
                temp = img[row, column]
                img[row, column] = img[row, height - column - 1]
                img[row, height - column - 1] = temp

        return image

    def negative(self, image):
        '''photographic negative — inverts every channel'''

        img = image.load()
        width, height = image.size

        for row in range(width):
            for column in range(height):
                r, g, b = img[row, column]
                img[row, column] = (255 - r, 255 - g, 255 - b)

        return image

    def sketch(self, image):
        '''pencil sketch effect: grayscale → edge detect → invert'''

        gray_image = self.grayscale(image)
        sketch_image = self.edge_detect(gray_image)
        return self.invert(sketch_image)

    def pixelate(self, image):
        '''reduces resolution to create a blocky effect'''

        image = image.convert("RGB")
        image_load = image.load()
        width, height = image.size
        block_size = 40

        for x in range(0, width, block_size):
            for y in range(0, height, block_size):

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

                avg_r = red   // count
                avg_g = green // count
                avg_b = blue  // count

                for bx in range(block_size):
                    for by in range(block_size):
                        px = min(x + bx, width - 1)
                        py = min(y + by, height - 1)
                        image_load[px, py] = (avg_r, avg_g, avg_b)

        return image

    def vigennete(self, image, strength=1.0):
        '''darkens edges, drawing focus to the center'''

        image_load = image.load()
        width, height = image.size
        cx = width / 2
        cy = height / 2
        max_distance = (cx ** 2 + cy ** 2) ** 0.5

        for row in range(width):
            for column in range(height):
                distance = ((row - cx) ** 2 + (column - cy) ** 2) ** 0.5
                fraction = distance / max_distance
                r, g, b = image_load[row, column]
                factor = max(0.0, 1 - fraction * strength)
                image_load[row, column] = (
                    round(r * factor),
                    round(g * factor),
                    round(b * factor),
                )

        return image

    def cartoon(self, image):
        '''combines blur, quantization, and edge overlay for a cartoon look'''

        cartoon = self.blur(image.copy())
        cartoon = self.quantize(cartoon)

        edges = self.edge_detect(image.copy())
        edges = self.invert(edges)

        cartoon_load = cartoon.load()
        edge_load = edges.load()

        width, height = image.size

        for x in range(width):
            for y in range(height):
                if edge_load[x, y][0] < 128:
                    cartoon_load[x, y] = (0, 0, 0)

        return cartoon

    def emboss(self, image):
        '''creates a raised, embossed texture effect'''

        image_load = image.load()
        width, height = image.size
        copy = image.copy().load()

        for row in range(width):
            if row % 100 == 0:
                print(f"row {row} done")

            for column in range(height):

                r_total = 0
                g_total = 0
                b_total = 0

                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < width and 0 <= column + j < height:
                            r, g, b = copy[row + i, column + j]
                            n = (i + 1) * (j + 1)
                            r_total += r * n
                            g_total += g * n
                            b_total += b * n

                image_load[row, column] = (
                    max(0, min(255, r_total // 9 + 128)),
                    max(0, min(255, g_total // 9 + 128)),
                    max(0, min(255, b_total // 9 + 128)),
                )

        return image

    def chromatic_aberration(self, image):
        '''color grading effect: maps brightness to a dark-purple → orange → red gradient'''

        image_load = image.load()
        width, height = image.size
        color1 = (20, 0, 80)
        color2 = (255, 140, 0)
        color3 = (255, 50, 50)

        for row in range(width):
            for column in range(height):
                r, g, b = image_load[row, column]
                brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255

                if brightness < 0.5:
                    t = brightness / 0.5
                    result_r = color1[0] * (1 - t) + color2[0] * t
                    result_g = color1[1] * (1 - t) + color2[1] * t
                    result_b = color1[2] * (1 - t) + color2[2] * t
                else:
                    t = (brightness - 0.5) / 0.5
                    result_r = color2[0] * (1 - t) + color3[0] * t
                    result_g = color2[1] * (1 - t) + color3[1] * t
                    result_b = color2[2] * (1 - t) + color3[2] * t

                if random.random() > 0.6:
                    image_load[row, column] = (
                        round(result_r),
                        round(result_g),
                        round(result_b),
                    )

        return image
