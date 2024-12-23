import configparser
import logging
from os import walk
import re

ASSETS_PATH = 'assets/'
INI_PATH = ASSETS_PATH + 'ini/'


class IniManager:
    def load(self):
        self.configs = {}

        # Read all files in INI directory
        _, _, filenames = next(walk(INI_PATH), (None, None, []))
        for filename in filenames:
            try:
                self.configs[filename] = load_file(INI_PATH + filename)
            except configparser.Error as e:
                logging.error(e.message)

    def __getitem__(self, filename):
        return self.configs[filename]


def load_file(filepath):
    config = configparser.ConfigParser(
        comment_prefixes=('#', '\''), inline_comment_prefixes=('#', '\''),
        allow_no_value=True, strict=False
    )

    with open(filepath, mode='r', encoding='cp1252') as f:
        # Read entire file and remove any unnamed section
        text = '\n'.join(f.readlines())
        text = re.sub(r'.*?(?=\[[\w\s]+\])', '', text, count=1, flags=re.DOTALL)

        config.read_string(text)

    return config