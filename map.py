import struct
from struct import Struct


ASSETS_PATH = 'assets/'
GRAPHICS_PATH = ASSETS_PATH + 'graphics/'
MAPS_PATH = ASSETS_PATH + 'maps/'

MAP_EXTENSION = '.map'
MAP_WIDTH = 100
MAP_HEIGHT = 100


def load(map_number: int):
    filepath = MAPS_PATH + 'mapa' + str(map_number) + MAP_EXTENSION

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
        s = struct_unpack(data)

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

                tile['npc'] = None
                tile['object'] = None

                tiles.append(tile)

        assert len(tiles) == MAP_WIDTH * MAP_HEIGHT

        map['tiles'] = tiles

    return map