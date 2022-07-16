from __future__ import annotations
from collections.abc import Mapping

import tensorflow as tf
import numpy as np

class TfrecordHelper():
    def __init__(self, path: str, ls_bands = "ms", nl_band = None):
        """
        Init function for creating the TfrecordHelper object.

        Args:
        - path (str): Path where tfrecord file is located.
        - ls_bands (str): Select landsat bands, "ms" (default) for all bands or "rgb" for RED, BLUE, GREEN bands.
        - nl_bands (str): For including the nightlight band, set any other value then None (default).

        """

        self.raw_dataset: tf.TFRecordDataset = tf.data.TFRecordDataset(path, compression_type="GZIP")
        self.dataset: tf.TFRecordDataset | None = None
        self.ls_bands: str = ls_bands
        self.nl_band: str | None = nl_band
        self.nbands = 8
        # use the keywords used in the csv file to scrape the tfrecords from gee
        self.keyword_year = "year"
        self.keyword_lat = "lat"
        self.keyword_lon = "lon"
        self.scalar_keys = [self.keyword_lat, self.keyword_lon, self.keyword_year] # used 
        self.means = None
        self.stads = None
    
    def process_dataset(self, normalize = False):
        """
        Method for processing the raw_dataset based on selected bands.
        """
        
        x = np.empty(shape=(255**2))
        x.fill(0)
        def_value = tf.convert_to_tensor(x, tf.float32)

        def process_tfrecord(record: tf.train.Example) -> dict[any, any, any]:
            """
            Helper function for the map call, which processes the each tfrecord (feature).

            Args: 
            - record (tf.train.Example): feature to process
            
            Returns: 
            result (dict[any, any, any]): contains processed feature
            """
            bands = []
            if self.ls_bands == "rgb":
                # bands = ["BLUE", "GREEN", "RED"]  # BGR order
                bands = ["RED", "GREEN", "BLUE"]
            elif self.ls_bands == "ms":
                bands = ["RED", "GREEN", "BLUE", "SWIR1", "SWIR2", "TEMP1", "NIR"]
            if self.nl_band is not None:
                bands += ["NIGHTLIGHTS"]

            keys_to_features = {}
            for band in bands:
                keys_to_features[band] = tf.io.FixedLenFeature(shape=[255**2], dtype=tf.float32, default_value=def_value)
            for key in self.scalar_keys:
                keys_to_features[key] = tf.io.FixedLenFeature(shape=[], dtype=tf.float32)
        
            
           
            # cons_pc = tf.cast(ex.get("cons_pc", -1), tf.float32)

            ex = tf.io.parse_single_example(record, features=keys_to_features)
            loc = tf.stack([ex[self.keyword_lat], ex[self.keyword_lon]])
            year = tf.cast(ex.get("year", -1), tf.int32)
            for band in bands:
                ex[band].set_shape([255 * 255])
                # reshape to (255, 255) and crop to (224, 224)
                ex[band] = tf.reshape(ex[band], [255, 255])[15:-16, 15:-16]
                if normalize:
                    if band == "NIGHTLIGHTS":
                        ex[band] = (ex[band] - self.means["VIIRS"]) / self.stads["VIIRS"]
                    else:
                        ex[band] = (ex[band] - self.means[band]) / self.stads[band]

            img = tf.stack([ex[band] for band in bands], axis=2)
            result = {"images": img, "locs": loc, "years": year}
            return result
        
        self.dataset = self.raw_dataset.map(process_tfrecord, num_parallel_calls=3)
    