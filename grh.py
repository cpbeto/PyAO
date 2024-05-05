import struct
from struct import Struct


ASSETS_PATH = 'assets/'
GRH_PATH = ASSETS_PATH + 'Graficos3.ind'

TILE_PIXEL_WIDTH = 32.0
TILE_PIXEL_HEIGHT = 32.0

def load():
    with open(GRH_PATH, 'rb') as f:
        # typedef struct {
        #     int32_t version;
        #     int32_t grh_count;
        # } grh_header_t;

        grh_header_t = Struct('<ii')
        data = f.read(grh_header_t.size)
        grh_count = grh_header_t.unpack_from(data)[1]

        grh_data = [None] * (grh_count + 1) # Workaround VB6 1-based indexes

        for _ in range(grh_count):
            # typedef struct {
            #     int16_t sx;
            #     int16_t sy;
            #     uint32_t filenum;
            #     int16_t pixel_width;
            #     int16_t pixel_height;
            #     float tile_width;
            #     float tile_height;
            #     int16_t num_frames;
            #     uint32_t *frames;
            #     float speed;
            # } grh_t;

            grh = {}

            try:
                grh_index_t = Struct('<I')
                data = f.read(grh_index_t.size)
                grh_index = grh_index_t.unpack_from(data)[0]

                num_frames_t = Struct('<h')
                data = f.read(num_frames_t.size)
                num_frames = num_frames_t.unpack_from(data)[0]

                assert num_frames > 0
                grh['num_frames'] = num_frames
                grh['frames'] = []

                if (num_frames == 1):
                    grh_t = Struct('<Ihhhh')
                    keys = ('filenum', 'sx', 'sy', 'pixel_width', 'pixel_height')
                    values = grh_t.unpack_from(f.read(grh_t.size))
                    grh.update(zip(keys, values))

                    grh['tile_width'] = grh['pixel_width'] / TILE_PIXEL_WIDTH
                    grh['tile_height'] = grh['pixel_height'] / TILE_PIXEL_HEIGHT

                    grh['frames'].append(grh_index)
                else:
                    for _ in range(num_frames):
                        frame_t = Struct('<I')
                        frame = frame_t.unpack_from(f.read(frame_t.size))[0]
                        grh['frames'].append(frame)

                    speed_t = Struct('<f')
                    speed = speed_t.unpack_from(f.read(speed_t.size))[0]
                    grh['speed'] = speed

                    frame_1 = grh['frames'][1]
                    grh['pixel_width'] = grh_data[frame_1]['pixel_width']
                    grh['pixel_height'] = grh_data[frame_1]['pixel_height']
                    grh['tile_width'] = grh_data[frame_1]['tile_width']
                    grh['tile_height'] = grh_data[frame_1]['tile_height']

                grh_data[grh_index] = grh
                
            except Exception:
                pass

    return grh_data