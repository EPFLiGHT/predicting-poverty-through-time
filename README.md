<div align="center">
<h1 align="center">Predicting poverty through time with publicly available data</h1>
</div>
<br>
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#General-Information">General Information</a></li>
    <li><a href="#Run-the-code">Run the code</a></li>
      <ol>
        <li><a href="#google-Colab-Setup">Google Colab</a></li>
        <li><a href="#dependencies">Dependencies</a></li>
        <li><a href="#Data">Data</a></li>
          <ol>
          <li><a href="#WorldBank-LSMS">WorldBank LSMS</a></li>
          <li><a href="#Satellite-data-and-features">Satellite data and features</a></li>
          <li><a href="#OSM-Features">OSM Features</a></li>
          </ol>
        <li><a href="#Evaluation">Evaluation</a></li>
        <li><a href="#Other-figures">Other figures</a></li>
        <li><a href="#lib-folder">Lib folder</a></li>
      </ol>
    <li><a href="#Work-In-Progress">Work In Progress</a></li>
    <li><a href="#Acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<div align="center">
<h2 align="center">General Information</h2>
</div><br>

Fighting poverty remains challenging due to laborious and expensive tracking and targeting methods, especially over time. 
Our work presents an accurate, scalable, inexpensive method to estimate consumption expenditure from publicly available data using surveys, satellite images and OpenStreetMap features from four African countries: **Nigeria**, **Tanzania**, **Ethiopia** and **Malawi**. We're currently testing our model to other countries, expanding our scope also to Asia and South America (see [WIP Section](#Work-in-progress) for more details).

Our approach is capable of predicting consumption through time. The features explain up to 75% of the variation in local-level economic outcomes, and for the temporal prediction, up to 60%. Our method presents a novel way to predict poverty over time. It could transform efforts to understand the development of poverty in developing countries and the tracking and targeting of poverty.

<div align="center">
<h2 align="center">Run the code</h2>
</div><br>

