from typing import Tuple

import pandas as pd
from bidict import bidict
from pandas import DataFrame

from lib.lsms_2 import LSMS2, KEYS
from lib.process_lsms import Loader, get_panda_reader


def pack_data(keys: set[str], paths: set[str], used_keys: bidict):
    packed_data = pd.DataFrame()
    loader = Loader(paths, keys)

    path_to_keys: dict[str, list[str]] = loader.match_paths_to_keys()

    for path, keys_in_path in path_to_keys.items():
        reader = get_panda_reader(path)
        # Get columns associated to keys
        data_of_keys = reader(path, usecols=keys_in_path)
        # Aggregate columns found in this file
        if packed_data.empty:
            packed_data = pd.concat([packed_data, data_of_keys], axis=1)
        else:
            on = set(packed_data.columns.values.tolist()) & set(data_of_keys.columns.values.tolist())
            packed_data = pd.merge(packed_data, data_of_keys, on=list(on))
    # Rename keys to default
    packed_data.rename(columns=dict(used_keys.inverse), inplace=True)
    packed_data = packed_data.reindex(columns=KEYS, )

    return packed_data


def uga(keys: set[str], paths: set[str], year: int, country_iso: str, used_keys: bidict, nominal: bool) -> pd.DataFrame:
    data: pd.DataFrame = pack_data(keys, paths, used_keys)
    ppp = 1 if nominal else -1
    lsms: LSMS2 = LSMS2(country_iso, year, data, ppp=ppp)
    lsms.process_survey(used_keys['rural_tag'], used_keys['urban_tag'], used_keys['multiply'], used_keys['monthly'])
    lsms.write_processed(f"../data/lsms/processed/UGA_{year}_{'nominal' if nominal else 'real'}.csv")
    return lsms.processed


def process_uga_2009(metadata: dict) -> tuple[DataFrame, DataFrame]:
    paths = {f'../{file_path}' for file_path in metadata["paths"]}
    keys = {"HHID",
            "lat_mod",
            "lon_mod",
            "welfare",
            "hsize_m",
            "urban"}

    matched_keys = bidict(metadata["keys"])

    df_nominal = uga(keys, paths, country_iso="UGA", year=2009, used_keys=matched_keys, nominal=True)
    df_real = uga(keys, paths, country_iso="UGA", year=2009, used_keys=matched_keys, nominal=False)
    return df_nominal, df_real


def process_uga_2010(metadata: dict) -> tuple[DataFrame, DataFrame]:
    paths = {f'../{file_path}' for file_path in metadata["paths"]}
    # hh and HHID maybe the same
    matched_keys = bidict(metadata["keys"])
    keys = {"HHID",
            "lat_mod",
            "lon_mod",
            "welfare",
            "hsize",
            "urban"}
    # Process UGA, yaer 2010
    df_nominal = uga(keys=keys, paths=paths, country_iso="UGA", year=2010, used_keys=matched_keys, nominal=True)
    df_real = uga(keys=keys, paths=paths, country_iso="UGA", year=2010, used_keys=matched_keys, nominal=False)
    return df_nominal, df_real

