import pandas as pd
import world_bank_data as wb


class LSMS:

    def __init__(self, country_iso: str, year: int, cons_path: str = "", hh_path: str = "", ppp: int = -1, read: bool = False) -> None:
        """Class to process the LSMS surveys. Since the World Bank is collecting the surveys from different sources, we are dealing with heterogenous data with different keys for the same data. The process is the same for all surveys. This class allows to process the data with the different keys for each file. The country and year are requires. By default the files are not read.

        Example:
            You have multiple options to use the object. The simplest one for the survey Nigeria 2015.

            lsms = LSMS('NG', 2015, 'cons_agg_wave3_visit1.csv', 'nga_householdgeovars_y3.csv')
            lsms.read()
            lsms.read_data()
            lsms.process_survey(cons_key='totcons', hhsize_key='hhsize', lat_key='LAT_DD_MOD', lon_key='LON_DD_MOD')

        Args:
            country_iso (str): ISO code of country. Please use the ones [provided](https://microdata.worldbank.org/index.php/api/catalog/country_codes) by the World Bank
            year (int): Specify the year
            cons_path (str): Path to file with the total consumption for a year
            hh_path (str): Path to geovariables which contains the link between the household id and the location of the cluster
            ppp (int): [Purchasing Power Parity](https://en.wikipedia.org/wiki/Purchasing_power_parity), if not provided it will be loaded from the [World Bank](https://data.worldbank.org/indicator/PA.NUS.PRVT.PP) by using  [world-bank-data](https://pypi.org/project/world-bank-data/)
            read (bool): Reading is lazy by default. By setting it `True` you can read it by initialization.             
        """
        self.country_iso: str = country_iso
        self.year: int = year
        self.cons_path: str = cons_path
        self.hh_path: str = hh_path
        self.ppp: float = ppp

        if self.ppp == -1:  # load if not specified
            self.ppp = self.load_ppp()

        self.df_cons = None
        self.df_hh = None
        self.processed = None
        if read:
            self.read_data()

    def load_ppp(self) -> float:
        """Load the [Purchasing Power Parity](https://en.wikipedia.org/wiki/Purchasing_power_parity) of the specified country and year. 

        Returns:
            float: The PPP of the country at year.

        Raises:
            ValueError: If the value is not founded it raises an ValueError. Please look up the [value](https://data.worldbank.org/indicator/PA.NUS.PRVT.PP) here manually. 
        """
        ppp: float = wb.get_series(
            "PA.NUS.PRVT.PP", country=self.country_iso, date=self.year)[0]

        if ppp == None:
            raise ValueError(
                f"ppp not found! Please look up the value manually here: https://data.worldbank.org/indicator/PA.NUS.PRVT.PP?locations={self.country_iso}")
        return ppp

    def read_data(self) -> None:
        """Read the cons. and geovar. file.
        """
        suffix = self.cons_path.split(".")[-1].lower()
        if suffix == "csv":
            cons_reader = pd.read_csv
        else:
            cons_reader = pd.read_spss
        suffix = self.hh_path.split(".")[-1].lower()
        if suffix == "csv":
            hh_reader = pd.read_csv
        else:
            hh_reader = pd.read_spss
        self.df_cons = cons_reader(self.cons_path)
        self.df_hh = hh_reader(self.hh_path)

    def process_survey(self, cons_key: str, hhsize_key: str, lat_key: str, lon_key: str, hhid_key: str = "hhid", rural_key: str = "rural", rural_tag: str = "", urban_tag: str = "", multiply: bool = True) -> None:
        """ Processes the surveys, to aggregate the average per capita consumption for each cluster and adjusted according to the PPP.

        Args:
            cons_key (str): key which contains the total consumption
            hhsize_key (str): key which contains the household size
            lat_key (str): key which contains the latitude of the cluster
            lon_key (str): key which contains the longitude of the cluster
            hhid_key (str): key which contains the household id (default `hhid`)
            rural_key (str): key for rural areas
            rural_tag (str): key for areas which are rural
            urban_tag (str): key for areas which are urban
        """
        # code explains well what we are doing here
        df_cons: pd.DataFrame = self.df_cons.copy()
        if multiply:
            df_cons["_cons_ph_"] = df_cons[cons_key] * df_cons[hhsize_key]
        else:
            df_cons["_cons_ph_"] = df_cons[cons_key]
            
        df_cons["_pph_"] = self.df_cons[hhsize_key]
        df_cons["_cons_ph_"] = df_cons["_cons_ph_"] / self.ppp / 365
        df_cons = df_cons[[hhid_key, "_cons_ph_", "_pph_", rural_key]]

        df_cords: pd.DataFrame = self.df_hh[[hhid_key, lat_key, lon_key]]
        df_cords = df_cords.rename(columns={lat_key: 'lat', lon_key: 'lon'})

        tmp_processed: pd.DataFrame = pd.merge(df_cons, df_cords, on=hhid_key)
        tmp_processed.dropna(inplace=True)  # can't use na values

        rural = tmp_processed[["lat", "lon", rural_key]
                              ].drop_duplicates().dropna()
        rural[rural_key] = rural[rural_key].to_list()

        if urban_tag == "":
            urban_tag = "urban"

        if "," in urban_tag:
            for tag in urban_tag.split(","):
                rural.loc[rural[rural_key].astype(str).str.contains(
                    tag, case=False), rural_key] = "urban"
        else:
            rural.loc[rural[rural_key].astype(str).str.contains(
                urban_tag, case=False), rural_key] = "urban"

        if rural_tag == "":
            rural_tag = "rural"

        if "," in rural_tag:
            for tag in rural_tag.split(","):
                rural.loc[rural[rural_key].astype(str).str.contains(
                    tag, case=False), rural_key] = "rural"
        else:
            rural.loc[rural[rural_key].astype(str).str.contains(
                rural_tag, case=False), rural_key] = "rural"

        self.processed = tmp_processed.groupby(
            ["lat", "lon"]).sum().reset_index()
        
        self.processed["_cons_pc_"] = self.processed["_cons_ph_"] / \
            self.processed["_pph_"]  # divides total cluster income by people
        self.processed["country"] = self.country_iso
        self.processed["year"] = self.year

        # self.processed["id"] = self.processed[hhid_key]
        self.processed = self.processed[[
            "country", "year", "lat", "lon", "_cons_pc_"]]

        self.processed["id"] = [
            f"{self.country_iso}_{self.year}_{i}" for i in range(len(self.processed))]

        self.processed = self.processed.merge(rural, on=["lat", "lon"])

        self.processed = self.processed.rename(
            columns={"_cons_pc_": "cons_pc", rural_key: "rural"})

    def write_processed(self, path: str) -> None:
        """Writes the processed file into the given path.

        Args:
            path (str): Path for writing the file
        """
        self.processed.to_csv(path, index=False)
