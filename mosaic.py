import pathlib
import json
import os
import math
import random
import cv2
import numpy as np


def make_mosaic(path_image, pathdir_name, details, tile_factor, scale_percent):
    tile_size = [3 * tile_factor, 2 * tile_factor]

    cache_path = "download/cache-" + str(details["id"]) + "/cache.json"

    if cache_path not in os.listdir():
        dataset_imgs_dir = pathlib.Path(pathdir_name)
        dataset_images = list(dataset_imgs_dir.glob("*.jpg"))
        dataset_avg = dataset_averages(dataset_images)

        with open(cache_path, "w") as file:
            json.dump(dataset_avg, file, indent=2, sort_keys=True)
        print("Dataset averages cached.")

    with open(cache_path, "r") as file:
        cache = json.load(file)

    main_image = cv2.imread(path_image)

    width = int(main_image.shape[1] * scale_percent / 100)
    height = int(main_image.shape[0] * scale_percent / 100)
    dim = (width, height)
    main_image = cv2.resize(main_image, dim, interpolation=cv2.INTER_AREA)

    main_image_height, main_image_width, _ = main_image.shape
    tile_height, tile_width = tile_size

    # We do this operation then reverse it so the number of tiles will eventually match exactly the image.
    num_tiles_height, num_tiles_width = (
        main_image_height // tile_height,
        main_image_width // tile_width,
    )
    main_image = main_image[
        : tile_height * num_tiles_height, : tile_width * num_tiles_width
    ]
    print("Image resized for alignment with number of tiles.")

    tiles = []
    # In x, y plot (y = height, x = width), we are going through the height and width of the image in the exact increment of the tiles. Then we will have the coordinates of every tile.
    for y in range(0, main_image_height, tile_height):
        for x in range(0, main_image_width, tile_width):
            # This assures that we don't write later in sections that exceed the image boundaries. If I tie the factor of the tiles and the image itself I might avoid this.
            if (
                y + tile_height > main_image.shape[0]
                or x + tile_width > main_image.shape[1]
            ):
                continue
            tiles.append((y, y + tile_height, x, x + tile_width))
    print("Coordinates for tiles measured.")

    index = 0
    for tile in tiles:
        # Now we unpack these values
        y0, y1, x0, x1 = tile
        # Get the average of each of the tiles
        avg_color = get_avg_color(main_image[y0:y1, x0:x1])
        closest_color = get_closest_color(avg_color, cache.keys())
        img_path = random.choice(cache[str(closest_color)])
        img_path = img_path.replace("\\", "/")  # ensures it works on WSL too.
        i = cv2.imread(img_path)
        i = cv2.resize(i, (tile_width, tile_height))
        main_image[y0:y1, x0:x1] = i
        index += 1
        if index % 50 == 0:
            print(f"Processed {index} of {len(tiles)}.")

    if not os.path.isdir("photomosaics"):
        os.makedirs("photomosaics")
        print(f"Directory made for photomosaic.")
    else:
        print("Photomosaics directory already present.")

    cv2.imwrite("photomosaics" + "/" + details["name"] + ".jpg", main_image)
    print(
        f"Processing finished. The image is in the photomosacs directory in the same folder as the app and is named {details['name']}.jpg."
    )


# This function return the average of all the RGB values of an image as a tuple of three values.
def get_avg_color(image):
    # The first average is a list of averages of a 3x3 grid representing each pixel, returning a list of arrays of size three.
    avg_color = np.average(image, axis=0)
    # The second average is a list of average for each of those lists, resulting in a single list of three values, for each color.
    avg_color = np.average(avg_color, axis=0)
    # Then we use numpy to round the numbers to closes integer.
    avg_color = np.around(avg_color)
    # Then we return as a tuple the average of each color in the pixel as an int after rounding so it is not a float anymore.
    avg_color = tuple(int(i) for i in avg_color)
    return avg_color


# This function receives an input of a list of image paths and returns a dictionary containing all the averages of those files.
def dataset_averages(dataset_images):
    data = {}
    for img_path in dataset_images:
        img = cv2.imread(str(img_path))
        avg_color = get_avg_color(img)
        # We use the values as the key so if by any chance there is two images with the same values, the program will choose a list of those images.
        if str(tuple(avg_color)) in data:
            data[str(tuple(avg_color))].append(str(img_path))
        else:
            data[str(tuple(avg_color))] = [str(img_path)]
    return data


# This functions receives the average color of an image and compares it to a list of averages of other images and returns the closest.
def get_closest_color(color_input, colors_list):
    ir, ig, ib = color_input
    min_diff = float("inf")
    closest_color = None
    # We are checking out every average in our colors list and registering the best result
    for c in colors_list:
        # eval read the string in our dict/json file and converts it back to a tuple
        r, g, b = eval(c)
        # This is math for finding the distance in three dimensions
        diff = math.sqrt((r - ir) ** 2 + (g - ig) ** 2 + (b - ib) ** 2)
        if diff < min_diff:
            min_diff = diff
            closest_color = eval(c)

    return closest_color
