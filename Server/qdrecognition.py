from keras.models import load_model
from keras.utils import np_utils
import numpy as np
import pandas as pd
import os
import sys
import cairocffi as cairo

class QdRecognition:
    def __init__(self):
        self.img_height = 28
        self.img_width = 28
        self.img_size = self.img_height * self.img_width
        self.img_dim = 1
        self.num_classes = 1
        self.model_path = os.path.join(sys.path[0], 'resources/model.h5')
        self.model = load_model(self.model_path, custom_objects={"top_3_acc": self.top_3_acc})
        self.labels = pd.read_csv(os.path.join(sys.path[0], 'resources/labels.csv'), index_col=0, header=None,squeeze=True).to_dict()

    def top_3_acc(self, y_true, y_pred):
        return metrics.top_k_categorical_accuracy(y_true, y_pred, k=3)

    def prepare(self, bitmaps):
        bitmaps = np.array(bitmaps)
        bitmaps = bitmaps.astype('float16') / 255.
        bitmaps_to_analyse = np.empty([self.num_classes, len(bitmaps), self.img_size ])
        bitmaps_to_analyse[0] = bitmaps
        bitmaps_to_analyse = bitmaps_to_analyse.reshape(bitmaps_to_analyse.shape[0] * bitmaps_to_analyse.shape[1], self.img_size)
        bitmaps_to_analyse = bitmaps_to_analyse.reshape(bitmaps_to_analyse.shape[0],self.img_width, self.img_height, self.img_dim)
        return bitmaps_to_analyse

    def vector_to_raster(self, vector_images, side=28, line_diameter=16, padding=16, bg_color=(0,0,0), fg_color=(1,1,1)):
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
    
    def recognize(self, drawing):
        drawings = []
        drawings.append(drawing)

        rastered_drawings = self.vector_to_raster(drawings)
        prepared_drawings = self.prepare(rastered_drawings)
        predictions = self.model.predict(prepared_drawings)
        return self.labels[predictions[0].argmax()]
        
if __name__ == '__main__':
    #proper type
    image_data = [((7, 14, 22, 38, 90, 147, 175, 201, 233, 250, 255, 245, 175, 73, 0), (4, 38, 49, 60, 80, 88, 88, 79, 51, 29, 14, 11, 9, 0, 1)), ((71, 69, 72, 96, 179, 184, 182), (80, 96, 101, 111, 119, 114, 98)), ((74, 39, 20, 15, 11, 10, 19, 35, 211, 224, 229, 221, 178), (105, 105, 107, 110, 116, 142, 155, 160, 169, 148, 127, 122, 119))]
    
    # improper type
    image_strokes = [[(7, 4), (14, 38), (22, 49), (38, 60), (90, 80), (147, 88), (175, 88), (201, 79), (233, 51), (250, 29), (255, 14), (245, 11), (175, 9), (73, 0), (0, 1)], [(71, 80), (69, 96), (72, 101), (96, 111), (179, 119), (184, 114), (182, 98)], [(74, 105), (39, 105), (20, 107), (15, 110), (11, 116), (10, 142), (19, 155), (35, 160), (211, 169), (224, 148), (229, 127), (221, 122), (178, 119)]]
    
    qd = QdRecognition()
    print(qd.recognize(image_data))