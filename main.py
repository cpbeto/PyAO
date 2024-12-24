import json
import sys

from ursina import *
import PIL.Image

import map
import grh
import ini
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

map_pool = {}
grh_data = grh.load()
ini_manager = ini.IniManager()
ini_manager.load()

layer_enabled = [True] * 4
need_to_render = True
position = Vec4(50, 50, 0, 1) # x, y, z-index, map-index
def input(key):
    global layer_enabled, need_to_render, position

    if key in 'wasd0123':
        need_to_render = True

    # TODO: Abstract into Camera, Player or Position class
    if key in 'wasd':
        if key == 'w':
            position += (0,-1)
        elif key == 's':
            position += (0,1)
        elif key == 'd':
            position += (1,0)
        elif key == 'a':
            position += (-1,0)

        map = map_pool[position.w]
        tile = map['tiles'][int(position.x) + 100 * int(position.y)]

        # Change map
        if tile['exit']:
            position = Vec4(tile['exit']['x'], tile['exit']['y'], position.z, tile['exit']['map'])
    else:
        if key == '0':
            layer_enabled[0] = not layer_enabled[0]
        elif key == '1':
            layer_enabled[1] = not layer_enabled[1]
        elif key == '2':
            layer_enabled[2] = not layer_enabled[2]
        elif key == '3':
            layer_enabled[3] = not layer_enabled[3]


texturePool = TexturePool()
sprite_pool = {}
npc_pool = {}
obj_pool = {}
def render(camera_position: Vec4):
    camera_position = round(camera_position)

    # TODO: Abstract into MapPool class
    if camera_position.w not in map_pool:
        map_pool[camera_position.w] = map.load(int(camera_position.w))

    # TODO: Unify entity pooling
    for sprite in sprite_pool.values():
        sprite.disable()
    for npc_entity in npc_pool.values():
        npc_entity.disable()
    for obj_entity in obj_pool.values():
        obj_entity.disable()

    for z in range(4):
        camera_position.z = z

        for j in range(-camera_height//2, camera_height//2 + 1):
            for i in range(-camera_width//2, camera_width//2 + 1):
                screen_position = Vec3(i, j, -z)
                world_position = camera_position + (i,-j)

                # Camera out of bounds
                # TODO: Render adyacent map?
                if world_position.x < 0 or world_position.x >= 100:
                    continue
                if world_position.y < 0 or world_position.y >= 100:
                    continue

                tiles = map_pool[world_position.w]['tiles']

                # TODO: Improve tile indexing
                tile = tiles[int(world_position.x) + 100 * int(world_position.y)]

                if layer_enabled[z]:
                    # TODO: Redefine these data structures so access is straightforward
                    grh_index = tile['grh'][z]
                    if not grh_index:
                        continue
                    grh = grh_data[grh_index]

                    if grh['num_frames'] != 1:
                        continue

                    filename = str(grh['filenum'])

                    texture = texturePool[filename]
                    width, height = texture.size

                    # Ad hoc offset found in legacy code
                    if z in [1, 2, 3]:
                        screen_position.y += (grh['pixel_height']/PIXELS_PER_TILE - 1) / 2

                    # TODO: Clean this up, refactor sprite pool
                    if world_position not in sprite_pool:
                        s = Sprite(
                            texture,
                            position=screen_position,
                            texture_scale=(grh['pixel_width']/width, grh['pixel_height']/height),
                            texture_offset=(grh['sx']/width, height - (grh['sy']/height + grh['pixel_height']/height))
                        )
                        s.scale = (grh['pixel_width']/PIXELS_PER_TILE, grh['pixel_height']/PIXELS_PER_TILE, 1)
                        sprite_pool[world_position] = s
                    else:
                        sprite_pool[world_position].set_position(screen_position)
                        sprite_pool[world_position].enable()

                if z == 0:
                    if tile['npc']:
                        npc_index = tile['npc']
                        if npc_index not in npc_pool:
                            npc_entity = Entity(model='cube', color=color.gold, collider='box', position=screen_position, scale=(0.5, 0.5))
                            npc_pool[npc_index] = npc_entity
                        npc_pool[npc_index].set_position(screen_position)
                        npc_pool[npc_index].enable()

                    if tile['obj']:
                        obj_index = tile['obj']['index']
                        if world_position not in obj_pool:
                            # obj_entity = Entity(model='cube', color=color.blue, collider='box', position=screen_position, scale=(0.5, 0.5))
                            objs = ini_manager['obj.dat']
                            grh_index = objs[f'OBJ{obj_index}'].getint('GrhIndex')
                            if not grh_index or grh_data[grh_index]['num_frames'] != 1:
                                obj_entity = Entity(model='cube', color=color.gray, collider='box', position=screen_position, scale=(0.5, 0.5))
                            else:
                                grh = grh_data[grh_index]
                                filename = str(grh['filenum'])
                                texture = texturePool[filename]
                                width, height = texture.size
                                screen_position.y += (grh['pixel_height'] / PIXELS_PER_TILE - 1) / 2
                                obj_entity = Sprite(
                                    texture,
                                    position=screen_position,
                                    texture_scale=(grh['pixel_width'] / width, grh['pixel_height'] / height),
                                    texture_offset=(
                                    grh['sx'] / width, height - (grh['sy'] / height + grh['pixel_height'] / height))
                                )
                            obj_pool[world_position] = obj_entity
                        obj_pool[world_position].set_position(screen_position)
                        obj_pool[world_position].enable()


def update():
    global need_to_render

    if need_to_render:
        need_to_render = False
        render(position)

app.run()