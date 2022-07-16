"""
Functions of estimation notebooks.
"""
from scipy.stats import pearsonr
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

import ast
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import string
import world_bank_data as wb


def get_data(lsms_path: str, cnn_path: str, osm_path: str):
    """
    Function to load data and merge it

    Args:
    - lsms_path: Path to lsms file
    - cnn_path: Path to cnn feature file
    - osm_path: Base path to OSM files

    Return:
    - pd.Dataframe: features of CNN
    - list: features of OSM
    """
    lsms = pd.read_csv(lsms_path)
    cnn = pd.read_csv(cnn_path, converters={'features': ast.literal_eval})

    lsms[lsms.select_dtypes(np.float64).columns] = lsms.select_dtypes(
        np.float64).astype(np.float32)
    cnn[cnn.select_dtypes(np.float64).columns] = cnn.select_dtypes(
        np.float64).astype(np.float32)

    cnn_lsms = lsms.merge(cnn, on=["lat", "lon", "year"])

    build = pd.read_csv(osm_path + "osm_features/_all_buildings.csv")
    pois = pd.read_csv(osm_path + "osm_features/_all_pois.csv")
    roads = pd.read_csv(osm_path + "osm_features/_all_road.csv")

    build_cols = build.columns[1:]
    pois_cols = pois.columns[:-1]  # id is last column in my case
    roads_cols = roads.columns[1:]

    all_cols = list(build_cols) + list(roads_cols) + list(pois_cols)

    osm = build.merge(pois, on="id")
    osm = osm.merge(roads, on="id")
    complete = osm.merge(cnn_lsms, on="id")

    return complete, all_cols


def run_ridge(X: np.array, y: np.array, alpha: int = 1000, seed=42):
    """
    Run Ridge Regression

    Args:
    - X (np.array): Features
    - y (np.array): Consumption
    - alpha (int): param for Ridge Regression
    - seed (int): For reproducibility

    Return:
    - r^2
    - predicated y
    - model
    """

    kf = KFold(n_splits=10, shuffle=True, random_state=seed)
    r2 = []
    for train_ind, test_ind in kf.split(X, y):
        x_train_fold, x_test_fold = X[train_ind], X[test_ind]
        y_train_fold, y_test_fold = y[train_ind], y[test_ind]
        model = Ridge(alpha)
        model.fit(x_train_fold, y_train_fold)
        y_predict = model.predict(x_test_fold)
        r2.append(pearsonr(y_test_fold, y_predict)[0]**2)

    y_hest = model.predict(X)
    return np.mean(r2), y_hest, model


def run_ridge_out(X: np.array, y: np.array, X_out: np.array, y_out: np.array, alpha: int = 1000):
    """
    Run Ridge Regression with training on X and predictions on X_out

    Args:
    - X (np.array): Features
    - y (np.array): Consumption
    - X_out (np.array): Features for evaluation
    - y_out (np.array): Consumption for evaluation
    - alpha (int): param for Ridge Regression

    Return:
    - r^2
    - predicated y
    - model
    """
    kf = KFold(n_splits=10, shuffle=True, random_state=1)
    r2 = []
    for train_ind, test_ind in kf.split(X, y):
        x_train_fold, x_test_fold = X[train_ind], X[test_ind]
        y_train_fold, y_test_fold = y[train_ind], y[test_ind]

        model = Ridge(alpha)
        model.fit(x_train_fold, y_train_fold)
        y_predict = model.predict(X_out)
        r2.append(pearsonr(y_out, y_predict)[0]**2)

    y_hest = model.predict(X_out)
    return np.mean(r2), y_hest, model


def plot_predictions(y: np.array, yhat: np.array, r2: float, country: str, year: str, n: int, max_y=None, x_label = False):
    """
    Util for plot predictions

    Args:
    - y (np.array): Ground truth
    - y_hat (np.array): Predictions
    - r2 (float): r2 value of predictions
    - country (str): Title (in most cases the country)
    - year (str): Year or timespan
    - n (int): For letter on plot
    - max_y (float): Max consumption 
    - x_label (bool): Check if label for x axis should be added 

    Return:
    - figure
    """
    if max_y is not None:
        yhat = yhat[y < max_y]
        y = y[y < max_y]
    fig = plt.figure(figsize=(5, 8))
    plt.scatter(y, yhat, alpha=0.6)
    plt.plot(np.unique(y), np.poly1d(
        np.polyfit(y, yhat, 1))(np.unique(y)), color='r')
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    plt.xlabel('Observed consumption($/day)', fontsize=14)
    if n == 0 or x_label:
        plt.ylabel('Predicted consumption($/day)', fontsize=14)
    plt.title(fr'$r^2$ {round(r2, 2)}', fontsize=14, loc='left')
    plt.suptitle(f'{country} {year}', ha="left", x=0.119, y=0.95, fontsize=18)
    plt.grid(alpha=1)
    ax.text(-0.1, 1.1, string.ascii_uppercase[n],
            size=20, weight='bold', transform=ax.transAxes)

    return fig

