import os
import pandas as pd
from lib.lsms import LSMS
def process_tza(data: any, year: str, ppp: int) -> pd.DataFrame:
    """Function to process the Tanzania Survey of 2015. The link between the coordinates of the clusters is done through `hh_sec_a.csv`.

    Args:
        data (any): json entry of the current data
        year (str): current year (should be 2015 in the gives case)
        ppp (int): ppp, for nominal and real cons

    Returns:
        pd.DataFrame: processed dataframe

    """
    df: pd.DataFrame = pd.read_csv(f"../{data['cluster_path']}")
    df_hh: pd.DataFrame = pd.read_csv(f"../{data['hh_path']}")
    tmp: pd.DataFrame = df_hh.merge(df, on=["clusterid"])
    name: str = "TZA-Areallyrandomfile39493208943.csv"  # tmp file
    tmp.to_csv(name)
    lsms: LSMS = LSMS(
        "TZA", year, cons_path=f"../{data['cons_path']}", hh_path=name)
    lsms.read_data()
    lsms.process_survey(cons_key=data["cons_key"], hhsize_key=data["hhsize_key"], lat_key=data["lat_key"],
                        lon_key=data["lon_key"],
                        hhid_key=data["hhid_key"], multiply=data["multiply"], rural_key=data["rural_key"],
                        rural_tag=data["rural"], urban_tag=data["urban"])
    lsms.write_processed(f"../data/lsms/processed/TZA_{year}.csv")
    os.remove(name)
    return lsms.processed
