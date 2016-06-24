import os


# Formats supported by the browser
raster_formats = ["jpg", "jpeg", "webp", "gif", "png", "apng", "tiff", "bmp", "ico"]
vector_formats = ["svg", "pdf"]
img_formats = raster_formats + vector_formats

data_formats = ["nc", "hdf5", "hdf4", "bin", "ascii", "text", "txt", "grib", "grb", "ctl", "xml", "pp", "dic"]


def is_img(path):
    _, ext = os.path.splitext(path)
    return ext[1:].lower() in img_formats


def is_data(path):
    _, ext = os.path.splitext(path)
    return ext[1:].lower() in data_formats