def get_inflation_perf(country, base, target):
    base_infl = wb.get_series("FP.CPI.TOTL", country=country, date=base)[0]
    target_infl = wb.get_series("FP.CPI.TOTL", country=country, date=target)[0]
    return target_infl / base_infl

def get_recent_features(df: pd.DataFrame, countries: list, osm_cols: list, infl: int = 1, scale_cnn: bool = True, scale_complete: bool = True, log_transform = True):
    """
    Return features from most recent survey for a country.

    Args
    - df (pd.Dataframe): Dataframe with data
    - countries (list): Countries for which data is requested
    - osm_cols (list): Columns for OSM features
    - infl (int): infaltion rate for scaling
    - scale_cnn (bool): standard. CNN features
    - scale_complete (bool): standard. combined features
    - log_transform (bool): Log Transform cons. 

    Return:
    - X (np.array): features
    - y (np.array): cons.
    """
    X = None
    y = None

    for country in countries:
        tmp_df = df.loc[df.country == country]
        
        years = tmp_df.groupby(["year"]).groups.keys()
        year = max(years)
        year_df = tmp_df.loc[tmp_df.year == year]
        cnn_X = np.array([np.array(x) for x in year_df["features"].values])
        
        if scale_cnn:
            cnn_X = StandardScaler().fit_transform(cnn_X)
        osm_X = year_df[osm_cols].values
        tmp_X = np.hstack((cnn_X, osm_X))
        y_ = year_df["cons_pc"].values

        if X is None:
            X = tmp_X
        else:
            X = np.vstack((X, tmp_X))
        if y is None:
            y = y_
        else:
            y = np.append(y, y_)

    if scale_complete:
        X = StandardScaler().fit_transform(X)
    
    y /= infl

    if log_transform:
        y = np.log(y)

    return X, y

def get_features(df: pd.DataFrame, countries: list, years: list, osm_cols: list, infl: int = 1, scale_cnn: bool = True, scale_complete: bool = True, log_transform = True):
    """
    Return features for a country by given years..

    Args
    - df (pd.Dataframe): Dataframe with data
    - countries (list): Countries for which data is requested
    - years (list): Selected years
    - osm_cols (list): Columns for OSM features
    - infl (int): infaltion rate for scaling
    - scale_cnn (bool): standard. CNN features
    - scale_complete (bool): standard. combined features
    - log_transform (bool): Log Transform cons. 

    Return:
    - X (np.array): features
    - y (np.array): cons.
    """
    X = None
    y = None

    for country in countries:
        tmp_df = df.loc[df.country == country]
        
        for year in years:
        
            year_df = tmp_df.loc[tmp_df.year == year]
            cnn_X = np.array([np.array(x) for x in year_df["features"].values])
            
            if scale_cnn:
                cnn_X = StandardScaler().fit_transform(cnn_X)
            osm_X = year_df[osm_cols].values
            tmp_X = np.hstack((cnn_X, osm_X))
            y_ = year_df["cons_pc"].values

            if X is None:
                X = tmp_X
            else:
                X = np.vstack((X, tmp_X))
            if y is None:
                y = y_
            else:
                y = np.append(y, y_)

    if scale_complete:
        X = StandardScaler().fit_transform(X)
    
    y /= infl

    if log_transform:
        y = np.log(y)

    return X, y

def get_features_allyears(complete_df, countries, osm_colls):
    """
    Return features for a country with all years in dataset. All data is scaled to inflation rate from 2010 on.

    Args
    - df (pd.Dataframe): Dataframe with data
    - countries (list): Countries for which data is requested
    - osm_cols (list): Columns for OSM features

    Return:
    - X (np.array): features
    - y (np.array): cons.
    """
    X = None
    y = None

    for country in countries:        
        tmp_df = complete_df.loc[complete_df.country == country]
        years = tmp_df.groupby(["year"]).groups.keys()
        for year in years:
            
            year_df = tmp_df.loc[tmp_df.year == year]
            cnn_X = np.array([np.array(x) for x in year_df["features"].values])
            osm_X = year_df[osm_colls].values
            tmp_X = np.hstack((cnn_X, osm_X))
            y_ = year_df["cons_pc"].values
            inflr = get_inflation_perf(country, 2010, year)
            y_ = y_ / inflr
            if X is None:
                X = tmp_X
            else:
                X = np.vstack((X, tmp_X))
            
            if y is None:
                y = y_
            else:
                y = np.append(y, y_)

    X = StandardScaler().fit_transform(X)
    return X, np.log(y)