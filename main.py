from ursina import *
import PIL.Image

import map
import grh

ASSETS_PATH = 'assets/'
GRAPHICS_PATH = ASSETS_PATH + 'graphics/'
MAPS_PATH = ASSETS_PATH + 'maps/'


app = Ursina()

width, height = window.size

camera.orthographic = True
camera.fov = height / 32

Sprite.ppu = 32
Texture.default_filtering = None

map = map.load(1)
tiles = map['tiles']

grh_data = grh.load()

camera_width = ceil(width / 32)
camera_height = ceil(height / 32)


need_to_render = True
position = Vec3(50, 50, 0)
def input(key):
    global need_to_render, position

    need_to_render = True
    if key == 'w':
        position += (0,1,0)
    elif key == 's':
        position -= (0,1,0)
    elif key == 'd':
        position += (1,0,0)
    elif key == 'a':
        position -= (1,0,0)


from pstat_debug import pstat

texture_pool = {}
sprite_pool = {}
@pstat
def render(x, y):
    x, y = int(x), int(y)

    for sprite in sprite_pool.values():
        sprite.disable()

    for j in range(-camera_height, camera_height):
        for i in range(-camera_width, camera_width):
            map_x, map_y = x + i, y + j
            tile = tiles[map_x + 100 * map_y]

            grh_index = tile['grh'][0] # Layer 0
            grh = grh_data[grh_index]

            filenum = grh['filenum']
            if filenum not in texture_pool:
                texture_pool[filenum] = Texture(PIL.Image.open(GRAPHICS_PATH + str(filenum) + '.BMP').convert('RGBA'))

            texture = texture_pool[filenum]
            width, height = texture.size

            if (map_x, map_y) not in sprite_pool:
                s = Sprite(
                    texture,
                    position=(i, j, 0),
                    texture_scale=(grh['pixel_width']/width, grh['pixel_height']/height),
                    texture_offset=(grh['sx']/width, grh['sy']/height)
                )
                s.scale = (1, 1, 1)
                sprite_pool[(map_x, map_y)] = s
            else:
                sprite_pool[(map_x, map_y)].set_position((i, j, 0))
                sprite_pool[(map_x, map_y)].enable()


def update():
    global need_to_render, position

    if need_to_render:
        need_to_render = False
        render(position.x, position.y)

    # global texture_pool, sprite_pool
    # print(f'# Textures: {len(texture_pool)}')
    # print(f'# Sprites: {len(sprite_pool)}')


# from panda3d.core import PStatClient
# PStatClient.connect()

app.run()