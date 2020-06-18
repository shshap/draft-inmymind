import logging
import struct
from urllib.parse import urlparse
import PIL

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


PATH_LARGE_DATA = 'file://localhost/data/inmymind_%d_%d_%s_data.%s'


def parse_pose(dict_pose: dict) -> str:
    return dict_pose


def parse_feelings(dict_feelings: dict) -> str:
    return dict_feelings


def _parse_rgb_colorimage_helper(dict_color: dict) -> str:
    dimensions = dict_color['color_image']['width'], dict_color['color_image']['height']
    size = dimensions[0] * dimensions[1] * 3
    pixels = struct.unpack(f'{size}B', dict_color['color_image']['data'])
    pixels = [pixels[i:i + 3] for i in range(0, size, 3)]
    image = PIL.Image.new('RGB', dimensions)
    image.putdata(pixels)
    path = PATH_LARGE_DATA % (dict_color['user_id'], dict_color['datetime'], "color", "jpg")
    # image.show()
    print(f'path of file is {urlparse(path).path[1:]}')
    image.save(urlparse(path).path[1:])
    return path


def parse_colorimage(dict_color: dict) -> str:
    path = _parse_rgb_colorimage_helper(dict_color)
    dict_color['color_image'].pop('data')
    dict_color['color_image'].update({'path': path, 'content_type': 'image/jpg'})
    return dict_color


def _parse_depthimage_helper(dict_depth: dict) -> str:
    dimensions = dict_depth['depth_image']['height'], dict_depth['depth_image']['width']
    pixels = np.asarray(dict_depth['depth_image']['data'])
    array_data = pixels.reshape(dimensions)
    path = PATH_LARGE_DATA % (dict_depth['user_id'], dict_depth['datetime'], "depth", "jpg")
    plt.imsave(urlparse(path).path[1:], array_data, cmap="hot")
    # plt.show()
    return path


def parse_depthimage(dict_depth: dict) -> str:
    path = _parse_depthimage_helper(dict_depth)
    dict_depth['depth_image'].pop('data')
    dict_depth['depth_image'].update({'path': path, 'content_type': 'image/jpg'})
    return dict_depth
