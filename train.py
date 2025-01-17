# -*- coding: utf-8 -*-
"""LAB 5. Regression. Linear Models SOLUTION.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZF551YYY6DAEBZfh_TIahtvmU2lh6Ci5

# Regression: New York City Taxi Trip Duration

For the following tasks, you will work with the dataset from the [Playground Prediction Competition: New York City Taxi Trip Duration](https://www.kaggle.com/competitions/nyc-taxi-trip-duration/code?competitionId=6960&sortBy=voteCount).

Based on individual trip attributes, the duration of the trip should be predicted.

**Data fields**

* `id` - a unique identifier for each trip
* `vendor_id` - a code indicating the provider associated with the trip record
* `pickup_datetime` - date and time when the meter was engaged
* `dropoff_datetime` - date and time when the meter was disengaged
* `passenger_count` - the number of passengers in the vehicle (driver entered value)
* `pickup_longitude` - the longitude where the meter was engaged
* `pickup_latitude` - the latitude where the meter was engaged
* `dropoff_longitude` - the longitude where the meter was disengaged
* `dropoff_latitude` - the latitude where the meter was disengaged
* `store_and_fwd_flag` - This flag indicates whether the trip record was held in vehicle memory before sending to the vendor because the vehicle did not have a connection to the server - Y=store and forward; N=not a store and forward trip
* `trip_duration` - duration of the trip in seconds (**target variable**)
"""

import pandas as pd
import numpy as np
import mlflow
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler


import common as common
# Gobal variables
DATA_PATH = common.CONFIG['paths']['path_data']
DIR_MLRUNS = common.CONFIG['paths']['mlruns']

TARGET = common.CONFIG['ml']['target_name']
RANDOM_STATE = common.CONFIG['ml']['random_state']

EXPERIMENT_NAME = common.CONFIG['mlflow']['experiment_name']
MODEL_NAME = common.CONFIG['mlflow']['model_name']
MODEL_VERSION = common.CONFIG['mlflow']['model_version']

def load_data():
    data = pd.read_csv(DATA_PATH, compression='zip')

    data['pickup_datetime'] = pd.to_datetime(data['pickup_datetime'])

    X = data.drop(columns=[TARGET])
    y = data[TARGET]
    
    return X, y


def transform_target(y):
    return np.log1p(y).rename('log_'+y.name)


def inverse_transform_target(y):
    return np.expm1(y)


def step1_add_features(X):
    res = X.copy()
    
    df_abnormal_dates = X.groupby('pickup_date').size()
    abnormal_dates = df_abnormal_dates[df_abnormal_dates < 6300]
    
    res['weekday'] = res['pickup_datetime'].dt.weekday
    res['month'] = res['pickup_datetime'].dt.month
    res['hour'] = res['pickup_datetime'].dt.hour
    res['abnormal_period'] = res['pickup_datetime'].dt.date.isin(abnormal_dates.index).astype(int)
    
    return res


def perform_preprocessing(X: pd.DataFrame, y: pd.Series):
    y = transform_target(y)
    X['pickup_date'] = X['pickup_datetime'].dt.date

    X = step1_add_features(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=RANDOM_STATE)
    print(f"{len(X_train)} objects in train set, {len(X_test)} objects in test set")
    
    return X_train, y_train, X_test, y_test


def perform_fitting_model(model, X_train, y_train, X_test, y_test):
    # Entraînement
    model.fit(X_train, y_train)

    # Signature du modèle
    signature = mlflow.models.infer_signature(X_train, y_train)

    # Logging du modèle
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="sklearn-model",
        signature=signature,
    )
    
    print(pd.concat([X_train, y_train], axis=1).head())
    
    # Évaluation du modèle
    results = mlflow.evaluate(
        model_info.model_uri,
        data=pd.concat([X_test, y_test], axis=1),
        targets="log_trip_duration",
        model_type="regressor",
        evaluators=["default"]
    )

    # Log des métriques
    mlflow.log_metric("rmse", results.metrics['root_mean_squared_error'])
    mlflow.log_metric("r2", results.metrics['r2_score'])

    return results


def perform_predict(X: pd.DataFrame):
    #load the model
    print("#"*20)
    print("Load model from the model registry")
    model_uri = f"models:/{MODEL_NAME}/{MODEL_VERSION}"
    print(f"Model URI: {model_uri}")
    model = mlflow.pyfunc.load_model(model_uri=model_uri)
    
    input_data = X.astype({
        "hour": np.int32,
        "abnormal_period": np.int32,
        "weekday": np.int32,
        "month": np.int32
    })
    
    prediction = model.predict(input_data)
    prediction = inverse_transform_target(pd.Series(prediction))[0]
    
    return prediction


if __name__ == '__main__':
    
    mlflow.set_tracking_uri("file:" + DIR_MLRUNS)
    
    np.random.seed(RANDOM_STATE)
    
    X, y = load_data()
    X_train, y_train, X_test, y_test = perform_preprocessing(X, y)
    
    exp_name = "nyc_taxi_trip_duration"
    mlflow.set_experiment(exp_name)
    
    run_name = "Ridge"
    best_score = float('inf')
    best_run_id = None
    
    with mlflow.start_run(run_name=run_name, description="Ridge regression") as run:
        num_features = ['abnormal_period', 'hour']
        cat_features = ['weekday', 'month']
        train_features = num_features + cat_features
        
        column_transformer = ColumnTransformer([
            ('ohe', OneHotEncoder(handle_unknown="ignore"), cat_features),
            ('scaling', StandardScaler(), num_features)]
        )
        
        pipeline = Pipeline(steps=[
            ('ohe_and_scaling', column_transformer),
            ('regression', Ridge())
        ])
        
        results = perform_fitting_model(pipeline, X_train[train_features], y_train, X_test[train_features], y_test)
        # mlflow.log_param("alpha", model.alpha)
        if results.metrics['root_mean_squared_error'] < best_score:
            best_score = results.metrics['root_mean_squared_error']
            best_run_id = run.info.run_id
        print(f"rmse: {results.metrics['root_mean_squared_error']}")
        print(f"r2: {results.metrics['r2_score']}")
        
    # register_model(best_run_id)