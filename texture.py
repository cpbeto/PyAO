from PIL import Image
from ursina import Texture


ASSETS_PATH = 'assets/'
GRAPHICS_PATH = ASSETS_PATH + 'graphics/'

TRANSPARENCY_MASK = (0, 0, 0, 255)


class TexturePool:
    def __init__(self):
        self.textures = {}

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError()
        
        if key not in self.textures:
            img = Image.open(GRAPHICS_PATH + key + '.BMP')
            img = img.convert('RGBA')

            pixels = img.load()

            width, height = img.size
            for y in range(height):
                for x in range(width):
                    if pixels[x, y] == TRANSPARENCY_MASK:
                        pixels[x, y] = (0, 0, 0, 0)

            self.textures[key] = Texture(img)

        return self.textures[key]