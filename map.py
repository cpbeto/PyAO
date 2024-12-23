import struct
from struct import Struct


ASSETS_PATH = 'assets/'
GRAPHICS_PATH = ASSETS_PATH + 'graphics/'
MAPS_PATH = ASSETS_PATH + 'maps/'

MAP_EXTENSION = '.map'
INF_EXTENSION = '.inf'
MAP_WIDTH = 100
MAP_HEIGHT = 100


def load(map_number: int):
    filepath = MAPS_PATH + 'Mapa' + str(map_number) + MAP_EXTENSION

    map = {}
    map['name'] = 'Ullathorpe'
    map['music'] = 'Ullathorpe.ogg'

    with open(filepath, 'rb') as f:

        # typedef struct {
        #     int16_t version;
        #     char desc[255];
        #     int32_t CRC;
        #     int32_t MagicWord;
        #     int16_t padding1;
        #     int16_t padding2;
        #     int16_t padding3;
        #     int16_t padding4;
        # } map_header_t;

        map_header_fmt = '<h255siihhhh'
        map_header_size = struct.calcsize(map_header_fmt)
        struct_unpack = Struct(map_header_fmt).unpack_from

        data = f.read(map_header_size)
        # s = struct_unpack(data)

        tiles = []
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile = {}

                # Read tile flags
                data = f.read(Struct('<B').size)
                flags = Struct('<B').unpack_from(data)[0]
                tile['flags'] = flags
                tile['blocked'] = flags & 1

                # Read tile graphic indexes
                grh = [None] * 4

                data = f.read(Struct('<H').size)
                grh_index = Struct('<H').unpack_from(data)[0]
                grh[0] = grh_index

                if (flags & 2):
                    data = f.read(Struct('<H').size)
                    grh_index = Struct('<H').unpack_from(data)[0]
                    grh[1] = grh_index

                if (flags & 4):
                    data = f.read(Struct('<H').size)
                    grh_index = Struct('<H').unpack_from(data)[0]
                    grh[2] = grh_index

                if (flags & 8):
                    data = f.read(Struct('<H').size)
                    grh_index = Struct('<H').unpack_from(data)[0]
                    grh[3] = grh_index

                tile['grh'] = grh

                # Read tile trigger
                if (flags & 16):
                    data = f.read(Struct('<H').size)
                    trigger = Struct('<H').unpack_from(data)[0]
                    tile['trigger'] = trigger

                tile['exit'] = None
                tile['npc'] = None
                tile['obj'] = None

                tiles.append(tile)

        assert len(tiles) == MAP_WIDTH * MAP_HEIGHT

        map['tiles'] = tiles

        load_inf(map_number, map)

    return map

def load_inf(map_number: int, map: dict):
    filepath = MAPS_PATH + 'Mapa' + str(map_number) + INF_EXTENSION

    with open(filepath, 'rb') as f:

        # typedef struct {
        #     int16_t padding1;
        #     int16_t padding2;
        #     int16_t padding3;
        #     int16_t padding4;
        #     int16_t padding5;
        # } inf_header_t;

        inf_header_fmt = '<hhhhh'
        inf_header_size = struct.calcsize(inf_header_fmt)
        struct_unpack = Struct(inf_header_fmt).unpack_from

        data = f.read(inf_header_size)
        # s = struct_unpack(data)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                # Read tile flags
                data = f.read(Struct('<B').size)
                flags = Struct('<B').unpack_from(data)[0]

                # Exit tile
                if flags & 1:
                    exit = {}

                    data = f.read(Struct('<H').size)
                    exit['map'] = Struct('<H').unpack_from(data)[0]

                    data = f.read(Struct('<H').size)
                    exit['x'] = Struct('<H').unpack_from(data)[0]
                    exit['x'] -= 1 # VB6 indexes are 1-based

                    data = f.read(Struct('<H').size)
                    exit['y'] = Struct('<H').unpack_from(data)[0]
                    exit['y'] -= 1 # VB6 indexes are 1-based

                    map['tiles'][x + 100 * y]['exit'] = exit

                # NPC
                if flags & 2:
                    data = f.read(Struct('<H').size)
                    npc = Struct('<H').unpack_from(data)[0]

                    if npc > 0:
                        map['tiles'][x + 100 * y]['npc'] = npc
                        # TODO: Create NPC
                        pass

                # Object
                if flags & 4:
                    data = f.read(Struct('<H').size)
                    obj_index = Struct('<H').unpack_from(data)[0]

                    data = f.read(Struct('<H').size)
                    obj_amount = Struct('<H').unpack_from(data)[0]

                    map['tiles'][x + 100 * y]['obj'] = {'index': obj_index, 'amount':obj_amount}

    return map