from PIL import Image
from ursina import Texture


ASSETS_PATH = 'assets/'
GRAPHICS_PATH = ASSETS_PATH + 'graphics/'

TRANSPARENCY_MASK = (0, 0, 0, 255)


class TexturePool:
    def __init__(self):
        self.textures = {}

    def load(self, texture_name, force_load=False):
        if not isinstance(texture_name, str):
            raise TypeError()

        if force_load or texture_name not in self.textures:
            img = Image.open(GRAPHICS_PATH + texture_name + '.BMP')
            img = img.convert('RGBA')

            pixels = img.load()

            width, height = img.size
            for y in range(height):
                for x in range(width):
                    if pixels[x, y] == TRANSPARENCY_MASK:
                        pixels[x, y] = (0, 0, 0, 0)

            self.textures[texture_name] = Texture(img)

        return self.textures[texture_name]

    def __getitem__(self, texture_name):
        return self.load(texture_name)