> **Deprecated**: Unfortunately, so far the usage of [colab-ssh](https://github.com/WassimBenzarti/colab-ssh) has been prohibited by Google Colab. You can still follow the procedure at your own risk (see Google Colab [FAQ](https://research.google.com/colaboratory/faq.html#limitations-and-restrictions)). However, we suggest you to skip the next section and simply use Google Colab directly through your browser.

We will present a step-by-step guide to setup the environment, download the data and test the model.

⚠ Disclaimer: we'll use [Google Colab](https://colab.research.google.com/) to execute our code, [VS Code](https://code.visualstudio.com/) as IDE and [ngork](https://ngrok.com/) to authenticate to the Google Colab server. We strongly recommend to use our configuration, in particular Google Colab, as you will directly have access to tools like [Google Earth Engine](https://earthengine.google.com/), [Pytorch](https://pytorch.org/), as well as the GPUs to speed up intensive computations.
However, some of the steps shown are independent from the specific configuration you'll decide to adopt.

### Google Colab SSH Setup

In order to setup the SSH connection to Google Colab follow these steps:

1. Get a free [ngork](https://ngrok.com/) account (you don't have to download ngrok, we'll just use the Authtoken).
2. Once logged in your ngork account, use this [link](https://dashboard.ngrok.com/get-started/your-authtoken) to see your Authtoken and copy it.
3. Using the provided link, open the notebook [SSH-Colab_sample](https://colab.research.google.com/drive/1Hrol-tbYl81RV6XmLCUvBMingZg1bZZZ?usp=sharing) and copy it in your Google Drive. Then fill it with the missing values (your ngork token and the password you'd like to use to connect to the host).
4. Run the notebook and copy the output, as it will be our configuration for the SSH connection (you have to give Colab the permissions to access your Google Drive account).
5. Open VSCode and change the SSH settings: press <kbd>CTRL</kbd> + <kbd>SHIFT</kbd> + <kbd>P</kbd>, select *Open SSH Configuration File* and then any of the file listed. Paste there the output of the Colab session and save. 
6. Now it's time to connect to the host: press again <kbd>CTRL</kbd> + <kbd>SHIFT</kbd> + <kbd>P</kbd>, select *Connect to Host* and then *google_colab_ssh*.
7. Select *Linux* as platform and then insert the password you have chosen in your notebook *colab_ssh*.
8. You should now be connected to the remote host! To install the Python Extension in your IDE, navigate through the tab Extension, search Python and click on *Install in SSH* (you can also install any other extension you like, as well as git by using apt).
9. You will need to attach your Google Drive storage, since the data stored in Colab expires within the session. If you executed correctly *colab_ssh*, you should have your Google Drive folder under the absolute path `/root/gdrive/MyDrive/`.

### Dependencies

All the packages dependencies are listed in the file [requirements.txt](\requirements.txt).
To install them execute `pip install -r requirements.txt`.

### Data

As a starting point, you'll find some pre-downloaded data files in the folder [data](data/). However, due to the size of some files, this is incomplete, thus you can follow the next steps to properly fill the folder and understand the source of our data.

#### WorldBank LSMS

We are using the surveys of the WorldBank as our true gold standart. In particular we'll use the ***Living Standards Measurement Study*** surveys ([LSMS](https://microdata.worldbank.org/index.php/catalog/lsms)). The data can be downloaded manually, however we succeeded in partly automate the process. You will find the code in the subfolder [src/0_lsms_processing](src/0_lsms_processing/):

- [0_download_country_codes](src/0_lsms_processing/0_download_country_codes.ipynb): Execute this notebook to download the country codes for all Sub Saharian African countries from the WorldBank API, in order to have an alignment on the country codes. It's used to update this [file](data/countries_meta/countries_code.csv).
- [1_check_lsms_availability](src/0_lsms_processing/1_check_lsms_availability.ipynb): Execute this notebook to automatically check the availability of LSMS surveys for the given countries. It's used to catalogate the countries in 2 files within the subfolder [data/countries_meta]: the countries which have more than one survey over time [here](data/countries_meta/countries_lsms_time_valid.csv) (it's possible to ***time travel***) and the ones which have just one survey [here](data/countries_meta/countries_lsms_valid.csv). Countries with no survey are so discarded.
- [2_consent_lsms_form](src/0_lsms_processing/2_consent_lsms_form.ipynb): Execute this notebook to automatically download some of the LSMS data (yet you have to do some manual work here). You firstly need to create your WorldBank account, then create a json file `accounts.json` with your credentials to access your WorldBank account of the following structure:
```javascript
{
  "worldbank": {
    "user": "xx",
    "pw": "xx"
  }
}
```
Place it in this current directory. The WorldBank requires to fill a consent form and this notebook does it for us. Follow the procedure explained in the notebook for more details. Alternatevely, you can download our downloaded surveys (not updated) from [here](https://drive.google.com/file/d/1IlF66tdPrty5OmGdWGd7iN39KZCV-iKD/view?usp=sharing) and then place the raw folder in the directory `data/lsms` (the uncompressed folder occupies 3.5GB).
- [3_process_surveys](src/0_lsms_processing/3_process_surveys.ipynb): 
Execute this notebook to preprocess the RAW survey data. Please find the processing steps in [lib/lsms.py](src/lib/lsms.py). After running this code you should have processed survey files in [data/lsms/processed](data/lsms/processed).

> ***Lazy setup***: 
If you don't want to have real-time updated data, you can rely on the data we downloaded and processed. Then, you'll find the data ready to be used [here](data/lsms/processed/).

#### Satellite data and features

Let's now move on the next data to download and process: satellite images!
You will find the code in the subfolder [src/1_feature_generation](src/1_feature_generation/):

- [0_download_satellite.ipynb](src/1_feature_generation/0_download_satellite.ipynb):
Execute this notebook to download the satellite images in the folder `data/tfrecords/raw`. However, in order to execute this locally, you would have to install Earth Engine. Thus, we recommend you to execute a modified [version](https://drive.google.com/file/d/1J8KCAey1WRQmb5qQOCUbbFz1pNqskYDE/view?usp=sharing) on Google Colab, which contains all necessary libs. Keep in mind that both ways you need a [Google Earth Engine](https://earthengine.google.com/) account to execute the code. Researchers, NGO's and country get free access within a short time.

> ***Lazy setup***: 
Alternatevely, you can download the data already downloaded by us from [here](https://drive.google.com/file/d/1HJ3Q6BhmcZsRxb-JjhSkL6zH7hoMj1HB/view?usp=sharing) and place them in the directory `data/tfrecords/raw` (the uncompressed folder occupies 1.76GB).

- You can now train the CNN running the notebook [1_cnn.ipynb](src/1_feature_generation/1_cnn.ipynb). Again, we recommend to execute on Colab the optimized [version](https://drive.google.com/file/d/1P77BSmtxFCypFoo49DxjuOrBG3Hu36bp/view?usp=sharing).

> ***Lazy setup***: 
If you don't want to train the model from scratch, you can download our [weights](https://drive.google.com/file/d/1Vt6wC4d0qdbyzJlIILPCaf8zWoMbTzGB/view?usp=sharing) and place them in the directory `data/cnn_weights`.


⚠ Caution: The tfrecords need a lot of RAM! 

#### OSM Features 

The OpenStreetMap Features extraction is straightforward, just execute [2_osm](src/1_feature_generation/2_osm.ipynb). 

All the OSM extracted features can be found in the [data](data/osm_features) directory. 

> ***Lazy setup***: 
If you don't want to have real-time updated data, you can rely on the data we downloaded. Then, you'll find the data ready to be used [here](data/osm_features/).
### Evaluation 

After you successfully downloaded, processed and extracted everything you can run the models in [2_evaluation](src/2_evaluation).  
- [0_recent_surveys](src/2_evaluation/0_recent_surveys.ipynb): Evaluation of the recent surveys for each country.
- [1_recent_combined](src/2_evaluation/1_recent_combined.ipynb): Evaluation on combined (pooled) features of the most recent surveys of each country.
- [2_time_travel](src/2_evaluation/2_time_travel.ipynb): Evaluation of the prediction through time. 

The figures generated in by this code are saved in the dir [figs](figs/).

### Other figures

The [3_figures](src/3_figures/) contains the code for all the figures generated in the report.

### Lib folder

The [lib folder](src/lib/) contains code used in the notebooks. Please read the code and the comments to understand in depth the functions. Here's an overview:

- [estimator_util](src/lib/estimator_util.py): contains the functions such as the ridge regression and data load for the estimation.
- [lsms](src/lib/lsms.py): Class for processing the surveys.
- [satellite_utils](src/lib/satellite_utils.py): Utils for satellite extraction.
- [tfrecordhelper](src/lib/tfrecordhelper.py): Class for processing tfrecords.

<div align="center">
<h2 align="center">Work In Progress</h2>
</div>

We're working to expand our work to several other countries, not only in the African continent, but also in Asia and South America. We're starting from countries with the highest number of LSMS surveys, you can get our data collection in this [spreadsheet](https://docs.google.com/spreadsheets/d/1zW4eHoUjAnlO5AthVc_PCBbKON2aWPVFCLMjHclapJ8/edit?usp=sharing).

<div align="center">
<h2 align="center">Acknowledgements</h2>
</div>

- [ohsome API](https://github.com/GIScience/ohsome-py): For extracting OSM Features
- [africa-poverty](https://github.com/sustainlab-group/africa_poverty): For satellite extraction code
