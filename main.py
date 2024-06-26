from ursina import *
import PIL.Image

import map
import grh
from texture import TexturePool


ASSETS_PATH = 'assets/'
GRAPHICS_PATH = ASSETS_PATH + 'graphics/'
MAPS_PATH = ASSETS_PATH + 'maps/'

PIXELS_PER_TILE = 32


app = Ursina()

window_width, window_height = window.size

camera.orthographic = True
camera.fov = window_height / PIXELS_PER_TILE
# TODO: EditorCamera()

camera_width = ceil(window_width / PIXELS_PER_TILE)
camera_height = ceil(window_height / PIXELS_PER_TILE)

Sprite.ppu = PIXELS_PER_TILE
Texture.default_filtering = None

map = map.load(1)
tiles = map['tiles']

grh_data = grh.load()


layer_enabled = [True] * 4
need_to_render = True
position = Vec3(50, 50, 0)
def input(key):
    global layer_enabled, need_to_render, position

    if key in 'wasd0123':
        need_to_render = True

    if key == 'w':
        position -= (0,1,0)
    elif key == 's':
        position += (0,1,0)
    elif key == 'd':
        position += (1,0,0)
    elif key == 'a':
        position -= (1,0,0)
    elif key == '0':
        layer_enabled[0] = not layer_enabled[0]
    elif key == '1':
        layer_enabled[1] = not layer_enabled[1]
    elif key == '2':
        layer_enabled[2] = not layer_enabled[2]
    elif key == '3':
        layer_enabled[3] = not layer_enabled[3]


texturePool = TexturePool()
sprite_pool = {}
def render(x, y):
    global layer_enabled

    x, y = int(x), int(y)

    for sprite in sprite_pool.values():
        sprite.disable()

    for k in range(4):
        if not layer_enabled[k]:
            continue
        
        for j in range(-camera_height//2, camera_height//2 + 1):
            for i in range(-camera_width//2, camera_width//2 + 1):
                map_position = Vec3(x + i, y - j, k)

                # Camera out of bounds
                # TODO: Render adyacent map?
                if map_position.x < 0 or map_position.x >= 100:
                    continue
                if map_position.y < 0 or map_position.y >= 100:
                    continue

                # TODO: Clean up these indices
                tile = tiles[int(map_position.x) + 100 * int(map_position.y)]

                # TODO: Re-define these data structures so access is straightforward
                grh_index = tile['grh'][k]
                if not grh_index:
                    continue
                grh = grh_data[grh_index]
                
                if grh['num_frames'] != 1:
                    continue

                filename = str(grh['filenum'])

                texture = texturePool[filename]
                width, height = texture.size

                sprite_position = Vec3(i, j, -k)
                if k in [1, 2, 3]:
                    sprite_position.y += (grh['pixel_height']/PIXELS_PER_TILE - 1) / 2

                # TODO: Clean this up, refactor sprite pool
                if map_position not in sprite_pool:
                    s = Sprite(
                        texture,
                        position=sprite_position,
                        texture_scale=(grh['pixel_width']/width, grh['pixel_height']/height),
                        texture_offset=(grh['sx']/width, height - (grh['sy']/height + grh['pixel_height']/height))
                    )
                    s.scale = (grh['pixel_width']/PIXELS_PER_TILE, grh['pixel_height']/PIXELS_PER_TILE, 1)
                    sprite_pool[map_position] = s
                else:
                    sprite_pool[map_position].set_position(sprite_position)
                    sprite_pool[map_position].enable()


def update():
    global need_to_render, position

    if need_to_render:
        need_to_render = False
        render(position.x, position.y)

app.run()