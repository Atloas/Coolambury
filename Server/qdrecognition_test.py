from keras.models import load_model
from keras.utils import np_utils
import numpy as np
import os
import sys
import cairocffi as cairo

from PIL import Image, ImageDraw

IMG_HEIGHT = 28
IMG_WIDTH = 28
IMG_SIZE = IMG_HEIGHT * IMG_WIDTH
IMG_DIM = 1
num_classes = 1  # number of scratches type like plane, motor etc


def top_3_acc(y_true, y_pred):
    return metrics.top_k_categorical_accuracy(y_true, y_pred, k=3)


model_path = 'resources/model.h5'


def preparation(bitmap):
    bitmap = np.array(bitmap)
    bitmap = bitmap.astype('float16') / 255.
    bitmaps_to_analyse = np.empty([num_classes, len(bitmap), IMG_SIZE ])
    bitmaps_to_analyse[0] = bitmap
    bitmaps_to_analyse = bitmaps_to_analyse.reshape(bitmaps_to_analyse.shape[0] * bitmaps_to_analyse.shape[1], IMG_SIZE)
    bitmaps_to_analyse = bitmaps_to_analyse.reshape(bitmaps_to_analyse.shape[0],IMG_WIDTH, IMG_HEIGHT, IMG_DIM)
    return bitmaps_to_analyse


def vector_to_raster(vector_images, side=28, line_diameter=16, padding=16, bg_color=(0,0,0), fg_color=(1,1,1)):
    """
    padding and line_diameter are relative to the original 256x256 image.
    """
    
    original_side = 256.
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(line_diameter)

    # scale to match the new size
    # add padding at the edges for the line_diameter
    # and add additional padding to account for antialiasing
    total_padding = padding * 2. + line_diameter
    new_scale = float(side) / float(original_side + total_padding)
    ctx.scale(new_scale, new_scale)
    ctx.translate(total_padding / 2., total_padding / 2.)

    raster_images = []
    for vector_image in vector_images:
        # clear background
        ctx.set_source_rgb(*bg_color)
        ctx.paint()
        
        bbox = np.hstack(vector_image).max(axis=1)
        offset = ((original_side, original_side) - bbox) / 2.
        offset = offset.reshape(-1,1)
        centered = [stroke + offset for stroke in vector_image]

        # draw strokes, this is the most cpu-intensive part
        ctx.set_source_rgb(*fg_color)        
        for xv, yv in centered:
            ctx.move_to(xv[0], yv[0])
            for x, y in zip(xv, yv):
                ctx.line_to(x, y)
            ctx.stroke()

        data = surface.get_data()
        raster_image = np.copy(np.asarray(data)[::4])
        raster_images.append(raster_image)
    
    return raster_images

if __name__ == '__main__':
    full_path = os.path.join(sys.path[0], model_path)
    # print(full_path)
    model = load_model(full_path, custom_objects={"top_3_acc": top_3_acc})

    # print(model.summary())
    
    #proper type
    image_data = [[((7, 14, 22, 38, 90, 147, 175, 201, 233, 250, 255, 245, 175, 73, 0), (4, 38, 49, 60, 80, 88, 88, 79, 51, 29, 14, 11, 9, 0, 1)), ((71, 69, 72, 96, 179, 184, 182), (80, 96, 101, 111, 119, 114, 98)), ((74, 39, 20, 15, 11, 10, 19, 35, 211, 224, 229, 221, 178), (105, 105, 107, 110, 116, 142, 155, 160, 169, 148, 127, 122, 119))]]
    
    # improper type
    image_strokes = [[(7, 4), (14, 38), (22, 49), (38, 60), (90, 80), (147, 88), (175, 88), (201, 79), (233, 51), (250, 29), (255, 14), (245, 11), (175, 9), (73, 0), (0, 1)], [(71, 80), (69, 96), (72, 101), (96, 111), (179, 119), (184, 114), (182, 98)], [(74, 105), (39, 105), (20, 107), (15, 110), (11, 116), (10, 142), (19, 155), (35, 160), (211, 169), (224, 148), (229, 127), (221, 122), (178, 119)]]
    
    rastered_image = vector_to_raster(image_data)
    # print(result)
    
    prepared_image = preparation(rastered_image)
    result =  model.predict(prepared_image)
    print(result[0].argmax())