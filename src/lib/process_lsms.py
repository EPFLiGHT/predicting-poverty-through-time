import os

import pandas as pd

from enum import Enum
from functools import reduce
from logging import warning, error


class Format(Enum):
    CSV = 'csv'
    SPSS = 'sav'


def get_panda_reader(filename: str, valid_types=None):
    if valid_types is None:
        valid_types = {'csv', 'spss', 'sav'}

    if not filename:
        error("Provided filename is None please give a valid filename")
        raise ValueError()
    suffix = filename.split('.')[-1].lower()

    if suffix not in valid_types:
        error("Provided file is not of a valid type. Allowed types are %s", valid_types)
        raise ValueError()

    match suffix:
        case 'csv':
            return pd.read_csv
        case 'spss' | 'sav':
            return pd.read_spss
        case _:
            raise ValueError(f'Invalid file type {suffix}')


class Loader:
    _paths: set[str]
    _keys: set[str]
    _matches: dict[str, list[str]]
    _reader: callable

    def __init__(self, _paths: set[str], _keys: set[str], _format: Format = Format.CSV):

        if not _paths or not _keys:
            raise ValueError("One of the provided lists is empty")

        self._paths = _paths
        self._keys = _keys

        # Set adequate reader
        match _format:
            case Format.CSV:
                _reader = pd.read_csv
            case Format.SPSS:
                _reader = pd.read_spss

    def match_paths_to_keys(self) -> dict[str, list[str]]:
        # Check for empty paths
        not_existing = [p for p in self._paths if not os.path.exists(p)]

        # Displays empty paths
        if not_existing:
            error("The paths does not exist %s", not_existing)

        # Read headers only from files in paths
        # get_panda_reader to get reader for file
        headers = {path:  get_panda_reader(path)(path).columns.values for path in self._paths}

        matches = {path: [] for path in self._paths}
        for path, header in headers.items():
            matching_keys = [key for key in self._keys if key in header]
            matches[path] = matching_keys

        # Warn that a path was ot used
        not_used_paths = self._paths ^ set(headers.keys())
        if not_used_paths:
            warning('Some paths were not used %s', not_used_paths)

        # Warn for not found keys
        not_found_keys = self._keys ^ set(reduce(lambda l1, l2: l1 + l2, matches.values()))
        if not_found_keys:
            warning('Some of the keys were not found in files %s', not_found_keys)

        return matches

    def get_data(self):
        # Get matches not already
        if not self._matches:
            self._matches = self.match_paths_to_keys()

        data: pd.DataFrame = pd.DataFrame()
        for path, keys in self._matches.items():
            data_keys = pd.read_csv(path, names=keys)
            data = pd.concat(data, data_keys)


if __name__ == '__main__':
    paths = {
        r'C:\Users\Mohamed\Desktop\Master\MA1\ML\ML4Science\forked-cm110-poverty\data\lsms\raw\UGA_2010_UNPS_v02_M_CSV\pov2010_11.csv',
        r'C:\Users\Mohamed\Desktop\Master\MA1\ML\ML4Science\forked-cm110-poverty\data\lsms\raw\UGA_2010_UNPS_v02_M_CSV\Socio\UNPS_Geovars_1011.csv'}
    keys = {'hh', 'lat_mod', 'lon_mod', 'pop', 'hsize', 'welfare', 'HHID'}
    loader = Loader(paths, keys, Format.CSV)

    import pprint

    print(pprint.pprint(loader.match_paths_to_keys()))
