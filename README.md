# Predicting poverty through time with publicly available data

TLDR: We are using data from Landsat and OpenStreetMap to predict consumption. Consumption is chosen, since we can compare it through time. We are analyzing four African countries, Nigeria, Tanzania, Ethiopia and Malawi. Our approach is capable of predicting consumption through time. The features explains up to 75% of the variation in local-level economic outcomes and for the temporal prediction up to 60%. 

## Running the code

TLDR: Go the `src` dir and follow the steps. 

### Setup
To run the code you have multiple options. For both you have to install the requirements file by executing `pip install -r requirements.txt`.

#### Google Colab

You can use Google Colab to setup a SSH connection and connect your IDE or Editor with your Google Colab machine and work remotely. The benefit here is, you directly using tools like [Google Earth Engine](https://earthengine.google.com/) and [Pytorch](https://pytorch.org/). Also you can use the GPU's. To setup the SSH connection follow the steps:

1. Get a free [ngork](https://ngrok.com/) account and copy your API keys.
2. Open the `colab_ssh.ipynb` in your Colab session and execute it.
3. Open your IDE and change the SSH settings to the one given in the last cell of the `colab_ssh.ipynb` and connect to the machine.
4. Now you should have remote access. You can install git using apt and the Python Extension in your IDE, to execute Jupyter Notebooks. 

#### Run local

Of course you can run the code on your local machine. We strongly recommend to execute the `0.1_download_satellite_colab.ipynb` and `1.1_cnn colab.ipynb` on Google Colab.

### LSMS

We are using the surveys of the WorldBank as our true gold standart. You have to download the [LSMS surveys](https://microdata.worldbank.org/index.php/catalog/lsms) more or less manually. However we automated the process partly. You can find the code in `src/0_lsms_processing`. 

- `src/0_lsms_processing/0_download_country_codes.ipynb`: Download the country codes for all Sub Saharian African countries from the WorldBank API to use the same country codes.
- `src/0_lsms_processing/1_check_lsms_availability.ipynb`: Checks the availability of the LSMS for the given countries.
-  `src/0_lsms_processing/2_consent_lsms_form.ipynb`: Poor mans approach to automate the download. The WorldBank requires to fill a consent form and this file does it for us and downloads the survey files for us. You can download our downloaded surveys from [here](https://drive.google.com/file/d/1IlF66tdPrty5OmGdWGd7iN39KZCV-iKD/view?usp=sharing).
-  `src/0_lsms_processing/3_process_surveys.ipynb`: Preprocesses the RAW survey data. Please find the processing steps in `src/lib/lsms.py`. 

After running this code you should have processed survey files in `data/lsms/processed`.

### Satellite data and features

To download the data please execute the [0_download_satellite.ipynb](src/1_feature_generation/0_download_satellite.ipynb) notebook. However we recommend you to execute it on Google Colab. For this we have a modified [Colab](src/1_feature_generation/0.1_download_satellite_colab.ipynb) of the notebook, which contains all necessary libs. Since you would need to install Earth Engine locally. You also need a [Google Earth Engine account](https://earthengine.google.com/) to execute the code. Researchers, NGO's and country get free access within a short time. You can download our extracted data from [here](https://drive.google.com/file/d/1HJ3Q6BhmcZsRxb-JjhSkL6zH7hoMj1HB/view?usp=sharing).

After you download the data you can train the CNN using [1_cnn.ipynb](src/1_feature_generation/1_cnn.ipynb). Again we recommend to execute it on Colab for this you can use our [colab](src/1_feature_generation/1.1_cnn colab.ipynb) version. If you don't want to train the network from scratch, you can use our [weights](https://drive.google.com/file/d/1Vt6wC4d0qdbyzJlIILPCaf8zWoMbTzGB/view?usp=sharing).

⚠ Caution: The tfrecords need a lot of RAM! 

### OSM Features 

The OpenStreetMap Features extraction is straight forward, just execute [2_osm](src/1_feature_generation/2_osm.ipynb). 


All the extracted features can be found in the [data](data/) directory. 

### Evaluation 

After you successfully downloaded, processed and extracted everything you can run the models in [2_evaluation](src/2_evaluation).  
- [0_recent_surveys](src/2_evaluation/0_recent_surveys.ipynb): Evaluation of the recent surveys for each country.
- [1_recent_combined](src/2_evaluation/1_recent_combined.ipynb): Evaluation on combined (pooled) features of the most recent surveys of each country.
- [3_time_travel](src/2_evaluation/3_time_travel.ipynb): Evaluation of the prediction through time. 

The figures generated in by this code are saved in the dir [figs](figs/).

### Other figures

The [3_figures](src/3_figures/) contains the code for all the figures generated in the report.

## Acknowledgements
- [ohsome API](https://github.com/GIScience/ohsome-py): For extracting OSM Features
- [africa-poverty](https://github.com/sustainlab-group/africa_poverty): For satellite extraction code