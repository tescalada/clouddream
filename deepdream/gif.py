from PIL import Image, ImageEnhance, ImageChops
from PIL.GifImagePlugin import getheader, getdata


# modified from https://github.com/wnyc/PIL/blob/master/Scripts/gifmaker.py
def makedelta(fp, sequence):
    """Convert list of image frames to a GIF animation file"""
    frames = 0
    previous = None
    loop_code = '!\xff\x0bNETSCAPE2.0\x03\x01\xff\xff\x00'
    for im in sequence:
        if not previous:
            # global header
            for s in getheader(im)[0] + [loop_code] + getdata(im):
                fp.write(s)
        else:
            # delta frame
            delta = ImageChops.subtract_modulo(im, previous)
            bbox = delta.getbbox()
            if bbox:
                # compress difference
                for s in getdata(im.crop(bbox), offset=bbox[:2]):
                    fp.write(s)
            else:
                # duplicate frame, write anyway
                for s in getdata(im):
                    fp.write(s)
        previous = im.copy()
        frames = frames + 1
    fp.write(";")
    return frames


# modified from http://code.activestate.com/recipes/362879-watermark-with-pil/
def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def blend_img(img1, img2, opacity):
    print "blending images with %d opacity" % opacity
    overlay = reduce_opacity(img2, opacity / 100.0)
    img = Image.composite(overlay, img1, overlay)
    img = img.convert('P', palette=Image.WEB)
    return img


def repeat_img(img, count):
    img = img.convert('P', palette=Image.WEB)
    return [img] * count


def generate_fade_images(start, end, count=10):
    pause_num = count / 2
    step = 100 / count
    start_base = start.convert("RGBA")
    images = []
    images.extend(repeat_img(start, pause_num))
    images.extend([blend_img(start_base, end, opacity) for opacity in range(0, 100 + step, step)])
    images.extend(repeat_img(end, pause_num))
    return images


def make_gif_from_pil_images(start, end, output_file):
    images = generate_fade_images(start, end, 10)
    images.extend(reversed(images))

    # open output file
    with open(output_file, "wb") as fp:
        makedelta(fp, images)


def make_gif(start_file, end_file, output_file):
    start = Image.open(start_file)  # open image
    end = Image.open(end_file)  # open image
    make_gif_from_pil_images(start, end, output_file)


if __name__ == "__main__":
    make_gif(
        start_file='/opt/deepdream/inputs/rupert.jpg',
        end_file='/opt/deepdream/outputs/rupert.jpg',
        output_file='/opt/deepdream/outputs/rupert.jpg',
    )
